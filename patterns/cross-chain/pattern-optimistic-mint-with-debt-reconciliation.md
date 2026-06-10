# Optimistic Mint With Debt Reconciliation

> Mint bridge assets before final settlement under bounded role risk, then repay that optimistic debt when the source-chain proof is finalized.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, optimistic, mint, debt, reconciliation |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Final source-chain settlement is slow but deposit discovery can be validated earlier
- A minter, guardian, or committee is an explicit bounded trust assumption
- The protocol can track optimistic debt per depositor or deposit id
- Later settlement can repay debt before ordinary minting proceeds

## Avoid When

- Users require trustless minting only after final proof
- The optimistic minter can mint without caps, delays, or cancellation
- Final settlement cannot be matched back to the optimistic mint

## Trade-offs

**Pros:**
- Users receive minted assets long before slow source-chain settlement completes.
- The debt ledger reconciles optimistic supply against final proofs, bounding inflation from acceleration errors.
- Guardian cancellation and pause stop optimistic acceleration without halting normal proof-based minting.
- Caps and delays bound worst-case loss from a compromised or careless minter.

**Cons:**
- Minter and guardian roles are explicit trust assumptions; collusion or key compromise can mint unbacked supply up to the caps.
- Two parallel mint paths double the accounting and test surface: cancellation, double mint, partial sweep repayment, and late settlement all need coverage.
- Reconciliation edge cases — sweeps smaller than recorded debt, repeated deposits against one key — are subtle insolvency bugs.
- The contract cannot verify everything on-chain (e.g., Bitcoin confirmations, refund timing); the unverified set must be documented and monitored off-chain.
- The sync-pool variant must keep deficit accounting strictly separate from ordinary liquidity, which rebalancing flows can easily corrupt.

## How It Works

Optimistic minting records debt before final source-chain settlement:

```solidity
function requestOptimisticMint(bytes32 depositKey, uint256 amount) external onlyMinter {
    require(_depositWasRevealed(depositKey), "not revealed");
    require(block.timestamp >= revealTime[depositKey] + optimisticDelay, "too early");

    optimisticDebt[depositKey] += amount;
    token.mint(depositor[depositKey], amount);
}

function finalizeSweep(bytes32 depositKey, uint256 sweptAmount) external {
    uint256 debt = optimisticDebt[depositKey];
    if (debt != 0) {
        optimisticDebt[depositKey] = 0;
        _repayOptimisticDebt(depositKey, debt);
        sweptAmount -= debt;
    }
    _mintFinalAmount(depositor[depositKey], sweptAmount);
}
```

Guardian cancellation or pause can stop optimistic acceleration while leaving standard proof-based minting available.

### Native Sync Pool Variant

When native assets are bridged through a sync pool, the destination chain can mint or release optimistically against a recorded deficit. Later source-chain settlement repays the deficit before fresh liquidity is treated as surplus. This variant needs the same debt ledger, caps, and cancellation paths as deposit-id optimistic mints.

## Key Points

- Track optimistic debt by deposit id or depositor and reconcile it before final minting.
- Require delay, caps, minter authorization, and guardian cancellation.
- Keep proof-based settlement independent so optimistic pause does not block normal minting.
- Document what the contract does not verify on-chain, such as Bitcoin confirmations or refund timing.
- For sync pools, keep deficit accounting separate from ordinary pool liquidity so later deposits repay optimistic releases before new minting proceeds.
- Test cancellation, double minting, partial sweep repayment, and late proof settlement.

## Source Evidence

- tBTC v2 optimistic minting allows faster minting after deposit reveal through minter and guardian roles, records depositor debt, supports cancellation, and reconciles debt when the later sweep finalizes.
- EtherFi sync pools track native bridge deficits and repay them during later source-chain settlement in [`contracts/native-minting/layerzero-base/L2BaseSyncPoolUpgradeable.sol`](https://github.com/etherfi-protocol/weETH-cross-chain/blob/cc6c220847217df8f9dcc4ba19c1c349106a002c/contracts/native-minting/layerzero-base/L2BaseSyncPoolUpgradeable.sol) and `contracts/native-minting/layerzero-base/L1BaseSyncPoolUpgradeable.sol`.

## Related Patterns

- [Self-Describing UTXO Deposit Reveal](./pattern-self-describing-utxo-deposit-reveal.md)
- [Bitcoin SPV State Transition Gate](./pattern-bitcoin-spv-state-transition-gate.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
- [Pairwise Bridge Rate Limits](./pattern-pairwise-bridge-rate-limits.md)
