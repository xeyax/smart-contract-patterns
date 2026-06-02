# Circulating Supply Exclusion Ledger

> Track addresses whose balances are intentionally excluded from circulating supply so mint limits, caps, and accounting views use the right denominator.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, supply, accounting, cap, exclusion |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A token has escrow, treasury, reserve, or protocol-owned balances that should not count as circulating supply
- Caps, mint limits, governance power, or accounting views depend on a supply denominator
- Excluded balances can change over time and must remain auditable
- The protocol can define the difference between total minted supply and circulating supply

## Avoid When

- ERC20 `totalSupply()` must be the only externally meaningful supply view
- Exclusions are discretionary and can be used to hide supply changes
- Integrators are likely to confuse circulating supply with redeemable backing
- Excluded addresses can transfer without updating the exclusion accounting

## Trade-offs

**Pros:**
- Separates raw minted supply from economically circulating supply
- Lets caps and accounting ignore known non-circulating balances
- Gives monitoring an explicit excluded-balance surface

**Cons:**
- Additional transfer hooks or balance updates are required
- Privileged exclusion changes can affect caps and governance economics
- Integrators may read the wrong supply function unless naming is clear

## How It Works

Maintain a set of excluded accounts and a running excluded balance:

```solidity
mapping(address => bool) public excludedFromCirculation;
uint256 public excludedSupply;

function _afterTokenTransfer(address from, address to, uint256 amount) internal {
    if (excludedFromCirculation[from]) excludedSupply -= amount;
    if (excludedFromCirculation[to]) excludedSupply += amount;
}

function circulatingSupply() public view returns (uint256) {
    return totalSupply() - excludedSupply;
}
```

When an address is added or removed, adjust `excludedSupply` by its current balance and emit the old and new status.

## Implementation

### Key Points

- Name the view precisely: `circulatingSupply`, `capSupply`, or `governanceSupply`, not a misleading replacement for `totalSupply`.
- Emit events for exclusion changes and excluded-supply deltas.
- Gate exclusion changes with governance delay or tight authority.
- Update excluded supply on transfers, mint, and burn.
- Test adding/removing an address with a nonzero balance and transfers between two excluded addresses.
- Document whether excluded balances are still redeemable, voteable, or cap-consuming.

## Source Evidence

- Euler Vault Kit's synth token tracks balances ignored for total-supply style accounting through `ignoredForTotalSupply` and tests supply/cap effects in `/private/tmp/defillama-source/euler-xyz__euler-vault-kit/src/Synths/ESynth.sol` and related synth tests.
- The inspected implementation shows the integration risk: a token can expose multiple supply concepts, so caps and accounting must choose the intended denominator explicitly.

## Real-World Examples

- Euler synths - excluded-balance supply accounting for protocol-specific token supply views.

## Related Patterns

- [Paired Supply Change Throttle](./pattern-paired-supply-change-throttle.md)
- [Balance-Sheet Solvency Gate](../lending/pattern-balance-sheet-solvency-gate.md)
- [Privileged Supply Mutation](../../ANTIPATTERNS.md#privileged-supply-mutation)

## References

- See Source Evidence.
