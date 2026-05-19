# Bridge Exit Cutover Custody Drain

> Bridge migration can strand valid exits if custody or mint authority moves before old source messages are fully bounded.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, migration, cutover, custody, exits |
| Type | Risk |
| Severity | High |

## Applies When

- A bridge disables old exits during migration
- Predicate or gateway custody can be moved to a new bridge
- Source-chain messages remain provable after the cutover
- Admins can execute arbitrary token migration calldata

## Impact

Users with valid burns, withdrawals, or messages may be unable to exit because the old bridge no longer holds custody or mint authority. The new bridge may not recognize the old proof format or source boundary, leaving value stranded even though the original source event was valid.

## Mitigations

- Publish a final accepted source block or message boundary before cutover.
- Keep old exit finalization funded until every valid old exit is processed, expired by rule, or migrated into a new claim path.
- Prove migrated custody is surplus above pending exits.
- Restrict migration calldata and token targets.
- Test old-exit, new-exit, duplicate-exit, and custody-drain scenarios.
- Keep historical withdrawal bridge mappings after disabling new deposits so old assets still have an authenticated exit route.

## Source Evidence

- Polygon PoS portal has explicit token migration status gates and predicate custody migration paths.
- Polygon withdraw tests cover old-exit behavior around migration cutover.
- ERC20 predicate migration can execute token-specific calldata, demonstrating why migration targets and amounts need tight review.
- StarkGate's registry model shows why deposit deactivation and historical withdrawal routing should be separate states.

## Related Patterns

- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
- [Proof Bridge Exit Safety Requirements](./req-proof-bridge-exit-safety.md)
- [Predicate-Mediated Bridge Custody](./pattern-predicate-mediated-bridge-custody.md)
