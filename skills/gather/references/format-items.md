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

## Parsing Rules

- `## Section` = group (Core Flows, Performance Fee, Constraints, etc.)
- `### ID: Title [Priority] Status` = item. ID prefix = type (FR-, NFR-, C-, R-).
- First paragraph after heading = item text
- `**Field:**` = metadata (Rationale, Source, Risks)
- `**Acceptance criteria:**` + bullet list = children
- Status: ✓ (confirmed), → (proposed), ? (open)
- Priority: [Must], [Should], [Could]

## Rules

- All types (FR, NFR, C, R) in one file, any group.
- Related items together (risk next to the FR it relates to).
- Requirements describe WHAT, not HOW.
- Each FR should have acceptance criteria.
- Purpose at the top, before any items. Out-of-scope items live in Deferred section.
