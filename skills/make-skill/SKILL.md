---
name: make-skill
description: Creates, improves, or extracts an Agent Skill (a SKILL.md folder) from a workflow, a past session, or an existing skill, and proves it works by running test cases with and without the skill. Use whenever a SKILL.md is about to be written or changed, even for a quick fix, and when the user says "make a skill for X", "turn this into a skill", "save this workflow so you always do it this way", "improve my X skill", "my skill never triggers", or "write evals for my skill". Not for project conventions (a rules or instructions file), behaviour that must happen every time (a hook), or installing someone else's skill.
license: MIT
compatibility: Works in any agent that reads SKILL.md. The test cases use the format of Claude Code's `claude plugin eval` (Claude Code 2.1.269 or later); without it, run them with subagents or by hand.
---

# Make a skill

A skill is instructions that a future session follows with no memory of this one. A good one
triggers on the requests it is for, stays quiet on the ones it isn't, carries knowledge a
capable model lacks, and is shown to do better than no skill at all. Skills that only restate
what the model already knows add context cost and nothing else. So write test cases early, and
treat the description as the most important line.

Done means all of these, even when the user is in a hurry or asked about only one part:

1. `SKILL.md` whose description says what the skill does and when to use it, with quoted
   phrasings a user would type.
2. Test cases in the skill's `evals/` folder (step 4): at least three, or the existing cases
   extended to cover the change. Only a pure wording fix that changes no behaviour skips them.
3. A report of what was tested and what wasn't.

Read each reference when its step comes up:

- `references/intake.md`: the facts to collect before drafting, and how to mark them.
- `references/authoring.md`: frontmatter, description, body, structure, portability, scripts.
- `references/evals.md`: writing test cases, running them, and the bar for "proven".
- `references/review.md`: the gates a draft must pass before it is ready.

## 1. Choose the artifact

| The material is | Write |
|---|---|
| A reusable multi-step workflow or body of know-how | A skill. Continue below. |
| A convention for one project ("we use pnpm here") | A rule or project instructions file, scoped to that project. |
| Something that must happen every time, without fail | A hook or a CI check. Skills are advice and can be skipped. |
| Context every session in a project needs | The project's instructions file (CLAUDE.md, AGENTS.md). |

Mixed material is common. Extract the workflow into the skill and leave the project residue
(paths, names, tokens) to a project rule, since a global skill that carries it breaks in the
next project. One skill does one job. Split a skill that serves two unrelated requests.

## 2. Gather evidence before asking

Look before you ask. Sources:

- **This session**, when the work happened here: the tools used and their order, exact commands
  and flags, input and output shapes, the user's corrections, and dead ends.
- **The project**, when the user describes past work: configs, scripts, outputs, docs, and any
  skills or rules that overlap.
- **Session history**, when a history or search tool is available. A recorded run turns a
  described workflow into an observed one.

When improving an existing skill, read every file in it, not just SKILL.md. Copy it aside
unchanged first. That copy is the baseline the new version has to beat.

## 3. Intake

Fill the fields in `references/intake.md` and mark each one verified, claimed or missing.
Then ask only about gaps whose answer would change what the skill does. Batch the questions
into one round, and lead with what you already have. If a fact can't be found, agree a smaller
scope with the user and write that limit into the skill. Don't guess.

## 4. Write the test cases first

Before writing the body, write at least three cases. This applies to improving a skill as much
as to making one, because the cases are how you show the new version beats the old.

- Two or more **should-fire** prompts, phrased the way a user would type them, with real
  detail and without naming the skill.
- One or more **should-stay-quiet** near-misses: requests that share words with the skill but
  need something else.

Each case is a folder, so test runners can find and run it:

```
<skill>/evals/<case-name>/prompt.md      settings block, then the prompt exactly as a user types it
<skill>/evals/<case-name>/graders/*.md   one check per file: did the skill fire, and what it added
```

Read `references/evals.md` before writing the first one and copy its templates, because the
format is strict. If the environment can run them, run the should-fire prompts with no skill
now. What goes wrong there is what the skill has to teach, and anything the baseline already
does well can be left out of the body.

## 5. Draft

Follow `references/authoring.md`. In short:

1. **Name**: lowercase letters, digits and single hyphens, at most 64 characters, the same as
   the folder name. Prefer a verb (`fix-issue`) or a domain noun (`pdf-forms`). Avoid vague
   names, and words a platform reserves such as `claude` and `anthropic`.
2. **Description**: say what the skill does, then when to use it with quoted phrasings a user
   would type, then the near-misses it is not for. Put the main use case first, because agents
   shorten descriptions when they list many skills. Write it in the third person, under 1024
   characters, with no agent tool names (the product the skill drives is fine).
3. **Body**: write in the imperative and give the reason wherever the rule isn't obvious.
   Include only what the model would otherwise get wrong. Give exact commands for fragile
   steps, and leave judgement free where several approaches work. Show a template for any
   structured output, and an input-to-output example where the shape is hard to describe.
4. **Size**: aim for SKILL.md under 150 lines; 500 is the hard limit. Move depth into
   `references/` one level deep, and point to each file with when to read it. A file nothing
   points to is never read. Keep each fact in one place.
5. **Scripts**: when every run would write the same helper, bundle it in `scripts/` and say
   how to run it. A script should handle its own errors and say what it needs.
6. **Side effects**: anything that pushes, publishes, deploys, sends or deletes is named in the
   description, and the body has the session ask the user before doing it. A skill can fire on
   its own, so nothing irreversible may hang on the trigger alone.
7. **Grounding**: every path, command, flag and format must come from evidence or from the
   user. An invented command looks plausible until someone relies on it.

## 6. Prove it

Run every case with the skill and without it, three runs each (how: `references/evals.md`).
The skill is proven when:

- each should-fire case fires the skill in at least two of three runs,
- every case meets its graders (a score of at least 0.8),
- and the skill beats no skill on average.

When a case fails, read its transcript before changing anything. A miss on firing is fixed in
the description; a wrong outcome is fixed in the body. Fix the general cause rather than
special-casing the test prompt, because the skill will meet prompts nobody tested. Cut any
instruction the transcripts show was ignored or wasted effort, then run all cases again.

## 7. Review and deliver

Check every gate in `references/review.md` and fix the failures. A gate can stay open only
when the user waives it and you record the waiver. Then present:

- the skill's files and where to put them: the user's skills folder for cross-project
  workflows, the project's skills folder for one repo, or a plugin to share;
- the test results: fire rate, scores with and without the skill, and the remaining failures;
- one phrase to try in a new session, since a skill loads only when a session starts.

A request to create or edit a skill already authorises writing its files. Ask again only to
overwrite something the user didn't point you at.
