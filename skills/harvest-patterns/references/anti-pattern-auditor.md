# Anti-Pattern Auditor Prompt

Use this prompt to audit a target repository or branch against the current
anti-pattern catalog and to discover new broadly reusable anti-pattern guidance.

## Task

Detect known anti-patterns, identify near misses, and propose generalized catalog
updates when the target repo reveals a reusable hazard not yet captured.

## Read

- `ANTIPATTERNS.md`.
- Target repo map from `repo-mapper`.
- Relevant contracts, libraries, tests, scripts, docs, ADRs, audit notes.
- Existing `patterns/<category>/risk-*.md` files when a finding is category-specific.

## Output

```
ANTI_PATTERN_AUDIT

1. Finding: <name>
   Severity: blocker | warning | note
   Type: known-antipattern | near-miss | new-antipattern | category-risk
   Catalog source: ANTIPATTERNS.md section or "new"
   Target evidence:
   - <path>:<line/symbol/test> — <what this proves>
   Why it matters: <impact>
   Existing mitigations in target: <none or evidence>
   Catalog action: none | update-antipattern | add-antipattern | add-risk-doc | update-risk-doc
   Target-repo action: <optional recommendation; do not apply unless user asked to fix target repo>
   Confidence: high | medium | low

SUMMARY
- Known anti-patterns: <N>
- New anti-pattern candidates: <N>
- Category risk updates: <N>
- No-action notes: <N>
```

## Severity Rules

- `blocker`: clear exploitable or high-impact unsafe pattern with no visible mitigation.
- `warning`: anti-pattern appears mitigated incompletely, or evidence is strong but impact is bounded.
- `note`: no explicit bug, but target lacks a decision or test covering a known hazard.

## Catalog Action Rules

- Use `update-antipattern` when `ANTIPATTERNS.md` already has the hazard but lacks this variant, trigger, or mitigation.
- Use `add-antipattern` when the hazard is broad across smart-contract systems and not category-specific.
- Use `add-risk-doc` or `update-risk-doc` when the hazard belongs mainly to one pattern category such as vaults or oracles.
- Use `none` when the target has a local issue but the catalog already covers it well.

## Rules

- Do not treat missing evidence as proof that a mitigation is absent; report it as "not found in inspected scope".
- Do not automatically patch the target repository. This skill enriches the catalog unless the user separately asks for target repo fixes.
- Generalize names and mitigations. Avoid importing project-specific labels into `ANTIPATTERNS.md`.
- Prefer evidence from tests, exploit reproductions, or audit findings over speculative code smells.
