# Seveneves skills

Agent Skills by [Seveneves](https://seveneves.ai), for Claude Code and any other agent that
reads `SKILL.md`: Codex, GitHub Copilot, Cursor, Gemini CLI and more.

Each skill is a folder of written know-how: when to use it, the steps, and any scripts or
references it needs. No skills are published yet. This repo is where they will appear.

## Install

**Claude Code**

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
