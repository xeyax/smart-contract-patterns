# Architecture Decision Detail Template

Standard sections for detail files. Each decision node in the tree links to a detail file via `[[details]](details/AD-NNN-slug.md)`.

File: `details/AD-NNN-slug.md`

## Sections

**Required:** Context, Decision, Alternatives, Consequences — every decision must have these (Consequences must include both positive and negative per decision-quality Rule 3). **Optional:** Formula, Assumptions, Edge Cases, Requirements — use what's relevant.

```markdown
# {Decision title}

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

- Detail file: `details/AD-NNN-slug.md` (e.g., `details/AD-003-fee-model.md`)
- Decision ID: `AD-NNN` (sequential, stable — never renumbered)

## Tree Node Format

Title format: `AD-NNN: <topic> → <choice>` — the reader should understand the decision from the title alone without opening the detail file. Topic = what question is being decided. Choice = what was chosen.

In the tree file, a decision node with clickable link to detail:
```
- ✓ AD-001: Contract decomposition → Vault + Strategy two-contract split [[details]](details/AD-001-contract-split.md)
  - ✓ AD-002: Fee gain tracking → global HWM with share dilution [[details]](details/AD-002-fee-hwm.md)
  - ✓ AD-003: Fee peak lifecycle → immutable (never reset) [[details]](details/AD-003-fee-reset.md)
```

Full reasoning in detail file. Link is relative to tree file.
