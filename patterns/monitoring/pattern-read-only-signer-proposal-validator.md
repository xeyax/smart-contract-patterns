# Read-Only Signer Proposal Validator

> Expose non-mutating validation for proposed off-chain signer payloads before threshold signers produce irreversible signatures.

## Metadata

| Property | Value |
|----------|-------|
| Category | monitoring |
| Tags | monitoring, signer, threshold, validation, bridge |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Off-chain signers must approve custody-moving payloads
- The chain can validate expected wallet, script, output, value, and protocol state
- Signers need a deterministic pre-signing check that mirrors on-chain rules
- Invalid signatures would be costly or slashable

## Avoid When

- Signers already derive payloads from fully trusted software
- The validator cannot access enough protocol state to reject dangerous proposals
- Validation mutates state or can be bypassed by signing a different payload format

## Trade-offs

**Pros:**
- Catches dangerous payloads before irreversible threshold signatures, reducing slashing and custody-loss exposure.
- Read-only design lets signer software and monitoring run the same check without gas or state risk.
- Deterministic on-chain rules give every signer an identical accept/reject answer, avoiding client-by-client reimplementation.
- One shared validator concentrates payload rules in a single audited location.

**Cons:**
- Validator success is advisory: signers can still sign a different payload than the one validated, so it does not prove honest signing.
- Must be versioned in lockstep with payload formats and bridge upgrades, or it starts rejecting good proposals or passing bad ones.
- Blind spots appear wherever the validator cannot read enough protocol state to reject a dangerous proposal.
- Duplicates protocol invariants in validation code, widening the audit surface and creating drift risk against the core.
- On-chain parsing of external payload formats (e.g. Bitcoin transactions) is expensive to implement and test exhaustively.

## How It Works

The validator checks a proposed signing payload against current protocol state and returns or reverts without changing state:

```solidity
function validateRedemptionProposal(bytes calldata bitcoinTx, bytes32 walletId) external view {
    Wallet memory wallet = bridge.wallets(walletId);
    require(wallet.state == WalletState.Live, "wallet not live");
    require(_outputsMatchPendingRedemptions(bitcoinTx, walletId), "bad outputs");
    require(_changeOutputReturnsToWallet(bitcoinTx, wallet), "bad change");
}
```

Signer software calls the validator before producing threshold signatures.

## Key Points

- Validate payload format, signer wallet, protocol state, outputs, values, and change handling.
- Keep validation read-only so it can run in signer infrastructure and monitoring.
- Version validators with payload formats and bridge upgrades.
- Do not treat validator success as proof the later signature was used honestly.
- Test known-good proposals and every slashable mismatch.

## Source Evidence

- tBTC v2 includes a wallet proposal validator that checks proposed Bitcoin signing payloads for deposits, redemptions, moving funds, and heartbeat-style actions before signers produce threshold signatures.

## Related Patterns

- [Threshold Custody Wallet Lifecycle](../cross-chain/pattern-threshold-custody-wallet-lifecycle.md)
- [Read-Only Protocol Health Checker](./pattern-read-only-protocol-health-checker.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
