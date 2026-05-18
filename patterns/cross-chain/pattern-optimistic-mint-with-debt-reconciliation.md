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

## Key Points

- Track optimistic debt by deposit id or depositor and reconcile it before final minting.
- Require delay, caps, minter authorization, and guardian cancellation.
- Keep proof-based settlement independent so optimistic pause does not block normal minting.
- Document what the contract does not verify on-chain, such as Bitcoin confirmations or refund timing.
- Test cancellation, double minting, partial sweep repayment, and late proof settlement.

## Source Evidence

- tBTC v2 optimistic minting allows faster minting after deposit reveal through minter and guardian roles, records depositor debt, supports cancellation, and reconciles debt when the later sweep finalizes.

## Related Patterns

- [Self-Describing UTXO Deposit Reveal](./pattern-self-describing-utxo-deposit-reveal.md)
- [Bitcoin SPV State Transition Gate](./pattern-bitcoin-spv-state-transition-gate.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
