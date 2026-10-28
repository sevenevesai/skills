# Test cases and proof

Contents: why test · the case format · graders · running with Claude Code · running without
it · the bar · iterating · tuning the description.

## Why test

Two failures are common, and only a comparison with no skill shows them:

- **The skill never fires.** Models skip skills for requests they think they can handle, so a
  skill that is never invoked teaches nothing, however good its body is.
- **The skill adds nothing.** A model often does as well without a skill that only restates
  general advice. Curated, focused knowledge is what improves results.

So every case runs twice, with and without the skill. The difference between the two scores
is what the skill contributes.

## The case format

Use the layout that Claude Code's `claude plugin eval` reads. These are plain files, so a
person or a subagent can run them by hand as well.

```
evals/
  summarises-standup-notes/      a case: lowercase-hyphen name saying what it tests
    prompt.md                    run settings, then the prompt exactly as a user types it
    graders/
      01-fires.md                one check per file
      02-lists-action-items.md
```

`prompt.md`:

```markdown
---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

here are my notes from this morning's standup, can you turn them into something I can paste in slack? ...
```

- Allowed keys: `max_turns` (default 10), `timeout_seconds` (default 300), `runs` (default
  3), `allowed_tools`, `tags`, `model`, `description`, `expected_outcome`. An unknown key stops
  the case from loading.
- Each run starts in an empty folder, and `@path` mentions are not expanded. Put the material
  the task needs in the prompt itself, or in a fixture: a `case.yaml` with
  `context.scaffold_script` (a bash script that creates files, run only when `--scaffold` is
  passed).
- Write prompts the way users really write: lowercase, typos, file names, a little
  backstory, and no mention of the skill.
- In non-interactive runs nobody answers questions. Make the prompt complete enough to act on,
  as a user who was in a hurry would.

## Graders

A grader is a Markdown file: frontmatter giving its `type` and options, and for `llm` graders
a body holding the rubric.

| Type | Passes when | Cost |
|---|---|---|
| `tool_used` | a tool was called between `min` (default 1) and `max` times; `input_match` filters the calls by regex | free |
| `regex` | `pattern` is found in the `target`: `last_message` (default), `trace`, or `{source: file, path: out.md}`; `match: not_contains` inverts it | free |
| `file_exists` | a file created in the run matches the `path` glob | free |
| `tool_order` | the first `before` call comes before the first `after` call | free |
| `llm` | a judge model votes PASS in two of three votes on the rubric | paid |

**Should-fire case.** Add a firing check and at least one check of the outcome.

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?summarise-standup"'
---
```

The firing check is reported as an indicator and doesn't count toward the score, because it
could never pass without the skill.

**Should-stay-quiet case.** Require zero calls, scored in both runs:

```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?summarise-standup"'
min: 0
max: 0
arm: both
---
```

**Outcome checks** test what the skill adds. That is not the same as what any answer would
contain. If a check passes just as often without the skill, it measures the model, not the
skill. Keep it only as a floor, and add one that tells the two runs apart.

- For long or mechanical output, use `regex` over the file, which checks the whole file the
  same way every time.
- For short output that needs judgement, use `llm` with concrete conditions:

```markdown
---
type: llm
focus: { source: file, path: standup.md }
---

PASS if every action item names an owner and the items are grouped by person.
FAIL if an action item has no owner, or the notes are restated as prose.
```

## Running with Claude Code

`claude plugin eval` loads a plugin, so lay the skill out as one:

```
my-plugin/
  .claude-plugin/plugin.json     {"name": "my-plugin"}
  skills/<skill-name>/SKILL.md   the skill folder, copied as is
  evals/<case>/...               the cases
```

Then run `claude plugin eval my-plugin --allow-tools Write Edit`. It runs each case three
times with the plugin and three times without. It writes `evals/results/<time>/` with
`aggregate-result.json` and `report.html`; add `results/` to `.gitignore`.

- Each run is a real, billed model session. Cost is roughly cases × runs × 2 sessions, plus
  judge calls. Cap it with `--max-cost-usd`.
- Pin `--model` to the weakest model you expect people to use, and pass a stronger
  `--judge-model` than the default when `llm` graders decide close calls.
- Shell tools need the OS sandbox: macOS, Linux with `bubblewrap` and `socat`, or WSL2 on
  Windows. Native Windows refuses runs that grant a shell, so test shell-heavy skills on one of
  the others.
- The first run in a new folder asks you to trust it. `--trust-plugin` answers yes, for CI.

## Running without it

Start two fresh subagents per case and run: one with the skill folder available and one
without. Save each run's output, then have a separate reader grade each check against it and
record pass or fail with evidence. The bar below still applies. Hand-run tests are weaker,
because the author's context leaks in, so prefer the CLI wherever it is available.

## The bar

A skill is proven when, over three runs per case:

- the suite has at least two should-fire cases and one should-stay-quiet case;
- each should-fire case fires the skill in at least two of its three runs;
- every case scores at least 0.8;
- and the average score with the skill beats the average without it.

Record the date, the model, the scores and the fire rates with the skill. Run again whenever
the skill or the cases change, and when a new model comes out.

## Iterating

1. Read the transcripts of failing runs, not just the scores.
2. Failed to fire: rework the description (see the next section). Fired but got it wrong:
   rework the body.
3. Fix the cause in general terms. The skill will meet prompts nobody tested, so a patch
   aimed at one test prompt helps nothing else.
4. Remove instructions the transcripts show were ignored or caused wasted steps.
5. If every run wrote the same helper, bundle it in `scripts/`.
6. Run all cases again, not just the one that failed.

## Tuning the description

When firing is unreliable, test the description on its own:

- Write about 20 queries: 8 to 10 that should fire and 8 to 10 near-misses that share its
  vocabulary but need something else. Obviously unrelated negatives test nothing.
- Make them substantive. Agents use skills for multi-step work, so a trivial one-line request
  may not fire a well-described skill at all.
- Hold back about 40% of them. Revise using the rest, run each query three times, and keep
  the version that scores best on the held-back queries. That way you don't tune to the
  queries you revised against.
- Don't paste words from failed queries into the description. Describe the intent those
  queries share.
