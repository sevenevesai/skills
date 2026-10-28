# Seveneves skills

Agent Skills by [Seveneves](https://seveneves.ai), for Claude Code and any other agent that
reads `SKILL.md`: Codex, GitHub Copilot, Cursor, Gemini CLI and more.

Each skill is a folder of written know-how: when to use it, the steps, and any scripts or
references it needs. Each one is tested before release by running realistic requests with
and without it: it has to fire on the requests it is for, stay quiet on near-misses, and do
better than no skill at all.

## Skills

| Skill | What it does | Claude Code |
|---|---|---|
| [make-skill](skills/make-skill) | Creates, improves or extracts a skill, and proves it works with test cases run with and without it. | `/plugin install make-skill --marketplace sevenevesai/skills` |

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

**Any agent**, with the [skills CLI](https://github.com/vercel-labs/skills):

```
npx skills add sevenevesai/skills --skill <skill>
```

**By hand:** copy `skills/<skill>/` into your project's `.claude/skills/`, or into
`~/.claude/skills/` to use it in every project.

Read a skill before installing it. A skill runs with the same permissions as your agent.

## Layout

```
skills/<name>/SKILL.md            one skill per folder (Agent Skills format)
.claude-plugin/marketplace.json   Claude Code marketplace, one plugin per skill
```

Every skill follows the open [Agent Skills spec](https://agentskills.io/specification), so it
works in any agent that reads `SKILL.md`.

## License

[MIT](LICENSE), unless a skill's own frontmatter says otherwise.
