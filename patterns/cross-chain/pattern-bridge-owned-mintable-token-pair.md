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

The bridged token stores immutable bridge and remote-token addresses, or stores
only bridge authority while the bridge registry owns the remote-token mapping:

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
- If the token stores only bridge authority, keep origin identity in bridge mappings and deterministic deployment salts, and validate that mapping before mint or burn.
- Support an interface marker so the bridge can reject arbitrary ERC20s pretending to be mintable bridge tokens.
- Keep token factory deployment deterministic where users need predictable addresses.
- Treat bridge upgrades as mint-authority migrations that must preserve pending exits.
- During bridge migration, activate new minter and burner roles only after reserve backing, peer configuration, and pending-exit boundaries are reconciled.

## Source Evidence

- Optimism's mintable ERC20 stores immutable bridge and remote token fields, restricts mint and burn to the bridge, and the standard bridge checks the local token's remote-pair identity before finalizing.
- Polygon zkEVM/Agglayer wrapped tokens store bridge authority while the bridge keeps origin token identity in mappings and deterministic deployment salts in `/private/tmp/defillama-source/0xPolygonHermez__zkevm-contracts/contracts/AgglayerBridge.sol` and `contracts/lib/TokenWrappedBridgeUpgradeable.sol`.
- USDT0 audit reports provide lower-confidence audit-source support for treating child-token minter/burner changes and bridge migrations as reserve-backing events, not only role-management events.

## Related Patterns

- [Canonical Bridge Counterpart Validation](./pattern-canonical-bridge-counterpart-validation.md)
- [Token-Owned Bridge Registration](./pattern-token-owned-bridge-registration.md)
- [Bridge Exit Liveness Requirements](./req-bridge-exit-liveness.md)
