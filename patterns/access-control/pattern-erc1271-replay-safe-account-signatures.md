# ERC-1271 Replay-Safe Account Signatures

> Wrap arbitrary external hashes in an account-specific EIP-712 domain before a smart account returns ERC-1271 signature validity.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, erc1271, account-abstraction, signatures, replay |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Smart accounts expose `isValidSignature(bytes32,bytes)` for external protocols
- The account supports multiple owner keys, passkeys, or modules
- Signatures may be checked by protocols that do not know the wallet's full replay domain
- The wallet can define a stable EIP-712 account domain

## Avoid When

- The external protocol already supplies a complete domain and action-specific digest
- The wallet cannot bind signatures to its own address and chain
- Signatures are intended to be replayable across accounts or chains
- Owner verification is off-chain only

## How It Works

Before validating owner signatures, wrap the caller-provided hash in a domain owned by the account:

```solidity
function isValidSignature(bytes32 hash, bytes calldata signature) external view returns (bytes4) {
    bytes32 accountHash = _hashTypedDataV4(keccak256(abi.encode(
        ACCOUNT_SIGNATURE_TYPEHASH,
        hash
    )));

    return _isOwnerSignature(accountHash, signature)
        ? IERC1271.isValidSignature.selector
        : bytes4(0xffffffff);
}
```

This prevents a signature produced for one smart account from being reused as a valid ERC-1271 signature for another account or chain.

## Key Points

- Bind the signature to chain id, verifying contract, account implementation domain, and owner set semantics.
- Keep the original external hash inside the account-domain wrapper instead of replacing protocol-specific checks.
- Test replay against another account, another chain/domain, and stale owner keys.
- Document whether contract signatures, passkeys, and EOAs share the same domain.
- Do not use this to bless arbitrary value-bearing actions that lack their own deadline, nonce, and action parameters.
- Protocols that accept ERC-1271 order signatures should distinguish EOA, proxy, safe, and contract-wallet signature types; require the intended maker/signer relationship; require code at contract signers; and test wrong type, non-contract maker, invalid contract, and maker/signer mismatch cases.

## Source Evidence

- Coinbase Smart Wallet wraps ERC-1271 external hashes in an account-specific EIP-712 domain before owner signature validation, with tests for replay behavior.
- Polymarket CTF Exchange validates multiple order signature types, including ERC-1271 contract signatures, and tests invalid contract signers and signer/maker mismatches.

## Related Patterns

- [Scoped Chain-ID Bypass For Wallet Maintenance](./pattern-scoped-chain-id-bypass-for-wallet-maintenance.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
