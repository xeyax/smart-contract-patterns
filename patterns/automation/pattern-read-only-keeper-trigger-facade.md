# Read-Only Keeper Trigger Facade

> Expose keeper work as read-only trigger checks that return whether execution is needed and the exact calldata to run.

## Metadata

| Property | Value |
|----------|-------|
| Category | automation |
| Tags | automation, keeper, trigger, calldata, vault |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Keepers need to discover report, tend, rebalance, auction, or claim work off-chain
- The executable calldata can be derived from current on-chain state
- Trigger checks must be safe to call from bots, simulations, or dashboards
- Operators need machine-readable reasons when work is not ready

## Avoid When

- Trigger evaluation mutates protocol state
- The returned calldata omits required user, vault, or risk parameters
- Work readiness depends on private off-chain information
- Anyone executing returned calldata would be unsafe

## Trade-offs

**Pros:**
- Standardizes keeper discovery across many maintenance actions
- Makes bot decisions reproducible and testable
- Lets monitoring inspect why an action is or is not executable

**Cons:**
- Read paths can become complex and expensive
- Returned calldata can go stale between simulation and execution
- Trigger facades must mirror execution guards without weakening them

## How It Works

Each trigger is a view function that checks state, risk limits, and cadence. It returns `(canExecute, calldataOrReason)`: executable calldata when true, or an encoded reason when false.

```solidity
function reportTrigger(address strategy) external view returns (bool, bytes memory) {
    if (!_reportDue(strategy)) {
        return (false, abi.encode("not due"));
    }
    if (!_healthCheckLikelyToPass(strategy)) {
        return (false, abi.encode("health check"));
    }
    return (true, abi.encodeCall(Strategy.report, ()));
}
```

Execution contracts must still validate every guard. The facade is a discovery and simulation aid, not an authorization boundary.

## Implementation

### Key Points

- Keep trigger functions `view` or `pure`.
- Return the exact target calldata or enough metadata for a stateless bot to build it.
- Encode failure reasons for dashboards and alerting.
- Mirror cadence, health, fee, and liquidity checks used by execution.
- Treat stale trigger output as expected; execution must re-check.
- Test both ready and not-ready branches for every trigger type.

## Source Evidence

- Yearn V3 periphery's `CommonTrigger.sol` returns `(bool, bytes)` style trigger decisions for reports, tends, auctions, and shutdown-related work in [`src/ReportTrigger/CommonTrigger.sol`](https://github.com/yearn/tokenized-strategy-periphery/blob/8d940ecc518c9b4e198e240cca634f315f37e318/src/ReportTrigger/CommonTrigger.sol).
- `CommonTrigger.t.sol` covers ready and not-ready trigger behavior for report, tend, and auction flows.

## Real-World Examples

- Yearn V3 periphery exposes keeper trigger facades for strategy and auction automation.

## Related Patterns

- [Operation Cadence Liveness Agent](../monitoring/pattern-operation-cadence-liveness-agent.md)
- [Changeable Trigger Gate](./pattern-changeable-trigger-gate.md)
- [Grace-Period Keeper Bounties](./pattern-grace-period-keeper-bounties.md)

## References

- See Source Evidence.
