# Oracle-Computed Async Settlement

> Queue mint or burn requests asynchronously, but compute completion economics from stored request data and oracle state instead of operator-supplied output amounts.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, async-settlement, oracle, mint, burn, operator |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Deposits or redemptions require off-chain processing before completion
- A completion operator is needed for liveness
- Request-time inputs, fees, or prices should constrain final economics
- Users need auditable pending request state

## Avoid When

- Settlement can be completed synchronously
- The operator must retain discretion over the final amount
- Oracle state is stale, unauthenticated, or not tied to request timing
- Users cannot cancel, expire, or otherwise reason about pending requests

## Trade-offs

**Pros:**
- Keeps operator role focused on liveness rather than pricing
- Makes request economics reproducible from on-chain state
- Reduces arbitrary completion amount risk

**Cons:**
- Requires careful oracle freshness and request timestamp handling
- Pending requests can still create liveness and custody risk
- More state than synchronous ERC-4626 flows

## How It Works

Store the request's amount, fee basis, receiver, and request timestamp. Completion recomputes the output:

```solidity
struct Request {
    address account;
    uint256 inputAmount;
    uint256 feeBps;
    uint256 requestedAt;
    bool completed;
}

function completeMint(uint256 id) external onlyOperator {
    Request storage r = requests[id];
    require(!r.completed, "complete");
    uint256 price = priceOracle.priceAtOrAfter(r.requestedAt);
    uint256 shares = _quoteMint(r.inputAmount, price, r.feeBps);
    r.completed = true;
    _mint(r.account, shares);
}
```

For burns, snapshot the fee or price rule at request time when later admin changes should not affect already-pending exits.

## Implementation

```solidity
function requestBurn(uint256 shares) external returns (uint256 id) {
    id = ++nextRequestId;
    requests[id] = Request({
        account: msg.sender,
        inputAmount: shares,
        feeBps: burnFeeBps,
        requestedAt: block.timestamp,
        completed: false
    });
    _escrowShares(msg.sender, shares);
}
```

### Key Points

- Store enough data to recompute the final amount without operator discretion.
- Snapshot fee terms for pending exits when fee changes should not be retroactive.
- Make completion idempotent and consume request state before external transfers.
- Document whether users can cancel or whether completion is permissioned custody.
- For solver-filled requests, bind request hashes to token, sender, request type, amount, slippage bound, solver tip, deadline, max price age, and fixed-price or auto-price mode.
- Emit skipped or failed request processing so off-chain operators can distinguish liveness failures from rejected economics.

## Source Evidence

- Avant MAX V1 completed mint and burn requests with service-supplied output amounts, while MAX V2 computes completion amounts from stored request data and `PriceStorage` in `/private/tmp/defillama-source/Avant-Protocol__Avant-Contracts-Max/src/RequestsManagerV2.sol`.
- MAX V2 tests cover arbitrary completion amount prevention and request-time burn fee locking in `/private/tmp/defillama-source/Avant-Protocol__Avant-Contracts-Max/test/RequestsManagerV2.t.sol`.
- Aera v3 hashes async deposit and redeem request parameters, supports solver tips, deadlines, max price age, fixed-price and auto-price modes, direct or vault-routed solving, and refund paths in `/private/tmp/defillama-source/aera-finance__aera-contracts-public/v3/src/core/Provisioner.sol`.

## Real-World Examples

- Avant MAX V2 - request manager computes settlement output from stored request state and price storage rather than trusting an operator amount.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Historical Bounds](../oracles/pattern-historical-bounds.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)

## References

- See Source Evidence.
