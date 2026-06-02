# Uncapped Chain Voting-Power Concentration

> A multi-chain validator or relay can let one chain dominate aggregate voting power unless per-chain contribution is capped or explicitly accepted.

## Metadata

| Property | Value |
|----------|-------|
| Category | governance |
| Tags | governance, voting-power, multi-chain, concentration, quorum |
| Type | Risk Description |

## Applies When

- Validator-set power is aggregated from multiple chains or subnetworks
- One chain can contribute enough stake to satisfy quorum alone
- Chain weights are not capped, delayed, or monitored
- Validator-set correctness depends on cross-chain power balance

## Requirements Affected

- Quorum should represent the intended operator set, not the largest source chain only.
- Chain onboarding and weight changes need explicit concentration review.

## Failure Modes

- A new chain with high stake concentration controls aggregate relay signatures.
- A price or vault issue on one chain changes global voting power abruptly.
- Smaller chains cannot meaningfully veto or detect malicious messages.

## Mitigations

- Cap per-chain or per-subnetwork contribution to global power.
- Add timelocks and alerts for chain weight increases.
- Require quorum across both aggregate stake and chain diversity when appropriate.
- Monitor effective voting-power share by chain and operator.

## Source Evidence

- Symbiotic Relay audit notes highlighted uncapped chain contribution as a validator-set concentration risk.

## Related Patterns

- [Composable Voting-Power Calculator](./pattern-composable-voting-power-calculator.md)
- [Epoch-Committed Validator Set Header](./pattern-epoch-committed-validator-set-header.md)
