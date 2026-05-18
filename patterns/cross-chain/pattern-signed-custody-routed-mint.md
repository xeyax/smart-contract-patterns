# Signed Custody-Routed Mint

> Authorize mint and redeem orders with typed signatures that bind route, custodian allocation, nonce, expiry, and asset ratios before custody-backed settlement.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | custody, mint, redeem, eip712, nonce, route, stablecoin |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Tokens are minted or redeemed against off-chain or custodied reserves
- The protocol routes settlement through multiple custodians or wallets
- Orders need off-chain approval but on-chain replay protection
- The same user-facing flow can settle through different custody routes

## Avoid When

- Reserve movement can be verified trustlessly on-chain
- Custodian allocation is opaque or not reconcilable
- Operators can sign orders without expiry, nonce, and route binding

## Trade-offs

**Pros:**
- Binds off-chain approval to exact on-chain execution terms
- Supports multi-custodian routing without arbitrary executor discretion
- Prevents replay across routes, chains, order types, and users

**Cons:**
- Custodian and signer trust remains central
- Operational mistakes in route configuration can block settlement
- Reserve proof and reconciliation are still required outside the order hash

## How It Works

The signed order should include all fields that affect settlement:

```solidity
struct MintOrder {
    address account;
    address asset;
    uint256 assetAmount;
    uint256 minTokensOut;
    uint256 nonce;
    uint256 deadline;
    bytes32 routeId;
    CustodySplit[] custody;
}
```

Validation checks the typed signature, consumes the nonce, verifies deadline, and enforces that the custody split is allowed and sums to the expected ratio.

```solidity
function mint(MintOrder calldata order, bytes calldata sig) external {
    require(block.timestamp <= order.deadline, "expired");
    require(_consumeNonce(order.account, order.nonce), "used nonce");
    require(_verifySigner(order, sig), "bad signature");
    require(_isAllowedRoute(order.routeId, order.custody), "bad route");
    require(_custodySplitSums(order.custody), "bad split");

    _transferIn(order.asset, order.assetAmount);
    _mint(order.account, _quote(order));
}
```

## Key Points

- Domain-separate signatures by chain id and verifying contract.
- Bind operation type, account, asset, amount, route, custodian allocation, nonce, and expiry.
- Use bitmap or mapping nonce consumption so replay is impossible.
- Check route and custodian allowlists on-chain, not only in the signer service.
- Pair with public reserve backing requirements and settlement traceability.

## Source Evidence

- Ethena uses typed signed mint/redeem orders with nonce replay protection, expiry, route/custodian constraints, and ratio checks for custody-routed settlement.

## Related Patterns

- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
- [Custodial Reserve Backing Requirements](./req-custodial-reserve-backing.md)
- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
