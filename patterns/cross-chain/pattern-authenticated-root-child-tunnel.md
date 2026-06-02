# Authenticated Root-Child Tunnel

> Pair root and child tunnel contracts so each side accepts messages only from the canonical bridge and configured peer tunnel.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, tunnel, root-child, state-sync, peer-authentication |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- A protocol exposes generic cross-chain message tunnels instead of one fixed bridge action
- One side sends through a canonical state sender or messenger
- The other side receives bridge callbacks from a privileged system address
- Application messages need peer binding in addition to bridge authentication

## Avoid When

- The bridge does not authenticate source chain and sender
- Any contract on the remote chain is allowed to emit messages
- The tunnel handles only governance actions that already use a timelock receiver

## Trade-offs

**Pros:**
- Makes the bridge trust boundary explicit at the tunnel boundary
- Reuses the same peer checks for many application message types
- Reduces per-feature cross-chain authentication mistakes

**Cons:**
- A tunnel bug affects all messages routed through it
- Peer replacement is a high-impact governance action
- Generic payloads still need application-level decoding and authorization

## How It Works

The root side sends through the canonical bridge and records the expected child tunnel. The child side accepts only the canonical state receiver or messenger and checks the root sender supplied by that bridge context.

For exits back to root, the root tunnel verifies a proven message log from the configured child tunnel before decoding the payload.

## Key Points

- Configure peers on both sides and reject zero or unknown peers.
- Authenticate bridge caller, remote sender, and event signature or message selector.
- Keep payload decoding separate from peer authentication.
- If the tunnel dispatches payloads with `address(this).call(data)`, every externally callable target selector must be self-only, selector-bounded, or independently authorized.
- Test replay, wrong peer, wrong bridge caller, and malformed payload cases.
- Treat tunnel upgrades as cross-chain security changes, not ordinary parameter changes.

## Source Evidence

- Polygon PoS `BaseChildTunnel.onStateReceive` accepts only the state-sync path and configured root sender.
- `BaseRootTunnel._validateAndExtractMessage` validates proven child-tunnel logs before returning the payload.
- Tunnel tests cover replay and wrong-message behavior.
- Rocket Pool's Polygon oracle uses a self-dispatched child payload, which makes target selector authorization part of the tunnel safety boundary.

## Related Patterns

- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Bridged Governance Timelock Receiver](./pattern-bridged-governance-timelock-receiver.md)
- [Bridge Endpoint Authentication Mismatch](../../ANTIPATTERNS.md#bridge-endpoint-authentication-mismatch)
