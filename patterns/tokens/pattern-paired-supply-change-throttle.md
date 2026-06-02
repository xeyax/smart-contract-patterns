# Paired Supply-Change Throttle

> Rate-limit issuance and redemption as paired directions so one side consumes capacity while the opposite side restores it.

## Metadata

| Property | Value |
|----------|-------|
| Category | tokens |
| Tags | token, supply, throttle, issuance, redemption |
| Complexity | Medium |
| Gas Efficiency | Medium |
| Audit Risk | Medium |

## Use When

- A redeemable token can be issued and redeemed directly against backing assets
- Large same-period supply expansion or contraction creates risk
- Issuance and redemption pressure should be coupled rather than independent
- The token can expose separate governance-configured limits for each direction

## Avoid When

- Mint and redeem flows have unrelated risk budgets
- A global per-block cap is sufficient
- Capacity restoration from the opposite direction would be economically misleading
- The backing system cannot determine whether the action reduces or increases risk

## Trade-offs

**Pros:**
- Damps rapid supply oscillation
- Lets redemptions restore issuance headroom and issuance restore redemption headroom
- Gives operators separate knobs for expansion and contraction risk

**Cons:**
- More complex than independent caps
- Capacity accounting must be intuitive to integrators
- Bad parameter changes can still bottleneck exits

## How It Works

Maintain two throttles. A supply-increasing action consumes issuance capacity and restores redemption capacity; a supply-decreasing action does the opposite:

```solidity
function issue(uint256 amount) external {
    issuanceThrottle.useAvailable(amount);
    redemptionThrottle.refund(amount);
    _mint(msg.sender, amount);
}

function redeem(uint256 amount) external {
    redemptionThrottle.useAvailable(amount);
    issuanceThrottle.refund(amount);
    _burn(msg.sender, amount);
}
```

The throttle may refill over time, but the paired refund keeps the two directions linked to net supply movement.

## Implementation

```solidity
struct Throttle {
    uint256 available;
    uint256 max;
    uint256 lastUpdated;
}

function _use(Throttle storage t, uint256 amount) internal {
    _refill(t);
    require(t.available >= amount, "throttled");
    t.available -= amount;
}

function _refund(Throttle storage t, uint256 amount) internal {
    _refill(t);
    t.available = _min(t.max, t.available + amount);
}
```

### Key Points

- Emit capacity changes and throttle parameter changes.
- Keep risk-increasing throttle raises behind governance or delay.
- Test oscillation: issue then redeem, redeem then issue, and both around refill boundaries.
- Do not let throttle configuration block emergency proportional exits without a documented reason.

## Source Evidence

- Reserve Protocol uses issuance and redemption throttles in `RToken.issueTo`, `redeemTo`, and `redeemCustom`, with `Throttle.useAvailable` and opposite-direction capacity restoration in `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/p1/RToken.sol` and `/private/tmp/defillama-source/reserve-protocol__protocol/contracts/libraries/Throttle.sol`.
- Reserve tests cover issuance and redemption throttle behavior in `/private/tmp/defillama-source/reserve-protocol__protocol/test/RToken.test.ts`.

## Real-World Examples

- Reserve Protocol RToken - paired issuance and redemption throttles around direct mint and redemption.

## Related Patterns

- [Block-Scoped Mint/Redeem Throttle](../access-control/pattern-block-scoped-mint-redeem-throttle.md)
- [Break-Glass Risk Limiter](../access-control/pattern-break-glass-risk-limiter.md)
- [Reserve Exposure Caps](../lending/pattern-reserve-exposure-caps.md)

## References

- See Source Evidence.
