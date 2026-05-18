# Isolated Vesting Schedule Escrow

> Create one escrow contract or isolated schedule per vesting grant so vested withdrawals and unvested revocation are tracked independently.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | vesting, escrow, rewards, revocation, schedule |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Beneficiaries can have multiple grants with different schedules
- Unvested tokens may be revocable by the schedule owner
- Anyone should be able to trigger withdrawal for a beneficiary
- Each schedule should be auditable independently

## Avoid When

- One global vesting curve is enough for all recipients
- Creating many escrows would be too expensive
- Attackers can append unlimited schedules to a victim's account

## How It Works

A controller creates schedule escrows and indexes them by beneficiary:

```solidity
function createVesting(address beneficiary, uint256 amount, Schedule memory schedule) external {
    require(amount >= minVestingAmount, "dust schedule");
    address escrow = address(new VestingEscrow(token, beneficiary, msg.sender, amount, schedule));
    vestings[beneficiary].push(escrow);
    token.transferFrom(msg.sender, escrow, amount);
}
```

Each escrow releases only vested value and revokes only unvested value:

```solidity
function revoke() external onlyOwner {
    uint256 unvested = total - vestedAmount(block.timestamp);
    token.transfer(owner, unvested);
}
```

## Key Points

- Track schedule owner separately from beneficiary.
- Allow `withdrawFor(beneficiary)` only if it cannot harm the beneficiary.
- Revoke only unvested amounts; vested amounts remain claimable.
- Enforce minimum economic size or pagination if anyone can append schedules.
- Test partial vesting, full vesting, revocation, third-party withdraw, and dust schedule rejection.

## Source Evidence

- SSV vesting controllers create per-schedule vesting contracts, allow third-party withdrawal for beneficiaries, and revoke only unvested value.

## Related Patterns

- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)
- [User-Owned Proxy Vault](../vaults/pattern-user-owned-proxy-vault.md)
