# Diamond Selector Collision Risk

> Diamond and proxy upgrade systems can route a function selector to the wrong implementation when collision checks miss proxy, diamond, or facet selectors.

## Metadata

| Property | Value |
|----------|-------|
| Category | upgrades |
| Tags | upgrade, diamond, selector, proxy, risk |
| Type | Risk Description |

## Problem Description

Diamond proxies dispatch by the four-byte function selector. Upgrade code often checks for duplicate selectors between facets, but collisions can also happen with hardcoded proxy functions, diamond management functions, or inherited dispatch paths.

If selector ownership is ambiguous, an upgrade can shadow a critical function, make a function unreachable, or route calls to unintended logic.

## Applies When

- A proxy or diamond delegates unknown selectors to implementation or facets
- Facets can be added, replaced, or removed after deployment
- Collision checks only compare new selectors against facet selectors
- The proxy itself also exposes admin or upgrade functions

## Mitigations

- Build a complete selector manifest including proxy hardcoded functions, diamond functions, and every facet.
- Reject additions or replacements that collide outside the intended replace set.
- Test remove/replace behavior and fallback routing.
- Keep admin functions out of the user-facing selector namespace where possible.
- Include selector diffing in upgrade review and CI.

## Source Evidence

- Venus Diamond Comptroller audit material warns that selector clash checks must include Unitroller, Diamond hardcoded functions, and facets, not only facet-to-facet duplicates.

## Related Patterns

- [Selector-Scoped Authority](../access-control/pattern-selector-scoped-authority.md)
- [Bytecode-Split Extension Delegate](./pattern-bytecode-split-extension-delegate.md)
- [Storage Layout Drift](../../ANTIPATTERNS.md#storage-layout-drift)
