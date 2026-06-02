# Shared Component Reentrancy Lock

> Put related protocol components behind one shared reentrancy status so callbacks cannot bypass a per-contract lock by entering a sibling component.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, reentrancy, components, callbacks, protocol-kernel |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Several components share accounting assumptions or token custody
- External callbacks can enter more than one component
- Per-contract `nonReentrant` locks leave sibling entrypoints open
- A central component registry or kernel can own the lock state

## Avoid When

- Components are truly independent and should not block each other
- The shared lock would create unacceptable liveness coupling
- Read-only calls must remain available during locked execution and cannot be separated

## Trade-offs

**Pros:**
- Blocks cross-component reentrancy through sibling contracts
- Makes the protocol's execution frame explicit
- Reduces callback reasoning surface for shared ledgers

**Cons:**
- One component can temporarily block value-changing actions in others
- Lock misuse can deadlock internal calls
- Requires clear rules for which calls are protected

## How It Works

Store the reentrancy status in a shared kernel or main contract:

```solidity
modifier globalNonReentrant() {
    main.beginTx();
    _;
    main.endTx();
}

function beginTx() external onlyComponent {
    require(status == NOT_ENTERED, "reentrant");
    status = ENTERED;
}

function endTx() external onlyComponent {
    status = NOT_ENTERED;
}
```

All value-changing component entrypoints that share invariants use the global lock.

## Implementation

```solidity
contract Component {
    Main public immutable main;

    modifier globalNonReentrant() {
        main.beginTx();
        _;
        main.endTx();
    }
}
```

### Key Points

- Define the component set authorized to acquire and release the lock.
- Protect every entrypoint that can mutate shared accounting or custody.
- Keep view functions separate and side-effect free.
- Test callbacks that try to enter sibling components, not only the same contract.

## Source Evidence

- Reserve Protocol components use `GlobalReentrancyGuard`, `Component.globalNonReentrant`, and `Main.beginTx/endTx` to share one reentrancy state across core components in `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/p1`.
- Reserve revenue and Dutch-trade tests include cross-component reentrancy checks in `/private/tmp/defillama-source/reserve-protocol__protocol/test/Revenues.test.ts`.

## Real-World Examples

- Reserve Protocol - core components share a protocol-level reentrancy guard through `Main`.

## Related Patterns

- [Adapter-Isolated Core Ledger](../token-integration/pattern-adapter-isolated-core-ledger.md)
- [Hook/Callback Trust](../../ANTIPATTERNS.md#hookcallback-trust)
- [Unkeyed Transient Execution Context](../../ANTIPATTERNS.md#unkeyed-transient-execution-context)

## References

- See Source Evidence.
