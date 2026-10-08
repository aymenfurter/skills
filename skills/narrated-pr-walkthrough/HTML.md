# HTML option

The goal: the user understands the change as if an engineer presented the PR
to them. The deck explains behavior. It does not only list facts.

## Rules

- Make one HTML file. Do not use external fonts, scripts, images, or CDNs.
- Write the file to the session artifacts directory. Do not change the
  worktree. Remove cache files that tools create in the worktree.
- Use real code from the diff. Label each shortened excerpt "excerpt" or
  "simplified". Do not invent code, numbers, timings, or quotes.
- Label mock-ups of a UI or terminal as "illustrative". Use the real names,
  flags, defaults, and messages from the code in each mock-up.
- Write narration in ASD-STE100 style: short, active sentences, one idea in
  each sentence.

## 1. Research

Do the research before you write a slide. Record the facts in a notes file in
the artifacts directory.

1. **PR type:** decide if the PR is a **bug fix** or a **feature**. Use the
   title, the body, the labels, the linked issue, and the changelog type (for
   example `fixed` or `added`). If the PR does both, use the type of its main
   purpose, and give the other part one slide. For a refactor or a
   performance change, use the feature story. Show the measured effect in
   place of the user value.
2. **PR metadata:** number, title, state, base, head SHA, author, reviewers,
   and review decision (`gh pr view <n> --json ...`).
3. **Diff:** compare with the merge base, not with the current base branch.
   Use `git diff --numstat <merge-base>..HEAD`. Put each file in one group:
   production, tests, docs, or CI/other. Give a count for each group.
4. **Version history:** compare the opening commit with the head. For each
   review-fix commit, get the code before and after the fix.
5. **Review threads:** use the GraphQL `reviewThreads`. For each finding,
   record the reviewer, the problem, the evidence (numbers, timings), the fix
   commit, and the regression test name.
6. **Origin:**
   - **Bug fix:** find the linked issue, the symptom that the user saw, and
     the exact error text. Search the source for the message string. Record
     the reproduction.
   - **Feature:** find the linked issue, spec, or design doc. Record the user
     need, the limit or workaround before the PR, and the user-facing surface
     (command, flag, API, setting, UI). Record the defaults and any feature
     flag or experiment that controls the feature. Find real usage in tests,
     docs, or the PR body. Do not invent command output.
7. **Runtime model:** find the state that the code manages (files, locks,
   enums, caches, config), all states, the transitions, and the callers. For
   a feature, also find the new components, the existing flow that they
   connect to, and the integration points. Read the type definitions. Do not
   guess serialized formats.
8. **Limits:** record the edge cases, error paths, and limits that the code
   handles, and the behavior when the feature is off.
9. **Status:** CI summary (`gh pr checks`), open threads, and work that is
   still in progress.

If you cannot verify a fact, leave it out or mark it as unknown.

## 2. Story

The default is 10 slides. For a small PR, merge slides. Do not add slides
that have no content. Slides 1, 8, 9, and 10 are the same for each PR type.

| # | Slide | Must show |
|---|-------|-----------|
| 1 | Overview | Title, PR type, PR metadata, file and line counts for each group, agenda |
| 2–7 | Main story | Use the table for the PR type below |
| 8–9 | Review rounds | One slide for each theme. Problem → evidence → fix commit → test |
| 10 | Result | Before/after matrix, invariants, risk, status with date and time |

### Bug fix: slides 2–7

| # | Slide | Must show |
|---|-------|-----------|
| 2 | Symptom | Mock-up of what the user saw, the report, the reproduction, the source of the error |
| 3 | State model | The data, files, or enums and all states. Mark the faulty state |
| 4 | How it breaks | Animated runtime sequence to the failure point |
| 5 | Before | Swimlane trace on the base branch with real code. Show the dead end |
| 6 | Change 1 | The main new concept (type, variant, API), the real diff, the callers |
| 7 | Change 2 | Runtime animation of the repair, with the real code |

### Feature: slides 2–7

| # | Slide | Must show |
|---|-------|-----------|
| 2 | Motivation | The user need, the limit or workaround before the PR, the issue or spec |
| 3 | Feature tour | Mock-up of the new surface (command, API, setting, or UI) with real names and defaults. Show the feature flag or experiment, if one exists |
| 4 | Model | The new data, types, config, or states, and how they connect to the existing model. Mark the new parts |
| 5 | Flow before and after | Swimlane trace of the existing flow. Animate where the new steps go in |
| 6 | Implementation 1 | The main new component or API, the real code, the entry points, the callers |
| 7 | Implementation 2 | Runtime animation from start to end, including one error path or limit and the behavior when the feature is off |

For a feature, the result slide (10) shows a capability matrix (what a user
can do before and after), compatibility, rollout (flag, experiment, default),
risk, and status.

## 3. Visual rules

- Each slide must have a visual that explains behavior: a state machine, a
  file tree, a swimlane, timeline bars, a pipeline, a race diagram, or a
  checklist that ticks. Bullet lists alone are not sufficient.
- Show the code before and after. Use diff blocks (+/−) for changes.
  Highlight the lines that the narrator talks about at that moment.
- For new files, show the most important new code and the diff at the call
  site that connects it to the existing code.
- Use a 1600×900 stage. Scale it to fit the window.
- Use a GitHub dark palette with fixed meanings: red = failure,
  green = success, amber = the state that the PR is about (the faulty state,
  or the new state), blue = current focus, purple = secondary. Mark new
  parts with a "new" tag.
- Do not use these generated-UI patterns: gradient text, colored glow
  shadows, thick accent borders on one side, decorative grid backgrounds.
- Animate only `opacity` and `transform`. Use `scaleX` for bars and progress.

## 4. Engine contract

### Step attributes

`n` is the current step on the slide.

- `data-s="k"`: show the element when `n ≥ k`.
- `data-x="k"`: hide the element when `n ≥ k`.
- `data-h="2-4,7"`: highlight the element while `n` is in the range.
- `data-c="k:cls k2:cls2"`: add the class `cls` when `n ≥ k`, for state
  changes such as `ok`, `err`, `dead`, or `full`.
- `HOOKS[slideIndex](n, el)`: timed effects, for example a retry counter.
  Clear the hook timers when the slide changes.

### Narration data

```js
const DECK = [
  /* slide 1 */ [[0, "Sentence."], [1, "Sentence for step one."]],
  /* slide 2 */ [[0, "..."]]
];
```

- Each cue sets the step for its slide. All elements with a lower or equal
  step become visible.
- Each step number from 0 to the maximum must have one or more cues.
- Estimate the duration at 130–150 words for each minute. Show it on the
  start screen.

### Code blocks

- Keep source text in `<script type="text/plain" id="c-name">`. Render it
  into `<pre class="code" data-src="c-name" data-lang="rust|ts|json">`. Add
  `data-diff` for +/−/@ lines.
- Put a marker at the end of a line to link it to a step: `⟪h3-4⟫` highlights
  the line, `⟪s2⟫` shows the line. The renderer removes the marker.
- Use a small regex highlighter for comments, strings, numbers, keywords,
  types, functions, macros, and `?`. Escape HTML.

### Text-to-speech

Browser speech is not reliable. Keep all of these measures:

- Show a start screen with "Start with voice" and "Start silent". Speech
  needs a user gesture.
- Load voices in `voiceschanged`. Prefer natural English voices. Give a
  voice list and a speed slider.
- Speak one sentence at a time. Chrome stops long utterances.
- Keep a global reference to the current utterance. If the browser deletes
  the utterance object, `onend` does not fire.
- Start a watchdog timer for each utterance (estimate × 1.8 + 5 s). On
  timeout, cancel the speech and continue.
- Ignore the `interrupted` and `canceled` errors. For other errors,
  continue on a timer.
- Increase a token at each pause, skip, or slide change. Old callbacks must
  check the token and do nothing.
- Silent and muted modes use the same timing: words ÷ (2.6 × rate) seconds.
- `speakable()` changes text for speech only: read commit hashes letter by
  letter, and change "I/O" to "I O".

### Controls

- Buttons: play/pause, previous and next slide, next step, show all, slide
  numbers, voice, speed, mute, captions, full screen, and a progress bar.
- Keys: Space, ←/→, ↓, Home/End, A, C, M, F.
- `#N` opens slide N.
- `?shot=N[&step=K]` hides the start screen, adds a `noanim` class (no
  transitions or animations), and shows all steps (or step K). Use it for
  screenshots.

## 5. Build

- The file is large (about 90 KB). A single `create` call fails at the
  output token limit.
- Write a skeleton with unique markers (for example `/*CSS2*/` and
  `<!--BODY-->`). Insert each part with a script that replaces exactly one
  marker and checks that the marker exists.
- Order: base CSS → slide CSS → slides → code blocks → `DECK` → engine.

## 6. Verify

1. Extract the `<script>` contents and run `node --check`.
2. Run a step coverage check. For each slide, the highest element step
   (`data-s`, `data-x`, `data-h`, `data-c`, and `⟪⟫` markers) must not be
   more than the highest cue step. Each step number must have a cue.
3. Take a headless Chrome screenshot of each slide (`?shot=N`, window
   1600×964). Look at each image for overflow, wrapped labels, overlaps, and
   text that is too small to read. Fix the problems and take the screenshots
   again.
   - Headless Chrome can stay open when CSS animations loop. Start it in the
     background, poll its PID, and stop it with `kill <PID>` after a time
     limit. Chrome still writes the screenshot.
4. Do a playback test through the Chrome DevTools Protocol on a private
   headless instance with its own port and profile. Check that:
   - silent mode moves through the cues and updates the captions,
   - the keys work and the hooks run,
   - voice mode continues when no audio plays (watchdog),
   - the console shows no errors.

   Do not use a browser that another session uses.
5. Just before you deliver, check the PR head, the threads, and CI again.
   Put the date and time on the status panel.
6. Delete the temporary files.

Tell the user what you could not verify, for example audible speech in
headless mode.

## 7. Deliver

Reply in 100 words or less. Give the file path and how to start it (Chrome,
Edge, or Safari; click "Start with voice"). Give the main keys. Say what you
verified and what you did not verify.
