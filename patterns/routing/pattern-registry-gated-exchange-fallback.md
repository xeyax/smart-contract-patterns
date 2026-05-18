# Registry-Gated Exchange Fallback

> Try an allowlisted aggregator route first, then fall back to an allowlisted on-chain wrapper while enforcing final balance-delta slippage.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, swap, aggregator, fallback, allowlist |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Off-chain routing can find better prices but cannot be fully trusted
- Aggregators and wrapper contracts can be allowlisted
- The protocol can measure final input and output balance deltas
- A deterministic on-chain fallback route exists

## Avoid When

- Backend-supplied calldata can target arbitrary contracts
- There is no final slippage check after fees and route execution
- The fallback wrapper has different asset or receiver semantics
- Users cannot set min-out, max-in, fee, and deadline bounds

## How It Works

Validate the aggregator and wrapper, execute the preferred route, and fall back only under controlled failure semantics:

```solidity
function sell(Swap calldata swap) external {
    require(exchangeRegistry.isAggregator(swap.aggregator), "aggregator");
    require(exchangeRegistry.isWrapper(swap.fallbackWrapper), "wrapper");

    uint256 beforeOut = tokenOut.balanceOf(address(this));
    if (!_tryAggregator(swap)) {
        _swapViaWrapper(swap.fallbackWrapper, swap);
    }
    uint256 out = tokenOut.balanceOf(address(this)) - beforeOut;
    require(out >= swap.minOut, "slippage");
}
```

The final balance-delta check is the user-facing safety boundary, not the backend route.

## Key Points

- Allowlist aggregators, wrappers, selectors, and approval targets.
- Enforce final balance-delta slippage after fees.
- Bind user-signed terms to input, output, receiver, deadline, and fee.
- Keep fallback behavior explicit; do not swallow arbitrary failures as success.
- Reset or scope approvals around route execution.

## Source Evidence

- Defi Saver V3 gates exchange aggregators and wrappers through registries, supports fallback routing, and checks final balance-delta slippage after route execution.

## Related Patterns

- [Balance-Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
