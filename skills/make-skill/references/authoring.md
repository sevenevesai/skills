# Authoring standard

Contents: format and frontmatter · the description · body · structure and size · scripts ·
portability across agents · safety · grounding. Read top to bottom when drafting; use it as a
lookup when editing.

The format is the open Agent Skills specification (agentskills.io/specification), which Claude
Code, Codex, GitHub Copilot, Cursor, Gemini CLI and others read.

## Format and frontmatter

A skill is a folder holding `SKILL.md`: YAML frontmatter, then Markdown. Optional `scripts/`,
`references/` and `assets/` sit beside it.

| Field | Rule |
|---|---|
| `name` | Required. 1-64 characters: lowercase letters, digits and single hyphens, no hyphen at either end. Must equal the folder name. Claude's platform rejects names containing `claude` or `anthropic`. |
| `description` | Required. 1-1024 characters, with no `<` or `>`: Anthropic's skill validator rejects them and Claude Code lists them as `&lt;` and `&gt;`. See below. |
| `license` | A license name, or the name of a license file in the folder. Set it for anything shared. |
| `compatibility` | Up to 500 characters: required tools and versions, services, network, operating system. |
| `metadata` | A map of string keys to string values, for things like `author` or `version`. Quote numbers so they stay strings. |
| `allowed-tools` | Experimental, and each agent treats it differently. Leave it out unless the skill needs it. |

Agents add fields of their own: Claude Code has `disable-model-invocation`, `argument-hint`,
`when_to_use`, `paths`, `context` and more, and Cursor and Codex have theirs. Other agents
ignore them, and claude.ai rejects an upload that has them. Use one only when the skill is
meant for that agent and needs the behaviour, such as keeping a deploy skill from firing on
its own.

## The description

Agents load only the name and description of every installed skill, and choose from those
alone. The body arrives after the decision, so guidance on when to use the skill must be in
the description or it does nothing.

Write it in this order:

1. What the skill does, with concrete verbs and objects.
2. When to use it: "Use when the user says ..." with three to six quoted phrasings, written the
   way people type them, including ones that don't name the topic directly.
3. What it is not for, when a neighbouring skill or tool could claim the same request.

Keep it to the point:

- **Main use case first.** When an agent lists many skills it shortens or drops descriptions to
  fit a budget (in Claude Code, about 1% of the context window), so the end of a long
  description may never be seen.
- **Third person** ("Creates ...", "Use when the user ..."). The description is routing data,
  not an address to the reader.
- **Claim the territory.** Models tend to skip skills for work they think they can handle
  alone, and quoted user phrasings don't fix that on their own. Name the moment the skill
  applies, in terms of the work itself ("whenever a migration file is about to be written,
  even a small one"), as well as the words users type. Bound the claim with near-misses
  rather than "use whenever in doubt".
- **No agent tool names or harness steering.** Names like `Bash` or `WebFetch` differ between
  agents, and steering belongs in the body. Naming the product the skill drives (a CLI, an
  API, a service) is fine and often the best trigger word.

Good: `Fixes a GitHub issue by number, following the repo's test and commit conventions. Use when the user says "fix issue #123", "pick up this ticket", or pastes an issue link. Not for opening new issues.`
Bad: `GitHub helper.` It has no verbs and no triggers, so nothing routes to it.

## Body

- **Imperative, with reasons.** "Validate the frontmatter before writing" rather than "you
  should". Give the reason where the rule isn't obvious, so the model can handle cases the
  rule didn't foresee. Capitals and bold commands make a model over-weight that line and
  neglect the rest; use plain sentences.
- **Only what the model lacks.** Assume a capable reader. Cut general advice it already
  follows; keep the gotchas, exact formats and decisions it would get wrong.
- **Gotchas name the failure.** List the non-obvious mistakes in one place, each with what
  goes wrong, how it shows and what to do instead. "Handle errors carefully" teaches nothing;
  "the export exits 0 on a locked file and writes an empty CSV, so check the row count" does.
- **One default, not a menu.** Name the tool or approach to use. Mention an alternative only
  with the condition that calls for it, or every run spends effort choosing.
- **Requirements first.** Put what every run must do, and the gates, ahead of depth. After
  compacting a long session an agent may keep only the start of a loaded skill (Claude Code
  keeps the first 5,000 tokens).
- **Match freedom to fragility.** Give exact commands and sequences where a deviation breaks
  something (migrations, releases). Give a parameterised template where a shape matters.
  Leave free judgement where many approaches work.
- **Templates for structured output.** Show the exact skeleton (headings, fields, order)
  rather than describing it.
- **Examples as input and output.** One concrete pair is worth paragraphs of description.
- **Checklists and feedback loops** for multi-step work: do, check, fix, check again. A check
  with a clear signal, such as an exit code, a validator or a diff, is worth more than an
  instruction to "be careful". For output a person will look at (a slide, a page, an image),
  the check is to render it and look, because code that reads as correct can still produce
  overlapping or clipped output.
- **Consistent terms.** Pick one word per concept and keep it throughout.
- **Nothing that goes stale silently.** Avoid "currently" and "the new API". When a fact
  depends on a version, name the version. When a list will age (models, prices, limits), date
  it, so a later run can tell when to check again.

## Structure and size

A skill loads in three stages. Design for each:

1. The name and description are always in context, for every installed skill. Keep them tight.
2. The body loads when the skill triggers. Aim for under 150 lines; the specification's limit is
   500 lines and about 5,000 tokens.
3. Bundled files load only when the body sends the model to them, and scripts can run without
   being read at all.

| Content | Place |
|---|---|
| Workflow, decision points, pointers to other files | `SKILL.md` |
| Schemas, API notes, long patterns, edge cases, long examples | `references/*.md` |
| Code each run would otherwise rewrite | `scripts/` |
| Templates, boilerplate, fonts and images used in the output | `assets/` |

- State every requirement a run must meet in SKILL.md itself, in a line, and leave the detail
  to the reference. Runs often skip references, so a requirement written only there gets
  skipped too. That is not duplication: SKILL.md says what must happen, the reference says how.
- Link every bundled file from SKILL.md with a relative path, and say when to read it. A file
  nothing points to is never read. Spell the name exactly as it is on disk, including letter
  case: `FORMS.md` for a file named `forms.md` resolves on Windows and macOS and not on Linux.
- Keep links one level deep: SKILL.md links to references, and references don't send the
  reader on to more files.
- Give a reference file over 100 lines a contents line at the top.
- For a domain with variants (cloud providers, languages), keep one reference per variant and
  put the selection logic in SKILL.md, so only the relevant file is read.
- Keep each fact in one place. Copies drift apart.

## Scripts

- Bundle a script when the work is deterministic or repeated: parsing, validation,
  conversion, API calls with fixed shapes.
- Say how to run it and what success looks like. Tell the model to run the script rather
  than read it, unless it needs to change it.
- A script handles its own errors and prints what went wrong and what to do next. It doesn't
  fail silently and leave the model to guess.
- Name the packages and versions it needs, and put them in `compatibility`.
- No unexplained constants. A timeout or limit carries a comment saying why it has that value.

An agent runs the script, not a person at a terminal, so its interface follows from that:

- It never waits for typed input. Agents run commands non-interactively, and a prompt hangs
  the run. Everything arrives as flags, arguments or standard input.
- `--help` describes the flags, so the model can learn the interface without reading the
  source.
- The result goes to standard output in a form that can be parsed, diagnostics go to standard
  error, and the exit code is non-zero whenever the work failed or a check found problems.
- Output stays bounded. Agents cut long command output (often somewhere past 10,000
  characters), so print a summary and write the bulk to a file whose path is printed.
- Anything destructive or run over many items offers a dry run that prints the plan, so the
  session can check it before the real run.

## Portability across agents

- Use forward slashes in paths, even for Windows users.
- Name a requirement by what it does ("run the shell command", "search the web") and list
  the tool in `compatibility`. Tool names such as `Bash` or `WebFetch` exist in only some
  agents.
- Leave out one agent's syntax in a skill meant for all of them: argument placeholders like
  `$ARGUMENTS`, inline command injection, or slash-command references.
- If the skill needs an MCP server, give the server's public name and where to get it.

## Safety

- **No surprises.** Nothing the skill does should surprise someone who read only its
  description. Name side effects in the description: network calls, writes outside the
  project, sending, publishing, deleting. Naming one is not permission for it: before an
  irreversible step, the body has the session show what will happen and wait for the user's
  yes, even when the request that fired the skill sounded like one. Where the agent supports
  it, turning off automatic invocation instead is the other safe option.
- **Pre-approve as little as possible.** A shell pre-approved in `allowed-tools` means any
  injected text can run commands.
- **Don't fetch instructions at run time.** A skill that downloads its own instructions can be
  changed after anyone has reviewed it. Data fetched at run time (a catalogue, a price list)
  is fine when the body treats it as data: say which fields to take, to ignore any
  instructions found in it, and what to do when the fetch fails.
- **Read every script before shipping it.** An installed skill runs with the agent's
  permissions.

## Grounding

- Don't invent file paths, package names, commands, flags, API shapes or conventions. Every
  concrete detail must trace to evidence or to the user.
- Don't ship placeholders such as `<TODO>`. A parameter written as `<name>` is fine when the
  text says how to fill it in.
- Generalise beyond the founding example. If an instruction only makes sense for the case the
  skill grew from, lift it to the pattern, or move the example into a reference as an
  illustration.
