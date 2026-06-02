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
- A redeem cap on burned shares or stablecoins does not necessarily cap collateral outflow when collateral amount is independently signed or priced

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

### Delayed Mint With Validator Veto Variant

When minting depends on collateral reports, a minter can create a proposal that
is executable only after a delay. Approved validators can cancel the proposal or
freeze the minter during the delay:

```solidity
function proposeMint(uint256 amount, address destination) external returns (uint48 id) {
    id = ++latestMintId;
    mintProposal[id] = Proposal(msg.sender, amount, destination, block.timestamp + mintDelay);
}

function mint(uint48 id) external {
    Proposal memory p = mintProposal[id];
    require(block.timestamp >= p.executableAt, "delay");
    require(!_frozen[p.minter], "frozen");
    _mint(p.destination, p.amount);
}
```

This is a stronger control than a same-block cap for reserve-backed issuers. It
adds liveness and governance dependencies but gives validators a window to react
to bad collateral or compromised minters.

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
- Ensure the limited amount is the economically scarce leg. If redeem orders burn one token but release independently specified collateral, also cap collateral value or hot-wallet exposure.
- If using delayed mint proposals, allow only approved validators to cancel or freeze and test the proposal delay, one-active-proposal rule, and frozen-minter rejection.

## Source Evidence

- Avant `AvUSDMintingV2` tracks `mintedPerBlock` and `redeemedPerBlock`, enforces `belowMaxMintPerBlock` and `belowMaxRedeemPerBlock`, and lets a gatekeeper disable mint/redeem by setting both caps to zero in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/contracts/AvUSDMintingV2.sol`.
- Avant Foundry tests cover same-block mint and redeem limit exhaustion in `/private/tmp/defillama-source/Avant-Protocol__avUSD-Contracts/test/foundry/minting/tests/AvUSDMinting.blockLimits.t.sol`.
- M0 `MinterGateway` creates delayed mint proposals, lets approved validators cancel mint proposals or freeze minters, and tests validator-signature and freeze behavior in `/private/tmp/defillama-source/m0-foundation__protocol/src/MinterGateway.sol` and `test/MinterGateway.t.sol`.
- Ethena's 2023 Code4rena snapshot applies `belowMaxRedeemPerBlock` to the burned USDe amount while collateral transfer uses a separately signed collateral amount, and its README notes that the per-block cap does not bound redeemer-key compromise in `/private/tmp/defillama-source/code-423n4__2023-10-ethena/contracts/EthenaMinting.sol` and `/private/tmp/defillama-source/code-423n4__2023-10-ethena/README.md`.

## Real-World Examples

- Avant avUSD - global per-block mint and redeem caps around signed mint/redeem orders.
- M0 - reserve-backed minting with delayed mint proposals and validator veto/freeze controls.

## Related Patterns

- [Break-Glass Risk Limiter](./pattern-break-glass-risk-limiter.md)
- [Consumer-Scoped Rate Limiter](./pattern-consumer-scoped-rate-limiter.md)
- [Custodial Reserve Backing Requirements](../cross-chain/req-custodial-reserve-backing.md)

## References

- See Source Evidence.
