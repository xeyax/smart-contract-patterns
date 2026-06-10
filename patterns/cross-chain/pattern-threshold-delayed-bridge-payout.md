# Threshold-Delayed Bridge Payout

> Delay large validator-approved bridge payouts behind a public execution window while allowing smaller payouts to settle immediately.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, delay, payout, threshold, safeguard |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge already has a validator, oracle, or operator approval path
- Large payouts deserve extra observation time after approval
- Token-specific thresholds can separate ordinary transfers from high-risk transfers
- Anyone can execute the delayed payout after the delay expires

## Avoid When

- Delay state can be overwritten or deleted by the same actor that approves payouts
- Users require source-chain finality scaling before approval, not post-approval delay
- Pausing the delay executor would permanently trap already-approved payouts
- Threshold and delay-period changes lack bounds, events, or governance delay

## Trade-offs

**Pros:**
- Adds monitoring time for unusually large bridge releases
- Keeps normal-size payouts fast
- Gives delayed transfers a stable public id and execution path

**Cons:**
- Does not prove source-chain finality or validator honesty
- Large users face worse liveness than small users
- Admin-controlled thresholds can silently weaken protection

## How It Works

After the ordinary bridge verification succeeds, the bridge either pays
immediately or records a delayed transfer keyed by the verified transfer id:

```solidity
function finalize(VerifiedTransfer calldata transfer) external {
    require(!_used[transfer.id], "used");
    _used[transfer.id] = true;
    _consumeVolumeCap(transfer.token, transfer.amount);

    if (transfer.amount > delayThreshold[transfer.token]) {
        delayed[transfer.id] = DelayedTransfer({
            receiver: transfer.receiver,
            token: transfer.token,
            amount: transfer.amount,
            timestamp: block.timestamp
        });
        return;
    }

    _send(transfer.receiver, transfer.token, transfer.amount);
}

function executeDelayed(bytes32 id) external {
    DelayedTransfer memory transfer = delayed[id];
    require(block.timestamp > transfer.timestamp + delayPeriod, "locked");
    delete delayed[id];
    _send(transfer.receiver, transfer.token, transfer.amount);
}
```

## Implementation

### Key Points

- Bind the delayed-transfer id to the already-verified bridge message or withdrawal id.
- Mark the original transfer consumed before adding delayed payout state.
- Let any caller execute after the delay, unless there is a narrowly scoped emergency reason.
- Pair amount thresholds with per-token or per-route volume caps when burst risk matters.
- Emit threshold, delay-period, delayed-add, and delayed-execute events.
- Test exact-threshold behavior, duplicate delayed ids, delayed execution before expiry, public execution after expiry, pause interactions, and cap accounting.

## Source Evidence

- Celer SGN bridge records delayed transfers with receiver, token, amount, and timestamp in [`contracts/safeguard/DelayedTransfer.sol:7`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/safeguard/DelayedTransfer.sol#L7).
- Celer SGN bridge only executes delayed transfers after the configured delay period and deletes the record before returning it in `DelayedTransfer.sol:53`.
- Celer liquidity bridge relay marks transfer ids used, consumes per-token volume, and delays transfers above token thresholds in [`contracts/liquidity-bridge/Bridge.sol:125`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/liquidity-bridge/Bridge.sol#L125).
- Celer pool withdrawals use the same delayed-transfer safeguard and expose public delayed execution in [`contracts/liquidity-bridge/Pool.sol:90`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/liquidity-bridge/Pool.sol#L90).
- Celer volume control enforces per-token epoch caps in [`contracts/safeguard/VolumeControl.sol:29`](https://github.com/celer-network/sgn-v2-contracts/blob/b8a27161e0b700e30f30452c73418b60d133163f/contracts/safeguard/VolumeControl.sol#L29).

## Real-World Examples

- Celer SGN liquidity bridge - large bridge relays and pool withdrawals can be delayed after validator approval while smaller transfers settle immediately.

## Related Patterns

- [Pairwise Bridge Rate Limits](./pattern-pairwise-bridge-rate-limits.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Value-Tiered Source Finality](./pattern-value-tiered-source-finality.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)

## References

- See Source Evidence.
