# Restaking Slashing Accounting Requirements

> Requirements for restaking vaults that must apply AVS, operator, beacon-chain, or resolver-delayed slashing without per-staker loops.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | restaking, slashing, withdrawal, epoch, accounting |
| Type | Requirement |

## R1: Slash Factors Are Explicit And Composable

**Restaking systems must model each slashing source as an explicit factor or cumulative loss bucket instead of mutating every staker balance.**

### What This Means

- Deposit shares or stake shares remain stable enough for scalable accounting.
- Withdrawable value is derived from stored shares and current or historical slashing factors.
- Multiple slashing sources define their composition order and rounding behavior.

## R2: Queued Withdrawals Preserve Slash Exposure

**A queued withdrawal must remain slashable for the exposure window documented by the protocol.**

### What This Means

- Queue entries store enough scaled-share or capture-time data to apply later slashes.
- Completion uses the correct historical or current factor for the withdrawal.
- Tests cover slashing before queue, after queue, and during completion.
- Operator-managed withdrawal queues should document whether queued requests remain slash-exposed until batch finalization, oracle report, or claim.

## R3: Capture Times Are Bounded By Vault Epochs

**A slash request based on historical stake must prove the capture timestamp is inside the vault's slashable epoch window.**

### What This Means

- The slash request references a capture timestamp or epoch.
- The vault rejects stale capture times outside the slashing window.
- Later cumulative slashes are subtracted so the same stake cannot be slashed twice.

## R4: Veto Or Resolver Delay Is A State Machine

**If slashing can be delayed or vetoed, the resolver path must define request, veto, execute, and expiry conditions.**

### What This Means

- Resolver changes are delayed or otherwise protected after first activation.
- Veto duration is shorter than the vault epoch or slash window.
- Execution behavior is explicit when no resolver is active.

## Verification Checklist

| Requirement | Question |
|-------------|----------|
| R1 | Are all slashing factors represented in state and composed with defined rounding? |
| R2 | Do queued withdrawals remain slashable through the intended window? |
| R3 | Does every historical slash prove capture time is still in range? |
| R4 | Can a veto resolver delay, cancel, or allow execution only through documented states? |

## Source Evidence

- EigenLayer derives withdrawable shares from deposit scaling factor, operator `maxMagnitude`, and beacon-chain slashing factor; queued withdrawals store scaled shares and complete against slash factors in [`src/contracts`](https://github.com/Layr-Labs/eigenlayer-contracts/blob/f84a5151080cdf0b77b9b6e46506cde723d06c28/src/contracts).
- Symbiotic computes slashable stake at a capture timestamp inside the vault epoch, subtracts later cumulative slashes, and optionally routes slashes through resolver veto request/execute states in [`src/contracts`](https://github.com/symbioticfi/core/blob/7cb06639c5cd656d1d212dafa2c270b5fde39306/src/contracts).
- Puffer's restaking protocol and withdrawal manager make validator/accounting finalization part of exit settlement in [`mainnet-contracts/src/PufferProtocol.sol`](https://github.com/PufferFinance/puffer-contracts/blob/380600060cd231fd8616ba167e674d4140486dbb/mainnet-contracts/src/PufferProtocol.sol) and [`mainnet-contracts/src/PufferWithdrawalManager.sol`](https://github.com/PufferFinance/puffer-contracts/blob/380600060cd231fd8616ba167e674d4140486dbb/mainnet-contracts/src/PufferWithdrawalManager.sol).

## Related Patterns

- [Liquid Staking Loss Accounting Requirements](./req-liquid-staking-loss-accounting.md)
- [Async Deposit/Withdrawal](./pattern-async-deposit.md)
- [Curated Validator Operator Registry](./pattern-curated-validator-operator-registry.md)
