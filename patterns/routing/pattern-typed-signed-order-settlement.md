# Typed Signed Order Settlement

> Keep matching off-chain while settling orders on-chain by binding every fillable term in an EIP-712 order and tracking fill state.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, orderbook, eip712, settlement, signature |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Orders are matched off-chain but assets settle non-custodially on-chain
- Makers may authorize a specific signer, taker, side, asset id, and fee
- Orders can be partially filled across multiple transactions
- The protocol can maintain nonce and order-status ledgers

## Avoid When

- The signed payload omits value-bearing settlement fields
- Fill state is tracked only off-chain
- Taker restrictions, expiration, or fee caps are optional but economically relevant
- The protocol accepts ambiguous contract-wallet signatures

## Trade-offs

**Pros:**
- Off-chain matching gives orderbook-grade UX and price discovery while settlement stays non-custodial.
- EIP-712 typed orders bind every economic term, so the matcher cannot alter terms without invalidating the signature.
- On-chain fill and nonce ledgers make partial fills and cancellations enforceable regardless of matcher honesty.
- Makers sign for free; only fills pay gas.

**Cons:**
- Field-binding completeness is the entire security model: one unsigned value-bearing field (fee, receiver, balance lane, extension hash) becomes a solver-extractable hole.
- The per-fill validation stack (signature, nonce, expiry, taker, asset, remaining amount) adds meaningful settlement gas.
- Cancellation costs an on-chain transaction or epoch bump — makers pay to escape stale prices.
- Invalidation storage must match fill policy; bit invalidators on partially fillable orders break remaining-amount tracking.
- ERC-1271 contract-wallet support reintroduces signature-ambiguity and replay surface that needs separate hardening.

## How It Works

Hash the order through an EIP-712 domain and require every fill to validate the signature, nonce, expiry, asset registration, fee cap, taker scope, and remaining fill amount:

```solidity
struct Order {
    address maker;
    address signer;
    address taker;
    uint256 tokenId;
    uint256 makerAmount;
    uint256 takerAmount;
    uint256 expiration;
    uint256 nonce;
    uint256 feeRateBps;
    Side side;
    SignatureType signatureType;
}

function fill(Order calldata order, uint256 fillAmount, bytes calldata sig) external {
    bytes32 orderHash = _hashTypedData(order);
    _validateSignature(order, orderHash, sig);
    _validateNonce(order.maker, order.nonce);
    _validateTaker(order.taker, msg.sender);
    _validateAsset(order.tokenId);
    _validateExpiry(order.expiration);
    _updateRemaining(orderHash, fillAmount);
    _settleAssets(order, fillAmount);
}
```

The off-chain matcher improves UX and price discovery, but the on-chain settlement contract remains the final safety boundary.

## Key Points

- Bind maker, signer, taker, asset id, maker amount, taker amount, expiration, nonce, fee rate, side, and signature type.
- Track remaining fill state on-chain before moving assets.
- Reject expired, cancelled, fully filled, or unknown-asset orders.
- Enforce taker scope before settlement.
- Cap or bind fees in the signed order.
- Test partial fills, cancellation, nonce invalidation, taker restriction, and signature-type mismatch.
- Bind settlement balance lanes, such as ERC20 balance versus vault/internal
  balance, and bind receiver/default semantics so solvers cannot redirect value
  through an unsigned settlement source.
- Bind extension envelopes or extension hashes for predicates, permits,
  amount-getters, and pre/post-interaction hooks.
- Match invalidation storage to fill policy: bit invalidators fit single-fill or
  fill-or-kill orders, remaining-amount ledgers fit partial fills, and bulk
  invalidation needs maker-scoped monotonic series or epoch boundaries.

## Source Evidence

- Polymarket's CTF Exchange documents off-chain matching with on-chain settlement, binds order fields in typed hashes, validates signature/nonce/expiry/status before settlement, and tests fill and match flows.
- CoW Protocol binds sell/buy balance lanes and receiver semantics in typed
  order hashes, validates on-chain order state before settlement, and tests
  balance-lane behavior in [`src/contracts/libraries/GPv2Order.sol:9-24`](https://github.com/cowprotocol/contracts/blob/c6b61ce75841ce4c25ab126def9cc981c568e6c6/src/contracts/libraries/GPv2Order.sol#L9-L24),
  [`src/contracts/libraries/GPv2Order.sol:71-100`](https://github.com/cowprotocol/contracts/blob/c6b61ce75841ce4c25ab126def9cc981c568e6c6/src/contracts/libraries/GPv2Order.sol#L71-L100),
  and [`test/GPv2Settlement/Swap/Balances.t.sol:41-73`](https://github.com/cowprotocol/contracts/blob/c6b61ce75841ce4c25ab126def9cc981c568e6c6/test/GPv2Settlement/Swap/Balances.t.sol#L41-L73).
- 1inch Limit Order Protocol binds extension hashes and uses separate bit and
  remaining-amount invalidators plus maker-scoped epoch invalidation in
  [`contracts/OrderLib.sol:175-184`](https://github.com/1inch/limit-order-protocol/blob/7da29889efa2e635611e1caf60f85f595ff7f05f/contracts/OrderLib.sol#L175-L184),
  [`contracts/libraries/BitInvalidatorLib.sol:5-13`](https://github.com/1inch/limit-order-protocol/blob/7da29889efa2e635611e1caf60f85f595ff7f05f/contracts/libraries/BitInvalidatorLib.sol#L5-L13),
  [`contracts/libraries/RemainingInvalidatorLib.sol:7-13`](https://github.com/1inch/limit-order-protocol/blob/7da29889efa2e635611e1caf60f85f595ff7f05f/contracts/libraries/RemainingInvalidatorLib.sol#L7-L13),
  and [`contracts/helpers/SeriesEpochManager.sol:21-48`](https://github.com/1inch/limit-order-protocol/blob/7da29889efa2e635611e1caf60f85f595ff7f05f/contracts/helpers/SeriesEpochManager.sol#L21-L48).
- 0x native orders combine per-order cancellation, pair/epoch invalidation, and
  fill-state reads in [`contracts/zero-ex/contracts/src/features/native_orders/NativeOrdersCancellation.sol:31-56`](https://github.com/0xProject/protocol/blob/b319a4dceb5053a4794bf53dbeeaeb416c31ef0a/contracts/zero-ex/contracts/src/features/native_orders/NativeOrdersCancellation.sol#L31-L56)
  and [`contracts/zero-ex/contracts/src/features/native_orders/NativeOrdersInfo.sol:258-286`](https://github.com/0xProject/protocol/blob/b319a4dceb5053a4794bf53dbeeaeb416c31ef0a/contracts/zero-ex/contracts/src/features/native_orders/NativeOrdersInfo.sol#L258-L286).

## Related Patterns

- [Registry-Gated Exchange Fallback](./pattern-registry-gated-exchange-fallback.md)
- [ERC-1271 Replay-Safe Account Signatures](../access-control/pattern-erc1271-replay-safe-account-signatures.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
