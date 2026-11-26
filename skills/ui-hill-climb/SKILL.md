---
name: ui-hill-climb
description: Improve a target UI through 10 variants, three independent model judges, and score-guided refinement. Use when the user requests "ui-hill-climb" or asks to apply this multi-model UI design process.
---

**`/ui-hill-climb`**: Have one Claude Opus subagent use [Anthropic's `frontend-design` skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md), existing components, and reference screenshots to build 10 variants of the target area. Have three independent judge subagents (Gemini 4 Neon, Claude Sonnet 5.5, and GPT-6.2 Sol) score every variant from 0 to 10 for clarity, usability, and consistency, with specific feedback. Track each version's screenshots, individual scores, average score, and feedback; have Opus improve the strongest candidates, then ask all three judges to score each revision independently using the same criteria. Keep a revision only when its average score increases, continue until improvements stop or an agreed budget is reached, and present the best version with before-and-after screenshots and its score history.
