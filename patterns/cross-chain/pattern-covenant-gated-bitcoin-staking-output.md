# Covenant-Gated Bitcoin Staking Output

> Represent native Bitcoin stake with a Taproot output whose timelock, unbonding, and slashing leaves are validated before app-chain voting power is activated.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bitcoin, staking, covenant, taproot, slashing |
| Complexity | High |
| Gas Efficiency | Low |
| Audit Risk | High |

## Use When

- A protocol wants native BTC economic security without bridging BTC custody
- Staked BTC should remain on Bitcoin under predefined spend paths
- An app chain grants voting power or rewards from proven Bitcoin outputs
- Slashing and unbonding transactions can be validated before activation

## Avoid When

- The protocol needs bridge custody or wrapped BTC minting
- Slashing keys, finality-provider keys, or unbonding paths cannot be documented
- App-chain validators cannot verify the exact Bitcoin script and presigned transactions
- Users expect trustless withdrawals without covenant or signature assumptions

## How It Works

Build a Taproot staking output with separate spend leaves:

```text
staking output
  timelock leaf: staker can withdraw after staking time
  unbonding leaf: staker plus covenant/finality-provider policy exits early
  slashing leaf: slashable spend sends penalty amount to the slashing destination
```

Before granting voting power, the app-chain activation path validates:

- the exact output script and value
- inclusion and confirmation depth
- presigned unbonding and slashing transactions
- fee and output amount sanity
- slashing amount and destination
- covenant, staker, and finality-provider signatures

## Key Points

- Do not describe the output as bridge custody; BTC remains in a constrained Bitcoin script.
- Validate unbonding and slashing transactions before activating voting power.
- Bind staking, unbonding, and slashing scripts to the same staking parameters.
- Treat covenant and finality-provider keys as explicit trust and safety boundaries.
- Test script construction, presigned transaction sanity, fee bounds, and signature failure cases.

## Source Evidence

- Babylon builds Taproot BTC staking outputs with timelock, unbonding, and slashing paths, validates presigned unbonding/slashing transaction sanity, and checks parsed staking messages before activating app-chain staking state.

## Related Patterns

- [Bitcoin SPV State Transition Gate](./pattern-bitcoin-spv-state-transition-gate.md)
- [Self-Describing UTXO Deposit Reveal](./pattern-self-describing-utxo-deposit-reveal.md)
- [Trusted SPV Boundary Omitted](../../ANTIPATTERNS.md#trusted-spv-boundary-omitted)
