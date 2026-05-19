# Typed Cross-Chain Executor Options

> Bind destination execution gas, value, ordering, and compose requirements into typed options that the route can enforce before fee quoting or delivery.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, executor, gas, options, compose |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Destination messages can need different gas or native-value budgets by message type
- Applications want a minimum execution envelope while callers can add more budget
- Executors price and validate typed options before delivery
- Compose or native-drop behavior must be constrained by protocol caps

## Avoid When

- Different parsers will interpret the same option bytes differently
- The executor cannot reject unsupported option types or over-cap native value
- Application safety depends on off-chain duplicate-option handling that is not monitored
- Failed execution should refund value rather than retry delivery

## Trade-offs

**Pros:**
- Prevents underfunded messages from entering routes that require minimum gas
- Lets applications enforce different options for different message types
- Makes native-drop and compose value caps explicit

**Cons:**
- Option bytes become part of the security boundary
- Duplicate option handling may be off-chain or executor-specific
- Overly strict options can make otherwise valid messages undeliverable

## How It Works

An application stores enforced options keyed by destination endpoint and message
type. Caller-supplied options are accepted only in the typed format that can be
combined with the enforced options:

```solidity
function combineOptions(uint32 dstDomain, uint16 messageType, bytes calldata callerOptions)
    public
    view
    returns (bytes memory)
{
    bytes memory enforced = enforcedOptions[dstDomain][messageType];
    if (enforced.length == 0) return callerOptions;
    if (callerOptions.length == 0) return enforced;

    require(_optionType(callerOptions) == TYPE_COMBINABLE, "bad option type");
    return bytes.concat(enforced, callerOptions[TYPE_PREFIX_BYTES:]);
}
```

The executor parser rejects unsupported option types, zero receive gas, zero read
calldata where required, and native value above the route cap.

## Implementation

```solidity
function _parseAndCheck(bytes calldata options, uint256 nativeCap) internal pure returns (ExecutionBudget memory b) {
    while (!_done(options)) {
        (uint8 optionType, bytes calldata option) = _next(options);
        if (optionType == LZ_RECEIVE) b.receiveGas += _decodeReceiveGas(option);
        else if (optionType == NATIVE_DROP) b.nativeValue += _decodeNativeDrop(option);
        else if (optionType == COMPOSE) b.composeGas += _decodeComposeGas(option);
        else revert("unsupported option");
    }

    require(b.receiveGas > 0, "zero receive gas");
    require(b.nativeValue <= nativeCap, "native cap");
}
```

### Key Points

- Key enforced options by destination route and message type.
- Use one canonical parser or bind exact option bytes into authorization.
- Reject unsupported option types instead of ignoring them.
- Cap native-drop value and require nonzero receive gas for deliverable messages.
- Test duplicate options, unsupported types, zero gas, read-message calldata size, over-cap native value, and caller/enforced option composition.

## Source Evidence

- LayerZero V2 OApps store enforced options per endpoint and message type in `/private/tmp/defillama-source/LayerZero-Labs__LayerZero-v2/packages/layerzero-v2/evm/oapp/contracts/oapp/libs/OAppOptionsType3.sol:16`.
- LayerZero V2 combines enforced and caller-supplied type-3 options, while comments note duplicate handling is off-chain, in `OAppOptionsType3.sol:51`.
- LayerZero V2 executor fee parsing rejects unsupported options, zero receive gas, zero read calldata size, and native value above cap in `/private/tmp/defillama-source/LayerZero-Labs__LayerZero-v2/packages/layerzero-v2/evm/messagelib/contracts/ExecutorFeeLib.sol:139`.
- LayerZero V2 tests cover native-drop caps and fee composition in `/private/tmp/defillama-source/LayerZero-Labs__LayerZero-v2/packages/layerzero-v2/evm/messagelib/test/ExecutorFeeLib.t.sol`.

## Real-World Examples

- LayerZero V2 - OApps can enforce type-3 execution options while executors parse and cap delivery budgets.

## Related Patterns

- [Retryable Cross-Domain Message Ledger](./pattern-retryable-cross-domain-message-ledger.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Divergent Message Parsing Between Authorization And Execution](../../ANTIPATTERNS.md#divergent-message-parsing-between-authorization-and-execution)

## References

- See Source Evidence.
