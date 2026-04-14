# participant-matrix.md formatting rules

## Participant categories (rows)

Default abstract categories (do not use specific role names like `owner`, `keeper` — those are architecture decisions):

- **Users** — unprivileged callers consuming the system's primary functions.
- **Privileged roles** — restricted operations: configuration, emergency actions, parameter changes.
- **Permissionless callers** — open to anyone; typically time-sensitive or maintenance triggers.
- **External systems** — oracles, base protocols, sibling components, callbacks.

Profile may add or replace categories (see profile-specific format file).

## Structure

```markdown
# Participant × Action Matrix

| Participant \ Action | Submit request | Query result | Configure parameter | Halt processing | Trigger maintenance |
|----------------------|----------------|--------------|---------------------|-----------------|---------------------|
| Users                | FR-001         | FR-002       | —                   | —               | —                   |
| Privileged roles     | —              | —            | FR-010              | FR-011          | —                   |
| Permissionless       | —              | —            | —                   | —               | FR-014              |
| External systems     | —              | —            | —                   | —               | —                   |

## Coverage notes

- Users: submit + query covered. No subscription or update actions yet.
- Privileged roles: configuration + halt covered. Recovery action missing.
  [GAP]: privileged recovery action implied by Purpose but no FR
- Permissionless: maintenance trigger covered.
- External systems: no FR describes interaction with declared external dependency yet.
  [GAP]: external dependency mentioned in Constraints but no FR uses it
```

## Rules

- One row per participant category, one column per distinct action.
- Cells: comma-separated FR-IDs or `—` (empty).
- An empty cell where the category is implied by Purpose → `[GAP]` line in coverage notes.
- A category with NO covered actions → `[GAP]: <category> mentioned but has no requirements`.
