# Two-Step Delegated Order Signer

> Let an account authorize a delegate signer only after both the account and signer confirm the delegation.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, eip712, delegated-signer, signatures, account-abstraction |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Smart-contract accounts need an EOA signer for typed orders
- A signer should not be able to self-appoint authority over an account
- Users can rotate, reject, or remove delegates on-chain
- The order verifier supports both direct account signatures and delegated signatures

## Avoid When

- The account can already validate orders directly through ERC-1271
- Delegation is off-chain only and cannot be audited or revoked on-chain
- A single signature should grant only one action, not ongoing signer authority

## Trade-offs

**Pros:**
- Prevents unilateral delegate registration
- Keeps delegated signing explicit and revocable
- Supports smart-contract accounts without `tx.origin` gates

**Cons:**
- Adds state and an extra activation transaction
- Users must understand who can sign for them
- Compromised delegates can sign until removed

## How It Works

Delegation starts in a pending state. The signer must accept before signatures are valid:

```solidity
enum DelegationStatus {
    NONE,
    PENDING,
    ACCEPTED,
    REJECTED
}

mapping(address signer => mapping(address account => DelegationStatus)) public delegatedSigner;

function requestDelegate(address signer) external {
    delegatedSigner[signer][msg.sender] = DelegationStatus.PENDING;
}

function acceptDelegation(address account) external {
    require(delegatedSigner[msg.sender][account] == DelegationStatus.PENDING, "not pending");
    delegatedSigner[msg.sender][account] = DelegationStatus.ACCEPTED;
}
```

Order validation accepts a recovered signer only when it is either the account itself or an accepted delegate.

## Implementation

```solidity
function _verifyOrder(Order calldata order, bytes calldata signature) internal view {
    bytes32 digest = _hashTypedData(order);
    address signer = ECDSA.recover(digest, signature);

    bool direct = signer == order.account;
    bool delegated = delegatedSigner[signer][order.account] == DelegationStatus.ACCEPTED;
    require(direct || delegated, "invalid signer");
}
```

### Key Points

- Bind delegated signatures to typed order domains, nonces, deadlines, and value-bearing fields.
- Let the account remove a delegate without delegate cooperation.
- Emit events for request, acceptance, and removal.
- Do not use `tx.origin` as a substitute for delegated signer checks.

## Source Evidence

- Avant `AvUSDMintingV2` implements `setDelegatedSigner`, `confirmDelegatedSigner`, `removeDelegatedSigner`, and accepts delegated signers in `verifyOrder` in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/contracts/AvUSDMintingV2.sol`.
- Avant tests cover pending delegation, confirmation, accepted delegate signatures, and removal in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/test/foundry/minting/tests/AvUSDMinting.Delegate.t.sol`.

## Real-World Examples

- Avant avUSD - two-step delegated EOA signing for smart-contract users of signed mint/redeem orders.

## Related Patterns

- [ERC-1271 Replay-Safe Account Signatures](./pattern-erc1271-replay-safe-account-signatures.md)
- [Typed Signed Order Settlement](../routing/pattern-typed-signed-order-settlement.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)

## References

- See Source Evidence.
