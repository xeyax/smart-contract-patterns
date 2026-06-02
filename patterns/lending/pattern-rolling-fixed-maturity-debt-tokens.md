# Rolling Fixed-Maturity Debt Tokens

> Issue tokenized debt claims whose ids encode rolling maturities, burn discounted stablecoin at mint, and mint face value after maturity.

## Metadata

| Property | Value |
|----------|-------|
| Category | lending |
| Tags | fixed-maturity, debt, erc1155, discount, stablecoin |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A stablecoin or credit protocol wants fixed-maturity funding instruments
- Maturities roll forward on a predictable schedule
- Debt supply should be capped per maturity and in aggregate
- Users can hold or transfer term claims independently from spot stablecoin
- Discount rates and maturity windows are governance-controlled risk parameters

## Avoid When

- Debt must be continuously redeemable at par before maturity
- The protocol cannot enforce maturity-specific debt ceilings
- Discount pricing depends on stale or discretionary off-chain quotes
- Integrations require a single fungible ERC20 claim rather than maturity-specific ids

## Trade-offs

**Pros:**
- Makes maturity buckets explicit in token ids
- Separates discounted issuance from par redemption
- Supports coupon-strip or ladder variants without deploying one token per maturity

**Cons:**
- Maturity windows and discount math are high-risk configuration
- Secondary integrations must handle ERC1155-style ids and approvals
- Liquidity and solvency depend on term-specific caps and balance-sheet checks

## How It Works

A term issuer exposes a rolling window of available ids. Each id maps to a
maturity timestamp derived from a genesis time and fixed interval. Minting burns
the discounted present value and mints face-value debt tokens:

```solidity
function mint(uint256 id, uint256 faceAmount) external returns (uint256 cost) {
    require(id >= earliestId() && id <= latestId(), "outside window");

    uint256 maturity = maturityTimestamp(id);
    cost = discount(faceAmount, maturity, discountRate[id]);

    stablecoin.burnFrom(msg.sender, cost);
    termToken.mint(msg.sender, id, faceAmount);
    totalDebt += faceAmount;
}

function redeem(uint256 id, uint256 faceAmount) external {
    require(block.timestamp >= maturityTimestamp(id), "not mature");
    termToken.burn(msg.sender, id, faceAmount);
    stablecoin.mint(msg.sender, faceAmount);
    totalDebt -= faceAmount;
}
```

Coupon-strip variants can mint a ladder of nearer maturities as coupons plus a
principal term. Principal redemption should require coupons to be claimed or
otherwise settled so the position cannot leave dangling claims.

Some protocols deploy serial ERC20 instruments per term instead of encoding
terms into an ERC1155 id. The same maturity, cap, and settlement requirements
still apply; the registry or servicer must prove which contract is active for
each maturity.

## Key Points

- Define earliest and latest mintable ids from time, not from caller input.
- Cap debt per maturity and include total term debt in protocol liabilities.
- Bound discount rates and update them through monitored governance.
- Burn discounted cost before minting face-value claims.
- Block redemption until maturity and decrement debt when face value is paid.
- Test window edges, maturity redemption, per-term cap exhaustion, discount rounding, coupon-claim order, and ERC1155 approval assumptions.
- For per-maturity ERC20 instruments, test term-token registration, rollover, and stale-token redemption separately from the shared servicer logic.

## Source Evidence

- Reservoir's `TermIssuer` maps ids to rolling maturity timestamps, burns discounted rUSD on mint, mints ERC1155 term claims, and mints face-value rUSD only after maturity in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/TermIssuer.sol`.
- Reservoir's `AccountManager` builds a coupon ladder on top of term ids and requires all coupons to be claimed before principal redemption in `/private/tmp/defillama-source/reservoir-protocol__reservoir/src/AccountManager.sol`.
- Reservoir term debt caps are covered by invariants and window tests in `/private/tmp/defillama-source/reservoir-protocol__reservoir/test`.
- Term Finance represents repo obligations through term-scoped token contracts and servicers under `/private/tmp/defillama-source/term-finance__term-finance-contracts/contracts`, alongside auction settlement that selects the active term cohort.

## Related Patterns

- [Balance-Sheet Solvency Gate](./pattern-balance-sheet-solvency-gate.md)
- [Reserve Exposure Caps](./pattern-reserve-exposure-caps.md)
- [Principal-Reward Split Derivative](../tokens/pattern-principal-reward-split-derivative.md)
