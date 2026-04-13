# Call Diagrams Formatting Rules

Rules for `call-diagrams.md` artifact. Also see `mermaid.md` for general mermaid rules.

## Structure

One `##` section per operation. Each section contains:
1. `sequenceDiagram` mermaid block
2. No text summary (call-diagrams are self-documenting via postconditions)

## Postconditions

Follow `mermaid.md` rules. Additionally:
- Every significant step should have a `POST:` note — these become test assertions.
- **Quantitative where possible.** If the relationship is expressible as a formula, write the formula, not prose. These POST notes become exact `assertEq` checks in specs.
  ```
  Good:  POST: shares == assets * totalSupply / totalAssets
  Bad:   POST: user received wrapper shares
  ```
  Use qualitative POST only when the exact formula depends on implementation details not decided at architecture level.
- Use `alt`/`else` for conditional paths, `loop` for iterations.
- Max 12 steps per diagram. If more complex — split into sub-diagrams.

## Operation coverage

Cover ALL operation categories:
- User actions (deposit, withdraw, redeem)
- Keeper/bot actions (rebalance, harvest)
- Admin/governance actions (setFee, pause)
- Emergency actions (pause, migration)
