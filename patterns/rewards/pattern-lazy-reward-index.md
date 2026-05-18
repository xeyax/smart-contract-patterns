# Lazy Reward Index

> Accrue rewards through a global index and update each user only when they interact or claim.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, index, lazy-accounting, staking, incentives |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Rewards accrue continuously or per emission update
- The protocol has many suppliers, stakers, or borrowers
- Updating every user on every reward event is impossible
- User rewards are needed only on interaction or claim

## Avoid When

- Rewards are one-off Merkle claims
- Per-user boosts require expensive global recomputation
- Reward tokens can be donated and mistakenly counted as newly accrued rewards

## How It Works

Track cumulative reward per unit of stake:

```solidity
function updateGlobalIndex(uint256 rewardAccrued) internal {
    if (totalStake == 0) return;
    rewardIndex += rewardAccrued * 1e18 / totalStake;
}

function updateUser(address user) internal {
    uint256 delta = rewardIndex - userIndex[user];
    accrued[user] += balance[user] * delta / 1e18;
    userIndex[user] = rewardIndex;
}
```

Call `updateUser` before changing the user's stake and before claiming.

## Key Points

- Update the global index before changing total stake if new rewards are available.
- Update the user index before mint, burn, transfer, borrow, repay, or claim changes their earning base.
- Define behavior when total stake is zero.
- Keep reward-token balance accounting separate from emitted reward accounting.
- If a user has zero earning balance, advance their user index cursor to the latest index so future stake cannot backfill historical rewards.
- Test multiple users entering, exiting, and claiming across emission updates.

## Source Evidence

- Aave V3 rewards accrue incentives through asset-level indexes and update users lazily when balances change or rewards are claimed.
- StakeWise V2 audit material highlights the need to checkpoint zero-balance users so later stake does not claim rewards from before the user entered.

## Related Patterns

- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Lazy Borrow Index](../lending/pattern-lazy-borrow-index.md)
- [Index-To-Distributor Reward Routing](./pattern-index-to-distributor-reward-routing.md)
