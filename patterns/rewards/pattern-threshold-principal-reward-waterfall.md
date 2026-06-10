# Threshold Principal Reward Waterfall

> Split unlabeled withdrawal-recipient inflows into principal and rewards by paying tracked principal up to an absolute threshold before routing residual value to rewards.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, principal, waterfall, staking, withdrawal-recipient |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A staking or validator withdrawal recipient receives unlabeled principal and reward inflows
- Principal must be repaid before reward recipients receive surplus
- The protocol tracks remaining principal independently from raw recipient balance
- Recipients may be contracts that can revert on push payments

## Avoid When

- Inflows are already labeled by source as principal or rewards
- Direct donations should not affect either principal or rewards
- Principal tracking can be updated by untrusted callers
- The system cannot tolerate delayed pull claims

## Trade-offs

**Pros:**
- Classifies unlabeled inflows fully on-chain with one threshold rule — no oracle or off-chain labeling needed.
- Pull-ledger fallback prevents one reverting recipient from blocking the other recipient's funds.
- Subtracting pending pull credits makes repeated `distribute()` calls safe against double counting.
- Distribution can stay permissionless: anyone can crank settlement without trust in the caller.

**Cons:**
- Misclassification is structural: donations and early reward inflows count as principal until the threshold is exhausted.
- Correctness hinges on the permissioned principal-tracking path; a stale `remainingPrincipal` mislabels every subsequent inflow.
- Pull-claim fallback delays receipt and forces an extra claim transaction on contract recipients.
- Internal accounting (`pendingPrincipal`, `pendingReward`, `remainingPrincipal`) must reconcile with raw balance; drift is hard to spot without events and dedicated tests.

## How It Works

Track remaining principal and split distributable balance by an absolute threshold:

```solidity
function distribute() external {
    uint256 distributable = address(this).balance - pendingPrincipal - pendingReward;
    uint256 principalPart = min(distributable, remainingPrincipal);
    uint256 rewardPart = distributable - principalPart;

    remainingPrincipal -= principalPart;
    _pushOrCredit(principalRecipient, principalPart);
    _pushOrCredit(rewardRecipient, rewardPart);
}
```

If a push transfer fails, credit the recipient to a pull ledger. Pending pull balances are subtracted from future distributable balance so repeated distribution cannot double count already-credited funds.

## Key Points

- Make the principal-tracking path authoritative and permissioned.
- Document how direct deposits or donations are classified.
- Subtract pending pull credits before splitting new distributable balance.
- Support pull claims so one reverting recipient cannot block the other recipient.
- Emit principal and reward split events.
- Test direct deposits, exact-threshold payments, over-threshold payments, push failures, and repeated distribution.

## Source Evidence

- Obol withdrawal-recipient contracts split ETH inflows between principal and reward recipients by a tracked principal threshold, support push and pull distribution, and test direct deposits, failed pushes, and threshold behavior.

## Related Patterns

- [Principal Reward Split Derivative](../tokens/pattern-principal-reward-split-derivative.md)
- [Checkpointed Epoch Reward Buckets](./pattern-checkpointed-epoch-reward-buckets.md)
