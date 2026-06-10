# Address Prefix Subaccount Namespace

> Encode small virtual subaccounts in low address bits and bind them to a first-use owner namespace.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, subaccount, operator, namespace, account |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Users need multiple isolated account slots under one wallet identity
- Operators should be authorized per subaccount or subaccount group
- The protocol can derive a common owner namespace from an address prefix
- Contract-code subaccounts are either unsupported or explicitly modeled

## Avoid When

- The protocol treats every address as an independent owner
- Low address bits may collide with externally assigned account semantics
- Smart-contract wallets need arbitrary subaccount addresses without additional validation
- Off-chain systems cannot display or explain the subaccount relationship

## Trade-offs

**Pros:**
- Hundreds of isolated subaccounts per wallet without deploying or initializing anything per slot
- Operator permissions stored once per owner prefix, so bitmap lookups stay cheap across all subaccounts
- Prefix comparison is a pure-function check that adds negligible gas to authorization paths
- Subaccount isolation requires no extra key management for the user

**Cons:**
- Breaks the default assumption that every address is an independent account, so integrators, indexers, and explorers must special-case the namespace
- First-use prefix binding is permanent; a mistaken binding cannot be corrected or migrated
- Smart-contract subaccounts must be rejected or explicitly integrated because their callback and signature behavior differs from virtual slots
- Low address bits can clash with external systems that assign their own meaning to those addresses
- Assets sent to a subaccount address from outside the protocol may be unreachable without protocol-level recovery support

## How It Works

Reserve a small suffix of the address for subaccount ids. The first interaction binds the prefix to an owner, and authorization checks compare future subaccounts against that prefix:

```solidity
function ownerPrefix(address account) internal pure returns (bytes19) {
    return bytes19(bytes20(account));
}

function isSameOwner(address a, address b) internal pure returns (bool) {
    return ownerPrefix(a) == ownerPrefix(b);
}

function setOperator(address subaccount, address operator, bool approved) external {
    require(isSameOwner(msg.sender, subaccount), "not owner namespace");
    operatorBitmap[ownerPrefix(subaccount)][operator] = approved;
}
```

If the protocol cannot safely call or validate contract subaccounts, reject accounts with code or require explicit contract-wallet integration.

## Key Points

- Document how many low bits are reserved and how many subaccounts exist per owner.
- Bind the namespace on first use and make rebinding impossible.
- Check operator permissions against the subaccount namespace, not only `msg.sender`.
- Reject contract-code subaccounts unless the protocol supports their callback and signature behavior.
- Test owner/subaccount mismatch, non-owner operator assignment, and contract subaccount rejection.

## Source Evidence

- Euler's Ethereum Vault Connector whitepaper describes 256 subaccounts sharing the first 19 address bytes; its contracts store operator bitmaps under that namespace and tests reject unsupported smart-contract subaccounts.

## Related Patterns

- [Participant Permission Bitmap](./pattern-participant-permission-bitmap.md)
- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)
