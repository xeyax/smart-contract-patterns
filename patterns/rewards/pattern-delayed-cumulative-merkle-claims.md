# Delayed Cumulative Merkle Claims

> Stage Merkle reward roots behind a delay and let users claim only the cumulative delta above what they have already received.

## Metadata

| Property | Value |
|----------|-------|
| Category | rewards |
| Tags | rewards, merkle, claims, delay, cumulative |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Rewards are computed off-chain and published periodically
- Users should not lose unclaimed rewards when a new root is posted
- A delay is useful for monitoring or challenging incorrect roots
- Multiple reward tokens or campaigns share the same claim mechanism

## Avoid When

- Rewards must be immediately claimable at publication
- The off-chain generator cannot produce cumulative totals reliably
- There is no process to detect and revoke bad pending roots during the delay

## How It Works

Publish a pending root that activates after a delay:

```solidity
function submitRoot(bytes32 root) external onlyPublisher {
    pendingRoot = root;
    rootActivationTime = block.timestamp + delay;
}

function activateRoot() public {
    require(block.timestamp >= rootActivationTime, "delay");
    claimableRoot = pendingRoot;
}
```

Claims use cumulative totals:

```solidity
function claim(address token, uint256 cumulativeAmount, bytes32[] calldata proof) external {
    require(_verify(claimableRoot, msg.sender, token, cumulativeAmount, proof), "bad proof");
    uint256 amount = cumulativeAmount - claimed[msg.sender][token];
    claimed[msg.sender][token] = cumulativeAmount;
    _transfer(token, msg.sender, amount);
}
```

## Key Points

- Store claimed cumulative amount per user and token.
- Delay activation long enough for monitoring and root validation.
- Include token, account, cumulative amount, and campaign context in the leaf.
- Decide who can cancel or replace a pending root.
- Test invalid proofs, delayed activation, repeated claims, and cumulative increases.

## Source Evidence

- Ether.fi stages pending Merkle reward roots behind a delay and claims per-token cumulative deltas after subtracting previously claimed amounts.

## Related Patterns

- [Indexed Merkle Airdrop](./pattern-indexed-merkle-airdrop.md)
- [Queued Reward Streaming](./pattern-queued-reward-streaming.md)
- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
