# Shared Liquidity Kernel

> Centralize custody and interest accounting in a restricted liquidity core while user-facing fTokens, vaults, and DEX modules act as adapters.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, kernel, lending, adapters, custody |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Multiple protocol modules need to draw from the same supplied liquidity
- The system can restrict writers to audited protocol contracts
- A single core can own token custody and authoritative accounting
- User-facing modules can translate actions into core operate calls

## Avoid When

- Independent products need isolated custody or blast-radius control
- External integrations can write to the core directly
- Core accounting cannot enforce per-protocol limits and callback settlement

## How It Works

The liquidity core owns reserves and exposes a narrow operation interface to approved protocols:

```solidity
function operate(
    address token,
    int256 supplyDelta,
    int256 borrowDelta,
    address callbackTarget,
    bytes calldata data
) external onlyProtocol returns (uint256 supplyExchangePrice, uint256 borrowExchangePrice) {
    _accrue(token);
    _applyProtocolLimits(msg.sender, token, supplyDelta, borrowDelta);
    _runSettlementCallback(callbackTarget, data);
    _reconcileBalances(token);
}
```

Adapters implement fTokens, vaults, DEX positions, or liquidations while the core remains the single accounting owner.

## Key Points

- Keep the core's writer set small and protocol-scoped.
- Enforce per-protocol borrow and withdrawal limits inside the core.
- Use callback or balance-delta settlement when adapters source tokens externally.
- Provide official resolvers so users do not depend on raw packed storage.
- Frame this as a controlled exception to generic shared mutable state warnings.

## Source Evidence

- Fluid uses a shared liquidity layer for custody and accounting, while fTokens, vaults, and DEX modules route user actions through protocol-scoped liquidity operations.

## Related Patterns

- [Progressive Protocol Liquidity Limits](../lending/pattern-progressive-protocol-liquidity-limits.md)
- [Verified Callback Settlement](./pattern-verified-callback-settlement.md)
- [Shared Mutable State](../../ANTIPATTERNS.md#shared-mutable-state)
