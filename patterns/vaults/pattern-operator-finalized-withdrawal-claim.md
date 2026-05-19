# Operator-Finalized Withdrawal Claim

> Burn or escrow user shares at request time, then let an operator fund specific request ids so users claim fixed entitlements instead of repricing at claim time.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, withdrawal, async, operator, claim-ledger |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Withdrawals depend on off-chain settlement, external redemption, or operator-provided liquidity
- User claims must remain independently traceable by request id
- The protocol can fix entitlement before the user-controlled claim call
- Operators may fund requests in batches but should not recalculate price during claim

## Avoid When

- Users require trust-minimized instant exit liquidity
- The operator can redirect, cancel, or reorder requests without objective rules
- The claim amount is recomputed from current NAV when the user claims
- There is no timeout, cancellation, or monitoring path for unfunded requests

## Trade-offs

**Pros:**
- Separates user request, operator liquidity movement, and user claim
- Gives each pending exit an auditable beneficiary and fixed amount
- Avoids user timing optionality after fulfillment

**Cons:**
- Operator funding cadence becomes an exit-liveness dependency
- Requires careful accounting for partially funded or emergency requests
- Can become permissioned custody if user entitlements are not enforceable

## How It Works

At request time, burn or escrow the user's shares and create a withdrawal record:

```solidity
function requestWithdraw(uint256 shares) external returns (uint256 id) {
    uint256 assets = previewRedeem(shares);
    _burn(msg.sender, shares);

    id = ++lastRequestId;
    requests[id] = Request({
        owner: msg.sender,
        shares: shares,
        assets: assets,
        funded: false,
        claimed: false
    });
}
```

An operator later funds explicit request ids:

```solidity
function distributeWithdraw(uint256 id, uint256 fundedAssets) external onlyOperator {
    Request storage r = requests[id];
    require(!r.funded, "funded");
    require(fundedAssets >= r.assets, "short funding");
    r.funded = true;
}
```

The user claim consumes the fixed entitlement:

```solidity
function claimWithdraw(uint256 id) external {
    Request storage r = requests[id];
    require(msg.sender == r.owner, "owner");
    require(r.funded && !r.claimed, "not claimable");

    r.claimed = true;
    _transferAssets(r.owner, r.assets);
}
```

## Implementation

### Key Points

- Record owner, receiver, asset, share amount, claim amount, and request id before any later operator action.
- Mark requests claimed before transferring assets.
- Keep funded request assets out of deployable capital and admin rescue paths.
- Bound operator batch sizes and emit per-request fulfillment events.
- Define emergency requests, cancellation, and timeout behavior explicitly.
- Treat the operator as a liveness dependency; do not describe the pattern as fully trustless exit unless users can force or self-claim from reserved assets.

## Source Evidence

- Astherus `Earn.sol` burns or accounts withdrawn share tokens in `_doRequestWithdraw`, stores numbered withdrawal requests, lets a bot distribute funding through `distributeWithdraw`, and lets users claim by request number in `claimWithdraw` in `/private/tmp/defillama-source/astherus-contract__astherus-earn-contract/contracts/Earn.sol`.
- The same contract separates emergency and ordinary withdrawal requests, making the operator-funded phase a distinct liveness surface rather than a synchronous redeem path.

## Real-World Examples

- Astherus Earn - request-numbered withdrawals with bot-funded distribution and user pull claims.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)
- [Vault Fairness Requirements](./req-vault-fairness.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)

## References

- See Source Evidence.
