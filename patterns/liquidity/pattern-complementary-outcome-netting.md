# Complementary Outcome Netting

> Net binary outcome-token orders by minting or merging complete sets when same-side orders cross.

## Metadata

| Property | Value |
|----------|-------|
| Category | liquidity |
| Tags | liquidity, prediction-market, outcome-token, netting, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Outcome tokens are complementary claims over the same collateral
- A complete set of outcomes is redeemable for one unit of collateral
- Same-side buy/buy or sell/sell orders can economically cross through the complement
- The exchange can validate registered complements on-chain

## Avoid When

- Outcome tokens are not mutually exhaustive or collateral-conserving
- Complement registration is mutable without governance controls
- The exchange cannot atomically mint or merge complete sets
- Fees and refunds cannot be reconciled per matched order

## Trade-offs

**Pros:**
- Same-side buy/buy and sell/sell orders cross through the complement, deepening effective liquidity beyond direct counterparties.
- Mint/merge keeps the system collateral-conserving by construction — complete sets always equal one unit of collateral.
- Matching needs no AMM inventory or price oracle; settlement is pure order-vs-order accounting.
- Atomic pull-mint/merge-deliver settlement leaves no open exchange exposure between legs.

**Cons:**
- Correctness hinges on the complement registry: an unregistered or wrongly registered pair lets matches mint claims that do not conserve collateral.
- Fee and surplus-refund accounting per matched order is intricate — fees must apply after complete-set math, and refund rounding paths are easy to get wrong.
- Fill state must be recorded before external token transfers, or reentrant/failed transfers desynchronize order bookkeeping.
- Only works for mutually exhaustive binary (or complete-set) outcomes; scalar or non-exhaustive markets cannot use the transform.
- Settlement gas is heavier than a direct swap: collateral pulls, set mint/merge, two-sided delivery, and dust refunds per match.

## How It Works

For a binary market, `YES + NO = collateral`. An exchange can match same-side orders by transforming collateral and outcome inventory:

```text
buy YES + buy NO
  -> pull collateral from both buyers
  -> mint complete YES/NO sets
  -> deliver each buyer's requested side
  -> refund surplus collateral

sell YES + sell NO
  -> pull both outcome tokens
  -> merge complete sets into collateral
  -> pay sellers from merged collateral
```

The settlement contract must validate that the two assets are registered complements before minting, merging, distributing proceeds, or refunding dust.

## Key Points

- Register complement pairs and condition ids before matching.
- Pull assets into the exchange before minting or merging complete sets.
- Apply fees after the complete-set accounting is known.
- Refund excess collateral deterministically.
- Track fill state before external token transfers complete.
- Test buy/buy, sell/sell, partial-fill, fee, and refund paths.

## Source Evidence

- Polymarket's CTF Exchange documents and tests buy/buy and sell/sell outcome matching, validates complement registration, mints or merges complete sets, and then distributes proceeds and refunds.

## Related Patterns

- [Typed Signed Order Settlement](../routing/pattern-typed-signed-order-settlement.md)
- [Invariant Delta Liquidity Accounting](./pattern-invariant-delta-liquidity-accounting.md)
