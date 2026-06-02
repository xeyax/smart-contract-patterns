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
