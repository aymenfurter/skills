---
name: simple-diff
description: 'Create a minimal before-and-after HTML explanation of key code changes. Use for "simple diff" or "/simple-diff".'
---

# Simple diff

Read the requested PR, commit range, patch, or current changes. Ask if the
target is unclear. Compare branches from their merge base. Do not modify source.

Group key changes by behavior, most important first. For each, show a short
title and:

- **Before: how it works.** Explain the old behavior.
- **After: how it works.** Explain the new behavior and what changed.

Use short sentences and only essential real code excerpts. Include source
paths when known. Do not invent missing code or behavior.

Exclude test code, fixtures, snapshots, generated code, formatting changes,
and boilerplate. Keep configuration changes when they affect behavior.
If nothing relevant remains, say so instead of inventing a comparison.

Write one `simple-diff.html` file in the session artifacts directory:

- Set both `html` and `body` backgrounds to exactly `#121213`.
- Put Before and After side by side; stack them on narrow screens.
- Use readable contrast, semantic headings, and wrapping code.
- Escape inserted text and code. Use inline CSS and no external dependencies.
- Keep it short. No slides, narration, test reports, or full patch.

Check the explanation against the source, then link the HTML file.
