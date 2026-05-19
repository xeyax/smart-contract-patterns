# Signed Custody-Routed Mint

> Authorize mint and redeem orders with typed signatures and constrain any custody route used for off-chain reserve settlement.

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
- Operators can choose settlement routes that change user price, asset, receiver, fee, or claim semantics without signer authorization

## Trade-offs

**Pros:**
- Binds off-chain approval to exact user-facing execution terms
- Supports multi-custodian routing with constrained executor discretion
- Prevents replay across routes, chains, order types, and users

**Cons:**
- Custodian and signer trust remains central
- Operational mistakes in route configuration can block settlement
- Reserve proof and reconciliation are still required outside the order hash

## How It Works

The strict variant includes every field that affects settlement, including the
route and custody split:

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

### Operator-Selected Custody Route Variant

Some issuers keep the custodian route outside the signed order so operations can
choose the wallet split at execution time. That is weaker than route-bound
signing and should be used only when route choice cannot change the user's
economics. The contract still needs to reject unknown custodians, zero-ratio
legs, and routes whose ratios do not sum to 100 percent.

```solidity
function mint(Order calldata order, Route calldata route, bytes calldata sig) external {
    _verifyOrder(order, sig);        // account, asset, amounts, nonce, expiry
    _consumeNonce(order.account, order.nonce);
    _verifyCustodyRoute(route);      // custodian allowlist and ratio sum
    _transferCollateral(order.asset, order.amount, route);
    _mint(order.receiver, order.tokensOut);
}
```

## Key Points

- Domain-separate signatures by chain id and verifying contract.
- Bind operation type, account, asset, amount, receiver, nonce, and expiry.
- Bind route and custodian allocation when the route can affect user-visible economics.
- If the executor supplies the route, prove it is only an internal custody allocation and validate the route on-chain.
- Use bitmap or mapping nonce consumption so replay is impossible.
- Check route and custodian allowlists on-chain, not only in the signer service.
- Pair with public reserve backing requirements and settlement traceability.

## Source Evidence

- Ethena's 2023 Code4rena snapshot signs typed mint/redeem orders with account, asset, amounts, nonce, and expiry, while the route is supplied to `mint(order, route, signature)` and checked by `verifyRoute` for custodian membership, nonzero ratios, and a total of 10,000 bps in `/private/tmp/defillama-source/code-423n4__2023-10-ethena/contracts/EthenaMinting.sol`.
- Ethena minting tests cover valid and invalid multi-custodian routes in `/private/tmp/defillama-source/code-423n4__2023-10-ethena/test/foundry/minting/tests/EthenaMinting.core.t.sol`.

## Related Patterns

- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
- [Custodial Reserve Backing Requirements](./req-custodial-reserve-backing.md)
- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
