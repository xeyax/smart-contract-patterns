# Branch Reviewer Prompt

Use this prompt when the user wants to evaluate proposed catalog changes already
present on a branch, PR, or commit range.

## Task

Compare the current branch's catalog changes against the base catalog and decide
whether each change should be kept, revised, split, or rejected.

## Inputs

- Base branch or commit. If not provided, infer from upstream tracking branch or main branch.
- Current branch or diff range.
- Optional target repo evidence used to justify the branch changes.

## Read

- `git diff --stat <base>...HEAD`.
- `git diff <base>...HEAD -- patterns/ ANTIPATTERNS.md README.md process/ skills/`.
- Added/modified source docs, not only `patterns/INDEX.md`.
- Relevant unchanged catalog docs that overlap with the diff.
- Evidence files in the target repo if the branch claims to harvest from one.

## Output

```
BRANCH_REVIEW
Base: <base>
Head: <head>

1. Change: <file or grouped files>
   Verdict: keep | revise | split | reject
   Reason: <why this is better/worse than base catalog>
   Evidence quality: high | medium | low | missing
   Catalog impact:
   - improves: <what future reuse improves>
   - risks: <duplication, contradiction, weaker safety claim, stale index, etc.>
   Required edits:
   - <specific change, or "none">

SUMMARY
- Keep: <N>
- Revise: <N>
- Split: <N>
- Reject: <N>
- Blockers: <list>
```

## Decision Rules

- `keep`: evidence-backed, reusable, scoped, and consistent with existing docs.
- `revise`: useful direction but wording, scope, links, metadata, or evidence needs work.
- `split`: one doc/change mixes distinct patterns or risks that should be separate.
- `reject`: duplicate, weaker than existing guidance, unsupported, too project-specific, or unsafe.

## Checks

- Does the branch improve selection quality for future agents, or just add more text?
- Does it make a stronger safety claim than the evidence supports?
- Does it duplicate a pattern/risk already present under another name?
- Are Use When / Avoid When boundaries clearer than before?
- Are requirements and related patterns linked correctly?
- Is `patterns/INDEX.md` regenerated, not hand-edited?
- Does README drift from generated catalog metadata?

## Rules

- Review source docs, not generated index changes alone.
- Do not equate "more detailed" with "better". Prefer concise reusable guidance.
- If a change is good but belongs in another existing doc, choose `revise`, not `reject`.
