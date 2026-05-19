# Historical Basket Redemption Nonces

> Let users redeem against a recorded basket version so basket changes do not make pending redemption quotes ambiguous.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, redemption, basket, nonce, slippage |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A redeemable token can switch its backing basket over time
- Users or integrators need to quote a specific basket version
- Redemptions should preserve slippage protection across basket changes
- The protocol keeps enough balance information for old basket redemptions

## Avoid When

- Redemptions are always against the current basket only
- Old basket redemption would bypass an intended migration or freeze
- Historical basket state is too large to store or unsafe to expose
- Users cannot provide minimum output amounts

## Trade-offs

**Pros:**
- Makes basket-change redemptions deterministic
- Gives users slippage protection by basket version
- Helps integrators reason about pending transactions during recollateralization

**Cons:**
- Requires storing historical basket composition
- Old-basket redemption rules can be subtle during undercollateralization
- Must cap outputs by available backing balances

## How It Works

Every basket switch increments a nonce and stores the active basket. Redemptions can specify a nonce plus minimum amounts:

```solidity
function redeemCustom(
    uint256 amount,
    uint48 basketNonce,
    uint256[] calldata minAmounts
) external {
    Basket storage basket = basketHistory[basketNonce];
    uint256[] memory amounts = _quote(basket, amount);
    _requireMinAmounts(amounts, minAmounts);
    _capByBackingManagerBalances(amounts);
    _burn(msg.sender, amount);
    _transferBasket(msg.sender, basket, amounts);
}
```

The current basket remains the default path. Historical redemption is for callers that intentionally bind to an old quote.

## Implementation

```solidity
function _switchBasket(Basket memory next) internal {
    basketNonce += 1;
    basketHistory[basketNonce] = next;
    activeBasket = next;
}
```

### Key Points

- Reject future nonces and unsupported old nonces.
- Require `minAmounts` so old-basket redemption cannot silently deliver less.
- Cap withdrawals by live backing balances, especially during undercollateralization.
- Document when historical baskets stop being valid.

## Source Evidence

- Reserve Protocol stores `basketHistory` by nonce, tracks `lastCollateralized`, and supports `RToken.redeemCustom` through `BasketHandler.quoteCustomRedemption` in `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/p1/BasketHandler.sol` and `contracts/p1/RToken.sol`.
- Reserve tests cover custom redemption after basket changes and invalid nonce handling in `/private/tmp/defillama-source/reserve-protocol__protocol/test/RToken.test.ts`.

## Real-World Examples

- Reserve Protocol RToken - custom redemptions quote historical basket nonces with minimum amount checks.

## Related Patterns

- [Target-Unit Backup Basket Substitution](./pattern-target-unit-backup-basket-substitution.md)
- [Proportional Deposit/Withdrawal](../vaults/pattern-proportional-deposit.md)
- [Missing Slippage Protection](../../ANTIPATTERNS.md#missing-slippage-protection)

## References

- See Source Evidence.
