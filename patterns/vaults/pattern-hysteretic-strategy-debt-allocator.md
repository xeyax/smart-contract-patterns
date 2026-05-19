# Hysteretic Strategy Debt Allocator

> Rebalance vault strategy debt only when deviation, elapsed time, idle liquidity, strategy liquidity, and gas conditions justify moving capital.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, strategy, debt, allocator, keeper |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A vault allocates capital across multiple strategies
- Small debt changes would create churn, gas waste, or strategy disruption
- Strategies expose liquidity and unrealized-loss constraints
- Keepers need deterministic rebalance triggers

## Avoid When

- Strategy allocation is fully manual or single-strategy
- The vault cannot observe strategy liquidity or withdrawal limits
- Debt updates can ignore current losses, base fee, or idle buffer
- Governance wants every tiny target drift to execute immediately

## Trade-offs

**Pros:**
- Reduces keeper churn and unnecessary strategy movement
- Makes rebalance timing and size thresholds explicit
- Avoids withdrawing from illiquid or loss-making strategies by default

**Cons:**
- More parameters to tune and monitor
- Capital can remain away from targets inside the hysteresis band
- Stale strategy reports can make allocator decisions misleading

## How It Works

For each strategy, compute target debt and compare it with current debt. Execute only when the change exceeds a minimum size, enough time has passed, the vault keeps required idle liquidity, the strategy can satisfy the change, base fee is acceptable, and unrealized loss checks pass.

```solidity
function shouldUpdateDebt(address strategy) external view returns (bool, bytes memory) {
    int256 delta = targetDebt(strategy) - currentDebt(strategy);
    if (abs(delta) < minChange[strategy]) return (false, "small");
    if (block.timestamp < lastUpdate[strategy] + minWait[strategy]) return (false, "wait");
    if (block.basefee > maxBaseFee) return (false, "gas");
    if (!_idleBufferPreserved(delta)) return (false, "idle");
    if (!_strategyCanAdjust(strategy, delta)) return (false, "liquidity");
    if (_wouldRealizeExcessLoss(strategy, delta)) return (false, "loss");

    return (true, abi.encodeCall(Vault.updateDebt, (strategy, targetDebt(strategy))));
}
```

### Allocation-Capped Lending-Reserve Variant

For vaults that allocate into lending reserves or cTokens, derive desired reserve
weights with per-reserve caps and an unallocated bucket. Increasing a reserve's
cap should require allowlisted reserve state, stale-reserve and invest-delay
checks should block unsafe movement, and invest or withdraw CPIs should reconcile
post-call token and cToken balance deltas.

## Implementation

### Key Points

- Use both minimum change size and minimum wait time to create hysteresis.
- Preserve idle buffers and queued-withdrawal liquidity before increasing debt.
- Query strategy liquidity and max debt before allocating or withdrawing.
- Gate execution on base fee when keeper economics matter.
- Treat unrealized losses as a guardrail, not only a reporting metric.
- Return machine-readable trigger data for keepers, but re-check inside execution.
- For lending-reserve wrappers, cap allocation per reserve, keep an explicit unallocated bucket, and reconcile post-CPI token and receipt-token deltas.
- Treat reserve allowlisting, stale reserve data, and minimum invest delay as part of allocation safety, not only admin configuration.

## Source Evidence

- Yearn V3 vault periphery's `DebtAllocator.sol` gates debt updates by change size, wait time, idle buffer, strategy liquidity, max debt, base fee, and unrealized-loss checks in `/private/tmp/defillama-source/yearn_vault-periphery/src/debtAllocators/DebtAllocator.sol`.
- `src/test/debtAllocators/TestDebtAllocator.t.sol` covers trigger behavior, debt limits, wait periods, and liquidity-dependent updates.
- Kamino KVault allocates vault assets into whitelisted lending reserves with target allocations, per-reserve caps, an unallocated bucket, stale-reserve and invest-delay checks, and post-CPI balance reconciliation in `/private/tmp/defillama-source/Kamino-Finance_kvault/programs/kvault/src/state.rs`, `handlers/handler_update_reserve_allocation.rs`, `operations/vault_operations.rs`, and `operations/vault_checks.rs`.

## Real-World Examples

- Yearn V3 periphery uses a debt allocator to decide when strategy debt should be updated by automation.

## Related Patterns

- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)
- [Read-Only Keeper Trigger Facade](../automation/pattern-read-only-keeper-trigger-facade.md)
- [Rate-Bounded NAV Report](./pattern-rate-bounded-nav-report.md)

## References

- See Source Evidence.
