# Capped Linear Voting Escrow

> Mint non-transferable voting power that accrues linearly from staked principal up to a configured cap and burns on unstake.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, voting-escrow, staking, non-transferable, cap |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Governance wants longer participation to earn more voting weight
- Voting power should grow predictably from principal and elapsed time
- A maximum voting-power multiple should bound long-duration concentration
- The voting token should not be transferable or marketable

## Avoid When

- Voting power must be transferable, delegated through a liquid token, or immediately liquid
- Long-lived stake should not receive extra governance weight
- The accrual formula cannot be recomputed consistently after stake changes
- Users need early-exit liquidity without forfeiting accrued power

## Trade-offs

**Pros:**
- Rewards duration without requiring explicit lock-end selection
- Caps voting-power concentration from old positions
- Keeps voting power tied to active stake because power burns on withdrawal

**Cons:**
- Users can lose accumulated power when unstaking
- Formula changes are governance-sensitive and hard to migrate
- Accrual and burn paths need careful rounding tests

## How It Works

Store staked principal and an accrual baseline per user. Voting power increases
linearly over time until it reaches a cap such as `principal * maxMultiple`.
The voting token is non-transferable, so power can only be created by staking
and destroyed by unstaking.

```solidity
function votingPower(address user) public view returns (uint256) {
    Position memory p = positions[user];
    uint256 elapsed = block.timestamp - p.lastUpdate;
    uint256 accrued = p.power + elapsed * p.principal * ratePerSecond / SCALE;
    uint256 cap = p.principal * maxPowerMultiple;
    return accrued > cap ? cap : accrued;
}

function unstake(uint256 amount) external {
    uint256 power = votingPower(msg.sender);
    uint256 burned = power * amount / positions[msg.sender].principal;
    _burnVotingPower(msg.sender, burned);
    _withdrawPrincipal(msg.sender, amount);
}
```

## Implementation

- Make the voting-power token non-transferable except for mint and burn paths.
- Cap accrued power as a multiple of current stake.
- Update accrued power before changing principal.
- Burn voting power proportionally on partial unstake.
- Test accrual below cap, at cap, partial unstake, full unstake, and zero-principal edge cases.

## Source Evidence

- BENQI's veQI computes accrued voting power from staked amount, elapsed time, and a maximum cap in [`veQI/VeQi.sol`](https://github.com/benqi-fi/BENQI-Smart-Contracts/blob/e0cfd244726719dfe027c9740878d64d1cad98f2/veQI/VeQi.sol).
- BENQI's `VeERC20Upgradeable` disables normal transfer and allowance flows, making the voting-power token non-transferable.

## Real-World Examples

- BENQI veQI mints voting power from QI staking, accrues power linearly up to a cap, and burns voting power when stake exits.

## Related Patterns

- [Time-Decaying Lock Voting Escrow](./pattern-time-decaying-lock-voting-escrow.md)
- [Composable Voting-Power Calculator](./pattern-composable-voting-power-calculator.md)
- [Bounded Token Inflation](./pattern-bounded-token-inflation.md)
- [Flash Loan Governance](../../ANTIPATTERNS.md#flash-loan-governance)

## References

- BENQI veQI contracts.
