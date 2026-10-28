# Review gates

Contents: G1 right artifact · G2 triggering · G3 self-contained · G4 grounded · G5 general ·
G6 lean · G7 self-checking · G8 no surprises · G9 portable · G10 proven.

Check every gate, with effort in proportion to what the skill can break. Record pass, fail or
waived for each one. Fix failures before calling the skill ready. Only the user can waive a
gate, after hearing what it costs. Record the waiver, and any limit it puts on the skill, in
the skill itself.

## G1. Right artifact

The content is a reusable workflow or body of know-how. It isn't a one-project convention, a
behaviour that must happen every time, or context every session needs.
*Fails when* the body names one repository's paths, tokens or preferences.
*Fix:* keep the workflow, and move the project residue to a project rule.

## G2. Triggering

Read the name and description alone, as an agent choosing among many skills would. They
should claim each should-fire phrasing and none of the near-misses. Compare them with the
installed skills nearby. Where two could both claim a request, sharpen the one that should
lose.
*Fails when* the description says what the skill is instead of when it is needed, has no
phrasings a user would type, or keeps its when-to-use guidance in the body.

## G3. Self-contained

A session with no memory of the authoring conversation can follow the skill from start to
finish. Read the body as someone who has only the file. Any point where you would hesitate
is a gap.
*Fails when* a step says "process it appropriately", or relies on "as discussed", or an
example only makes sense with the original conversation.

## G4. Grounded

Every concrete detail traces to a verified intake field or to the user: paths, commands,
flags, package names, API shapes, formats.
*Fails when* a command was never run, a schema was recalled rather than read, or a
placeholder remains.
*Fix:* verify it, or ask. If neither works, scope it out and say so in the skill.

## G5. General

The skill still works for uses that differ from the founding example. Imagine two plausible
future uses with different details, and check that every instruction still makes sense.
*Fails when* values from the one worked example are hard-coded, or a rigid rule papers over a
failure nobody understood.

## G6. Lean

SKILL.md holds the workflow in about 150 lines. Depth sits in references one level deep,
code in `scripts/`, and output materials in `assets/`. Every bundled file is linked with when
to read it, and no fact appears twice.
*Fails when* SKILL.md runs long with no split, a file is linked from nowhere, or the test
transcripts show instructions that were ignored or caused wasted steps.

## G7. Self-checking

The skill tells the session running it how to know it succeeded: a command and its success
signal, a property to check, or the review questions for subjective work.
*Fails when* the workflow ends at "produce the output" with no check.

## G8. No surprises

Nothing it does would surprise someone who read only the description. Network calls,
writes outside the project, sending, publishing and deleting are named in the description or
need confirmation in the body.
*Fails when* an automatically triggered skill pushes, deploys, deletes or posts, or makes an
external call nobody was told about.

## G9. Portable

The skill keeps to the open format for the agents it targets. Frontmatter uses only the
specification's fields, unless one agent's field is needed for the behaviour it gives. Paths
use forward slashes, and tools are named by what they do. Every requirement is listed in
`compatibility`. The name avoids reserved words.
*Fails when* the body relies on one agent's syntax or tool names without saying so, or a
requirement only shows up when the skill fails.

## G10. Proven

The test cases in `evals.md` meet the bar there, and the results are recorded: fire rate per
should-fire case, scores with and without the skill, the model and the date.
*Fails when* there are no cases, every case passes just as well without the skill, or the
skill or its cases changed after the last run.

## After the review

Present the draft, its bundled files, the gate results (with anything still open), the test
results and where to put the skill.
