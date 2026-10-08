# Video option

Create a short, evidence-based video walkthrough for a pull request.

The video must explain:

1. What changes for the user.
2. How the important implementation path changes.
3. What evidence supports the change.
4. What remains unverified or requires manual testing.

Do not present an explanation, passing CI, or an AI review as proof that the
pull request is correct.

## Input

Accept one of these inputs:

- A GitHub pull request URL.
- A repository and pull request number.
- Local base and head revisions.

If the pull request is not in the current repository, use the fully qualified
repository name when referring to it.

## Requirements

Use the installed `drawio-pitch` and `drawio-iterate` skills, GPT-6 Astra
subagents, a draw.io PNG export tool, Docker, FFmpeg, and FFprobe.
If a required skill, model, or tool is unavailable, explain the limitation
and ask the user how to proceed. Do not silently substitute another model
or skip a required skill.

## Output

Write outputs to the task artifact directory, not the repository.

Deliver:

- One final MP4 video.
- One narration transcript per slide.
- One combined transcript.
- One WAV narration file per slide.
- The final PNG for each slide.
- The editable `.drawio` source for each slide.
- Source and asset credits.
- The retained pitch and refinement artifacts required by `drawio-iterate`.

Do not commit, push, publish, comment on, approve, or modify the pull request.

## 1. Collect evidence

Record the initial repository status. Resolve and record the base and head
commit IDs so that every claim refers to the same revisions.

Read:

- The pull request title and description.
- Linked issues or specifications.
- The complete diff.
- The changed-file list.
- Commit messages.
- Recorded CI checks.
- Relevant changed tests.

Use source priority in this order:

1. Explicit requirements and linked specifications.
2. Existing product behavior.
3. Pull request diff.
4. Pull request description.
5. Commit messages.
6. Inferences from the implementation.

Do not treat the pull request description as an independent source of truth
when the diff contradicts it.

Separate all claims into:

- **Code-evidenced:** directly supported by the diff.
- **CI-evidenced:** supported by a recorded automated check.
- **Manually verified:** directly exercised during this task.
- **Unverified:** not exercised through the real user boundary.

Never label unit tests as end-to-end evidence.

## 2. Choose the slide count

Create between **one and five slides**.

A simple pull request can use **one slide** when one visual can clearly explain:

- The intended change.
- Its main implementation path.
- Available verification evidence.
- Remaining risks or untested behavior.

Do not add slides to meet a minimum count.

Use additional slides only when they improve understanding. A typical larger
pull request can use:

1. User-facing change.
2. Architecture or data-flow change.
3. Verification evidence and remaining user checks.

Keep the complete video concise. Target approximately 30-65 seconds of
narration per slide.

## 3. Plan the deck

For each slide, define:

- Slide number.
- Title.
- Single communication objective.
- Facts that must appear.
- Claims that must not be made.
- Source evidence.
- Draft narration.
- Visual metaphor or composition.

Create one shared deck direction that specifies:

- Color palette.
- Typography.
- Visual density.
- Icon style.
- Background.
- Repeated title and slide-number treatment.

Use a landscape A5 draw.io page because the draw.io skills require A5.
Design it so it remains legible when fitted into a 1920x1080 video frame.

Prefer large labels and visual explanations over paragraphs.

## 4. Create each slide through a subagent

Launch **one GPT-6 Astra subagent per slide**. Slides can run in parallel.

Give each subagent:

- The pull request evidence.
- Its slide objective.
- Its draft narration.
- The shared deck direction.
- Its output directory.
- The required final filenames.

Each slide subagent must:

1. Invoke `drawio-pitch`.
2. Complete all requirements of `drawio-pitch`.
3. Invoke `drawio-iterate`.
4. Complete all requirements of `drawio-iterate`, including at least four
   post-pitch review passes, the meaningful diagram-code growth requirement,
   full-size and enlarged-detail PNG inspection, orientation, overlap, and
   arrow checks, and a separate `.drawio` and PNG pair for every pass.
5. Return `slide-NN-final.drawio`, `slide-NN-final.png`, `narration.txt`,
   and `sources.md`.

The final PNG must be a normal RGB or RGBA raster PNG.

Keep text readable at video resolution. Do not use small source code, long
paragraphs, or dense tables that cannot be read without zooming.

Use logos and other brand assets only when their source and usage rights are
clear. Record all credits. Do not upload private task material to public
research or rendering services.

## 5. Review the completed slides

After all slide subagents finish:

- Inspect every final PNG.
- Check title consistency.
- Check slide numbering.
- Check palette and visual consistency.
- Check that all important text remains readable at 1920x1080.
- Check for clipping, overlap, wrong arrows, and incorrect orientation.
- Check that no slide claims more verification than the evidence supports.
- Check that the slides form one coherent story.

Request a correction from the responsible slide subagent when needed. Do not
silently edit only the raster image. Corrections must be made in the `.drawio`
source and exported again.

Finalize the narration only after the visual content is stable.

## 6. Start local Kokoro text-to-speech

Use Kokoro-FastAPI for narration.

Use an available loopback port. The examples below use port `18880`.

Start only one task-owned container:

```bash
docker run --rm \
  --name copilot-pr-video-kokoro \
  -p 127.0.0.1:18880:8880 \
  ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

Wait until the health endpoint succeeds:

```bash
curl -fsS http://127.0.0.1:18880/health
```

Expected response:

```json
{"status":"healthy"}
```

The initial image download requires internet access. Speech generation runs
locally after the image and model files are available.

Do not stop or replace an existing user-owned container. Choose a different
port or container name when either is already in use. Use the chosen port
and name consistently in all subsequent commands.

## 7. Generate narration

Use the same voice and speed for every slide.

Default settings:

- Model: `kokoro`
- Voice: `af_heart`
- Response format: `wav`
- Speed: `0.96`

Example request:

```bash
curl -fsS \
  -X POST http://127.0.0.1:18880/v1/audio/speech \
  -H 'Content-Type: application/json' \
  --output slide-01.wav \
  --data '{
    "model": "kokoro",
    "voice": "af_heart",
    "input": "Narration text goes here.",
    "response_format": "wav",
    "speed": 0.96
  }'
```

Encode actual transcripts with a JSON serializer or send a JSON file. Do not
interpolate arbitrary narration into shell quoting.

Prepare narration text for speech:

- Write short, direct sentences.
- Expand unclear abbreviations.
- Write version numbers in spoken form when necessary.
- Add punctuation for natural pauses.
- Avoid reading long filenames or implementation symbols.
- Replace arrow symbols with spoken words.
- Spell acronyms as separate letters when normal pronunciation is ambiguous.
- Use phonetic wording for identifiers that Kokoro is likely to mispronounce.

Do not change factual meaning to improve pronunciation. Save the exact text
used for speech in both the per-slide and combined transcripts.

Use FFprobe to confirm that every WAV has a finite, positive duration:

```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  slide-01.wav
```

## 8. Build one video clip per slide

Hold each slide until its narration finishes, plus approximately 0.65 seconds.

Create a 1920x1080, 30 fps H.264/AAC clip.

Fit and pad the slide. Do not crop or stretch it:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -loop 1 \
  -framerate 30 \
  -i slide-01-final.png \
  -i slide-01.wav \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,\
pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0xF4F7FB,\
setsar=1,format=yuv420p" \
  -af "apad" \
  -t "<NARRATION_DURATION_PLUS_0.65>" \
  -c:v libx264 \
  -preset medium \
  -crf 18 \
  -c:a aac \
  -b:a 192k \
  -ar 48000 \
  -ac 2 \
  -movflags +faststart \
  clip-01.mp4
```

Replace the duration placeholder with the measured narration duration plus
the hold. Round the clip duration up to a complete video frame.

Confirm that the clip is not shorter than its narration.

## 9. Join the clips

Create a concat manifest in slide order. Include only the clips that exist;
the following example is for a three-slide video:

```text
file 'clip-01.mp4'
file 'clip-02.mp4'
file 'clip-03.mp4'
```

Join the clips without unnecessary re-encoding:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -f concat \
  -safe 1 \
  -i clips.txt \
  -c copy \
  -movflags +faststart \
  pr-walkthrough.mp4
```

## 10. Verify the final video

Use FFprobe to verify:

- H.264 video.
- AAC audio.
- 1920x1080 dimensions.
- 30 fps.
- 48 kHz stereo output.
- Positive, finite duration.

Decode the complete video to detect damaged media:

```bash
ffmpeg -hide_banner -loglevel error \
  -i pr-walkthrough.mp4 \
  -f null -
```

Extract and inspect:

- A frame near the start.
- A middle frame from every slide.
- A frame immediately after each slide transition.
- A frame near the end.

Check that:

- No slide is cropped or stretched.
- The order is correct.
- The final slide remains visible until narration ends.
- No narration is cut off.
- Audio levels are reasonably consistent.
- Text remains readable at 1920x1080.
- The visual content matches the active narration.
- Claims about verification remain accurate.

If an audio playback or speech-recognition tool is available, review
pronunciation and narration completeness. Correct the transcript and
regenerate affected audio when necessary.

If auditory inspection is unavailable, state this limitation. Do not claim
that pronunciation was verified.

## 11. Clean up

Stop only the Kokoro container started by this task:

```bash
docker stop copilot-pr-video-kokoro
```

If this task started a local container runtime solely for the task, restore it
to its previous state after the container stops. Do not stop the runtime if
other work now depends on it.

Remove temporary concat manifests and intermediate files only when they are
not part of the requested deliverables.

Confirm that the repository working tree matches its initial state.

## 12. Deliver

Provide direct links to:

- The final MP4.
- The combined transcript.
- Each final `.drawio` source.
- Each final PNG.
- Each WAV file or containing artifact directory.

State:

- Video duration.
- Resolution and codecs.
- Number of slides.
- TTS engine and voice.
- Whether visual inspection completed.
- Whether auditory pronunciation inspection completed.
- Any behavior that remains unverified.

Do not claim that the pull request is correct because the video was created.
The video explains the change and its evidence; it does not replace user
verification.
