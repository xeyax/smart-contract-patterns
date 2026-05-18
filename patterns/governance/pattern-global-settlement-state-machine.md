# Global Settlement State Machine

> Shut down a protocol through explicit phases that freeze new risk, snapshot prices, process positions, compute redemption rates, and let claimants redeem.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, shutdown, settlement, state-machine, redemption |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A system needs a credible emergency shutdown path
- Liabilities must be redeemed against remaining collateral
- Prices and positions need final snapshots
- Auctions, claims, or debt queues need orderly unwinding

## Avoid When

- A simple pause and user withdrawal flow is sufficient
- Final settlement prices cannot be trusted or frozen
- The protocol cannot define who has priority over remaining assets

## How It Works

Global settlement is a state machine, not a single pause:

```text
Live
  -> cage system and freeze new risk
  -> snapshot collateral prices
  -> process unsafe positions and auctions
  -> compute final redemption rates
  -> allow liability holders to redeem collateral
```

Each phase should expose the functions that are allowed and the prerequisites for entering the next phase.

## Key Points

- Freeze new deposits, borrows, and parameter changes before settlement math.
- Snapshot prices once and define who can provide them.
- Keep solvent exit and claim paths open.
- Define how auctions, bad debt, surplus, and collateral shortfall are handled.
- Test every phase transition and invalid transition.

## Source Evidence

- Sky/Maker DSS global settlement freezes system entrypoints, snapshots collateral prices, processes positions and auctions, computes final redemption rates, and lets Dai holders redeem collateral.

## Related Patterns

- [Pause Traps Funds](../../ANTIPATTERNS.md#pause-traps-funds)
- [State Machine Gaps](../../ANTIPATTERNS.md#state-machine-gaps)
- [Credit Loss Accounting Requirements](../lending/req-credit-loss-accounting.md)
