# Architecture Decision Detail Template

Standard sections for detail files. Each decision node in the tree links to a detail file via `[d:tag]`.

File: `details/d:{tag}.md`

## Sections

All sections optional — use what's relevant. But Context, Decision, and Alternatives are expected for every non-trivial decision.

```markdown
# d:{tag} — {Decision title}

## Context
Why this decision is needed. Which requirements drive it (FR-NNN, NFR-NNN, R-NNN).
What constraints apply.

## Decision
The chosen approach. Concrete: names patterns, mechanisms, specific choices.
One paragraph.

## Alternatives
- **{Alternative 1}** — ✓ chosen: {why this is best for our context}
- **{Alternative 2}** — rejected: {concrete reason}
- **{Alternative 3}** — rejected: {concrete reason}

Each alternative: what it is + why chosen/rejected. ≥2 alternatives required.

## Consequences
What follows from this decision — both positive and negative.
- {Positive consequence}
- {Negative consequence / trade-off} — accepted because {reason}

## Formula
(If applicable) Mathematical relationship. All variables defined.

Example:
feeShares = supply × feePerShare / (currentPPS - feePerShare)
where feePerShare = (currentPPS - hwm) × feeBps / 10000

## Assumptions
What must be true for this decision to be safe. Each assumption is a potential failure point.
- {Assumption 1} — if violated: {consequence}
- {Assumption 2} — if violated: {consequence}

## Edge Cases
Boundary conditions and special states.
- Zero supply → {behavior}
- Maximum value → {behavior}
- First time → {behavior}

## Requirements
Traceability: which requirements this decision satisfies.
- FR-003: fee on net gains → this decision defines HOW
- NFR-004: fee accrual safety → cache + nonReentrant
```

## Naming

- Detail file: `details/d:{slug}.md` (e.g., `details/d:fee-model.md`)
- Tag in tree: `[d:{slug}]` links to detail
- Decision ID in tree: `AD-NNN` (sequential)

## Tree Node Format

In the tree file, a decision node looks like:
```
- ✓ AD-003: Fee only on net positive gains [d:fee-model]
  - ✓ AD-004: Fee peak immutable [d:fee-reset]
  - ✓ AD-005: Fee collection as share dilution [d:fee-collection]
```

Short answer inline. Full reasoning in detail file.
