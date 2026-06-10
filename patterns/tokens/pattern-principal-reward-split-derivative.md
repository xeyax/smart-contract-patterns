# Principal-Reward Split Derivative

> Represent a staking position with one token for principal and a separate token for accrued rewards.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | staking, derivative, principal, rewards, migration |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Principal should remain close to 1:1 with deposited assets
- Rewards need separate transferability, claiming, or migration semantics
- Slashing or negative rewards should not silently rebase the principal token
- Successor migrations need to burn both claims into a new asset

## Avoid When

- A single rebasing token or ERC4626 share is the simpler user model
- Principal and rewards cannot be priced or migrated separately
- Integrations assume one token fully represents the position value

## Trade-offs

**Pros:**
- Principal stays near 1:1 with deposits, so principal-side integrations avoid rebasing accounting entirely.
- Rewards get independent transferability, claiming, and migration semantics without disturbing principal.
- Slashing and reward deficits surface explicitly in the reward layer instead of silently rebasing principal supply.
- Burning both tokens into a successor gives a clean migration path covering the full position.

**Cons:**
- Two tokens double the integration surface: listings, oracles, liquidity, and approvals per position.
- Integrators reading only principal supply systematically undervalue positions — a documented but recurring footgun.
- Reward accrual depends on a trusted oracle or updater pushing reward totals.
- Liquidity fragments across two assets, worsening secondary-market pricing for both.
- Migration requires user action on both tokens; partial migrations leave stranded reward claims.

## How It Works

Mint principal on deposit and accrue rewards through a separate reward token or accounting layer:

```solidity
function deposit(uint256 amount) external {
    asset.transferFrom(msg.sender, address(this), amount);
    principalToken.mint(msg.sender, amount);
}

function updateRewards(uint256 newRewards) external onlyOracle {
    rewardToken.increaseTotalRewards(newRewards);
}

function migrate(uint256 principalAmount, uint256 rewardAmount) external {
    principalToken.burnFrom(msg.sender, principalAmount);
    rewardToken.burnFrom(msg.sender, rewardAmount);
    successor.mint(msg.sender, _convert(principalAmount, rewardAmount));
}
```

## Key Points

- Document what each token claims: deposited principal, rewards, or both.
- Keep slashing and penalty accounting explicit so reward deficits do not hide in principal supply.
- Make migration burn requirements clear for both tokens.
- Warn integrators that principal supply alone is not total position value.
- Test transfers, reward toggles, migration, and negative reward periods.

## Source Evidence

- StakeWise V2 splits liquid staking exposure into sETH2 principal and rETH2 rewards, with migration flows that burn both into successor vault assets.

## Related Patterns

- [Lazy Reward Index](../rewards/pattern-lazy-reward-index.md)
- [Liquid Staking Loss Accounting Requirements](../vaults/req-liquid-staking-loss-accounting.md)
- [Rebasing Token Accounting](../../ANTIPATTERNS.md#rebasing-token-accounting)
