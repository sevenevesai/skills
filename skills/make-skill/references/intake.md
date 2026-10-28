# Intake

Fill these fields before drafting. Mark each one:

- **verified**: there is evidence in the session, the files or the history;
- **claimed**: the user said it, and it is plausible but unconfirmed;
- **missing**.

The marks decide what to ask about. A claimed fact that the skill's behaviour rests on is worth
a question. A claimed detail that only colours an example is not.

## Fields

**Job.** One sentence: what does a session do better with this skill than without it?

**Baseline failures.** What a capable model gets wrong or does slowly without the skill. This
is the skill's reason to exist, and the first thing its test cases check. A run with no skill
verifies it best. Second best is a correction the user made in a past session.

**Trigger phrasings.** Requests a user would actually type, in their own words, plus the
near-misses that belong to something else. A skill with no neighbours needs two or three. One
that competes with similar skills needs enough to show where the boundary is.

**Workflow.** The ordered steps, each decision point with its criteria, and the order
constraints that really matter (not just the order things happened in once).

**Expert knowledge.** Gotchas with their symptom and remedy, constraints with the cost of
breaking them, formats, and failure modes. A skill whose steps are all obvious is a
checklist. That can still be worth writing, but write it as a checklist rather than padding
it into more.

**Inputs and outputs.** What the skill consumes (files, arguments, context) and the exact
shape of what it produces.

**Worked example.** A concrete input and its output. Worth including when the output shape is
hard to describe, or the first attempt is likely to be structured wrong.

**Verification.** How the session running the skill knows it succeeded: a command and its
success signal, a property to check, or the questions the user would ask of subjective output.

**Requirements.** CLI tools and minimum versions, MCP servers, paid services and logins, the
operating system, and network access. These go into `compatibility` and decide where the
skill can run at all.

**Boundaries.** What is out of scope, and when the skill should not fire. Anything scoped out
because a fact couldn't be verified goes here and into the body.

**Reusable resources.** What to bundle: scripts (code each run would otherwise rewrite),
references (schemas, API notes, long patterns), assets (templates, boilerplate). The signal is
repetition. If two runs write the same helper, it belongs in `scripts/`.

**Test prompts.** At least two should-fire prompts and one near-miss, drawn from the trigger
phrasings. They become the first test cases.

## Before drafting

Job, baseline failures, workflow, expert knowledge and verification should be verified or
confirmed by the user, since the skill's value rests on them. Trigger phrasings and boundaries
can be drafted now and checked with the user when you present the skill. A missing fact that
would change what the skill does goes back to the user. A missing fact that wouldn't is left
out, not invented.
