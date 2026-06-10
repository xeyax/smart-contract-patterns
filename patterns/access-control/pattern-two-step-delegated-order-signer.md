# Two-Step Delegated Order Signer

> Let an account authorize a delegate signer only after both the account and signer confirm the delegation.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, eip712, delegated-signer, signature, account-abstraction |
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
- Signer acceptance is intentionally not required and immediate account-owned delegation is acceptable

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

### One-Step Account-Owned Variant

If signer consent is not a requirement, the account can register and remove a
delegate directly:

```solidity
function setDelegatedSigner(address delegate) external {
    delegatedSigner[delegate][msg.sender] = true;
}

function removeDelegatedSigner(address delegate) external {
    delegatedSigner[delegate][msg.sender] = false;
}
```

This is lower friction, but weaker than the two-step model. Use it only when the
account is the sole authority boundary and typo protection or signer acceptance
does not matter.

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
- If using one-step registration, document that account compromise or a mistaken delegate address becomes active immediately.

## Source Evidence

- Avant `AvUSDMintingV2` implements `setDelegatedSigner`, `confirmDelegatedSigner`, `removeDelegatedSigner`, and accepts delegated signers in `verifyOrder` in [`contracts/AvUSDMintingV2.sol`](https://github.com/Avant-Protocol/avUSD-Contracts/blob/43858abc5a3c481e3b2d02790d168b88e630e7b1/contracts/AvUSDMintingV2.sol).
- Avant tests cover pending delegation, confirmation, accepted delegate signatures, and removal in [`test/foundry/minting/tests/AvUSDMinting.Delegate.t.sol`](https://github.com/Avant-Protocol/avUSD-Contracts/blob/43858abc5a3c481e3b2d02790d168b88e630e7b1/test/foundry/minting/tests/AvUSDMinting.Delegate.t.sol).
- Ethena's 2023 Code4rena snapshot implements a one-step account-owned delegated signer in [`contracts/EthenaMinting.sol`](https://github.com/code-423n4/2023-10-ethena/blob/9fd8e26fc596601c3359ceac8951740c4d5e09c7/contracts/EthenaMinting.sol), with delegate success, failure, and removal tests in [`test/foundry/minting/tests/EthenaMinting.Delegate.t.sol`](https://github.com/code-423n4/2023-10-ethena/blob/9fd8e26fc596601c3359ceac8951740c4d5e09c7/test/foundry/minting/tests/EthenaMinting.Delegate.t.sol).

## Real-World Examples

- Avant avUSD - two-step delegated EOA signing for smart-contract users of signed mint/redeem orders.
- Ethena USDe contest snapshot - one-step account-owned delegated EOA signing for signed mint/redeem orders.

## Related Patterns

- [ERC-1271 Replay-Safe Account Signatures](./pattern-erc1271-replay-safe-account-signatures.md)
- [Typed Signed Order Settlement](../routing/pattern-typed-signed-order-settlement.md)
- [Signature Scope Drift](../../ANTIPATTERNS.md#signature-scope-drift)

## References

- See Source Evidence.
