# Bounded Token Inflation

> Constrain privileged token minting with explicit rate, amount, recipient, and delay bounds so governance cannot silently create unlimited supply.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, token, minting, inflation, supply-cap |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Governance or a rewards controller can mint protocol tokens
- Inflation is expected but should be predictable
- Token holders need enforceable supply-change bounds
- Minting powers are distributed across multiple modules or chains

## Avoid When

- Token supply is intended to be immutable
- Minting limits are only documented off-chain
- Emergency actors can bypass the same bounds

## Trade-offs

**Pros:**
- Makes dilution risk inspectable on-chain
- Reduces governance-key blast radius
- Gives monitoring systems clear thresholds

**Cons:**
- Legitimate large emissions require staged governance
- Supply-cap math must account for all minters
- Bounds can create coordination work during migrations

## How It Works

Track a minting budget over a window:

```solidity
struct MintBudget {
    uint256 windowStart;
    uint256 mintedInWindow;
    uint256 maxPerWindow;
}

function mint(address to, uint256 amount) external onlyMinter {
    _rollWindowIfNeeded();
    require(mintedInWindow + amount <= maxPerWindow, "inflation cap");
    mintedInWindow += amount;
    _mint(to, amount);
}
```

Governance can change the cap only within a hard maximum and through a delay:

```solidity
require(newCap <= hardMaxPerWindow, "above hard max");
```

## Key Points

- Bound both per-transaction and per-window minting where possible.
- Include all minting paths in the same global budget or explicitly partition budgets.
- Emit budget usage so supply monitors do not need to infer it from transfer events.
- Timelock cap increases; cap decreases can be immediate.
- Test migration, bridge, reward, and emergency mint paths against the same invariant.

## Source Evidence

- Ethena's governance token design includes bounded mint authority so token issuance can expand under governance without becoming unrestricted arbitrary supply creation.

## Related Patterns

- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
- [Flash Loan Governance](../../ANTIPATTERNS.md#flash-loan-governance)
- [Governance as Arbitrary Execution](../../ANTIPATTERNS.md#governance-as-arbitrary-execution)
