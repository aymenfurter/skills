# Skills

My reusable agent skills.

## Skills

| Skill | Purpose |
| --- | --- |
| [Differential regression review](skills/differential-regression-review/SKILL.md) | Compare base and pull request behavior with temporary end-to-end tests. |
| [Draw.io pitch](skills/drawio-pitch/SKILL.md) | Research the subject and visual direction, then create a dense A5 diagram and PNG. |
| [Draw.io iterate](skills/drawio-iterate/SKILL.md) | Complete at least four PNG review passes: an 800% diagram-code increase, then corrections only. |
| [Narrated PR walkthrough](skills/narrated-pr-walkthrough/SKILL.md) | Create an animated HTML walkthrough by default, or a narrated MP4 video when requested. |

Use `drawio-pitch` for the initial proposal, then `drawio-iterate` to refine it.
The skills do not prescribe a visual style or PNG export tool.
Differential regression review requires Git and the target project's test dependencies.
Narrated PR walkthrough uses HTML by default. The video option requires both
draw.io skills, GPT-6 Astra subagents, a draw.io PNG export tool, Docker,
FFmpeg, and FFprobe. The skill works best with a Claude Opus 5.5 or higher
subagent for the HTML option. The video option uses the model requirements in
its instructions and the linked draw.io skills.

## Install

### Copilot marketplace

In Copilot's plugin marketplace settings, add `aymenfurter/skills` as the
source. Then install `aymenfurter-skills` from the `aymenfurter-skills`
marketplace. The plugin includes all four skills and their supporting files.

From Copilot CLI:

```bash
copilot plugin marketplace add aymenfurter/skills
copilot plugin install aymenfurter-skills@aymenfurter-skills
```

To use a local checkout before publication, run these commands from the
repository root:

```bash
copilot plugin marketplace add .
copilot plugin install aymenfurter-skills@aymenfurter-skills
```

The marketplace catalog is in
[`.github/plugin/marketplace.json`](.github/plugin/marketplace.json).
The root [`plugin.json`](plugin.json) uses the Agent Plugins 1.0 format.
It loads each skill from an immediate subdirectory of `skills/`.

### Individual skills

From a local checkout, use GitHub CLI 2.90.0 or later:

```bash
gh skill install . --all \
  --from-local --agent github-copilot --scope user
```

To install one skill, replace `--all` with its name.
Use either the plugin or individual skill installation to avoid duplicate
copies.

## Diagram samples

**Recommended model: GPT-6 Astra.** It delivered the best result in this comparison.
Both models refined the same AI Engineer Coach draft through four
`drawio-iterate` passes.

### GPT-6 Astra

![AI Engineer Coach architecture: local analysis, hosting environments, and optional model calls](samples/ai-engineer-coach-gpt-6-astra.png)

<details>
<summary>GPT-5.6 Sol reference output</summary>

Kept for comparison only. This version has clipped labels and omits some
secondary connectors that are present in the Astra result.

![AI Engineer Coach architecture reference produced by GPT-5.6 Sol](samples/ai-engineer-coach-gpt-5.6-sol.png)

</details>

[Source and asset credits](samples/NOTICE.md).

## Source and license

Differential regression review is copied unchanged from
[aymenfurter/differential-regression-review](https://github.com/aymenfurter/differential-regression-review/tree/d2304f1292473cd6708a61bbadffa36760f41ce7).

[MIT License](LICENSE). Each skill directory also includes the license for
standalone distribution.
