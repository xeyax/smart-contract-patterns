# Receipt-Acknowledged Relayer Rewards

> Lock message fees on send and release relayer rewards only after an authenticated reverse receipt confirms delivery.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, relayer, rewards, receipt, fee |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Cross-chain messages are delivered by third-party relayers
- The source chain can receive authenticated messages back from the destination chain
- Relayer incentives should pay for delivery, not destination application success
- Fees may be paid in ERC20 assets that need balance-delta accounting

## Avoid When

- The destination chain cannot send authenticated receipts back to the source chain
- Relayer payment must be synchronous with destination execution
- The protocol cannot distinguish delivery from semantic application acknowledgement
- Reward redemption would create unbounded loops or push payments to arbitrary receivers

## Trade-offs

**Pros:**
- Rewards release only on an authenticated receipt, so relayers cannot claim fees for undelivered messages.
- Balance-delta fee accounting handles fee-on-transfer ERC20s without crediting phantom amounts.
- Idempotent receipt handling makes duplicate or unknown receipts harmless no-ops.
- Pull-based redemption with zero-before-transfer avoids push-payment reentrancy and receiver-DoS.

**Cons:**
- Relayer payment waits for a full reverse-message round trip; fees sit escrowed in the meantime.
- A stalled or paused return channel strands both rewards and escrowed fees indefinitely.
- Pending-message records accumulate until receipts arrive, growing storage and creating unbounded backlog risk.
- Receipt batching must be gas-bounded or selectable, or delivery transactions can exceed block gas limits.
- Paying for delivery rather than execution means applications still need separate handling for delivered-but-failed messages.

## How It Works

The sending endpoint transfers the fee into escrow and stores the actual received
amount with the message hash:

```solidity
function send(MessageInput calldata input) external returns (bytes32 id) {
    uint256 received = _safeTransferIn(input.feeToken, input.feeAmount);
    id = _messageId(input);
    sent[id] = SentMessage({
        messageHash: keccak256(_encode(input)),
        feeToken: input.feeToken,
        feeAmount: received
    });
    _emitAndSend(input);
}
```

When a later authenticated reverse message carries receipts, the source endpoint
checks whether each original message is still awaiting acknowledgement. Unknown
or already-processed receipts return early, making duplicate receipts idempotent.
Valid receipts delete the pending message and credit the reward address:

```solidity
function markReceipt(Receipt calldata receipt) internal {
    SentMessage memory info = sent[receipt.messageId];
    if (info.messageHash == bytes32(0)) return;

    delete sent[receipt.messageId];
    rewards[receipt.relayer][info.feeToken] += info.feeAmount;
}

function redeemRewards(address feeToken) external {
    uint256 amount = rewards[msg.sender][feeToken];
    require(amount > 0, "no reward");
    rewards[msg.sender][feeToken] = 0;
    IERC20(feeToken).safeTransfer(msg.sender, amount);
}
```

Allowed-relayer lists can be used as an optional delivery guardrail, but the
reward release still depends on an authenticated receipt.

## Key Points

- Account for the actual fee amount received, not the requested amount.
- Store the message hash and fee info until an authenticated receipt arrives.
- Make duplicate or unknown receipts idempotent and non-paying.
- Credit rewards before pull-based redemption, then zero balances before transfer.
- Define whether rewards pay for delivery, execution, or semantic receiver acknowledgement.
- Keep receipt batching gas-bounded or expose explicit receipt selection.

## Source Evidence

- Avalanche ICM Teleporter transfers message fees into `TeleporterMessenger`, stores adjusted fee info, processes receipts from authenticated reverse messages, ignores duplicate receipts, credits relayer reward balances, and uses pull-based reward redemption in [`contracts/teleporter/TeleporterMessenger.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/TeleporterMessenger.sol).
- Teleporter tests cover receipt reward attribution and duplicate/unknown receipt behavior in [`contracts/teleporter/tests/MarkReceiptTests.t.sol`](https://github.com/ava-labs/icm-contracts/blob/0b68b03c906d17850712b49aa20f2dc18ed55568/contracts/teleporter/tests/MarkReceiptTests.t.sol).

## Related Patterns

- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
