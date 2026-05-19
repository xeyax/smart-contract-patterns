# Proposer-Validated MemCLOB Settlement

> Settle an appchain orderbook by having the block proposer inject deterministic CLOB operations that consensus validates before state writes.

## Metadata

| Property | Value |
|----------|-------|
| Category | perps |
| Tags | perps, orderbook, appchain, proposer, settlement |
| Complexity | High |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A dedicated appchain runs an in-memory central limit orderbook
- The proposer can construct a deterministic operations transaction
- Consensus can enforce where app-injected operations appear in the block
- Deliver-time state writes can revalidate the raw operations before settlement

## Avoid When

- Order matching is purely contract-local and does not depend on proposer memory
- Proposers cannot be constrained to deterministic message shape and placement
- The chain cannot reject malformed injected operations before state writes

## Trade-offs

**Pros:**
- Keeps high-throughput matching off the persistent state path
- Gives consensus a deterministic settlement envelope
- Rejects malformed proposer operations before balances or positions mutate

**Cons:**
- Proposer behavior becomes part of protocol safety
- ProcessProposal and DeliverTx validation must remain consistent
- Debugging requires reasoning across mempool, proposal, ante, and keeper layers

## How It Works

The proposer builds an app-injected transaction that contains matched orderbook
operations. ProcessProposal verifies that the injected transaction appears in the
expected position and has the expected message shape. DeliverTx then validates
the raw operations against queued placements and writes fills to state.

```go
func PrepareProposal(ctx Context) Tx {
    operations := memclob.BuildProposerOperations()
    return NewInjectedTx(MsgProposedOperations{Operations: operations})
}

func ProcessProposal(ctx Context, txs []Tx) error {
    requireInjectedTxAtExpectedIndex(txs)
    requireOnlyProposedOperationsMessage(txs[operationsIndex])
    return nil
}

func DeliverTx(ctx Context, msg MsgProposedOperations) error {
    ops := ValidateAndTransformRawOperations(msg.Operations)
    return keeper.ProcessProposerOperations(ctx, ops)
}
```

## Implementation

- Define the exact transaction order ProcessProposal expects.
- Reject app-injected messages from normal user transactions.
- Revalidate order matches and referenced placements in DeliverTx.
- Keep raw operation encoding versioned and deterministic.
- Test missing injected tx, wrong tx position, extra messages, missing referenced placements, and invalid order matches.

## Source Evidence

- dYdX v4 builds proposer operations in `/private/tmp/defillama-source/dydxprotocol__v4-chain/protocol/app/prepare/prepare_proposal.go` through `GetProposedOperationsTx`.
- dYdX defines expected proposal transaction order in `protocol/app/prepare/transactions.go` and decodes the layout in `protocol/app/process/transactions.go`.
- dYdX validates and transforms raw operations in `protocol/x/clob/types/message_proposed_operations.go`, then writes state in `protocol/x/clob/keeper/process_operations.go`.
- dYdX ante handling rejects app-injected messages outside the isolated deliver path in `protocol/app/ante/msg_type.go`.

## Real-World Examples

- dYdX v4 uses proposer-injected operations for appchain CLOB settlement.

## Related Patterns

- [Bounded Orderbook Maintenance](../liquidity/pattern-bounded-cranked-orderbook-maintenance.md)
- [Bounded Orderbook Liquidation Deleveraging](./pattern-bounded-orderbook-liquidation-deleveraging.md)
- [Unbounded Iteration](../../ANTIPATTERNS.md#unbounded-iteration)

## References

- dYdX v4 chain protocol source.
