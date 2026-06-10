# Zero Consideration Signed Order Risk

> Signed order settlement can transfer maker assets for zero payment when zero maker or taker consideration is accepted accidentally.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, orderbook, signature, zero-amount, settlement |
| Type | Risk Description |

## Applies When

- Orders bind maker and taker amounts but allow either amount to be zero
- Matching code treats zero taker amount as crossing or fillable
- Gratis transfers are not an explicit order type
- Off-chain matchers can submit arbitrary signed orders to on-chain settlement

## Requirements Affected

- Signed orders must bind economically meaningful consideration.
- Matching logic must reject unintended zero-value fills.
- User signatures must not authorize value transfer under ambiguous pricing terms.

## Failure Modes

- A valid maker signature transfers the full maker amount while the maker receives zero.
- A zero-taker order is treated as crossing and drains one side of a match.
- Off-chain UI assumptions about minimum amounts are bypassed by direct settlement calls.

## Mitigations

- Reject zero maker and taker consideration unless a separate gratis order type is intentional.
- Include explicit side and order type in the signed payload.
- Test zero maker amount, zero taker amount, and partial-fill edge cases.
- Keep final settlement checks on-chain even when an off-chain matcher filters orders.

## Source Evidence

- Polymarket CTF Exchange tests and helper math show zero maker/taker amounts can produce zero taking amounts or crossing behavior, motivating explicit rejection unless zero-consideration orders are intended.

## Related Patterns

- [Typed Signed Order Settlement](./pattern-typed-signed-order-settlement.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)
