# Virtual Share Offset

> Add virtual assets and virtual shares to vault conversion math so first-depositor donations cannot round later depositors to zero shares.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, erc4626, shares, inflation, rounding, first-depositor |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Low |

## Use When

- Vault share minting uses `assets * totalSupply / totalAssets`
- `totalAssets()` can increase through direct token transfers or donations
- First deposit can be very small
- Deposits can be routed through arbitrary ERC-20 tokens or external strategies
- Need ERC4626-compatible inflation attack protection

## Avoid When

- Vault uses strictly internal accounting and rejects direct asset donations
- Minimum initial liquidity is seeded by a trusted deployer and enforced forever
- Shares are non-transferable accounting units with no external depositor surface
- The offset would materially distort expected share price UX for tiny vaults

## Trade-offs

**Pros:**
- Prevents the classic first-depositor inflation attack
- Preserves simple proportional share accounting
- Low gas overhead
- Compatible with ERC4626-style conversion functions

**Cons:**
- Share price has a small synthetic component at low TVL
- Requires careful documentation so integrations understand preview behavior
- Does not replace zero-share checks or actual-received asset accounting
- Offset size must be chosen for the asset/share precision domain

## How It Works

The vault behaves as if it always has a small amount of virtual liquidity:

```
shares = assets * (totalSupply + virtualShares) / (totalAssets + virtualAssets)
assets = shares * (totalAssets + virtualAssets) / (totalSupply + virtualShares)
```

If an attacker deposits 1 wei, receives 1 share, and then donates assets directly to the vault, the virtual shares dilute the attacker's ownership of the donated assets. Later depositors still receive non-zero shares because the denominator and numerator both include the offset.

### Credit-Offset Savings Variant

Some savings ledgers use an exchange-rate credit unit instead of ERC4626 shares. A small credit offset in the conversion math can avoid zero-credit or division-edge behavior:

```solidity
credits = underlying * WAD / exchangeRate + 1;
exchangeRate = totalCollateral * WAD / (totalCredits - 1);
```

The offset must be applied consistently in both directions and should not be described as withdrawable collateral.

## Implementation

```solidity
contract VirtualOffsetVault {
    uint256 internal constant VIRTUAL_ASSETS = 1;
    uint256 internal constant VIRTUAL_SHARES = 1e6;

    function previewDeposit(uint256 assets) public view returns (uint256 shares) {
        shares = assets * (totalSupply() + VIRTUAL_SHARES)
            / (totalAssets() + VIRTUAL_ASSETS);
    }

    function deposit(uint256 assets, address receiver) external returns (uint256 shares) {
        uint256 beforeBalance = _assetBalance();
        _pullAsset(msg.sender, assets);
        uint256 received = _assetBalance() - beforeBalance;

        shares = previewDeposit(received);
        require(shares > 0, "zero shares");

        _mint(receiver, shares);
    }

    function totalAssets() public view returns (uint256);
    function totalSupply() public view returns (uint256);
    function _assetBalance() internal view returns (uint256);
    function _pullAsset(address from, uint256 assets) internal;
    function _mint(address to, uint256 shares) internal;
}
```

### Key Points

- Apply the offset consistently in all preview and conversion functions.
- Still require `shares > 0` on minting paths.
- Measure actual received assets before conversion when supporting arbitrary ERC-20s.
- The virtual values are not withdrawable assets; they only affect conversion math.
- Use enough virtual shares to make donation attacks economically unattractive at expected deposit sizes.
- Virtual offsets can prevent profitable theft while still allowing loss-making donation grief if the offset is too small or zero-share mints are not rejected.
- Do not treat any nonzero offset as complete protection. The offset's strength
  depends on asset decimals, share decimals, expected first deposits, and whether
  direct donations can still distort previews or oracles.
- If direct asset transfers are later counted as rewards, seed initial liquidity atomically with deployment or enforce a minimum first deposit.
- For credit-offset savings ledgers, test tiny deposits, full withdrawals, exchange-rate refreshes, and the first/last credit edge cases.

## Source Evidence

- EigenLayer `StrategyBase` uses virtual `SHARES_OFFSET` and `BALANCE_OFFSET` in deposit conversion math and rejects zero-share mints.
- EigenLayer tests validate asset/share conversion integrity with non-zero total shares.
- Firelight and Reserve staking audit/test material show that insufficient offsets or missing zero-share checks can still allow donation-based griefing or dust-denial before a vault is seeded.
- MetaMorpho applies ERC4626 conversion offsets but warns that 18-decimal assets
  receive weak inflation protection from the chosen offset in `/private/tmp/defillama-source/morpho-org__metamorpho/src/MetaMorpho.sol:526`
  and `/private/tmp/defillama-source/morpho-org__metamorpho/src/MetaMorpho.sol:646`.
- mStable SavingsContract converts underlying to credits with a `+1` credit offset and computes exchange rates against `totalCredits - 1` in `/private/tmp/defillama-source/mstable__mStable-contracts/contracts/savings/SavingsContract.sol`.

## Real-World Examples

- [OpenZeppelin ERC4626](https://docs.openzeppelin.com/contracts/4.x/erc4626) — describes virtual offset defense for ERC4626 inflation attacks.
- [EigenLayer StrategyBase](https://github.com/Layr-Labs/eigenlayer-contracts) — strategy share math uses virtual shares/assets offsets.

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base share accounting pattern this hardens
- [Share-Denominated Lending Accounting](../lending/pattern-share-denominated-lending-accounting.md) — lending-market variant of share conversion math
- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — separate NAV pricing risk
- [Async Deposit/Withdrawal](./pattern-async-deposit.md) — timing mitigation, not a replacement for offset math

## References

- [OpenZeppelin ERC4626 Security](https://docs.openzeppelin.com/contracts/4.x/erc4626)
- [EIP-4626: Tokenized Vault Standard](https://eips.ethereum.org/EIPS/eip-4626)
