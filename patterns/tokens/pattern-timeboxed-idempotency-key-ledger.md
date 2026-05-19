# Timeboxed Idempotency Key Ledger

> Record operation keys for a bounded retention window so retried mints, burns, transfers, or redemptions execute at most once.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, idempotency, replay, batch, soroban |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Off-chain operations can be retried after network or operator failures
- The same request may arrive through batch and single-operation flows
- Duplicate execution would mint, burn, transfer, or redeem value twice
- Storage retention can be bounded by business process deadlines
- Or the operation is cross-chain and needs permanent or chain-scoped duplicate protection

## Avoid When

- The operation is already uniquely keyed by a nonce consumed on-chain
- Keys cannot be domain-separated by operation and economic terms
- Users need indefinite replay protection after the retention window, unless the key is deliberately permanent
- Operators can choose keys that collide across users or assets

## How It Works

Before executing, derive or receive an idempotency key and mark it as consumed with an expiry:

```solidity
function execute(Request calldata request) external {
    bytes32 key = keccak256(abi.encode(
        request.operation,
        request.caller,
        request.token,
        request.amount,
        request.receiver,
        block.chainid,
        address(this)
    ));

    require(consumedUntil[key] < block.timestamp, "duplicate");
    consumedUntil[key] = block.timestamp + retentionWindow;
    _execute(request);
}
```

The key must bind the economic terms. A raw operator-provided string can prevent exact retries, but it can also collide with unrelated operations or let one caller grief another.

## Key Points

- Bind operation type, account, asset, amount, receiver, chain, and contract.
- Keep the retention window longer than expected retry and settlement periods.
- Emit key-consumption events for reconciliation.
- Treat expiry as a deliberate replay boundary, not permanent uniqueness.
- Apply the same key rules to batch and single-request entrypoints.
- For cross-chain top-ups or bridge settlements, include source chain, destination chain, transfer id, asset, amount, and recipient, and keep keys permanent when duplicate settlement must never be allowed.

## Source Evidence

- Spiko's Stellar contracts use temporary idempotency keys around mint, burn, redeem, and safe-transfer flows, with tests for duplicate rejection and expiry behavior.
- EtherFi Cash top-up settlement records chain-scoped top-up ids to reject duplicate destination execution in `/private/tmp/defillama-source/etherfi-protocol_cash-contracts/src/top-up/TopUpDest.sol`.

## Related Patterns

- [Chain-Bound Request Hash](../cross-chain/pattern-chain-bound-request-hash.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)
