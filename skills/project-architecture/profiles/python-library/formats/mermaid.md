# Mermaid Formatting Rules

Rules for all mermaid diagrams across artifacts (call-diagrams, data-flows, state-machines).

## Syntax

- **No semicolons in text.** Mermaid parses `;` as a statement separator. In `Note`, labels, and messages: use commas, periods, or split into multiple statements.

## Postconditions

- One `Note right of X: POST: ...` per postcondition. Don't combine multiple postconditions into one Note.
- POST notes go immediately after the step they apply to.
- Explanatory notes (not postconditions) omit the `POST:` prefix.

## Participants (sequenceDiagram)

- Consistent alias across all diagrams in the file. If `participant S as Session` in diagram 1, use the same in all diagrams.
- No qualifiers like `(as read-only)` in participant aliases. If a module is used in a different capacity, note it in a comment or explanatory Note.
- External resources as participants with bracketed names: `[filesystem]`, `[subprocess]`, `[network]`.

## Actors (sequenceDiagram)

- Use `actor` for external callers (User code, CLI user).
- One actor per diagram unless the flow genuinely involves two external parties.
