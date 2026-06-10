# Nonce-Bound Delayed Reward Claim Ledger

> Separate reward accrual from delayed claim execution by hashing amount, owner, receiver, unlock time, and nonce into a claim id.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, claim, delay, nonce, idempotency |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Rewards accrue on-chain but should become transferable only after a delay
- A user can choose a receiver when requesting the claim
- Claims need replay protection without off-chain Merkle roots
- Operators may need a force-execution or cancellation path with explicit status

## Avoid When

- Rewards should be immediately claimable on every interaction
- Off-chain reward generation already uses cumulative Merkle roots
- The protocol cannot safely reserve or subtract the requested amount before the delay
- The receiver, amount, or unlock time is meant to remain mutable after request

## Trade-offs

**Pros:**
- Makes delayed claims individually auditable
- Prevents replay by binding each request to a nonce and full claim tuple
- Lets reward accrual remain lazy while execution is delayed

**Cons:**
- Pending-claim state grows with requested claims
- Users must preserve or reconstruct claim tuple data
- Force-execution paths can become privileged settlement controls

## How It Works

On request, checkpoint rewards, subtract the requested amount from pending
rewards, derive a claim id, and mark it pending:

```solidity
function requestClaim(uint256 requested, address receiver) external returns (bytes32 claimId) {
    _updateReward(msg.sender);

    uint256 amount = min(requested, pendingRewards[msg.sender]);
    require(amount > 0, "zero reward");

    uint256 unlockTime = block.timestamp + claimDelay;
    uint256 nonce = nonces[msg.sender]++;
    claimId = keccak256(abi.encode(amount, msg.sender, receiver, unlockTime, nonce));

    pendingRewards[msg.sender] -= amount;
    claimStatus[claimId] = ClaimStatus.Pending;
}

function executeClaim(
    uint256 amount,
    address owner,
    address receiver,
    uint256 unlockTime,
    uint256 nonce,
    bytes32 claimId
) external {
    require(claimId == keccak256(abi.encode(amount, owner, receiver, unlockTime, nonce)), "claim id");
    require(block.timestamp >= unlockTime, "not ready");
    require(claimStatus[claimId] == ClaimStatus.Pending, "status");

    claimStatus[claimId] = ClaimStatus.Claimed;
    _mintReward(receiver, amount);
}
```

Status is updated before minting or transfer so callbacks cannot replay the same
claim.

## Key Points

- Bind amount, owner, receiver, unlock time, and nonce into the claim id.
- Increment the nonce when the request is created, not when executed.
- Subtract or reserve the requested amount so later reward updates cannot double-spend it.
- Mark claimed before external mint or transfer calls.
- Define whether force execution pays the user, redirects rewards, or cancels the claim.
- Test duplicate request ids, wrong receiver, wrong nonce, early execution, repeated execution, force execution, and lazy index updates around request time.

## Source Evidence

- Satoshi Farm computes claim ids from amount, owner, receiver, claimable time, and nonce; stores pending/claimed status; subtracts pending rewards at request; and marks claims as claimed before minting in [`src/core/Farm.sol`](https://github.com/Satoshi-Protocol/satoshi-farm/blob/174d930eb3c220fa3163a677cea019fc1550074e/src/core/Farm.sol).
- Satoshi Farm tests cover delayed claim request and execution paths in [`test/FarmManager.t.sol`](https://github.com/Satoshi-Protocol/satoshi-farm/blob/174d930eb3c220fa3163a677cea019fc1550074e/test/FarmManager.t.sol).

## Related Patterns

- [Lazy Reward Index](./pattern-lazy-reward-index.md)
- [Delayed Cumulative Merkle Claims](./pattern-delayed-cumulative-merkle-claims.md)
- [Timeboxed Idempotency Key Ledger](../tokens/pattern-timeboxed-idempotency-key-ledger.md)
