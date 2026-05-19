# Typed Signed Order Settlement

> Keep matching off-chain while settling orders on-chain by binding every fillable term in an EIP-712 order and tracking fill state.

## Metadata

| Property | Value |
|----------|-------|
| Category | routing |
| Tags | routing, orderbook, eip712, settlement, signatures |
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

## Source Evidence

- Polymarket's CTF Exchange documents off-chain matching with on-chain settlement, binds order fields in typed hashes, validates signature/nonce/expiry/status before settlement, and tests fill and match flows.

## Related Patterns

- [Registry-Gated Exchange Fallback](./pattern-registry-gated-exchange-fallback.md)
- [ERC-1271 Replay-Safe Account Signatures](../access-control/pattern-erc1271-replay-safe-account-signatures.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
