# participant-matrix.md formatting rules — Solidity

## Participant categories (rows) — abstract, NOT specific role names

- **Depositors / users** — unprivileged callers consuming primary functions.
- **Privileged roles** — restricted operations (configuration, emergency, parameter changes). Do NOT use specific names (`owner`, `keeper`, `operator`, `admin`) — those are architecture decisions.
- **Permissionless callers** — open to anyone (typically time-sensitive: liquidations, rebalances).
- **External protocols** — oracles, base vaults, lending markets, DEX routers, callbacks.

## Structure

```markdown
# Participant × Action Matrix (Solidity)

| Participant \ Action | Deposit | Redeem | Configure fee | Pause | Liquidate |
|----------------------|---------|--------|---------------|-------|-----------|
| Depositors           | FR-001  | FR-002 | —             | —     | —         |
| Privileged roles     | —       | —      | FR-010        | FR-011| —         |
| Permissionless       | —       | —      | —             | —     | FR-014    |
| External protocols   | —       | —      | —             | —     | —         |

## Coverage notes

- Depositors: deposit + redeem covered.
- Privileged roles: configuration + pause covered. Emergency unwind missing.
  [GAP]: privileged emergency unwind implied by Purpose but no FR
- Permissionless: liquidations covered.
- External protocols: oracle interaction needed but no FR describes it.
  [GAP]: oracle in Constraints but no FR uses it
```

## Rules

Same as generic, but:
- Use Solidity-domain action names: `deposit`, `redeem`, `claim`, `pause`, `liquidate`, `rebalance`, etc.
- DO NOT name specific roles (`owner`, `keeper`) — use abstract categories.
- For multi-action capabilities, one cell may list multiple FRs.
