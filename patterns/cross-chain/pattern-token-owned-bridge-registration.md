# Token-Owned Bridge Registration

> Let token contracts opt into bridge mappings while preventing unauthorized peer remapping after registration.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, token-registration, mapping, gateway, opt-in |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Tokens choose custom bridge gateways or remote token implementations
- Registration must be mirrored across bridge domains
- A default gateway exists but custom mappings need explicit token opt-in
- Unauthorized remapping would redirect deposits or mint rights

## Avoid When

- Token mappings are purely governance-curated and tokens do not opt in
- The bridge cannot authenticate registration messages on the remote domain
- Token peers may need frequent mutable remapping without a migration plan

## Trade-offs

**Pros:**
- Prevents third parties from registering a token to a hostile peer
- Keeps custom bridge behavior under token-owner control
- Makes irreversible or sticky mappings easier to reason about

**Cons:**
- Token contracts need registration hooks or owner-driven helpers
- Owner override paths remain trusted and must be documented
- Mistaken first registration can be hard to correct safely

## How It Works

The bridge accepts custom registration only when the token initiates or explicitly proves opt-in:

```solidity
function registerToken(address l1Token, address l2Token) external {
    require(msg.sender == l1Token || _authorizedOwner(l1Token, msg.sender), "not token");
    require(_tokenOptedIn(l1Token), "not enabled");
    require(existingPeer[l1Token] == address(0), "already mapped");

    existingPeer[l1Token] = l2Token;
    _sendRegistrationToRemote(l1Token, l2Token);
}
```

Remote registry updates are accepted only from the authenticated bridge counterpart.

## Key Points

- Bind registration to token, gateway, remote peer, and source domain.
- Prevent changing non-default mappings without an explicit migration flow.
- Reject zero peers and non-contract gateway addresses where possible.
- Distinguish token-owned registration from trusted owner bulk registration.
- Test wrong caller, wrong peer, remapping, and unauthenticated remote registration.
- Separate the active deposit bridge from historical withdrawal bridges so deactivation can stop new deposits without erasing withdrawal routes for previously bridged assets.

## Source Evidence

- Arbitrum custom gateway registration requires token opt-in and prevents changing an already registered L2 token.
- Gateway router registration validates gateway contracts and token opt-in before setting custom routes.
- L2 gateway/router registry updates are accepted only from authenticated L1 counterpart messages.
- StarkGate registry and manager flows distinguish active deposit bridges from historical withdrawal bridges so tokens can be deactivated for new deposits while preserving old withdrawal routes.

## Related Patterns

- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Predicate-Mediated Bridge Custody](./pattern-predicate-mediated-bridge-custody.md)
- [Selector-Scoped Authority](../access-control/pattern-selector-scoped-authority.md)
