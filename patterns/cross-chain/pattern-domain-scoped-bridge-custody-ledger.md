# Domain-Scoped Bridge Custody Ledger

> Hold shared source-chain bridge custody while accounting each destination domain's spendable balance separately.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, custody, shared-escrow, domain, ledger |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- One bridge escrow holds the same token for multiple destination domains
- Withdrawals or failed-deposit refunds for one domain must not consume another domain's deposits
- The bridge has authenticated source/destination domain identifiers for every settlement path
- Shared-liquidity or hyperbridge accounting is not yet enabled, or is enabled only for selected domains

## Avoid When

- Each destination domain has isolated custody with no shared escrow balance
- The protocol intentionally treats all bridge liquidity as fungible and has a separate solvency invariant for that model
- Withdrawals and refunds cannot be keyed to a proven source or destination domain
- Admins can bypass the per-domain ledger without an explicit migration or emergency playbook

## Trade-offs

**Pros:**
- Limits cross-domain spillover from failed deposits, exits, or proof bugs
- Lets a shared bridge escrow launch before full shared-liquidity accounting is safe
- Makes per-domain bridge obligations observable on-chain

**Cons:**
- Internal ledger drift can strand funds even when the token balance is sufficient
- A later migration to pooled liquidity must retire or reconcile the domain ledger
- Every refund, withdrawal, and emergency path must update the same domain balance semantics

## How It Works

Credit the destination domain when a deposit is accepted into the shared escrow,
then debit the same domain before paying refunds or withdrawals:

```solidity
mapping(uint256 domain => mapping(address token => uint256 amount)) public domainBalance;

function bridgeDeposit(uint256 dstDomain, address token, uint256 amount) external {
    uint256 received = _pullExact(token, msg.sender, amount);
    require(received == amount, "unsupported transfer semantics");

    domainBalance[dstDomain][token] += amount;
    _sendDepositMessage(dstDomain, token, amount);
}

function finalizeWithdrawal(
    uint256 srcDomain,
    address token,
    address receiver,
    uint256 amount,
    Proof calldata proof
) external {
    _verifyWithdrawalProof(srcDomain, token, receiver, amount, proof);
    domainBalance[srcDomain][token] -= amount;
    _safeTransfer(token, receiver, amount);
}
```

Failed-deposit refunds use the same debit path after proving that the destination
settlement failed and that the recorded deposit handle belongs to the original
depositor.

## Key Points

- Key balances by authenticated domain and token, not only token.
- Use balance-delta accounting or exact-transfer rejection before crediting the ledger.
- Consume deposit or exit handles before transferring funds.
- Debit the domain balance before external token transfers.
- Define how the ledger is disabled, reconciled, or migrated when shared liquidity becomes active.
- Test two domains sharing one token balance, insufficient per-domain balance, duplicate refund, duplicate withdrawal, and migration between domain-scoped and pooled liquidity modes.

## Source Evidence

- Sophon's custom USDC shared bridge stores `chainBalance[chainId][token]` to prevent spending across hyperchains until hyperbridging is enabled in `/private/tmp/defillama-source/sophon-org__custom-usdc-bridge/src/L1USDCBridge.sol`.
- Sophon credits the chain balance on `bridgehubDeposit`, debits it on failed-deposit claims and L2-to-L1 withdrawal finalization, and tests insufficient per-chain balance failures in `/private/tmp/defillama-source/sophon-org__custom-usdc-bridge/test/l1USDCBridge/L1USDCBridgeFails.t.sol`.

## Related Patterns

- [Authorized Shared Bridge Lockbox](./pattern-authorized-shared-bridge-lockbox.md)
- [Sovereign Bridge Local Balance Tree](./pattern-sovereign-bridge-local-balance-tree.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Shared Mutable State](../../ANTIPATTERNS.md#shared-mutable-state)
