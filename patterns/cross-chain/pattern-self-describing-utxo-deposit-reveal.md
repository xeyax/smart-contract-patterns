# Self-Describing UTXO Deposit Reveal

> Encode depositor, wallet, refund, and routing terms into a Bitcoin deposit script, then reveal and sweep that UTXO with proof-based settlement.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, bitcoin, utxo, deposit, reveal |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge accepts deposits from a UTXO chain into an account-based chain
- Deposit terms must be recoverable from the UTXO script and reveal payload
- Deposits need refund paths if sweep or mint settlement fails
- Final settlement is separate from initial deposit discovery

## Avoid When

- The source chain has account-native messages that can directly call the bridge
- A trusted custodian manually maps deposits to users
- The bridge cannot later prove the deposit transaction and output inclusion

## How It Works

Users create a deposit script that commits to the bridge wallet, depositor, refund path, blinding factor, and optional destination routing:

```solidity
function revealDeposit(DepositReveal calldata reveal) external {
    bytes32 scriptHash = buildDepositScriptHash(reveal);
    bytes32 depositKey = keccak256(abi.encode(scriptHash, reveal.outpoint));
    require(deposits[depositKey].state == State.Unknown, "known");

    deposits[depositKey] = DepositState({
        depositor: reveal.depositor,
        wallet: reveal.wallet,
        refundLocktime: reveal.refundLocktime,
        vault: reveal.vault,
        state: State.Revealed
    });
}

function submitSweepProof(bytes calldata proof, bytes32 depositKey) external {
    require(_provesSweepOfDeposit(proof, depositKey), "bad sweep");
    deposits[depositKey].state = State.Swept;
    _mintOrCredit(deposits[depositKey]);
}
```

Reveal records a candidate deposit; sweep proof finalizes accounting.

## Key Points

- Treat reveal as discovery and precommit verification, not final settlement.
- Bind refund script, refund locktime, depositor, wallet, blinding, and routing data to the deposit id.
- Require later SPV or relay proof before minting final assets.
- Define duplicate reveal, dust, timeout, and refund behavior.
- Test mismatched script fields and reused outpoints.

## Source Evidence

- tBTC v2 deposit reveal reconstructs Bitcoin deposit scripts from depositor, wallet, refund, blinding, vault, and routing data, while deposit sweep with SPV proof finalizes bridge accounting.

## Related Patterns

- [Bitcoin SPV State Transition Gate](./pattern-bitcoin-spv-state-transition-gate.md)
- [Chain-Bound Request Hash](./pattern-chain-bound-request-hash.md)
- [Custodian-Attested Mint/Burn](./pattern-custodian-attested-mint-burn.md)
