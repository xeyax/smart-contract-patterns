# Items Data Format

Requirements and other items are stored as markdown. Human-readable, editable, parseable by agents.

## File Structure

```markdown
# Requirements: Project Name

## Purpose

What the system is — one paragraph.

## Glossary

- **Term** — definition used in this document.

## Group Name

### FR-001: Title [Must] ✓
Requirement text. One sentence, WHAT not HOW.

**Rationale:** Why this exists.
**Source:** Where it came from.
**Risks:** R-001

**Acceptance criteria:**
- Observable pass/fail condition
- Edge case behavior
- Negative case (→ reverts)

### R-001: Risk title [Must] ✓
Risk description. May include technical details about the threat vector.

### C-001: Constraint title [Must] ✓
Constraint text.

### NFR-001: NFR title [Must] ✓
Non-functional requirement text.
**Acceptance criteria:**
- Measurable criterion
```

## Special Fields

### `**Deferred:**`

Item skipped with reasoning. Status `?`. Contains user's reasoning and dependency. Proposer sees it and won't re-propose. Validator can suggest revisit if conditions change.

### `**Validated:**`

User reviewed a specific validator concern and rejected the flag — the item text is intentionally as-is. One line per rejected concern:

```markdown
**Validated:** "output metrics define the product interface, not implementation" — WHAT/HOW concern rejected (Round 2)
**Validated:** "'efficiency' is a named metric category, quantified in AC" — vague terms concern rejected (Round 4)
```

Structure: `**Validated:** "<reasoning>" — <concern description> rejected (Round N)`

- **Reasoning** (in quotes) — WHY the user considers the text correct despite the validator flag. Must clearly describe the concern being addressed. "User confirmed" alone is not enough — the reasoning must explain why the item is correct.
- **Concern description** — human-readable description of what was flagged (e.g. "WHAT/HOW concern", "vague terms concern", "boundary coverage concern", "missing failure mode"). No numeric IDs needed — validator matches semantically.
- **Round** — when rejected.

Validator behavior: match by the **concern described in the annotation**, not by exact string. If the annotation's reasoning and concern description clearly address the same issue your rule checks — skip. Example: annotation says "WHAT/HOW concern" and you are checking the WHAT-not-HOW rule → match, skip. Other rules still apply.

When writing the annotation, gather MUST include a meaningful concern description. Bad: "user says it's fine" (no concern identified). Good: "output metrics are product interface — WHAT/HOW concern" (concern is clear).

Lifecycle: if item **title, body text, OR acceptance criteria** are changed, ALL `**Validated:**` annotations are removed (changed content = new validation needed). Only pure metadata changes (priority, group, source, rationale) preserve annotations.

## Parsing Rules

- `## Section` = group (Core Flows, Performance Fee, Constraints, etc.)
- `### ID: Title [Priority] Status` = item. ID prefix = type (FR-, NFR-, C-, R-).
- First paragraph after heading = item text
- `**Field:**` = metadata (Rationale, Source, Risks, Deferred, Validated)
- `**Acceptance criteria:**` + bullet list = children
- Status: ✓ (confirmed), → (proposed), ? (open)
- Priority: [Must], [Should], [Could]

## Rules

- All types (FR, NFR, C, R) in one file, any group.
- Related items together (risk next to the FR it relates to).
- Requirements describe WHAT, not HOW.
- Each FR should have acceptance criteria.
- Purpose at the top, before any items. Out-of-scope items live in Deferred section.
