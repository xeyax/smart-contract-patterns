# Index-To-Distributor Reward Routing

> Route rewards for disabled or restricted accounts from a lazy reward index into a distributor checkpoint, then claim them through a separate proof path.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, index, distributor, merkle, restrictions |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Most users should accrue through a lazy reward index
- Some accounts are not allowed to receive rewards directly
- Restricted-account rewards should remain attributable and claimable through a distributor
- The system can maintain separate principal and distributor checkpoints

## Avoid When

- All rewards can be paid directly to holders
- Restrictions require immediate confiscation rather than delayed distribution
- Distributor checkpoints cannot be audited or proven to users

## How It Works

When rewards are disabled for an account, its earning principal is moved to a distributor bucket:

```solidity
function toggleRewards(address account, bool enabled) external onlyController {
    _checkpoint(account);
    if (!enabled) {
        distributorPrincipal += principal[account];
        rewardEnabled[account] = false;
    } else {
        distributorPrincipal -= principal[account];
        rewardEnabled[account] = true;
    }
}

function balanceOfRewards(address account) public view returns (uint256) {
    if (!rewardEnabled[account]) return 0;
    return _indexedRewards(account);
}
```

The distributor accrues the redirected rewards and later pays eligible claims through a Merkle or equivalent claim mechanism.

## Key Points

- Checkpoint users before toggling reward eligibility.
- Keep restricted-account principal in a separate distributor earning base.
- Define who can claim redistributed rewards and how proofs are updated.
- Prevent transfers from bypassing reward-enabled state.
- Test toggling around reward updates, transfers, and claims.

## Source Evidence

- StakeWise V2 routes rewards for disabled accounts into distributor principal while normal holders accrue through a lazy reward index, then supports distributor Merkle claims.

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Indexed Merkle Airdrop](./pattern-indexed-merkle-airdrop.md)
- [Threshold Reporter Consensus](../oracles/pattern-threshold-reporter-consensus.md)
