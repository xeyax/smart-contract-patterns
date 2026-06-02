# Extractor Prompt

Use this prompt for subagents that extract candidate catalog items from a mapped
target repository. Run separate extractors for patterns, risks, requirements, and
decisions when the repo is large enough.

## Task

Find reusable knowledge in the target repo. Return structured candidates only;
do not write catalog files.

## Candidate Types

- `pattern`: a reusable solution or implementation approach.
- `risk`: a failure mode, exploit path, or unsafe condition.
- `requirement`: a cross-pattern guarantee, invariant, or safety property.
- `decision`: an ADR-like choice with alternatives and trade-offs.
- `anti-pattern`: a broadly dangerous approach suitable for `ANTIPATTERNS.md`.

## Evidence To Prefer

1. Invariant/fuzz/property tests.
2. Unit tests for edge cases or attack scenarios.
3. Implementation plus comments explaining why.
4. ADRs, design docs, audit reports, postmortems.
5. README claims only when backed by code or tests.

## Output

```
CANDIDATES: <N>

1. Type: pattern|risk|requirement|decision|anti-pattern
   Title: <short name>
   Category: <vaults/oracles/access-control/...>
   Summary: <one paragraph>
   Reusable because: <why this generalizes beyond target repo>
   Use when: <bullets, for patterns/decisions>
   Avoid when: <bullets, for patterns/decisions>
   Trade-offs: <pros/cons or risk impact>
   Evidence:
   - <path>:<line or symbol> — <what this proves>
   Tests:
   - <path>:<test name> — <what behavior is verified>
   Related existing catalog docs:
   - <known doc if obvious, else "unknown">
   Confidence: high|medium|low
   Recommended action: add|update|merge|reject
```

## Rejection Rules

Mark as `reject` when:

- The finding is purely project-specific configuration.
- The behavior is standard boilerplate already well covered by existing docs.
- There is no evidence beyond a weak comment.
- The candidate cannot be explained with clear Use When / Avoid When boundaries.

## Rules

- Do not invent missing motivations. Say when motivation is inferred.
- Keep source terminology in Evidence, but generalize titles and summaries.
- If a candidate conflicts with the current catalog, mark the conflict explicitly instead of smoothing it over.
