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
- Pausing claim after an operator finalizes a request traps a fixed entitlement; use narrower pause scopes, expiry, or an emergency claim route.
- If batch finalization can use a rate lower than the original request preview, record the exact finalized rate or amount per request so later claims cannot reprice opportunistically.

## Source Evidence

- Astherus `Earn.sol` burns or accounts withdrawn share tokens in `_doRequestWithdraw`, stores numbered withdrawal requests, lets a bot distribute funding through `distributeWithdraw`, and lets users claim by request number in `claimWithdraw` in [`contracts/Earn.sol`](https://github.com/astherus-contract/astherus-earn-contract/blob/1472bad4d7267a2c9dbf490b646201ad673e9285/contracts/Earn.sol).
- The same contract separates emergency and ordinary withdrawal requests, making the operator-funded phase a distinct liveness surface rather than a synchronous redeem path.
- EtherFi beHYPE finalizes withdrawal requests through an operator-managed queue and exposes claim pausing as an exit-liveness risk in [`src/WithdrawManager.sol`](https://github.com/etherfi-protocol/beHYPE/blob/06ee135254508fa3f0ab6b1bd8e80dc805884420/src/WithdrawManager.sol).
- Puffer finalizes withdrawal requests through `PufferWithdrawalManager`, records claimable request data, and exposes the claim path as a separate liveness surface in [`mainnet-contracts/src/PufferWithdrawalManager.sol`](https://github.com/PufferFinance/puffer-contracts/blob/380600060cd231fd8616ba167e674d4140486dbb/mainnet-contracts/src/PufferWithdrawalManager.sol).
- Swell `swEXIT` and `RswEXIT` batch requests into operator-finalized exits and claim against finalized batch data in [`contracts/lst/contracts/implementations/swEXIT.sol`](https://github.com/SwellNetwork/v3-core-public/blob/ba1eeff12ab994a26492fa5dcd0aa8937733dbb4/contracts/lst/contracts/implementations/swEXIT.sol) and [`contracts/lrt/contracts/implementations/RswEXIT.sol`](https://github.com/SwellNetwork/v3-core-public/blob/ba1eeff12ab994a26492fa5dcd0aa8937733dbb4/contracts/lrt/contracts/implementations/RswEXIT.sol).

## Real-World Examples

- Astherus Earn - request-numbered withdrawals with bot-funded distribution and user pull claims.
- Puffer and Swell - batch-finalized withdrawal tickets with user pull claims.

## Related Patterns

- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Withdrawal Liquidity Buffer](./pattern-withdrawal-liquidity-buffer.md)
- [Vault Fairness Requirements](./req-vault-fairness.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)

## References

- See Source Evidence.
