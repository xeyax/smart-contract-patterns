# Frame-Scoped Callback Capability

> Authorize a callback only for the current execution frame, then clear the capability as soon as it is consumed.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | callback, capability, transient-storage, approvals, merkle |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A protocol intentionally cedes control to an external callback during an operation
- The callback caller, selector, and allowed follow-up actions are known before the external call
- Temporary token approvals or callback side effects must be settled before the frame ends
- The environment supports reliable frame-local scratch state or an equivalent keyed context

## Avoid When

- The callback can be modeled as a normal pull claim or post-operation call
- The callback target, selector, or approval spender is not predictable
- Nested callbacks cannot be bounded by a shared reentrancy model
- The implementation cannot prove that transient context is cleared on all paths

## Trade-offs

**Pros:**
- Limits callback authority to one expected caller and selector
- Makes callback permissions auditable before execution
- Lets the protocol reject leftover approvals or unconsumed callback state

**Cons:**
- Complex frame accounting and nested-callback behavior
- Transient storage misuse can create hidden cross-operation coupling
- Requires strong tests around callback absence, wrong caller, and residual approvals

## How It Works

Before the external operation, encode the callback capability into frame-local state:

```solidity
function _allowCallback(bytes32 root, address caller, bytes4 selector) internal {
    callbackCaller = caller;
    callbackSelector = selector;
    callbackRoot = root;
}

fallback(bytes calldata data) external returns (bytes memory) {
    require(msg.sender == callbackCaller, "bad caller");
    require(msg.sig == callbackSelector, "bad selector");

    bytes32 root = callbackRoot;
    callbackCaller = address(0);
    callbackSelector = bytes4(0);
    callbackRoot = bytes32(0);

    return _runCallbackOperations(root, data);
}
```

The caller that expected the callback then checks that the capability was consumed and that no temporary approvals remain:

```solidity
_allowCallback(root, expectedCaller, expectedSelector);
_callExternalOperation();
require(callbackCaller == address(0), "callback missing");
_assertNoPendingApprovals();
```

## Implementation

### Key Points
- Bind the callback to expected caller, selector, and the permission root or operation id.
- Clear frame-local state when it is read, not at the end of an arbitrary outer function.
- Reject the operation if the expected callback is not received.
- Track approvals created inside normal operations and callback operations, then require them to be zero before returning.
- Use a reentrancy guard or shared frame model across every contract that reads the same callback context.
- Test wrong caller, wrong selector, missing callback, nested callback, approval persistence, and revert cleanup.

## Source Evidence

- Aera v3 stores expected callback caller, selector, callback data offset, and Merkle root in transient slots before an operation, validates them in `CallbackHandler.fallback`, clears them on read, and verifies callback approval cleanup in `/private/tmp/defillama-source/aera-finance__aera-contracts-public/v3/src/core/CallbackHandler.sol` and `BaseVault.sol`.

## Real-World Examples

- Aera v3 uses frame-scoped callback capabilities so guardian-submitted vault operations can receive flash-loan-style callbacks while remaining bound to the same Merkle permission root.

## Related Patterns

- [Selector-Scoped Authority](./pattern-selector-scoped-authority.md)
- [Verified Callback Settlement](../liquidity/pattern-verified-callback-settlement.md)
- [Shared Component Reentrancy Lock](./pattern-shared-component-reentrancy-lock.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
- [Unkeyed Transient Execution Context](../../ANTIPATTERNS.md#unkeyed-transient-execution-context)
- [Approval Persistence](../../ANTIPATTERNS.md#approval-persistence)
