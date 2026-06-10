# Stakeholder-Extensible Governance Timelock

> Let economically exposed stakeholders lock claims into a signaling escrow that extends proposal delay and can escalate to an exit path.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, timelock, veto, signaling, stakeholder |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Token governance can execute actions that affect another stakeholder class
- Stakeholders need time to exit before hostile or disputed proposals execute
- Veto support can be measured from locked assets or withdrawal claims
- The system can define bounded escalation and de-escalation states

## Avoid When

- Stakeholders cannot be represented by on-chain claims
- Exit liquidity is unavailable or externally permissioned without recovery
- A fixed governance timelock is already sufficient
- Veto thresholds can be flash-borrowed or rapidly recycled

## Trade-offs

**Pros:**
- Gives a non-voting stakeholder class real, economically weighted leverage over hostile proposals without granting them governance power.
- Delay scales with measured dissent, so uncontroversial proposals keep normal latency.
- Locked-claim measurement makes veto support costly to fake compared to snapshot voting.
- Bounded escalation states provide a credible endgame (exit) instead of an indefinite standoff.

**Cons:**
- State machine with support thresholds, cooldowns, and escalation paths is a large audit surface; every transition needs tests against shifting support.
- Denominator accounting (rebases, finalized withdrawals) is subtle — errors silently move thresholds.
- Adds worst-case latency to all governance, including legitimate emergency actions, while veto support is elevated.
- Deadlock risk: badly tuned thresholds or resubmission rules can let a minority stall execution indefinitely.
- Locking assets for signaling imposes opportunity cost on dissenters and can be griefed by repeated escalation cycles.

## How It Works

Stakeholders lock assets or exit claims into a signaling escrow. Governance proposals remain executable only when veto support is below state-specific thresholds:

```solidity
function canSchedule(bytes32 proposalId) public view returns (bool) {
    VetoState state = dualGovernanceState();
    if (state == VetoState.Normal) return true;
    if (state == VetoState.Delay) return block.timestamp >= proposalDelayUntil[proposalId];
    return false;
}
```

As support increases, the protocol extends delay, enters cooldowns, or escalates to an exit mechanism before proposals can proceed.

## Key Points

- Define support denominators and how rebases or finalized withdrawals affect them.
- Prevent indefinite proposal submission or execution deadlocks.
- Keep one active escalation path at a time unless concurrency is explicitly designed.
- Make post-veto cooldown and proposal resubmission rules deterministic.
- Test support changes across all state transitions.

## Source Evidence

- Lido Dual Governance lets stETH holders lock support in signaling escrow to delay DAO proposal execution and escalate unresolved disputes into rage quit.

## Related Patterns

- [Local Settlement Rage-Quit Escrow](./pattern-local-settlement-rage-quit-escrow.md)
- [Veto Governance Liveness And Exit Safety Requirements](./req-veto-governance-liveness-and-exit-safety.md)
