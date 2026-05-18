# Bridge-Owned Mintable Token Pair

> Represent bridged assets with mintable tokens whose bridge and remote-token identity are immutable and checked on every mint or burn path.

## Metadata

| Property | Value |
|----------|-------|
| Category | cross-chain |
| Tags | bridge, token, mint, burn, remote-token |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- A canonical bridge mints a destination representation of a remote token
- The local representation should be controlled only by the bridge
- The bridge can validate the local token's declared remote token before minting or burning
- Users need deterministic token identity across domains

## Avoid When

- Tokens must register multiple independent bridges
- Mint authority can be transferred without bridge migration controls
- The local token cannot expose a reliable remote-token interface

## How It Works

The bridged token stores immutable bridge and remote-token addresses:

```solidity
contract BridgeMintableToken {
    address public immutable bridge;
    address public immutable remoteToken;

    function mint(address to, uint256 amount) external {
        require(msg.sender == bridge, "only bridge");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == bridge, "only bridge");
        _burn(from, amount);
    }
}
```

The bridge validates both local token class and remote-token pairing before changing supply.

## Key Points

- Make bridge and remote-token identity immutable or migration-gated.
- Check the declared remote token before every bridge mint or burn.
- Support an interface marker so the bridge can reject arbitrary ERC20s pretending to be mintable bridge tokens.
- Keep token factory deployment deterministic where users need predictable addresses.
- Treat bridge upgrades as mint-authority migrations that must preserve pending exits.

## Source Evidence

- Optimism's mintable ERC20 stores immutable bridge and remote token fields, restricts mint and burn to the bridge, and the standard bridge checks the local token's remote-pair identity before finalizing.

## Related Patterns

- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Token-Owned Bridge Registration](./pattern-token-owned-bridge-registration.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
