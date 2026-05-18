# Escrow Mint-Burn Refund Fallback

> Pair source escrow or burn with destination validation and automatic refund when bridge settlement cannot safely mint or release.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, escrow, mint-burn, refund, settlement |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Bridge deposits lock or burn assets before destination settlement
- Destination token deployment or peer binding may fail
- The bridge can send a compensating withdrawal or refund message
- Users need liveness even when custom token registration is misconfigured

## Avoid When

- Failed destination settlement cannot be proven or refunded
- Source assets are transferred to an irreversible external custodian
- The protocol cannot distinguish invalid destination state from temporary failure

## Trade-offs

**Pros:**
- Avoids minting wrapped assets into invalid token mappings
- Gives users a recovery path for failed destination settlement
- Makes bridge token deployment failures fail closed

**Cons:**
- Refund paths must be replay-safe and may be delayed
- Partial failures create extra accounting and monitoring burden
- Destination validation must be strict enough to prevent counterfeit peers

## How It Works

On deposit, source-side assets are escrowed or burned. On the destination chain, finalization validates the token contract and peer binding. If validation fails, the bridge sends a refund or withdrawal back instead of minting.

```solidity
function finalizeInbound(address token, address to, uint256 amount) external onlyCounterpart {
    if (!_validDestinationToken(token)) {
        _refundToSource(token, to, amount);
        return;
    }

    _mintOrRelease(token, to, amount);
}
```

## Key Points

- Use balance-delta accounting for source-side escrow transfers.
- Validate destination token code, registered peer, and expected origin token before minting.
- Refund only through authenticated bridge messages.
- Make refund paths available even while new deposits are paused.
- Include failed deployment and wrong-peer tests.

## Source Evidence

- Arbitrum token bridge escrow transfer paths release only from authenticated counterpart messages.
- L2 gateway finalization validates deployed tokens and `l1Address()` bindings.
- Gateway fallback handlers trigger refund withdrawals when token deployment or peer validation fails.

## Related Patterns

- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Balance Delta Transfer Accounting](../token-integration/pattern-balance-delta-transfer-accounting.md)
- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
