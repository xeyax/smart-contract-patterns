# Launch-Locked Recipient-Scoped Transfer Gate

> Launch a governance or distribution token as non-transferable, then allow controlled transfers through account allowlists and recipient-scoped spend budgets until full transferability is enabled.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, launch, transfer-gate, allowance, governance |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A token has an intentional non-transferable launch or distribution phase
- Specific holders need to transfer limited amounts to specific recipients before launch unlock
- Budgets should burn down as transfers or burns occur
- Full transferability can later be enabled irreversibly or through governance

## Avoid When

- The token represents redeemable vault shares, bridge claims, or exit entitlements
- Transfer restrictions would trap users from a solvent exit path
- Owner minting or budget changes are unrestricted and unmonitored
- Recipient-scoped budgets cannot be explained to holders and integrators

## How It Works

While the token is paused or launch-locked, normal transfers fail unless the sender is exempt or has a budget for the recipient:

```solidity
function _update(address from, address to, uint256 amount) internal override {
    if (!transferable && from != address(0) && to != address(0)) {
        if (!ownerExempt[from] && !allowlisted[from]) {
            _spendTransferBudget(from, to, amount);
        }
    }
    super._update(from, to, amount);
}
```

Budgets are scoped by sender and recipient, and finite budgets decrease on use. Infinite budgets should be explicit and evented.

## Key Points

- Use only for tokens where non-transferability is an explicit launch state, not for withdrawal claims.
- Scope budgets by sender and recipient; global allowances are easier to misuse.
- Prefer increase/decrease budget APIs over overwrite-style setters.
- Emit budget, allowlist, and transferability events with old and new values.
- Pair supply assumptions with bounded inflation or documented mint authority.
- Define whether an allowlisted sender can delegate transfer authority through ERC20 approvals.

## Source Evidence

- Karpatkey's KPK token launches paused, then permits owner exemptions, account allowlists, recipient-scoped transfer budgets, burn-down on transfer, and full unpaused behavior in tests.

## Related Patterns

- [Participant Permission Bitmap](../access-control/pattern-participant-permission-bitmap.md)
- [Bounded Token Inflation](../governance/pattern-bounded-token-inflation.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
