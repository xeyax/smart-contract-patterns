# gaps.md formatting rules

## Structure

```markdown
# Gaps

| # | Marker | Artifact | Description | Parent | Item type | Item text | Priority |
|---|--------|----------|-------------|--------|-----------|-----------|----------|
| 1 | GAP | participant-matrix | Privileged recovery action implied in Purpose but no FR | FR-013 | FR | Privileged role can trigger recovery from failed state | Must |
| 2 | GAP | boundary-map | No failure mode for declared external dependency | C-003 | R | External dependency becomes unavailable or returns invalid response | Must |
| 3 | CHOICE | glossary | Term 'quota' defined by inferring from FR-012 usage | FR-012 | C | Define quota scope and reset policy formally in glossary | Should |
| 4 | GAP | threat-coverage | Resource exhaustion via unbounded input | — | R | Caller can submit input of unbounded size | Must |
```

If empty:
```markdown
# Gaps

No gaps — all artifacts are clean.
```

## Rules

- Marker: `GAP` or `CHOICE`.
- Parent: nearest existing item ID (FR-NN / NFR-NN / C-NN / R-NN), or `—` if none.
- Item type: `FR`, `NFR`, `C`, `R`, or `?` (only if truly undecidable — boundary/threat → C/R, behavior gap → FR, quantification gap → NFR).
- Item text: WHAT-not-HOW one-line statement, no mechanism names / formulas / role names. This text is the basis for the proposed item the user will see.
- Priority: `Must` for safety-critical (boundary, threat, consistency) and structural gaps; `Should` for completeness or quality polish; `Could` for nice-to-haves.
- One row per distinct marker (deduplicated).
- Order: roughly by artifact generation order (overview → glossary → matrices → coverage → consistency/ambiguity).
- Do NOT include acceptance criteria here — the reviewer adds them when converting a gap into a proposed item.
- Do NOT include mitigation for R items — R items are threat descriptions only at the requirements level.
