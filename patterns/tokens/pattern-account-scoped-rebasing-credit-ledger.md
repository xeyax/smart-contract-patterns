# Account-Scoped Rebasing Credit Ledger

> Track rebasing supply through global credits per token while allowing selected accounts to opt into non-rebasing or delegated-yield credit modes.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, rebasing, credit, yield, accounting |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A token distributes yield by rebasing balances
- Some accounts, wrappers, or integrations need non-rebasing balances
- Yield from one account may be delegated to another account
- The token can maintain per-account credit accounting safely

## Avoid When

- Integrators cannot tolerate balance changes without transfers
- Account mode changes are not explicit and auditable
- Rebasing math would be based on raw token balances that donations can distort
- The protocol cannot test transfers between every account mode

## Trade-offs

**Pros:**
- Supports rebasing holders and fixed-balance integrations in one token
- Allows yield delegation without moving principal
- Keeps supply changes in a credit ledger rather than ad hoc minting

**Cons:**
- Transfer math is more complex than ordinary ERC20 accounting
- Mode switching can surprise integrators if not explicit
- Rounding and dust handling need strong tests

## How It Works

The token stores global credits per token for rebasing accounts. Accounts that
opt out receive their own fixed conversion rate or credit bucket:

```solidity
function balanceOf(address account) public view returns (uint256) {
    uint256 credits = creditBalance[account];
    uint256 cpt = accountCreditsPerToken[account];
    if (cpt == 0) cpt = rebasingCreditsPerToken;
    return credits / cpt;
}

function changeSupply(uint256 newTotalSupply) external onlyVault {
    rebasingCreditsPerToken = rebasingCredits / newTotalSupply;
}

function optOut(address account) external {
    accountCreditsPerToken[account] = rebasingCreditsPerToken;
}
```

## Implementation

### Key Points

- Make rebasing, non-rebasing, and yield-delegating modes explicit.
- Settle account credits before changing mode or delegation.
- Test transfers across every mode pair.
- Use supply and credit totals, not raw token balance, for wrapper conversion.
- Document integration expectations for balance-changing rebases.

## Source Evidence

- Origin OUSD stores rebasing and non-rebasing credit accounting in [`contracts/contracts/token/OUSD.sol`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/contracts/token/OUSD.sol).
- Origin documents credits-per-token, non-rebasing accounts, and yield delegation in [`contracts/contracts/token/README-token-logic.md`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/contracts/token/README-token-logic.md).
- Origin token tests cover rebase and transfer behavior in [`contracts/test/token/ousd.js`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/test/token/ousd.js) and `token-transfers.js`.
- Origin WOETH derives wrapper assets from OETH credit accounting rather than raw donated token balance in [`contracts/contracts/token/WOETH.sol`](https://github.com/originprotocol/origin-dollar/blob/cd7218c2b070a52470b2621c3ce0ce12378ba700/contracts/contracts/token/WOETH.sol).

## Real-World Examples

- Origin OUSD - rebasing stablecoin with account-scoped credits and non-rebasing integrations.

## Related Patterns

- [Liability-Backed ERC4626 Savings Share](../vaults/pattern-liability-backed-erc4626-savings-share.md)
- [Rebasing Token Accounting](../../ANTIPATTERNS.md#rebasing-token-accounting)
- [Donation Attack Surface](../../ANTIPATTERNS.md#donation-attack-surface)

## References

- See Source Evidence.
