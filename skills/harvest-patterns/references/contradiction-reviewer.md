# Contradiction Reviewer Prompt

Use this prompt before writing or after draft edits to check consistency between
new harvested knowledge and the existing catalog.

## Task

Find contradictions, duplicate claims, stale links, and requirement mismatches.

## Read

- Candidate report or draft diff.
- Target source evidence.
- Relevant existing pattern/risk/req docs.
- `ANTIPATTERNS.md` when the change concerns hazards, mitigations, or "never do this" guidance.
- `patterns/INDEX.md` if docs were already regenerated.

## Checks

1. **Requirement alignment** — does a pattern claim to satisfy/violate the right R1-Rn items?
2. **Use/Avoid consistency** — does a new Use When contradict an existing Avoid When without explaining scope?
3. **Risk direction** — are mitigations described as eliminating a risk when they only reduce it?
4. **Formula/rounding consistency** — are formulas and rounding directions compatible across docs?
5. **Oracle/security claims** — are freshness, manipulation resistance, availability, and centralization claims precise?
6. **Evidence integrity** — does every new claim trace to source evidence or a clearly labeled inference?
7. **Link integrity** — are relative links valid and related docs linked both ways when appropriate?
8. **Generated index consistency** — does `patterns/INDEX.md` reflect source docs after regeneration?
9. **Anti-pattern consistency** — does a pattern recommend behavior that `ANTIPATTERNS.md` warns against without naming the required guardrail?

## Output

```
CONTRADICTIONS: <N>

1. Severity: blocker|warning|note
   Files: <paths>
   Claim A: <quote or precise paraphrase>
   Claim B: <quote or precise paraphrase>
   Problem: <why they cannot both stand as written>
   Fix: <specific section-level change>

EVIDENCE GAPS: <N>
- <claim without sufficient evidence>

SAFE TO WRITE: yes|no
```

## Rules

- Block only real contradictions or unsupported safety claims.
- Do not block on wording/style preferences.
- If both claims are true in different scopes, recommend adding the scope boundary rather than deleting either claim.
