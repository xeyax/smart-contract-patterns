# Catalog Comparer Prompt

Use this prompt after extraction to decide how candidates relate to the current
smart-contract-patterns catalog.

## Task

Compare candidate items against the current catalog and recommend exact write actions.
Also decide whether a proposed update is materially better than what the catalog
already says, especially during branch review.

## Read

- Candidate report from extractors.
- `patterns/INDEX.md`.
- Relevant `patterns/<category>/*.md` files.
- `ANTIPATTERNS.md` when candidates are broad dangerous practices.
- `README.md` only for navigation drift, not as source of truth.

## Output

```
COMPARISON

1. Candidate: <title>
   Decision: add-new | update-existing | merge-into-existing | add-antipattern | reject
   Worth applying: yes | no | only-after-revision
   Target file: <path or none>
   Existing overlap:
   - <doc>: <overlap>
   Novel contribution:
   - <what is actually new>
   Required edits:
   - <section-level edit plan>
   Conflict risk:
   - none | <specific existing claim that may conflict>
   Confidence: high|medium|low
```

## Decision Rules

- `update-existing`: candidate adds caveat, variant, example, mitigation, or edge case to an existing doc.
- `merge-into-existing`: candidate overlaps several docs; recommend the single primary doc and cross-links.
- `add-new`: candidate has distinct mechanics, separate Use When / Avoid When, and enough evidence.
- `add-antipattern`: candidate is a broad hazard not specific to one pattern category.
- `reject`: candidate is too narrow, unsupported, duplicate, or contradicted by stronger catalog guidance.

## Rules

- Prefer fewer, better docs over many tiny patterns.
- Do not recommend an update unless it improves future selection, safety reasoning, scope boundaries, source evidence, or contradiction resolution.
- If the existing doc is stronger or clearer than the candidate, reject or recommend a narrower note instead of replacing it.
- Preserve generated `patterns/INDEX.md`; only recommend source doc changes plus regeneration.
- If README differs from the generated index, recommend either updating README or making the manual section defer to `patterns/INDEX.md`.
