# Fixed-Maturity Principal/Yield Tokenization

> Split a yield-bearing asset into principal and yield claims for a specific expiry.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | yield, principal-token, yield-token, expiry, maturity |
| Complexity | High |
| Gas Efficiency | Medium |
| Audit Risk | High |

## Use When

- Users need to trade fixed-rate principal exposure separately from floating yield
- A yield-bearing asset has an exchange rate that can be observed through a standardized interface
- Maturity defines a clear boundary between principal redemption and remaining yield
- Markets or vaults can price principal and yield claims separately

## Avoid When

- The underlying asset cannot expose a reliable exchange rate
- Negative yield or slashing cannot be represented clearly
- Integrators expect one token to represent the full position value
- There is no clear policy for post-expiry rewards and residual yield

## Trade-offs

**Pros:**
- Creates fixed-rate and yield-trading primitives from one asset
- Lets principal converge toward maturity value
- Makes post-expiry redemption rules explicit

**Cons:**
- More token surfaces and approval paths
- Accounting depends on exchange-rate correctness
- Pre-expiry and post-expiry redemption have different asset requirements

## How It Works

For each `(standardizedYield, expiry)` pair, deploy a principal token and yield token:

```solidity
function tokenize(uint256 syAmount, uint256 expiry) external {
    sy.transferFrom(msg.sender, address(this), syAmount);
    principalToken[expiry].mint(msg.sender, syAmount);
    yieldToken[expiry].mint(msg.sender, syAmount);
}

function redeemPreExpiry(uint256 amount) external {
    principalToken.burnFrom(msg.sender, amount);
    yieldToken.burnFrom(msg.sender, amount);
    sy.transfer(msg.sender, amount);
}

function redeemPostExpiry(uint256 principalAmount) external {
    principalToken.burnFrom(msg.sender, principalAmount);
    _redeemMaturePrincipal(msg.sender, principalAmount);
}
```

Yield tokens receive or track the yield component before expiry. After expiry, principal redemption no longer requires paired yield tokens, and residual yield/rewards follow the documented treasury or yield-token policy.

## Implementation

### Key Points
- Key deployments by both yield source and expiry.
- Restrict principal mint/burn authority to the paired yield-token controller or factory.
- Define pre-expiry redemption as paired PT+YT burn.
- Define post-expiry redemption, reward ownership, and residual yield explicitly.
- Track exchange-rate drops and slashing separately from ordinary yield.
- Freeze the maturity exchange rate separately from post-maturity observed rates so later appreciation does not change matured principal claims.
- Emergency mode should block new strip/tokenize actions while allowing safe staged claims or interest collection when the claim basis is already fixed.
- Test maturity boundary, early redemption, late rewards, and negative exchange-rate periods.

## Source Evidence

- Pendle V2 splits standardized yield into PT/YT contracts per `(SY, expiry)`, authorizes PT mint/burn through YT, requires paired PT/YT redemption before expiry, and supports PT-only redemption after expiry in [`contracts/core/YieldContracts`](https://github.com/pendle-finance/pendle-core-v2-public/blob/fdcfe39ed7b45717f0e6e286581bdcf96bb2f9ce/contracts/core/YieldContracts).
- Exponent Core mints paired PT/YT from SY, blocks new stripping in emergency mode, burns YT only while the vault is active, and freezes `final_sy_exchange_rate` after expiry in [`programs/exponent_core/src/instructions/vault`](https://github.com/exponent-finance/exponent-core/blob/2897c660eeef647002b62ba971e19457182e0b37/programs/exponent_core/src/instructions/vault) and `src/state/vault.rs`.

## Real-World Examples

- Pendle V2 tokenizes yield-bearing assets into principal and yield tokens for fixed maturities.

## Related Patterns

- [Principal-Reward Split Derivative](./pattern-principal-reward-split-derivative.md)
- [Fixed-Yield Implied-Rate AMM](../liquidity/pattern-fixed-yield-implied-rate-amm.md)
- [Exchange-Rate Valuation Risk](../oracles/risk-exchange-rate-valuation.md)
- [Liquid Staking Loss Accounting Requirements](../vaults/req-liquid-staking-loss-accounting.md)
