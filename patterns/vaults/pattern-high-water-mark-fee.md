# High-Water Mark Performance Fee

> Charge performance fee only on new profit above the previous peak, paid via share dilution.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, fee, performance-fee, high-water-mark, shares, erc4626 |
| Complexity | Medium |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- Vault generates yield and protocol needs to capture a share of profits
- Fee should be fair: only on actual gains, never on recovery from losses
- Vault uses share-based accounting (ERC4626 or similar)
- Need gas-efficient fee without asset transfers

## Avoid When

- Fee must be based on AUM (use management fee instead)
- Vault has no yield (fee would never accrue)
- Share price is manipulable via direct token transfers (fee could be gamed)
- Need fee denominated in specific asset, not vault shares

## Trade-offs

**Pros:**
- Fair: no double-charging after drawdowns
- Gas efficient: no asset transfers, just a mint
- No liquidity required: fee paid in shares, not assets
- Composable with deposit/redeem flow (accrue inline)

**Cons:**
- Fee recipient receives illiquid vault shares (must redeem to realize)
- High-water mark never resets: prolonged drawdown means no fees even on partial recovery
- Share dilution slightly lowers PPS for all holders (by design)
- First-deposit HWM initialization must be chosen carefully

## How It Works

### Core Idea

Track the post-fee PPS after each fee accrual. When current PPS exceeds this mark, the difference is "new profit". Protocol takes a percentage of that profit by minting new shares to a fee recipient.

```
PPS timeline (20% fee):

  1.00 ──── initial HWM
  1.10 ──── fee on 1.00→1.10 → new HWM = 1.08 (post-fee PPS)
  1.03 ──── drawdown: no fee
  1.08 ──── recovery to HWM: no fee
  1.12 ──── fee on 1.08→1.12 → new HWM = 1.112
```

Fee is only charged on growth above the post-fee HWM. Recovery from drawdowns is not taxed.

### Fee Collection: Share Dilution vs Asset Transfer

Two approaches: (a) transfer assets to fee recipient — simple, but requires liquid assets and changes NAV; (b) mint new shares to fee recipient (this pattern) — NAV unchanged, each existing share represents a slightly smaller fraction. Dilution is preferred: no liquidity requirement, atomic, no NAV discontinuity.

### Accrual Timing

Fee must be accrued **before every deposit and redeem**:

- **Before deposit:** if yield accrued since last check, fee must be minted first. Otherwise the new depositor dilutes pending fees (protocol loses revenue).
- **Before redeem:** if yield accrued, fee must be minted first. Otherwise the redeemer exits without paying their share of the fee.

Additionally, a periodic heartbeat (keeper call) ensures fees are accrued even when there are no deposits/redeems.

### The Math

Given:
- `nav` — total vault assets
- `supply` — total shares before fee mint
- `currentPPS = nav / supply`
- `hwm` — high-water mark (previous peak PPS)
- `feeBps` — fee in basis points (e.g., 2000 = 20%)

```
if currentPPS <= hwm: no fee (skip)

profitPerShare = currentPPS - hwm
feePerShare    = profitPerShare * feeBps / 10000
feeShares      = supply * feePerShare / (currentPPS - feePerShare)

mint(feeRecipient, feeShares)
hwm = nav / (supply + feeShares)          // post-fee PPS
```

**Formula derivation.** We need: after minting `feeShares`, the fee recipient owns exactly `feePerShare / currentPPS` of the vault.

```
feeShares / (supply + feeShares) = feePerShare / currentPPS

Solving:
feeShares * currentPPS = supply * feePerShare + feeShares * feePerShare
feeShares * (currentPPS - feePerShare) = supply * feePerShare
feeShares = supply * feePerShare / (currentPPS - feePerShare)
```

PPS after mint = `currentPPS - feePerShare` for existing holders. The "missing" value went to fee recipient's new shares.

### Example

1. Vault has 1000 shares, NAV = 1100 (PPS = 1.10), HWM = 1.00, fee = 20%
2. `profitPerShare = 1.10 - 1.00 = 0.10`
3. `feePerShare = 0.10 * 20% = 0.02`
4. `feeShares = 1000 * 0.02 / (1.10 - 0.02) = 20 / 1.08 ≈ 18.52`
5. After mint: 1018.52 shares, NAV still 1100, PPS = 1.08
6. Fee recipient owns 18.52 shares worth ~20 in assets (20% of profit)
7. HWM updated to 1.08 (post-fee PPS, not 1.10)

## Implementation

```solidity
abstract contract HighWaterMarkFee {
    uint256 public highWaterMark;
    uint256 public performanceFeeBps;
    address public feeRecipient;

    uint256 private constant MAX_BPS = 10000;
    uint256 private constant WAD = 1e18;

    function _accruePerformanceFee() internal returns (uint256 nav, uint256 supply) {
        supply = _totalSupply();
        nav = _totalAssets();

        if (performanceFeeBps == 0 || supply == 0) return (nav, supply);

        uint256 currentPPS = (nav * WAD) / supply;
        if (currentPPS <= highWaterMark) return (nav, supply);

        uint256 profitPerShare = currentPPS - highWaterMark;
        uint256 feePerShare = (profitPerShare * performanceFeeBps) / MAX_BPS;
        uint256 feeShares = (supply * feePerShare) / (currentPPS - feePerShare);

        if (feeShares > 0) {
            _mintShares(feeRecipient, feeShares);
            supply += feeShares;
            highWaterMark = (nav * WAD) / supply; // post-fee PPS
        }

        return (nav, supply);
    }

    // --- Integration points ---

    // Call _accruePerformanceFee() BEFORE deposit and redeem:
    //
    //   function deposit(uint256 assets) external {
    //       (uint256 nav, uint256 supply) = _accruePerformanceFee();
    //       // ... mint shares using post-fee nav and supply ...
    //   }
    //
    //   function redeem(uint256 shares) external {
    //       _accruePerformanceFee();
    //       // ... burn shares and transfer assets ...
    //   }

    // --- Abstract functions ---

    function _totalSupply() internal view virtual returns (uint256);
    function _totalAssets() internal view virtual returns (uint256);
    function _mintShares(address to, uint256 amount) internal virtual;
}
```

### Key Points

- **HWM initialization:** set to `1e18` (1:1 PPS) at vault deployment. If set to 0, the first yield accrual mints an outsized fee.
- **Rounding:** `feeShares` rounds down naturally (Solidity integer division), which favors depositors over fee recipient. This is the safe direction.
- **Zero checks:** skip when `supply == 0` (no shares to price), `feeShares == 0` (profit too small), or `feeBps == 0` (fees disabled).
- **HWM update timing:** update HWM to **post-fee PPS** (`nav / supplyAfterMint`), not to pre-fee `currentPPS`. The post-fee PPS is the actual share price holders experience. Growth above it is real new yield that should be subject to fee. Setting HWM to pre-fee PPS would create a dead zone where protocol earns no fee on recovery from its own dilution (see Enzyme V4, MetaMorpho for reference).
- **Return values:** returning post-fee `nav` and `supply` allows callers (deposit/redeem) to use them directly without re-reading storage.

## Security Considerations

### Fee-on-Deposit Ordering

If `_accruePerformanceFee()` is not called before `deposit()`, a large deposit inflates `supply` before fee mint, diluting the fee. Always accrue first.

### Direct Token Transfer

An attacker can send tokens directly to the vault, inflating NAV and triggering fee accrual on "phantom profit". Mitigation: track assets internally instead of using `balanceOf()`, or accept this as a donation to all shareholders (fee recipient included).

### PPS Manipulation via Flash Loan

If `_totalAssets()` depends on spot prices, an attacker could flash-loan-inflate NAV, trigger fee accrual (minting shares to fee recipient), then let NAV return. The fee shares remain, extracting value from depositors.

Mitigation: ensure `_totalAssets()` uses manipulation-resistant pricing (TWAP, oracle). See [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md).

### Redeem Before Heartbeat

If fee accrual happens only via a public heartbeat (not inline in deposit/redeem), a user can redeem before the heartbeat, exiting at pre-fee PPS and avoiding fee dilution. The unpaid fee is redistributed among remaining holders.

```
1. Yield accrues, PPS = 1.10, HWM = 1.00 (fee pending but not accrued)
2. User redeems at PPS 1.10 (no fee taken)
3. Heartbeat: fee mint, PPS drops to 1.08 for remaining holders
4. User avoided 0.02/share fee that others pay
```

Mitigation: accrue fees inline in deposit/redeem, not only via external heartbeat.

## Variants

### Management Fee (Time-Based)

Instead of (or in addition to) performance fee, charge a flat annual fee on AUM. Same share-dilution mechanic, but based on time elapsed rather than PPS increase.

```
feeShares = supply * annualFeeBps * elapsed / (MAX_BPS * SECONDS_PER_YEAR)
```

No high-water mark needed. Can be combined with performance fee.

### Crystallization Period

Instead of continuous accrual, fee is calculated once per period (e.g., quarterly). Prevents gaming through short-term PPS spikes.

### Hurdle Rate

Fee only charged on profit above a minimum return (e.g., risk-free rate). Modifies the formula:

```
profitPerShare = currentPPS - hwm * (1 + hurdleRate * elapsed / YEAR)
```

## Real-World Examples

- [Enzyme Finance V4](https://github.com/enzymefinance/protocol) — share-based performance fee with HWM and crystallization period; HWM set to post-fee PPS via two-step settle/update
- [MetaMorpho](https://github.com/morpho-org/metamorpho) — performance fee via share dilution; uses `lastTotalAssets` baseline (equivalent to post-fee HWM)
- [Yearn V2 Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy) — performance fee on per-strategy reported gains (no vault-level HWM, different approach)

## Related Patterns

- [Delta NAV Share Accounting](./pattern-delta-nav.md) — base share accounting that this fee pattern extends
- [Premium Buffer](./pattern-premium-buffer.md) — entry/exit fee (different purpose: covers swap costs, not protocol revenue)

## References

- [EIP-4626: Tokenized Vault Standard](https://eips.ethereum.org/EIPS/eip-4626)
- [Yearn V2 Fee Mechanism](https://docs.yearn.fi/getting-started/products/yvaults/overview)
