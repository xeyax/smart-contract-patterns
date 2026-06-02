# Module-Owned Portfolio Position Ledger

> Store portfolio-token component positions as module-owned default and external units so integrations can mutate positions without bypassing the core ledger.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, portfolio, module, ledger, index, external-position |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A tokenized portfolio holds many component assets and integrations
- Modules need to create, remove, or mutate component positions
- Positions may include default holdings plus external debt, staking, lending, or derivative state
- Fees or rebases should adjust all component units through a shared multiplier

## Avoid When

- A single vault strategy can own all accounting internally
- Modules would have broad arbitrary-call authority without target or selector constraints
- External positions cannot be valued, unwound, or excluded from issuance safely
- Component arrays can grow without bounds or cleanup paths

## Trade-offs

**Pros:**
- Keeps one canonical position ledger for issuance, redemption, and valuation
- Lets specialized modules manage integrations without owning the core token
- Supports portfolio-wide unit changes through a position multiplier

**Cons:**
- Module privileges become the main trust boundary
- External position data can be hard for integrators to interpret
- Position mutations must stay synchronized with actual component balances

## How It Works

The portfolio token stores component positions as virtual units. A component can have a default position and module-owned external positions:

```solidity
struct ComponentPosition {
    int256 virtualUnit;
    address[] externalModules;
    mapping(address => ExternalPosition) externalPositions;
}
```

Only initialized modules can add or remove components, edit default units, add external position modules, edit external position units or data, mint or burn shares, and invoke component integrations:

```solidity
function editDefaultPositionUnit(address component, int256 realUnit) external onlyModule {
    positions[component].virtualUnit = _toVirtual(realUnit, positionMultiplier);
}
```

The position multiplier converts between real units and virtual units so a fee module can update all positions without rewriting every component.

## Key Points

- Treat modules as privileged writers to the portfolio ledger.
- Separate default positions from external positions and expose both to valuation and issuance code.
- Convert real units to virtual units consistently through the position multiplier.
- Lock the token during multi-step module operations so another module cannot interleave state changes.
- Exclude airdrops, external positions, or unmanaged balances from issuance unless a module explicitly imports them.
- Test module initialization state, lock ownership, component removal, external position cleanup, and multiplier changes.

## Source Evidence

- Set Protocol V2 stores default and external component positions, virtual units, modules, locks, and a position multiplier in `/private/tmp/defillama-source/SetProtocol__set-protocol-v2/contracts/protocol/SetToken.sol`.
- Set Protocol position helper logic manages default/external position arrays and unit edits in `/private/tmp/defillama-source/SetProtocol__set-protocol-v2/contracts/protocol/lib/Position.sol`.

## Real-World Examples

- Set Protocol V2 - SetToken modules own portfolio position mutations while the token stores the canonical component ledger.

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md)
- [Selector-Scoped Authority](../access-control/pattern-selector-scoped-authority.md)
- [Adapter-Routed Index Rebalance](./pattern-adapter-routed-index-rebalance.md)
