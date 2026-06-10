# Local Settlement Rage-Quit Escrow

> Resolve a governance dispute by moving locked stakeholder claims into an immutable local exit escrow while the main system continues with a fresh signaling escrow.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, rage-quit, escrow, exit, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A veto or dispute mechanism must offer an exit without globally shutting down the protocol
- Locked stakeholders have identifiable escrowed claims
- Exit processing can be public, bounded, and independent of new signaling
- The protocol can isolate one dispute cohort from later governance states

## Avoid When

- Exiting users cannot receive a deterministic entitlement
- Exit finalization depends on the same blocked governance action
- The system needs global settlement rather than cohort-specific exit
- Batch processing cannot be kept live under mass exit load

## Trade-offs

**Pros:**
- The protocol keeps operating for everyone outside the dispute cohort — no global shutdown cost.
- Freezing the cohort at activation makes each exiter's entitlement deterministic and immune to later governance states.
- Fresh escrow deployment cleanly separates the active dispute from future signaling, avoiding state contamination.
- Bounded public batch processing means exits do not depend on any privileged operator staying live.

**Cons:**
- Two live escrow lifecycles (exiting + fresh) double the state to reason about and audit.
- Exit completion inherits external dependencies — withdrawal queues, oracles, bridges — any of which can stall claims.
- Mass exits stress the batch path; if batch bounds are miscalibrated, processing can become economically or technically stuck.
- Users locked in the rage-quit escrow lose liquidity and signaling power for the full processing duration.
- Repeated escalations spawn escrow instances, growing operational and monitoring surface over time.

## How It Works

When the dispute escalates, the current signaling escrow becomes a local exit escrow and a new signaling escrow is deployed for future disputes:

```solidity
function activateRageQuit() external {
    Escrow exiting = currentEscrow;
    exiting.lockForRageQuit();
    currentEscrow = _deployFreshEscrow();
    activeRageQuit = exiting;
}
```

Users then process and claim exits through bounded public batches from the local escrow.

## Key Points

- Keep the rage-quit cohort immutable after activation.
- Deploy or select a fresh escrow for later signaling.
- Bound public processing calls so mass exits cannot brick completion.
- Document dependencies on withdrawal queues, oracles, bridges, and claim assets.
- Do not describe local rage quit as full protocol global settlement.

## Source Evidence

- Lido Dual Governance converts signaling escrow into a rage-quit escrow, deploys a fresh signaling escrow, and processes exits through bounded public batches.

## Related Patterns

- [Stakeholder-Extensible Governance Timelock](./pattern-stakeholder-extensible-governance-timelock.md)
- [Global Settlement State Machine](./pattern-global-settlement-state-machine.md)
