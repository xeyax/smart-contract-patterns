# Vault Wrapper (Meta-Vault)

> Thin ERC4626 vault that wraps a base strategy vault, adding fee/access layers without duplicating strategy logic.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | ERC4626, composability, fees, referral, whitelabel |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- Multiple fee tiers needed over a single strategy (e.g. 0%, 10%, 15%)
- Referral/whitelabel programs where each partner gets a branded vault with custom fee split
- Fee accounting should be independent from strategy logic (separation of concerns)
- Operational cost matters — one keeper, one Morpho position, one set of alerts for all vaults

## Avoid When

- Wrapper needs its own strategy logic (use a standalone vault instead)
- Single fee tier is sufficient (add fee directly to base vault)
- Every deposit/redeem gas cost is critical (wrapper adds ~50K gas for extra ERC4626 hop)
- Base vault doesn't support `redeem()` or has non-standard ERC4626 interface

## Trade-offs

**Pros:**
- One strategy position shared by all wrappers — single keeper, single rebalance, single liquidation monitor
- Clean separation: base vault = strategy, wrapper = fee policy
- Trivial to deploy new fee tiers (especially with [Clone Factory](./pattern-clone-factory.md))
- Each wrapper is an independent ERC20 — separate token, separate holder registry, separate integrations

**Cons:**
- Extra gas per deposit/redeem (~50K for second ERC4626 hop)
- [Composability risks](./risk-vault-composability.md) — double rounding, pause propagation, capacity sharing
- `previewDeposit` precision: wrapper estimate may diverge from actual due to base vault rounding
- Base vault upgrade can silently break wrappers

## How It Works

### Architecture

```
User A (no fee)                 User B (10% fee)              User C (15% fee)
    │                               │                              │
    │                        ┌──────┴───────┐              ┌───────┴──────┐
    │                        │ Wrapper B    │              │ Wrapper C    │
    │                        │ fee: 1000bps │              │ fee: 1500bps │
    │                        │ recv: 0xBBB  │              │ recv: 0xCCC  │
    │                        └──────┬───────┘              └───────┬──────┘
    │                               │                              │
    └───────────────┬───────────────┴──────────────────────────────┘
                    ▼
           ┌────────────────┐
           │   Base Vault   │
           │   (fee = 0)    │
           │   ERC4626      │
           └───────┬────────┘
                   ▼
              Strategy (Morpho, Aave, etc.)
```

### Deposit Flow

1. User sends USDT to wrapper
2. Wrapper accrues pending performance fee (critical — must happen before share calculation)
3. Wrapper approves base vault for USDT amount
4. Wrapper calls `baseVault.deposit(assets, address(this))` — receives base shares
5. Wrapper mints its own shares proportional to value added

### Redeem Flow

1. User burns wrapper shares
2. Wrapper accrues pending performance fee
3. Wrapper calculates how many base shares correspond to burned wrapper shares
4. Wrapper calls `baseVault.redeem(baseShares, receiver, address(this))` — user receives USDT

### Total Assets

Wrapper's total assets = value of all base shares it holds:

```
totalAssets = baseVault.convertToAssets(baseVault.balanceOf(address(this)))
```

### Fee Accounting

Wrapper tracks HWM (high-water mark) of base vault's price-per-share. When base PPS grows above HWM, wrapper mints fee shares to `feeRecipient`:

```
basePPS = baseVault.convertToAssets(1e18)

if basePPS > highWaterMark:
    profit = basePPS - highWaterMark
    feePerShare = profit * feeBps / BPS
    feeShares = supply * feePerShare / (basePPS - feePerShare)
    mint(feeRecipient, feeShares)
    highWaterMark = basePPS_after_dilution
```

See [High-Water Mark Performance Fee](./pattern-high-water-mark-fee.md) for derivation and edge cases.

### Fee Split (Variation)

For referral programs, fee can be split between protocol and referrer:

```
protocolShares = feeShares * protocolSplitBps / BPS
referrerShares = feeShares - protocolShares
```

## Implementation

```solidity
contract FeeWrapperVault is ERC4626, Initializable {
    IERC4626 public baseVault;
    uint256 public performanceFeeBps;
    uint256 public highWaterMark;
    address public feeRecipient;
    uint256 public protocolSplitBps;
    address public protocolFeeRecipient;

    uint256 private constant BPS = 10000;
    uint256 private constant WAD = 1e18;

    function initialize(
        address _baseVault,
        address _asset,
        address _feeRecipient,
        uint256 _feeBps,
        string calldata _name,
        string calldata _symbol
    ) external initializer {
        baseVault = IERC4626(_baseVault);
        feeRecipient = _feeRecipient;
        performanceFeeBps = _feeBps;
        highWaterMark = baseVault.convertToAssets(WAD);
        // ERC4626 + ERC20 init with _asset, _name, _symbol
    }

    function totalAssets() public view override returns (uint256) {
        return baseVault.convertToAssets(baseVault.balanceOf(address(this)));
    }

    function _deposit(address caller, address receiver, uint256 assets, uint256 shares)
        internal override
    {
        _accruePerformanceFee();

        IERC20(asset()).safeTransferFrom(caller, address(this), assets);
        IERC20(asset()).approve(address(baseVault), assets);
        baseVault.deposit(assets, address(this));

        _mint(receiver, shares);
    }

    function _withdraw(address caller, address receiver, address owner,
                       uint256 assets, uint256 shares) internal override
    {
        _accruePerformanceFee();
        _burn(owner, shares);

        // Use redeem, not withdraw — base vault may not support withdraw()
        uint256 baseSharesNeeded = baseVault.convertToShares(assets);
        baseVault.redeem(baseSharesNeeded, receiver, address(this));
    }

    function _accruePerformanceFee() internal {
        uint256 basePPS = baseVault.convertToAssets(WAD);
        if (basePPS <= highWaterMark) return;

        uint256 profit = basePPS - highWaterMark;
        uint256 feePerShare = profit * performanceFeeBps / BPS;
        uint256 supply = totalSupply();
        if (supply == 0) {
            highWaterMark = basePPS;
            return;
        }

        uint256 feeShares = supply * feePerShare / (basePPS - feePerShare);
        _mint(feeRecipient, feeShares);

        // HWM = post-fee PPS to avoid dead zone
        highWaterMark = baseVault.convertToAssets(
            baseVault.balanceOf(address(this))
        ) * WAD / (supply + feeShares);
    }
}
```

### Key Points

- **Fee accrual ordering is critical.** `_accruePerformanceFee()` MUST execute before `_mint`/`_burn` in every deposit/redeem. Without this, new deposits dilute pending fees, and early redeems avoid fee payment.
- **Use `redeem()`, not `withdraw()`.** Some base vaults (e.g. vaults supporting only `redeem` and `deposit`) don't implement `withdraw()`. Always convert to base shares via `convertToShares(assets)` and call `redeem()`.
- **Delegate `maxDeposit` to base vault.** Wrapper's capacity is bounded by base vault's remaining capacity: `maxDeposit = baseVault.maxDeposit(address(this))`. If base vault is paused or full, wrapper returns 0.
- **Base vault must whitelist wrapper.** If base vault has access control, each wrapper address needs to be whitelisted. Automate this via [Clone Factory](./pattern-clone-factory.md).
- **`previewDeposit` may diverge.** Wrapper's preview depends on `baseVault.previewDeposit()`, which ERC4626 spec allows to differ from actual `deposit()`. Wrapper should not guarantee exact preview match — use it as estimate.

## Security Considerations

- **Double rounding:** Both base vault and wrapper round in vault's favor. Cumulative error is ~2 wei per operation — negligible for normal amounts, but set a minimum deposit threshold to prevent dust griefing.
- **Pause propagation:** When base vault is paused, wrapper cannot deposit or redeem. Wrapper should expose `maxDeposit() == 0` in this case, not revert with a confusing error.
- **Base vault upgrade:** If base vault is UUPS-upgradeable and changes behavior (e.g. different rounding, new fees, changed `convertToAssets`), wrapper continues operating on new logic without any update. This can silently change wrapper's economics. Monitor base vault upgrades.

See [Vault Composability Risk](./risk-vault-composability.md) for comprehensive risk analysis.

## Real-World Examples

- [Yearn V3 Vaults](https://github.com/yearn/yearn-vaults-v3) — "Allocator" vaults deposit into underlying strategy vaults, adding management/performance fees on top
- [ERC-4626 Alliance](https://erc4626.info/) — composability catalog showing multi-layer vault deployments
- [Morpho MetaMorpho](https://github.com/morpho-org/metamorpho) — meta-vault allocating across multiple Morpho Blue markets

## Related Patterns

- [High-Water Mark Performance Fee](./pattern-high-water-mark-fee.md) — fee accounting logic reused in wrapper
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base vault's share calculation that wrapper delegates to
- [Clone Factory](./pattern-clone-factory.md) — mass deployment of parameterized wrappers
- [Vault Composability Risk](./risk-vault-composability.md) — risks introduced by layered composition

## References

- [ERC-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626) — standard vault interface enabling composability
- [EIP-1167: Minimal Proxy Contract](https://eips.ethereum.org/EIPS/eip-1167) — cheap clone deployment for wrapper variants
- [OpenZeppelin ERC4626](https://docs.openzeppelin.com/contracts/5.x/api/token/erc20#ERC4626) — reference implementation
