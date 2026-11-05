#!/usr/bin/env python3
"""Measure a change, and find names that exist only in that change.

Read-only: the script runs only git rev-parse, merge-base, diff, show, grep,
and ls-files.

  measure.py size  BASE HEAD [--worktree] [--files] [--json]
                   [--test GLOB]... [--generated GLOB]...
  measure.py leaks BASE HEAD TEXT_FILE

Both commands compare HEAD with the merge-base of BASE and HEAD, the same
range as `git diff BASE...HEAD`.
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

CATEGORIES = ("production", "tests", "generated", "docs")
TEST_DIRS = {"test", "tests", "__tests__", "e2e", "spec", "specs", "fixtures",
             "testdata", "test-data", "__mocks__", "mocks", "stories", "benches",
             "test_support", "test-support", "test_utils", "test-utils", "testutils"}
TEST_NAMES = ("*.test.*", "*.spec.*", "*_test.*", "*_tests.*", "test_*.py",
              "*Test.*", "*Tests.*", "*.stories.*", "conftest.py", "tests.rs",
              "*_fixtures.*", "fixtures.*", "*test_support.*", "*test_utils.*",
              "*test_helpers.*")
GENERATED_DIRS = {"generated", "__generated__", "__snapshots__", "captures",
                  "recordings", "cassettes", "dist"}
GENERATED_NAMES = ("package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml",
                   "yarn.lock", "bun.lockb", "Cargo.lock", "poetry.lock",
                   "uv.lock", "Pipfile.lock", "go.sum", "Gemfile.lock",
                   "composer.lock", "*.snap", "*.min.js", "*.min.css",
                   "*.generated.*", "*.pb.go", "*_pb2.py")
DOC_DIRS = {"docs", "doc"}
DOC_NAMES = ("*.md", "*.mdx", "*.rst", "*.adoc")

RUST_CFG_TEST = re.compile(r"^\s*#\[cfg\(test\)\]")
RUST_MOD_OPEN = re.compile(r"^\s*(pub(\([^)]*\))?\s+)?mod\s+\w+\s*\{")
HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
MIXED_CASE = re.compile(r"[a-z][A-Z]|[A-Z]{2}[a-z]")
DIFF_FLAGS = ("--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/")


def git(repo, *args, ok=(0,)):
    result = subprocess.run(
        ["git", "-C", repo, "-c", "core.quotePath=false", *args],
        capture_output=True, check=False)
    if result.returncode not in ok:
        sys.exit(f"git {' '.join(args)} failed:\n"
                 + result.stderr.decode(errors="replace"))
    return result.stdout.decode(errors="replace")


def resolve_range(repo, base, head):
    root = git(repo, "rev-parse", "--show-toplevel").strip()
    base_sha = git(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
    head_sha = git(root, "rev-parse", "--verify", f"{head}^{{commit}}").strip()
    merge_base = git(root, "merge-base", base_sha, head_sha).strip()
    return root, merge_base, head_sha


def matches(value, patterns):
    return any(fnmatch.fnmatchcase(value, pattern) for pattern in patterns)


def classify(path, extra_tests, extra_generated):
    parts = path.split("/")
    name, dirs = parts[-1], set(parts[:-1])
    if matches(path, extra_generated) or matches(name, GENERATED_NAMES) or dirs & GENERATED_DIRS:
        return "generated"
    if matches(path, extra_tests) or matches(name, TEST_NAMES) or dirs & TEST_DIRS:
        return "tests"
    if matches(name, DOC_NAMES) or dirs & DOC_DIRS:
        return "docs"
    return "production"


def count_lines(data):
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def numstat(root, merge_base, head, worktree):
    target = [] if worktree else [head]
    fields = git(root, "diff", "--numstat", "-z", "-M", *DIFF_FLAGS,
                 merge_base, *target).split("\0")
    rows, i = [], 0
    while i < len(fields):
        entry = fields[i]
        if not entry.strip():
            i += 1
            continue
        added, deleted, path = entry.split("\t", 2)
        if path == "":
            # Rename or copy: the old path and the new path follow.
            old, path = fields[i + 1], fields[i + 2]
            i += 3
        else:
            old = path
            i += 1
        binary = added == "-"
        rows.append({"path": path, "old": old, "binary": binary,
                     "added": 0 if binary else int(added),
                     "deleted": 0 if binary else int(deleted)})
    if worktree:
        untracked = git(root, "ls-files", "-z", "--others", "--exclude-standard")
        for path in filter(None, untracked.split("\0")):
            with open(os.path.join(root, path), "rb") as handle:
                data = handle.read()
            binary = b"\0" in data
            rows.append({"path": path, "old": path, "binary": binary,
                         "added": 0 if binary else count_lines(data),
                         "deleted": 0, "untracked": True})
    return rows


def read_version(root, rev, path, worktree):
    if worktree:
        try:
            with open(os.path.join(root, path), encoding="utf-8", errors="replace") as handle:
                return handle.read()
        except OSError:
            return ""
    return git(root, "show", f"{rev}:{path}", ok=(0, 128))


def rust_test_ranges(text):
    """Return 1-based inclusive line ranges of inline `#[cfg(test)] mod x { }` blocks."""
    lines, ranges, i = text.splitlines(), [], 0
    while i < len(lines):
        if RUST_CFG_TEST.match(lines[i]):
            j = i + 1
            while j < len(lines) and (not lines[j].strip()
                                      or lines[j].lstrip().startswith(("#[", "//"))):
                j += 1
            if j < len(lines) and RUST_MOD_OPEN.match(lines[j]):
                depth, k = 0, j
                while k < len(lines):
                    depth += lines[k].count("{") - lines[k].count("}")
                    if depth <= 0:
                        break
                    k += 1
                end = min(k, len(lines) - 1)
                ranges.append((i + 1, end + 1))
                i = end + 1
                continue
        i += 1
    return ranges


def in_ranges(line, ranges):
    return any(start <= line <= end for start, end in ranges)


def rust_inline_test_lines(root, merge_base, head, worktree, row):
    """Count added and deleted lines of a Rust file that are inside inline test modules."""
    new_ranges = rust_test_ranges(read_version(root, head, row["path"], worktree))
    old_ranges = rust_test_ranges(read_version(root, merge_base, row["old"], False))
    if not new_ranges and not old_ranges:
        return 0, 0
    target = [] if worktree else [head]
    paths = sorted({row["old"], row["path"]})
    diff = git(root, "diff", "-U0", "-M", *DIFF_FLAGS, merge_base, *target, "--", *paths)
    added = deleted = 0
    old_line = new_line = 0
    for line in diff.splitlines():
        hunk = HUNK.match(line)
        if hunk:
            old_line, new_line = int(hunk.group(1)), int(hunk.group(2))
            continue
        if line.startswith(("+++ ", "--- ")) and old_line == 0 and new_line == 0:
            continue
        if line.startswith("+"):
            added += in_ranges(new_line, new_ranges)
            new_line += 1
        elif line.startswith("-"):
            deleted += in_ranges(old_line, old_ranges)
            old_line += 1
    return added, deleted


def size(args):
    root, merge_base, head = resolve_range(args.repo, args.base, args.head)
    rows = numstat(root, merge_base, head, args.worktree)
    totals = {c: {"files": 0, "added": 0, "deleted": 0} for c in CATEGORIES}
    files = []
    for row in rows:
        category = classify(row["path"], args.test, args.generated)
        added, deleted = row["added"], row["deleted"]
        if category == "production" and row["path"].endswith(".rs") and not row.get("untracked"):
            test_added, test_deleted = rust_inline_test_lines(root, merge_base, head, args.worktree, row)
            if test_added or test_deleted:
                totals["tests"]["added"] += test_added
                totals["tests"]["deleted"] += test_deleted
                files.append({"category": "tests", "path": row["path"] + " (inline tests)",
                              "added": test_added, "deleted": test_deleted})
                added, deleted = added - test_added, deleted - test_deleted
        totals[category]["files"] += 1
        totals[category]["added"] += added
        totals[category]["deleted"] += deleted
        files.append({"category": category, "path": row["path"], "added": added,
                      "deleted": deleted, "binary": row["binary"]})
    total = {key: sum(t[key] for t in totals.values()) for key in ("files", "added", "deleted")}
    countable = {key: totals["production"][key] + totals["tests"][key] for key in ("added", "deleted")}
    report = {"merge_base": merge_base, "head": "WORKTREE" if args.worktree else head,
              "categories": totals, "total": total,
              "countable_changed": countable["added"] + countable["deleted"]}
    if args.files:
        report["files"] = files
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print(f"Range: {merge_base[:12]}..{report['head'][:12]}")
    print(f"{'Category':<12}{'Files':>7}{'Added':>9}{'Deleted':>9}{'Changed':>9}")
    for name in CATEGORIES + ("total",):
        t = totals[name] if name in totals else total
        print(f"{name:<12}{t['files']:>7}{t['added']:>9}{t['deleted']:>9}{t['added'] + t['deleted']:>9}")
    print(f"Countable changed lines (production + tests): {report['countable_changed']}")
    print("Files counts each file once; inline Rust test lines move to tests.")
    if args.files:
        print()
        for f in sorted(files, key=lambda f: (CATEGORIES.index(f["category"]),
                                              -(f["added"] + f["deleted"]))):
            print(f"{f['category']:<12}{'+' + str(f['added']):>8}{'-' + str(f['deleted']):>8}  {f['path']}")
    return 0


def identifier_like(token):
    return len(token) >= 6 and ("_" in token.strip("_") or bool(MIXED_CASE.search(token)))


def diff_identifiers(root, merge_base, head):
    """Return names on added lines (with the first file that adds each) and names on removed lines."""
    diff = git(root, "diff", "-U0", "-M", *DIFF_FLAGS, merge_base, head)
    first_file, removed, path, in_header = {}, set(), None, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            in_header, path = True, None
        elif in_header and line.startswith("+++ "):
            target = line[4:]
            path = None if target == "/dev/null" else target[2:]
        elif line.startswith("@@"):
            in_header = False
        elif not in_header and line.startswith(("+", "-")):
            for token in IDENT.findall(line[1:]):
                if not identifier_like(token):
                    continue
                if line.startswith("-"):
                    removed.add(token)
                elif path:
                    first_file.setdefault(token, path)
    return first_file, removed


def present_at(root, rev, tokens):
    """Return the tokens that occur as whole words anywhere in rev."""
    # One `git grep -q` per name: a combined pattern prints every hit of common names and is slow.
    ordered = sorted(tokens)
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as pool:
        hits = pool.map(lambda token: grep_status(root, rev, token), ordered)
        return {token for token, hit in zip(ordered, hits) if hit}


def grep_status(root, rev, token):
    result = subprocess.run(["git", "-C", root, "grep", "-q", "-I", "-w", "-F", "-e", token, rev],
                            capture_output=True, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.returncode == 0


def leaks(args):
    root, merge_base, head = resolve_range(args.repo, args.base, args.head)
    with open(args.text, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    text_tokens = {t for t in IDENT.findall(text) if identifier_like(t)}
    added, removed = diff_identifiers(root, merge_base, head)
    candidates = (text_tokens & set(added)) - removed
    leaked = sorted(candidates - present_at(root, merge_base, candidates))
    new_files = filter(None, git(root, "diff", "--name-only", "-z", "--diff-filter=A",
                                 "-M", merge_base, head).split("\0"))
    named_files = sorted(p for p in new_files
                         if p in text or (len(os.path.basename(p)) >= 8
                                          and re.search(r"(?<![\w/.-])" + re.escape(os.path.basename(p))
                                                        + r"(?![\w.-])", text)))
    print(f"Range: {merge_base[:12]}..{head[:12]}")
    print(f"Names that exist only in the change and appear in the text: {len(leaked)}")
    for token in leaked:
        print(f"  {token:<40} first added in {added[token]}")
    print(f"New files of the change named in the text: {len(named_files)}")
    for path in named_files:
        print(f"  {path}")
    clean = not leaked and not named_files
    print("Result: " + ("CLEAN" if clean else "REVIEW EACH ITEM"))
    print("This check finds names, not ideas. Read the text for leaked design too.")
    return 0 if clean else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="repository directory (default: .)")
    sub = parser.add_subparsers(dest="command", required=True)

    size_parser = sub.add_parser("size", help="changed lines by category")
    size_parser.add_argument("base")
    size_parser.add_argument("head")
    size_parser.add_argument("--worktree", action="store_true",
                             help="measure the working tree of --repo instead of HEAD, with untracked files")
    size_parser.add_argument("--files", action="store_true", help="list each file")
    size_parser.add_argument("--json", action="store_true")
    size_parser.add_argument("--test", action="append", default=[], metavar="GLOB",
                             help="path glob to count as tests")
    size_parser.add_argument("--generated", action="append", default=[], metavar="GLOB",
                             help="path glob to count as generated")
    size_parser.set_defaults(run=size)

    leak_parser = sub.add_parser("leaks", help="names new in the change that appear in a text file")
    leak_parser.add_argument("base")
    leak_parser.add_argument("head")
    leak_parser.add_argument("text", help="brief, or a diff of the rebuild")
    leak_parser.set_defaults(run=leaks)

    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
