---
name: poka-yoke
description: "Make repeated agent mistakes impossible: find mistake classes, rank candidate fixes by confidence, let the user select fixes, and run each fix in its own child session. Prove each check fails on a past mistake and verify behavior change. Use for /poka-yoke."
disable-model-invocation: true
---

# Poka-Yoke

Assume agents read one file, copy nearby code, and stop when checks pass. Make the local right path the global right path.

## 1. Find classes

Use GitHub Copilot subagents in parallel to scan commits, reverts, agent rules, operator corrections, and PR review comments. Prioritize PRs that stayed open longest or had the most review rounds. Group repeats into classes (2+ occurrences).

## 2. Rank and select fixes

For each class, pick the highest enforcement level that blocks it:

1. **Architecture:** One owner per state, one path per task, one source of truth. Hide internals; delete legacy patterns.
2. **Types:** Make invalid states uncompilable.
3. **Lint / hook / CI:** Name the replacement file, type, or function in the error. Run the same fast check locally and in CI. Ratchet legacy violations so only new ones fail.
4. **Behavior test:** Assert observable outcomes; delete brittle or non-failing tests.
5. **Docs / rules (last):** Judgment calls only.

Group candidate fixes by **Confidence**:
- **Clear-cut:** Deterministic invariant with no design trade-off.
- **Likely:** Strong repeat pattern with a minor scope or style choice.
- **Judgment call:** Opinionated change or real trade-off.

Before changing any code:
1. Show a Markdown table grouped by **Confidence** with columns: `ID | Confidence | Class | Evidence | Level | Proposed fix`.
2. Call `ask_user` with multi-select checkboxes grouped by **Confidence** so the user picks which fixes to run.

## 3. Execute in child sessions

Create one child session (`create_session`) for each selected fix. Give each child session standalone context: the mistake class, evidence, target level, and the verification rules below.

Each child session must:
- Implement the fix in one commit.
- Prove each new check fails on a real past mistake before passing.
- For non-trivial changes, run a small, temporary blind GitHub Copilot subagent eval on a real past task before and after the change to confirm behavior improves; delete temporary artifacts afterward. Skip only for trivial checks.
- Require reason, expiry date, and human approval for inline exceptions.
- Keep a `Rule | Enforcer` table in the agent instruction file. Escalate repeated unenforced rules to levels 1–4; drop rules once impossible.

**Output (per selected fix):** Evidence, level, why higher levels failed, failure proof, and before/after eval result (or why skipped).
