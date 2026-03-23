# ZapIn Proportional Deposit

> External periphery contract converts single-token input into a proportional multi-token deposit, pushing swap slippage to the depositor and eliminating slippage socialisation in managed vaults.

## Metadata

| Property | Value |
|----------|-------|
| Category | vaults |
| Tags | vault, zapin, proportional, slippage, periphery, multi-token, managed-vault |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Low–Medium |

## Use When

- Multi-token vault where a manager rebalances after single-token deposits (slippage socialised across holders)
- Deposits are continuous (open-end fund, ETF-style vault)
- Portfolio tokens have reasonable DEX liquidity
- Dynamic deposit fees are complex to tune or lag real market conditions

## Avoid When

- Single-asset vault — no proportional deposit needed
- Closed-end vault with a single deposit phase — all participants share slippage equally by design
- Portfolio contains illiquid tokens with no DEX market — ZapIn swaps will have prohibitive slippage
- Gas cost of multi-token transfer is prohibitive relative to deposit size

## Trade-offs

**Pros:**
- Zero slippage socialisation — existing holders fully protected
- No oracle needed at deposit time — share calculation is purely ratio-based
- Eliminates dynamic deposit fee complexity — no slippage tracking, no peak decay, no manager overrides
- Depositor has full control — sees slippage upfront via `minSharesOut`, can abort
- Vault logic is trivial — min-ratio across token balances

**Cons:**
- Worse UX than single-token deposit — requires ZapIn periphery + frontend integration
- Higher gas — multiple DEX swaps + multi-token transfer vs single transfer
- ZapIn swaps are MEV-exposed — standard DEX trade risks (sandwiching)
- Bootstrap problem — first deposit (zero balances) requires separate mechanism
- Weight drift: deposits lock in current (possibly drifted) proportions

## Problem

A managed multi-token vault that accepts deposits in a single token (e.g. USDC) must rebalance after each deposit — swap the deposit token into portfolio tokens to restore target weights. The swap slippage reduces NAV and is borne by **all** shareholders, even though the depositor already holds shares priced at the pre-slippage PPS.

```
Vault: 10% USDC, 45% WETH, 45% WBTC  (NAV $100K)
Deposit: $500K USDC
Manager must swap $450K USDC → WETH/WBTC
At 1% slippage → $4,500 NAV loss, socialised across all holders

A 0.5% deposit fee covers only $2,500 → existing holders lose $2,000
```

Dynamic deposit fees (tracking observed slippage, non-deposit weight, etc.) mitigate this but are:
- **Reactive** — lag real conditions by design
- **Complex** — peak tracking, decay windows, manager overrides
- **Imprecise** — overcollect on small deposits, undercollect on large ones

## How It Works

The pattern splits responsibilities between two contracts:

```
┌─────────┐     any ERC-20      ┌──────────┐  proportional tokens  ┌───────────┐
│  User    │ ──────────────────► │  ZapIn   │ ────────────────────► │   Vault   │
│          │                     │(periphery)│                      │           │
│          │ ◄── shares ──────── │          │ ◄── shares ────────── │           │
│          │ ◄── refund ──────── │          │                      │           │
└─────────┘                     └──────────┘                      └───────────┘
                                     │
                                     │ swaps (slippage here)
                                     ▼
                                ┌──────────┐
                                │   DEX    │
                                └──────────┘
```

1. **User** sends a single token (USDC, DAI, WETH — anything) to ZapIn.
2. **ZapIn** reads vault's current token balances and computes target proportions.
3. **ZapIn** swaps input token into each portfolio token to match proportions. Slippage on each swap is the depositor's cost.
4. **ZapIn** calls `vault.depositProportional(amounts)` with the resulting basket.
5. **Vault** computes `min(amount[i] / balance[i])` across all tokens — the proportional increase. Mints `totalSupply × minRatio` shares. Pulls only proportional amounts; surplus refunded.
6. Shares and any unused tokens returned to user.

### Why This Eliminates Slippage Socialisation

| Step | Who pays | Vault NAV impact |
|------|----------|------------------|
| ZapIn swaps input → portfolio tokens | **Depositor** (swap slippage) | None — swaps are external |
| Vault receives tokens in exact proportion | — | NAV increases proportionally |
| Shares minted at min-ratio | Depositor gets fewer shares (lost value to slippage) | PPS unchanged |
| Manager rebalances after deposit? | Nobody — **not needed** | None |

The depositor's effective cost is the DEX slippage they incurred — market-determined, transparent, and fair. The vault never touches a DEX.

### No Oracle at Deposit Time

Share calculation uses only the ratio `amount[i] / balance[i]` — no oracle prices involved.  This eliminates [oracle arbitrage risk](./risk-oracle-arbitrage.md) at the deposit boundary entirely.

Compare with alternatives:

| Deposit method | Oracle needed at deposit? | Slippage bearer |
|---------------|--------------------------|-----------------|
| Single-token + manager rebalance | Yes (for NAV → share calc) | All holders (socialised) |
| Single-token + dynamic fee | Yes (for NAV + fee calc) | Approximated via fee |
| **Proportional via ZapIn** | **No** | **Depositor only** |

## Numerical Example

### Initial state

| Token | Balance | Price | Value | Weight |
|-------|---------|-------|-------|--------|
| USDC | 30 000 | $1.00 | $30 000 | 30% |
| WETH | 13.333 | $3 000 | $40 000 | 40% |
| WBTC | 0.4286 | $70 000 | $30 000 | 30% |
| **Total** | | | **$100 000** | 100% |

Supply: 100 000 shares · PPS = $1.00

### Deposit: user sends $10 000 USDC to ZapIn

**ZapIn splits by vault weights (30 / 40 / 30):**

| Token | Target value | Swap | Received | Slippage |
|-------|-------------|------|----------|----------|
| USDC | $3 000 | None | 3 000 USDC | — |
| WETH | $4 000 | 4 000 USDC → WETH | 1.320 WETH ($3 960) | $40 |
| WBTC | $3 000 | 3 000 USDC → WBTC | 0.04243 WBTC ($2 970) | $30 |

Depositor lost $70 to slippage.

**Vault computes min-ratio:**

| Token | Balance | Deposited | Ratio |
|-------|---------|-----------|-------|
| USDC | 30 000 | 3 000 | 10.00% |
| WETH | 13.333 | 1.320 | **9.90%** ← min |
| WBTC | 0.4286 | 0.04243 | **9.90%** ← min |

```
minRatio     = 9.90%
sharesMinted = 100 000 × 9.90% = 9 900

USDC used:  30 000 × 9.90% = 2 970    (refund 30 USDC)
WETH used:  13.333 × 9.90% = 1.320    (exact)
WBTC used:  0.4286 × 9.90% = 0.04243  (exact)
```

### Post-deposit state

| Token | Balance | Value | Weight |
|-------|---------|-------|--------|
| USDC | 32 970 | $32 970 | 30.0% |
| WETH | 14.653 | $43 960 | 40.0% |
| WBTC | 0.4710 | $32 970 | 30.0% |
| **Total** | | **$109 900** | 100% |

Supply: 109 900 shares · PPS = $1.00

### Verification

- **PPS unchanged:** $1.00 → $1.00 ✓
- **Weights unchanged:** 30 / 40 / 30 → 30 / 40 / 30 ✓
- **Zero vault-side slippage:** all swaps in ZapIn ✓
- **Existing holders:** 100 000 × $1.00 = $100 000 (no loss) ✓
- **Depositor bears slippage:** sent $10 000, received 9 900 shares worth $9 900 ✓

### Comparison with single-token deposit + manager rebalance

| Metric | Single-token deposit | Proportional via ZapIn |
|--------|---------------------|------------------------|
| Vault-side swaps | ~$7 000 | $0 |
| Slippage socialised | ~$70 | $0 |
| Slippage on depositor | $0 | $70 |
| Deposit fee needed | ~70 BPS (dynamic) | 0 |
| Manager action | Must rebalance | None |
| Weight distortion | Until rebalanced | None |

## Implementation

### Vault: `depositProportional`

```solidity
/// @notice Accepts portfolio tokens in current proportion. Mints shares
///         based on the minimum proportional increase across all tokens.
function depositProportional(
    uint256[] calldata amounts,
    address receiver
) external nonReentrant returns (uint256 sharesToMint) {
    uint256 n = portfolioTokens.length;
    require(amounts.length == n, "length mismatch");

    uint256 minRatioX18 = type(uint256).max;

    for (uint256 i; i < n; ++i) {
        uint256 bal = _getTrackedBalance(portfolioTokens[i]);
        require(bal > 0, "zero balance");
        uint256 ratioX18 = (amounts[i] * 1e18) / bal;
        if (ratioX18 < minRatioX18) minRatioX18 = ratioX18;
    }

    sharesToMint = (totalSupply() * minRatioX18) / 1e18;
    require(sharesToMint > 0, "zero shares");

    for (uint256 i; i < n; ++i) {
        uint256 used = (_getTrackedBalance(portfolioTokens[i]) * minRatioX18) / 1e18;
        _pullToken(portfolioTokens[i], msg.sender, used);
        _increaseTrackedBalance(portfolioTokens[i], used);
    }

    _mintShares(receiver, sharesToMint);
}
```

### ZapIn: periphery contract

```solidity
struct SwapRoute {
    uint256 amountIn;     // how much of inputToken to use for this leg
    uint256 minAmountOut; // per-swap slippage protection
    bytes swapData;       // DEX-specific calldata
}

/// @notice Converts a single token into a proportional vault deposit.
///         Slippage from DEX swaps is borne entirely by the caller.
function zapDeposit(
    address vault,
    address tokenIn,
    uint256 amountIn,
    uint256 minSharesOut,
    SwapRoute[] calldata routes,
    address receiver
) external returns (uint256 shares) {
    IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);

    address[] memory tokens = IMultiTokenVault(vault).getPortfolioTokens();
    uint256[] memory amounts = new uint256[](tokens.length);

    for (uint256 i; i < tokens.length; ++i) {
        if (tokens[i] == tokenIn) {
            amounts[i] = routes[i].amountIn;
        } else {
            amounts[i] = _executeSwap(
                tokenIn, tokens[i],
                routes[i].amountIn, routes[i].minAmountOut,
                routes[i].swapData
            );
        }
        IERC20(tokens[i]).forceApprove(vault, amounts[i]);
    }

    shares = IMultiTokenVault(vault).depositProportional(amounts, receiver);
    require(shares >= minSharesOut, "below minSharesOut");

    _sweepAll(tokens, receiver);
    _sweepToken(tokenIn, receiver);
}
```

### Key Points

- Vault's `depositProportional` is the **only deposit path** — no single-token deposit on the vault itself
- ZapIn is stateless, permissionless, and holds no funds between transactions
- `minSharesOut` gives the depositor end-to-end slippage protection across all swaps
- Per-swap `minAmountOut` provides granular MEV protection on each DEX leg
- Surplus tokens (from slippage variance across legs) are swept back to the user
- The vault never executes a swap — it only receives pre-assembled baskets

## Variations

### Proportional ZapOut (Symmetric Withdrawal)

Same pattern in reverse: vault redeems shares → user receives proportional tokens → ZapOut swaps all to a single token. Eliminates withdrawal-driven rebalancing.

```
User burns shares → vault sends proportional tokens to ZapOut
→ ZapOut swaps all to desired output token → sends to user
```

### Hybrid: Proportional + Single-Token Fallback

Vault accepts both proportional deposits and single-token deposits (with a weight gate limiting how much any token can grow). More flexible, but reintroduces oracle dependency and weight drift for the single-token path. ZapIn route through proportional deposit remains the recommended default.

### Weighted Proportional (Target vs Actual)

Instead of matching *current* balances, match *target weights*. A deposit at target weights nudges the vault toward its target allocation. Requires the vault to expose target weights and accept slightly non-proportional deposits. Adds oracle dependency (need to value tokens to compute weights).

## Edge Cases

### Bootstrap (First Deposit)

When all balances are zero, the min-ratio formula divides by zero. Requires a separate bootstrap mechanism:
- **Manager seed deposit:** privileged call that sets initial balances and mints shares at oracle-determined value
- **Factory pre-seed:** factory deploys vault with non-zero initial balances (funded by deployer)
- **First-deposit special case:** first call bypasses ratio check, mints shares at `sum(amount[i] * price[i])`

### New Token Added to Portfolio

If the manager adds a new portfolio token with zero balance, `depositProportional` reverts for that token. The manager must first `rebalance()` into the new token (acquiring some balance) before proportional deposits resume.

### Weight Drift Between Rebalances

If token A appreciates 20%, the vault's balance-based proportions drift from target weights. Proportional deposits at drifted weights lock in the imbalance. This is bounded by the drift magnitude and is symmetric (helps as often as it hurts). The manager's regular rebalancing corrects drift independently.

If drift tolerance is important, the vault can pause proportional deposits when balance-derived weights deviate from target weights beyond a threshold.

### Rounding and Dust

The min-ratio calculation may leave dust per token (used < deposited). ZapIn sweeps all surplus back to the user. For very small deposits, rounding may cause zero `used` for some tokens — `sharesToMint = 0` and the deposit reverts.

## ERC4626 Compatibility

ERC4626 mandates `asset()` returning a single token and `deposit(uint256, address)` accepting that token.

| Approach | ERC4626 | Complexity |
|----------|---------|------------|
| **Dual interface:** keep one token as `asset()` for ERC4626; add `depositProportional` as the primary path | Full compliance on the legacy path | Two deposit entry points |
| **ERC4626 wrapper:** separate contract wraps the multi-token vault, embeds ZapIn logic internally | Full compliance via adapter | Extra contract + gas overhead |
| **Partial compliance:** `asset()` returns a stablecoin; `deposit()` reverts with guidance | Read-only compliance | Simplest; breaks deposit composability |

## Real-World Examples

- [Index Coop ExchangeIssuanceZeroEx](https://github.com/IndexCoop/index-coop-smart-contracts) — ZapIn for Set Protocol TokenSets; swaps single token into proportional basket and issues set tokens
- [Set Protocol BasicIssuanceModule](https://github.com/SetProtocol/set-protocol-v2) — proportional deposit (all component tokens required); no built-in ZapIn
- [Balancer Proportional Join](https://docs.balancer.fi/concepts/pools/joins-and-exits.html) — weighted pool proportional join; single-sided join charges implicit swap fee
- [StakeDAO / StoneVault ZapIn](https://docs.stakedao.org/) — peripheral ZapIn contract for single-token entry into multi-strategy vaults

## Related Patterns

- [Proportional Deposit/Withdrawal](./pattern-proportional-deposit.md) — base pattern for the vault-side math; this pattern adds the ZapIn periphery layer
- [Oracle Arbitrage Risk](./risk-oracle-arbitrage.md) — the risk this pattern avoids at deposit time by not using oracles
- [Dynamic Premium](./pattern-dynamic-premium.md) — alternative: keep single-token deposit, charge adaptive fee. More complex, less precise.
- [Premium Buffer](./pattern-premium-buffer.md) — alternative: fixed deposit fee. Simpler but can't match actual slippage.
- [Delta NAV Share Accounting](./pattern-delta-nav.md) — the oracle-based share calculation this pattern replaces for deposits

## References

- [Set Protocol: Issuance Module Docs](https://docs.tokensets.com/developers/contracts/protocol/modules/basic-issuance-module)
- [EIP-4626: Tokenized Vaults](https://eips.ethereum.org/EIPS/eip-4626) — single-asset standard that this pattern extends
- [Balancer Docs: Joins and Exits](https://docs.balancer.fi/concepts/pools/joins-and-exits.html)
