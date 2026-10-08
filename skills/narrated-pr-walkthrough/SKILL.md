---
name: narrated-pr-walkthrough
description: Explain a pull request with an evidence-based narrated presentation. Create an animated HTML presentation by default, or create a narrated MP4 video when the user asks for video.
user-invocable: true
argument-hint: "[PR number or URL, or local base and head revisions] [optional format: html or video]"
license: MIT
---

# Narrated PR walkthrough

Create a clear, evidence-based presentation that explains a pull request. Use
HTML by default. Use the video option only when the user requests a video,
MP4, or slide-based video.

## Choose the format

- **Default: HTML.** Read `HTML.md` in this directory and follow its
  instructions. It creates one self-contained HTML presentation with animated
  steps and browser text-to-speech.
- **Video: only when requested.** Read `VIDEO.md` in this directory and follow
  its instructions. It creates an MP4 with draw.io slides and local Kokoro
  narration.
- Do not create both formats unless the user asks for both.

For the default HTML option, use a Claude Opus 5.5 or higher subagent when one
is available. This option works best with that model. If it is not available,
continue with the available model. The video option follows the model
requirements in `VIDEO.md` and the linked draw.io skills.

## Shared requirements

- Use the pull request URL, repository and pull request number, or local base
  and head revisions provided by the user.
- Do not change, commit, push, publish, comment on, approve, or otherwise
  modify the pull request.
- Write deliverables to the task artifact directory, not the repository.
- Use real evidence. Do not invent code, behavior, numbers, timings, quotes, or
  verification results.
- Separate code evidence, CI evidence, manual verification, and unverified
  behavior. Do not present an explanation, passing CI, or an AI review as
  proof that the pull request is correct.
- Write narration in ASD-STE100 style: short, active sentences with one idea
  in each sentence.
- State what you could not verify.
