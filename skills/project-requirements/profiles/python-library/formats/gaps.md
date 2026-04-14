# gaps.md formatting rules

## Structure

```markdown
# Gaps

| # | Marker | Artifact | Description | Parent | Item type | Item text | Priority |
|---|--------|----------|-------------|--------|-----------|-----------|----------|
| 1 | GAP | participant-matrix | Extension capability implied in Purpose but no FR | FR-006 | FR | Library accepts user-provided implementations of the input filter capability | Must |
| 2 | GAP | boundary-map | No failure mode for filesystem reads | C-002 | R | Filesystem read fails or returns truncated content | Must |
| 3 | CHOICE | glossary | Term 'cache' defined by inferring from FR-008 usage | FR-008 | C | Define cache scope and invalidation policy formally in glossary | Should |
| 4 | GAP | threat-coverage | DoS via unbounded input | — | R | Caller can submit arbitrarily large input | Must |
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
