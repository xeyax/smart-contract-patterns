# Liquidity-Captain Storage-Proof Bridge

> Let users assign a liquidity captain to front destination liquidity, then reimburse the captain after proving source-chain bridge state.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, liquidity, storage-proof, refund, state-root |
| Complexity | High |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- Destination users need faster liquidity than canonical settlement provides
- Captains or market makers can predeposit liquidity on the destination
- The destination can verify source-chain storage through a state-root oracle
- Users need refund or deadline behavior if no captain fulfills the transfer

## Avoid When

- There is no reliable source-chain state-root or storage-proof verifier
- Captain liquidity is not isolated from protocol reserves
- Users cannot choose or bound their captain and amount
- Captain withdrawals can race pending fulfillment without delay

## Trade-offs

**Pros:**
- Separates user UX liquidity from canonical proof settlement
- Allows competitive or user-selected liquidity providers
- Source-chain storage proofs can reimburse captains without trusting an operator batch

**Cons:**
- Depends on state-root oracle correctness and freshness
- Captains need withdrawal delays and exposure caps
- Proof generation and verification are complex

## How It Works

On the source chain, a user records a transfer assigned to a captain and amount. On the destination, the captain pays the user from predeposited liquidity. Later the captain proves the source-chain storage slot and collects reimbursement:

```solidity
function disembark(Proof calldata proof, Transfer calldata t) external {
    _verifySourceStorage(proof, hashTransfer(t));
    _consumeTransfer(t.id);
    _payUserFromCaptain(t.captain, t.receiver, t.amount);
}

function collect(Proof calldata proof, Transfer calldata t) external {
    _verifyDestinationFulfillment(proof, t.id);
    _releaseSourceFunds(t.captain, t.amount);
}
```

If no captain fulfills by the user deadline, the user can collect a refund through the canonical path.

## Implementation

```solidity
function depositCaptainLiquidity(uint256 amount) external {
    captainBalance[msg.sender] += amount;
    _transferIn(amount);
}

function requestCaptainWithdrawal(uint256 amount) external {
    pendingWithdrawal[msg.sender] = Withdrawal(amount, block.timestamp + withdrawalDelay);
}
```

### Key Points

- Cap each captain's outstanding assigned amount.
- Require withdrawal delays so captains cannot pull liquidity ahead of pending obligations.
- Bind storage proofs to source chain, contract, slot, transfer id, captain, receiver, amount, and deadline.
- Provide a no-fulfillment refund path.
- Treat state-root oracle provider uniqueness and finality as security-critical.

## Source Evidence

- Fraxferry V2 lets users choose captains with cumulative amount caps in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/FraxferryV2/FerryOnL1.sol`.
- Fraxferry V2 destination liquidity, captain predeposit, withdrawal delay, storage-proof `disembark`, and refund/collect flows are implemented in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/contracts/FraxferryV2/FerryOnL2.sol`.
- Fraxferry V2 tests cover L1-to-L2 proof payout, L2-to-L1 captain collection, and no-disembark refund behavior in `/private/tmp/defillama-source/FraxFinance__frax-solidity/src/hardhat/test/FraxferryV2`.

## Real-World Examples

- Fraxferry V2 - captain liquidity bridge using source storage proofs and refund deadlines.

## Related Patterns

- [Checkpointed Receipt Exit Proof](./pattern-checkpointed-receipt-exit-proof.md)
- [Threshold Reporter Consensus](../oracles/pattern-threshold-reporter-consensus.md)
- [Permissioned Exit Custody](../../ANTIPATTERNS.md#permissioned-exit-custody)

## References

- See Source Evidence.
