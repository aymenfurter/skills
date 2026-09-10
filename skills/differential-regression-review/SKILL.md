---
name: differential-regression-review
description: Review a pull request for user-visible regressions by running risk-based ephemeral end-to-end tests against both the base and PR revisions, then report evidence-backed results and draft review comments. Use for any regression, blast-radius, or differential PR review.
license: MIT
---

# Differential Regression Review

The base branch is the control, the PR branch is the experiment. Reading code produces hypotheses. Only end-to-end behavior counts as evidence.

- Pin intent from the PR description, linked issues, and spec. Ask the user only when the written intent can't settle a question (the sources contradict each other, or a test finds a difference none of them explain), or when a found regression needs a check that it isn't intentional. If no PR exists, ask for one comparison point (branch, tag, or commit) and review locally.
- Assume every risky change broke something, then write ephemeral e2e tests to catch it. When subagents are available, have 2-3 identify risks independently from the intent, diff, and history, each on the most capable current model at maximum reasoning effort, across different providers if possible (2026: Fable 5 Max, Opus 5 Max, GPT-5.6 Sol Max, Grok 4.6), then merge and deduplicate before scoring. Their analysis is hypotheses, never evidence. These tests are probes: built in the disposable worktrees for this review only, never added to the PR or the real test suite, and deleted at the end. A change is exonerated only by surviving them. Being disposable is an advantage: push each test as close to production behavior as possible, using real dependencies, staging endpoints, and even local credentials that could never be committed to CI. The safety rules below still bind, and when in doubt whether something is safe to touch, ask the user. Each hypothesis must trace a causal chain from the diff; skip invented disasters and assertions on differences no user would notice. Plan up to 100 numbered tests at public boundaries (browser, API, CLI, service contract), highest severity first, spread across four classes: the new feature's contract, preservation of adjacent journeys the diff didn't touch (including paths that must still fail correctly: permission denials, validation rejections), realistic limits, and recovery or compatibility paths. Risks outside the new feature count. Also cover: flag states guarding changed code (test the production default; ask if unclear), clock variation when the diff touches time or timezone logic, and writes read back through a public interface. Out of scope unless asked: resource leaks, observability, accessibility.
- Create two disposable worktrees with equivalent setup, one at the PR head and one at the merge-base. Treat the checkout and branches as read-only. Never commit or push. Delete all temporary files; the final `git status` must match the initial one. Write tests with the repository's existing e2e framework and conventions, building a minimal harness only if none exists. Before adding tests, run the relevant existing e2e tests on base: a broken control makes every comparison inconclusive.
- Run each test twice on PR and once on base, transferring only the test changes. Parallelize for elapsed time only across isolation: the two worktrees may run concurrently, and test groups too when they share no state, ports, services, or rate limits. Default to sequential; rerun any flaky parallel result sequentially before classifying it. Execution subagents also take the strongest available model, but one step below maximum reasoning effort (e.g., GPT-5.6 on very high). A regression means base passes, PR fails consistently, and the failure is the predicted, unintended user effect. Classify everything else as Pass, Expected difference, Expected absent (verified missing on base), Inconclusive, Blocked, or Not tested, each with a reason. For Critical and High risks, show the test can fail for the predicted fault, failing at the assertion rather than from a crash or setup error. A regression can also be non-functional: a journey consistently slower on the PR by a margin users would feel, compared as medians over repeated runs rather than single timings, meets the same gate.
- Score each risk as S (Critical 4 to Low 1) times P (Likely 3 to Remote 1), and expect defects: human industry rates run 10-20 per 1,000 new lines, and studies find AI-authored code carries more review issues, not fewer. Also check each changed area's git history (SZZ-style: fix and revert commits point back to the changes that caused them): if its past commits were often followed by fixes or reverts, bump its P one level. History ranks risks; it is never evidence of a regression. Residual score = pre-score times 1/4 after a pass with proven sensitivity, 1/2 after an unproven pass, 1 otherwise, including when the trigger environment (an unavailable OS, say) was never exercised. Round residuals up to whole points. A confirmed regression becomes a finding at certainty, where severity is all that remains. Scores are rankings, not probabilities.
- Run nothing destructive against production. Get approval before side effects. Secrets may be used to run tests but never recorded in commands, fixtures, logs, screenshots, or output.

**Output:** Show ranked risk bars as the plan before execution (bar length = score, sort order = test order). Label each bar with the concrete user-visible failure — what breaks, for whom — never with a description of the test that probes it. In text, draw each bar on a fixed 12-cell track, one cell per score point: `█` open risk, `▒` retired, `░` unused track, findings full-width `▓`, all in a monospace code block with aligned columns. Display levels, never raw scores: LOW 1-3, MODERATE 4-6, ELEVATED 7-9, SEVERE 10-12; after execution show each transition with its outcome reason, plus the percent reduction in open risk and the share of Critical/High risks with conclusive evidence. Sample:

```text
R1  ████████████  SEVERE    Guest checkout shows totals without tax
R2  █████████░░░  ELEVATED  Saved filters lost after profile edit
R3  ██████░░░░░░  MODERATE  Search returns stale results after rename
```

```text
R1  ███▒▒▒▒▒▒▒▒▒  SEVERE → LOW   pass, sensitivity proven
R2  █████████░░░  ELEVATED → ELEVATED   blocked: Windows env unavailable
R3  ▓▓▓▓▓▓▓▓▓▓▓▓  CONFIRMED   stale results reproduced on PR only
Open risk −67% · 1 finding · Critical/High conclusive: 2 of 3
```

**GitHub Copilot app rendering:** When the current interface is GitHub
Copilot app, replace the monospace Plan and Result blocks with rendered
KaTeX tables. For all other interfaces, keep the monospace format above.

Use these rendering rules:

- Use inline `\(...\)` expressions.
- Keep each complete expression on one physical Markdown line.
- Do not wrap the expression in a code fence in the actual review output.
- Use `\textsf` for text and `\mathsf` for large values.
- Use `\rule` for risk tracks.
- Use a six-em track. Each risk point equals `0.5em`.
- Use `\begin{array}{r l c c c l}` with empty spacer columns.
- Use one header rule and no bottom rule.
- Add `\rule{0pt}{1.4em}` to the first data row.
- Add `\\[4pt]` between rows.
- Do not use `\multicolumn` or display-math delimiters.
- Show levels, never raw scores.

Use these colors:

- Confirmed or Severe: `#ff7b72`
- Elevated: `#f59e0b`
- Moderate: `#eab308`
- Low: `#58a6ff`
- Pass: `#3fb950`
- Expected: `#d2a8ff`
- Muted or retired: `#8b949e`
- Residual: `#f0f6fc`
- Unused track: `#30363d`
- Finding track: `#c9d1d9`

Before E2E execution, render only the Plan table:

```latex
\(\begin{array}{r l c c c l}\textsf{\textbf{ID}}&\textsf{\textbf{User-visible risk}}&&\textsf{\textbf{Open risk}}&&\textsf{\textbf{Level}}\\ \hline \rule{0pt}{1.4em}R1&\textsf{Guest checkout shows totals without tax}&&\textcolor{#ff7b72}{\rule{6em}{0.42em}}&&\textcolor{#ff7b72}{\textsf{SEVERE}}\\[4pt]R2&\textsf{Saved filters are lost after profile edit}&&\textcolor{#f59e0b}{\rule{4.5em}{0.42em}}\textcolor{#30363d}{\rule{1.5em}{0.42em}}&&\textcolor{#f59e0b}{\textsf{ELEVATED}}\\[4pt]R3&\textsf{Search returns stale results after rename}&&\textcolor{#eab308}{\rule{3em}{0.42em}}\textcolor{#30363d}{\rule{3em}{0.42em}}&&\textcolor{#eab308}{\textsf{MODERATE}}\end{array}\)
```

After E2E execution, render the Result table. For each transition:

- Show the original level in muted gray.
- Use `\rightarrow`.
- Show the destination in bold and with its outcome color.
- Keep the reason neutral and in sentence case.
- For a finding, use `CONFIRMED <SEVERITY>` as the destination.

```latex
\(\begin{array}{r l c c c l}\textsf{\textbf{ID}}&\textsf{\textbf{User-visible risk}}&&\textsf{\textbf{Evidence}}&&\textsf{\textbf{Transition and reason}}\\ \hline \rule{0pt}{1.4em}R1&\textsf{Guest checkout shows totals without tax}&&\textcolor{#8b949e}{\rule{4.5em}{0.42em}}\textcolor{#f0f6fc}{\rule{1.5em}{0.42em}}&&\textcolor{#8b949e}{\textsf{SEVERE}}\rightarrow\textcolor{#3fb950}{\textsf{\textbf{LOW}}}\quad\textsf{pass, sensitivity proven}\\[4pt]R2&\textsf{Saved filters are lost after profile edit}&&\textcolor{#f0f6fc}{\rule{4.5em}{0.42em}}\textcolor{#30363d}{\rule{1.5em}{0.42em}}&&\textcolor{#8b949e}{\textsf{ELEVATED}}\rightarrow\textcolor{#f59e0b}{\textsf{\textbf{ELEVATED}}}\quad\textsf{blocked, Windows unavailable}\\[4pt]R3&\textsf{Search returns stale results after rename}&&\textcolor{#c9d1d9}{\rule{6em}{0.42em}}&&\textcolor{#8b949e}{\textsf{MODERATE}}\rightarrow\textcolor{#ff7b72}{\textsf{\textbf{CONFIRMED MEDIUM}}}\quad\textsf{stale results reproduced}\end{array}\)
```

For a non-finding Result track, calculate:

- Retired width: `(pre-score - rounded residual) × 0.5em`
- Residual width: `rounded residual × 0.5em`
- Unused width: `(12 - pre-score) × 0.5em`

For a confirmed finding, use one full six-em finding track.

After the Result table, insert this vertical spacer:

```latex
\(\rule{0pt}{1.4em}\)
```

Then render exactly three framed cards on the same line:

1. Open-risk reduction.
2. Confirmed findings.
3. Review verdict.

Do not show a Critical/High evidence card. Continue to use Critical/High
evidence internally when deciding the verdict.

```latex
\(\boxed{\begin{array}{c}\rule{0pt}{2.8em}\qquad\quad\textcolor{#3fb950}{\Huge\mathsf{-70\%}}\qquad\quad\\[9pt]\textsf{OPEN RISK}\\[-1pt]\rule[-1em]{0pt}{2em}\textsf{REDUCTION}\end{array}}\qquad\boxed{\begin{array}{c}\rule{0pt}{2.8em}\qquad\quad\textcolor{#3fb950}{\Huge\mathsf{0}}\qquad\quad\\[9pt]\textsf{CONFIRMED}\\[-1pt]\rule[-1em]{0pt}{2em}\textsf{FINDINGS}\end{array}}\qquad\boxed{\begin{array}{c}\rule{0pt}{2.8em}\qquad\quad\textcolor{#3fb950}{\Huge\mathsf{LGTM}}\qquad\quad\\[9pt]\textsf{REVIEW}\\[-1pt]\rule[-1em]{0pt}{2em}\textsf{VERDICT}\end{array}}\)
```

Replace the example values with the actual results.

- Use green for zero findings and `LGTM`.
- Use red for one or more findings and `NEEDS WORK`.
- Round open-risk reduction to the nearest whole percent.
- Do not show cards or a verdict before E2E execution.

Then give the numbered results with base behavior, both PR runs,
sensitivity, classification, and reason. Include no test code and make no
production fixes.

If a PR exists, give evidence-backed draft review comments anchored as
`<path>:<line>`. Never post them without explicit user confirmation. If
there are no comments, write `No evidence-backed review comments.`

If no PR exists, give a prioritized list of recommended actions based on
confirmed findings and unresolved risks. Include the related risk ID,
expected corrected behavior, and required verification.

The verdict card must show `LGTM` only when there are no confirmed
regressions, no required follow-up actions, and all Critical/High risks
have conclusive evidence. Otherwise, show `NEEDS WORK`.

Do not describe blocked, inconclusive, or untested results as confirmed
regressions. Never submit a review, approve a PR, post comments, or make
fixes without explicit user confirmation.

If the run uncovered something new, end by offering the user another iteration: reassess the risks with what was learned and propose the additional verification it suggests.
