---
name: clean-room-design-review
description: Review the design of a large pull request by rebuilding it in a clean room. List its terminal and instrumental objectives, let a strong model rebuild only the terminal objectives without seeing the PR, verify the rebuild, and compare both designs. Use for clean-room or rebuild reviews, and when a PR seems too large for what it does.
---

# Clean-Room Design Review

PRs grow one fix at a time: a review finds a race, a commit adds a lock, a test protects the lock. A strong model rebuilds only the required outcomes from base, without the PR. The comparison shows which code the problem needs and which code only the design needs.

- **Terminal objective:** an observable outcome that the PR exists to deliver ("a retried webhook never ships an order twice").
- **Instrumental objective:** a mechanism that the chosen design needs (a lock around the webhook handler). Keep the outcome that it protects. Do not keep the mechanism.

## Rules

- Each gate needs explicit user approval. Do not push, post, or open a PR without explicit confirmation.
- The child never sees the PR diff, branch, commits, review threads, or design.
- Fewer lines that drop a requirement, weaken a test, or hide complexity do not make a better design.
- Measure both sides with `python3 <skill-dir>/scripts/measure.py size <base> <head>` and the same options. Say which statements you verified.

## 1. Objectives (Gate 1)

Read the PR, issues, diff, commits, and review threads. Find why each mechanism was added. Review-fix commits often explain one. Measure with `--files`, and correct categories with `--test` or `--generated GLOB`.

Show a table `ID | Objective | Kind | Serves | Origin | Prod | Tests` (T1… terminal, I1… instrumental), with "must never", failure, and concurrency outcomes. Show the totals and the instrumental share. Ask the user to confirm.

## 2. Brief (Gate 2)

Write the child's first prompt: design your own solution and do not read PR #n or `<branch>`. Give the problem in user terms, one testable requirement per terminal objective, facts that are true on base, and the scope. Require one end-to-end test at a public boundary and a few focused tests that fail without the change. Give the budget and the `measure.py` command. The child asks before it drops a requirement or exceeds the budget, commits locally, and reports size, evidence per requirement, and trade-offs.

Name nothing that the PR adds, and do not hint at its flow or structures. Remove each hit of `measure.py leaks <base> <pr-head> <brief>` that is not a terminal contract. Then read the brief for leaked ideas.

Default budget: a quarter of the PR's production and test lines, rounded up to 50. Default model: `claude-opus-5.5` at `xhigh`, or the newest flagship model. Show the brief verbatim and ask to start.

## 3. Rebuild

Start one autonomous child agent with a fresh context, its own branch from base, the brief, and a way to notify you (for example `create_session` in the GitHub Copilot app). Otherwise, ask the user to start it. Wait, and do not poll. Answer base facts, never PR design. Send requirement and budget changes to the user.

## 4. Verify

The child's report is a claim.

1. The branch starts on base. Many hits of `measure.py leaks <base> <pr-head> <child-diff>` make the result Inconclusive.
2. Measure the size with the same options.
3. Each requirement has a test that asserts the outcome at a public boundary: Met (verified), Met (reported), Partly met, or Not met.
4. Run the key tests in a disposable worktree. Revert the core change, and make sure that they fail.
5. Report shortcuts as trade-offs: narrowed requirements, mocked tests, suppressions, hidden state, new dependencies, timing risks.

## 5. Verdict

Compare size, state, locks, and API. Mark each I row Gone, Also needed, or Replaced. Say where the PR is better.

- **Redesign:** all requirements met, about 70 % or less of the lines or a mechanism gone.
- **Hybrid:** the rebuild is the better base, but named PR parts stay.
- **Design confirmed:** about 80 % or more, or the same mechanisms. This is a good result.
- **Inconclusive:** requirements not met, leaked clean room, or weak evidence.

## Review comment

For a redesign or a hybrid, write feedback that a reviewer could give from the PR and base alone. Do not show that a rebuild exists: no "rebuild", "prototype", "I tried", IDs, line counts, percentages, tools, rebuild-only names, or claims that only the rebuild proves.

Start with "Reviewed at `<sha>`. Suggestion: <one line>." Name the PR parts that become unnecessary ("significantly smaller, including tests"), the current design in the PR's names, a sketch of 15 lines or fewer, and two or three facts that the author can check. No thanks, alternatives, or closing question.

Keep only those hits of `measure.py leaks <base> <rebuild-head> <draft>` that the PR head also contains. Post only after confirmation, then give the link.
