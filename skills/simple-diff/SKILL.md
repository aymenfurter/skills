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

Write one `simple-diff.html` file in the session artifacts directory. Copy
`assets/template.html` and keep its CSS and script; they set the `#121213`
background, syntax highlighting, and diff layout. Fill in the title, summary,
and one `<section class="change">` per change with Before/After sentences and
only the relevant HTML-escaped `git diff` hunks. Keep it short. No slides,
narration, test reports, or full patch.

Check the explanation against the source. Once the HTML file is created,
automatically open it in the integrated browser, if available. Otherwise,
only provide the file link. Link the HTML file in the final reply.
