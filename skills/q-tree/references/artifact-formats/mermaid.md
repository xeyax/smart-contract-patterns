# Mermaid Formatting Rules

Rules for all mermaid diagrams across artifacts (call-diagrams, token-flows, state-machines).

## Syntax

- **No semicolons in text.** Mermaid parses `;` as a statement separator. In `Note`, labels, and messages: use commas, periods, or split into multiple statements.

## Postconditions

- One `Note right of X: POST: ...` per postcondition. Don't combine multiple postconditions into one Note.
- POST notes go immediately after the step they apply to.
- Explanatory notes (not postconditions) omit the `POST:` prefix.

## Participants (sequenceDiagram)

- Consistent alias across all diagrams in the file. If `participant W as VaultFeeWrapper` in diagram 1, use the same in all diagrams.
- No qualifiers like `(as ERC-20)` in participant aliases. If the contract is used in a different capacity, note it in a comment or explanatory Note.

## Actors (sequenceDiagram)

- Use `actor` for external callers (User, Owner, Keeper, Anyone).
- One actor per diagram unless the flow genuinely involves two external parties.
