---
name: poka-yoke
description: "Make repeated agent mistakes impossible: architecture, types, lint/hook/CI, behavior tests, docs last. Prove each check fails on a past mistake and verify behavior change. Use for /poka-yoke."
disable-model-invocation: true
---

# Poka-Yoke

Assume agents read one file, copy nearby code, and stop when checks pass. Make the local right path the global right path.

## 1. Find classes

Use GitHub Copilot subagents in parallel to scan commits, reverts, agent rules, operator corrections, and PR review comments. Prioritize PRs that stayed open longest or had the most review rounds. Group repeats into classes (2+ occurrences).

## 2. Enforce at the highest level

Pick the first level that blocks the class:

1. **Architecture:** One owner per state, one path per task, one source of truth. Hide internals; delete legacy patterns.
2. **Types:** Make invalid states uncompilable.
3. **Lint / hook / CI:** Name the replacement file, type, or function in the error. Run the same fast check locally and in CI. Ratchet legacy violations so only new ones fail.
4. **Behavior test:** Assert observable outcomes; delete brittle or non-failing tests.
5. **Docs / rules (last):** Judgment calls only.

## 3. Prove and maintain

- Fix top classes now, one commit each; use GitHub Copilot subagents to verify independent checks in parallel.
- Prove each new check fails on a real past mistake before passing.
- For non-trivial changes, run a small, temporary blind GitHub Copilot subagent eval on a real past task before and after the change to confirm behavior improves; delete temporary artifacts afterward. Skip only for trivial checks.
- Inline exceptions require: reason, expiry date, human approval.
- Keep a `Rule | Enforcer` table in the agent instruction file. Escalate repeated unenforced rules to levels 1–4; drop rules once impossible.

**Output:** Per class: evidence, level, why higher levels failed, failure proof, and before/after eval result (or why skipped).
