# Block-Scoped Mint/Redeem Throttle

> Bound total minting and redemption per block so a hot operator or signer cannot move more than the configured amount inside one block.

## Metadata

| Property | Value |
|----------|-------|
| Category | access-control |
| Tags | access-control, throttle, mint, redeem, block-limit |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | Medium |

## Use When

- A privileged minter, redeemer, bridge, or issuer can change supply quickly
- A same-block cap is useful even when operators are allowlisted
- The protocol wants a simple emergency knob that can be set to zero
- Per-user or per-route rate limits are unnecessary or handled elsewhere

## Avoid When

- Throughput must be smoothed across longer windows than one block
- One actor should not be able to consume global capacity for everyone
- The chain has highly variable block production and a time-based bucket is safer
- Supply changes are already bounded by stronger reserve or solvency checks

## Trade-offs

**Pros:**
- Very cheap to enforce
- Resets automatically with `block.number`
- Limits same-block blast radius from compromised hot roles

**Cons:**
- One actor can consume the block's capacity
- Does not limit multi-block drain without a separate daily or bucket cap
- Block production assumptions differ across chains

## How It Works

Track the amount consumed in the current block for each supply-changing direction:

```solidity
mapping(uint256 => uint256) public mintedInBlock;
mapping(uint256 => uint256) public redeemedInBlock;

function _consumeMintLimit(uint256 amount) internal {
    uint256 used = mintedInBlock[block.number] + amount;
    require(used <= maxMintPerBlock, "mint block cap");
    mintedInBlock[block.number] = used;
}

function _consumeRedeemLimit(uint256 amount) internal {
    uint256 used = redeemedInBlock[block.number] + amount;
    require(used <= maxRedeemPerBlock, "redeem block cap");
    redeemedInBlock[block.number] = used;
}
```

Administrative setters can raise or lower the caps. A separate emergency role can often only lower them or set them to zero.

## Implementation

```solidity
function mint(MintOrder calldata order, bytes calldata sig) external onlyMinter {
    _verifyOrder(order, sig);
    _consumeMintLimit(order.mintAmount);
    _mint(order.receiver, order.mintAmount);
}

function redeem(RedeemOrder calldata order, bytes calldata sig) external onlyRedeemer {
    _verifyOrder(order, sig);
    _consumeRedeemLimit(order.burnAmount);
    _burn(order.owner, order.burnAmount);
    _releaseCollateral(order.receiver, order.collateralAmount);
}
```

### Key Points

- Consume the limit before external settlement calls.
- Emit old and new cap values on cap changes.
- Test multiple calls in the same block and the first call in the next block.
- Pair with reserve, custody, or solvency accounting; a block cap is not proof of backing.

## Source Evidence

- Avant `AvUSDMintingV2` tracks `mintedPerBlock` and `redeemedPerBlock`, enforces `belowMaxMintPerBlock` and `belowMaxRedeemPerBlock`, and lets a gatekeeper disable mint/redeem by setting both caps to zero in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/contracts/AvUSDMintingV2.sol`.
- Avant Foundry tests cover same-block mint and redeem limit exhaustion in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/test/foundry/minting/tests/AvUSDMinting.blockLimits.t.sol`.

## Real-World Examples

- Avant avUSD - global per-block mint and redeem caps around signed mint/redeem orders.

## Related Patterns

- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Consumer-Scoped Rate Limiter](./pattern-consumer-scoped-rate-limiter.md)
- [Custodial Reserve Backing Requirements](../cross-chain/req-custodial-reserve-backing.md)

## References

- See Source Evidence.
