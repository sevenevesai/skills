# Seveneves skills

Agent Skills by [Seveneves](https://seveneves.ai), for Claude Code and any other agent that
reads `SKILL.md`: Codex, GitHub Copilot, Cursor, Gemini CLI and more.

Each skill is a folder of written know-how: when to use it, the steps, and any scripts or
references it needs. None ships until it is proven: realistic requests run with and without
the skill, and a real run of anything those test runs can't reach.

## Skills

| Skill | What it does | Needs | Claude Code |
|---|---|---|---|
| [codex-image](skills/codex-image) | Generates or edits raster images with OpenAI Codex on your ChatGPT login, runs batches in parallel, and cuts sprite and icon sheets into transparent files. | [Codex CLI](https://github.com/openai/codex) signed in to a ChatGPT plan with image generation; Python 3.8+ | `/plugin install codex-image --marketplace sevenevesai/skills` |
| [make-skill](skills/make-skill) | Creates, improves or extracts a skill, and proves it works with test cases run with and without it. | Nothing beyond the agent; running its tests uses Claude Code's `claude plugin eval` | `/plugin install make-skill --marketplace sevenevesai/skills` |

Each skill's `compatibility` line in its `SKILL.md` lists the exact requirements.

## Install

**Claude Code** 2.1.275 or later, in one step:

```
/plugin install <skill> --marketplace sevenevesai/skills
```

On older versions, add the marketplace first:

```
/plugin marketplace add sevenevesai/skills
/plugin install <skill>@seveneves
```

**Any agent**, with the [skills CLI](https://github.com/vercel-labs/skills) (`-a` picks the agent;
leave it out to choose interactively):

```
npx skills add sevenevesai/skills --skill <skill> -a claude-code
```

**By hand:** copy `skills/<skill>/` into your project's `.claude/skills/`, or into
`~/.claude/skills/` to use it in every project.

Read a skill before installing it. A skill runs with the same permissions as your agent.

## Use

Skills load when a session starts. Then ask in your own words; the agent picks the skill whose
description matches:

- "Draw a watercolour hero image for the landing page and save it to assets/hero.png"
- "Turn the release steps we just did into a skill"

## How skills here are proven

Every skill passes the bar its author tool, [make-skill](skills/make-skill), sets in
[references/evals.md](skills/make-skill/references/evals.md):

- **With and without.** A suite of realistic requests runs three times with the skill installed
  and three times without, through Claude Code's `claude plugin eval`. Each should-fire request
  must load the skill in at least two of three runs, near-miss requests must leave it alone,
  every case must score at least 0.8 on its graders, and the skill must beat no skill on average.
- **A real smoke run.** Test runs get a temporary home and a fenced network, so they can't reach
  a login such as Codex's. A skill that needs one also passes a script that runs it for real and
  checks the output.

Latest results, 2026-10-28, Claude Code 2.1.312, Sonnet as agent and judge. Scores are the mean
over the should-fire cases; every near-miss case stayed quiet in all runs.

| Skill | Fired | With skill | Without | Smoke run |
|---|---|---|---|---|
| codex-image | 6 of 6 runs | 1.00 | 0.00 | passed: batch, edit and sheet cut, 3 images |
| make-skill | 6 of 6 runs | 1.00 | 0.42 | not needed |

The suites and run records stay in the maintainers' workspace; this repo ships only what an
installer needs.

## Layout

```
skills/<name>/SKILL.md            one skill per folder (Agent Skills format)
.claude-plugin/marketplace.json   Claude Code marketplace, one plugin per skill
```

Every skill follows the open [Agent Skills spec](https://agentskills.io/specification), so it
works in any agent that reads `SKILL.md`.

## License

[MIT](LICENSE), unless a skill's own frontmatter says otherwise.
