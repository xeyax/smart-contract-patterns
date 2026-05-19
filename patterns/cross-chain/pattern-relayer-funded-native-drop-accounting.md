# Relayer-Funded Native Drop Accounting

> Separate bridge token redemption from destination native-token funding so users can receive gas while relayers recover bounded funding and fees.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, relayer, native-drop, accounting, refund |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A bridge transfer may need destination native gas for the recipient
- Relayers execute destination redemption and can front native value
- The message can encode relayer fee, native-drop amount, and final recipient
- The bridge can cap token-to-native conversion and refund excess native value

## Avoid When

- The relayer fee or native-drop amount is not bound into the bridged message
- The destination chain cannot distinguish self-redemption from relayer execution
- Native conversion rates, caps, or fee recipients can be changed without monitoring
- Users need authenticated reverse receipts for relayer rewards

## Trade-offs

**Pros:**
- Lets recipients receive destination gas without already owning native tokens
- Bounds relayer-funded native value and refunds overpayment
- Keeps self-redemption available without relayer fee extraction

**Cons:**
- Requires careful token/native accounting and rounding
- Implementations may differ on who receives relayer fees or residual value
- Native-drop funding is not the same as a proof of destination acknowledgement

## How It Works

The bridge payload commits to the relayer fee, requested native-drop amount, and
recipient. On completion, self-redemptions skip relayer accounting. Relayer
redemptions cap the native conversion, require enough `msg.value`, refund any
excess native value, pay the fee recipient, and transfer remaining bridge tokens
to the recipient:

```solidity
function complete(bytes calldata payload, address token, uint256 amount) external payable {
    DropMessage memory m = decodeDropMessage(payload);
    address recipient = _toAddress(m.recipient);

    if (msg.sender == recipient) {
        _transferToken(token, recipient, amount);
        return;
    }

    uint256 nativeInToken = min(m.nativeDropAmount, _maxNativeSwapIn(token));
    uint256 nativeOut = _quoteNativeOut(token, nativeInToken);
    require(msg.value >= nativeOut, "native underfunded");

    _refundNative(msg.sender, msg.value - nativeOut);
    _sendNative(recipient, nativeOut);
    _payRelayerFee(token, m.relayerFee + nativeInToken);
    _transferToken(token, recipient, amount - m.relayerFee - nativeInToken);
}
```

## Implementation

### Key Points

- Decode one typed payload that includes relayer fee, native-drop amount, and recipient.
- Reject malformed payload length or wrong payload id.
- Cap native-drop conversion by registered token or route limits.
- Refund relayer overpayment before or in the same frame as recipient payment.
- Keep self-redemption behavior explicit and test it separately from relayer execution.
- Document fee-recipient semantics; paying a protocol fee recipient differs from reimbursing the caller.

## Source Evidence

- Wormhole's example token bridge relayer encodes relayer fee, native-drop amount, and recipient in `/private/tmp/defillama-source/wormhole-foundation__example-token-bridge-relayer/evm/src/token-bridge-relayer/TokenBridgeRelayerMessages.sol:16`.
- Wormhole EVM relayer completion separates self-redemption from relayer execution in `/private/tmp/defillama-source/wormhole-foundation__example-token-bridge-relayer/evm/src/token-bridge-relayer/TokenBridgeRelayer.sol:324`.
- Wormhole EVM relayer completion caps native conversion, requires relayer-funded native value, refunds excess native value, pays a fee recipient, and transfers remaining tokens in `TokenBridgeRelayer.sol:359`.
- Wormhole EVM tests cover relayer/native accounting in `/private/tmp/defillama-source/wormhole-foundation__example-token-bridge-relayer/evm/forge-test/TokenBridgeRelayer.t.sol`.
- deBridge pays destination execution fee to the executor during auto-call settlement in `/private/tmp/defillama-source/debridge-finance__debridge-contracts-v1/contracts/transfers/DeBridgeGate.sol:897`.

## Real-World Examples

- Wormhole example token bridge relayer - destination redemptions can include native-token drops funded by the relayer.
- deBridge - auto-call settlement pays an execution fee to the destination executor.

## Related Patterns

- [Escrow Mint-Burn Refund Fallback](./pattern-escrow-mint-burn-refund-fallback.md)
- [Receipt-Acknowledged Relayer Rewards](./pattern-receipt-acknowledged-relayer-rewards.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Unchecked External Return](../../ANTIPATTERNS.md#unchecked-external-return)

## References

- See Source Evidence.
