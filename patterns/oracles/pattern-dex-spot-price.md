# DEX Spot Price

> Read current price directly from DEX pool — real-time but manipulation-vulnerable.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, spot, dex, uniswap, real-time |
| Complexity | Low |
| Gas Efficiency | High |
| Audit Risk | High |

## Use When

- Need real-time price for display purposes
- Combined with other validation (not used alone for value transfer)
- As one input to multi-source validation
- For low-value operations where manipulation is unprofitable

## Avoid When

- Price directly determines asset transfers (liquidations, swaps)
- No additional manipulation protection exists
- High-value operations vulnerable to MEV
- Asset has low liquidity in the pool

## Trade-offs

**Pros:**
- Real-time, no lag
- Simple implementation
- Low gas cost (single storage read)
- Always available if pool exists

**Cons:**
- Vulnerable to flash loan manipulation
- Sandwich attacks can move price
- Single-block manipulation is trivial
- Accuracy depends on pool liquidity

## How It Works

Read the current price from the pool's state:

**Uniswap V2:** Read reserves and calculate price
```
price = reserve1 / reserve0
```

**Uniswap V3:** Read current tick from slot0
```
sqrtPriceX96 = slot0.sqrtPriceX96
price = (sqrtPriceX96 / 2^96)^2
```

**Warning:** This price can be manipulated within a single transaction!

## Requirements Satisfied

This pattern satisfies [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — always current
- **R2: Accuracy** — reflects current pool state (but may not reflect true market)
- ❌ **R3: Manipulation Resistance** — easily manipulated
- **R4: Availability** — always available

## Implementation

### Uniswap V3 Spot Price

```solidity
import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

contract SpotPriceOracle {
    IUniswapV3Pool public immutable pool;

    constructor(address _pool) {
        pool = IUniswapV3Pool(_pool);
    }

    function getSpotPrice() public view returns (uint256 price) {
        (uint160 sqrtPriceX96, , , , , , ) = pool.slot0();
        return _sqrtPriceToPrice(sqrtPriceX96);
    }

    function _sqrtPriceToPrice(uint160 sqrtPriceX96) internal pure returns (uint256) {
        // price = (sqrtPriceX96 / 2^96)^2
        // Scaled to 18 decimals
        uint256 price = uint256(sqrtPriceX96) * uint256(sqrtPriceX96);
        return price >> 192;  // Divide by 2^192
    }
}
```

### Uniswap V2 Spot Price

```solidity
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";

contract V2SpotPriceOracle {
    IUniswapV2Pair public immutable pair;
    bool public immutable token0IsBase;

    constructor(address _pair, bool _token0IsBase) {
        pair = IUniswapV2Pair(_pair);
        token0IsBase = _token0IsBase;
    }

    function getSpotPrice() public view returns (uint256 price) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();

        if (token0IsBase) {
            // Price of token1 in terms of token0
            price = (uint256(reserve0) * 1e18) / reserve1;
        } else {
            // Price of token0 in terms of token1
            price = (uint256(reserve1) * 1e18) / reserve0;
        }
    }
}
```

### With Liquidity Check

```solidity
function getSpotPriceWithLiquidityCheck() public view returns (uint256 price) {
    uint128 liquidity = pool.liquidity();
    require(liquidity >= minLiquidityThreshold, "Insufficient liquidity");

    (uint160 sqrtPriceX96, , , , , , ) = pool.slot0();
    return _sqrtPriceToPrice(sqrtPriceX96);
}
```

## Attack Vectors

### Flash Loan Manipulation

```
1. Attacker takes flash loan of 10,000 ETH
2. Swaps all ETH → USDC, moving price significantly
3. Protocol reads manipulated spot price
4. Attacker exploits the wrong price (liquidation, deposit, etc.)
5. Swaps back USDC → ETH
6. Repays flash loan
```

**Cost:** Only swap fees and gas
**Profit:** Can be enormous if protocol uses spot price for value transfer

### Sandwich Attack

```
1. Attacker sees pending tx that will read spot price
2. Front-runs with swap that moves price favorably
3. Victim tx executes at manipulated price
4. Attacker back-runs to restore price and profit
```

## Safe Usage Patterns

### As Validation Input Only

```solidity
function validateWithSpot(uint256 primaryPrice) internal view returns (bool) {
    uint256 spotPrice = getSpotPrice();

    // Spot only used to validate, not as source of truth
    uint256 deviation = _calculateDeviation(primaryPrice, spotPrice);
    return deviation <= maxDeviationBps;
}
```

### For Display/UI Only

```solidity
// Safe: Only for display, not value transfer
function getCurrentPriceForUI() external view returns (uint256) {
    return getSpotPrice();
}

// UNSAFE: Don't do this!
function deposit(uint256 amount) external {
    uint256 price = getSpotPrice();  // Manipulable!
    uint256 shares = amount * 1e18 / price;  // Attacker profits
    _mint(msg.sender, shares);
}
```

### Combined with TWAP

```solidity
function getSafePrice() external view returns (uint256) {
    uint256 spotPrice = getSpotPrice();
    uint256 twapPrice = getTWAP(30 minutes);

    // Use TWAP, but validate with spot
    uint256 deviation = _calculateDeviation(spotPrice, twapPrice);
    require(deviation <= 500, "Price deviation too high");  // 5%

    return twapPrice;  // Return manipulation-resistant price
}
```

## When Spot Price IS Safe

Spot price can be used safely when:

1. **No value transfer in same tx:**
   ```solidity
   // Safe: async settlement at later price
   function requestWithdraw() external {
       emit WithdrawRequested(msg.sender, block.timestamp);
       // Price determined in separate tx by keeper
   }
   ```

2. **Operation is unprofitable to manipulate:**
   ```solidity
   // Safe if manipulation cost > profit
   // For tiny amounts, gas + swap fees > potential profit
   function microDeposit(uint256 amount) external {
       require(amount <= 100e18, "Use large deposit flow");
       // Small enough that manipulation is unprofitable
   }
   ```

3. **Used for informational purposes only:**
   ```solidity
   function estimateShares(uint256 amount) external view returns (uint256) {
       return amount * 1e18 / getSpotPrice();  // Just an estimate
   }
   ```

## Real-World Examples

- [Uniswap V3 Pool](https://docs.uniswap.org/contracts/v3/reference/core/UniswapV3Pool) — `slot0()` for current price
- [SushiSwap](https://docs.sushi.com/) — spot price for routing estimates

## Related Patterns

- [TWAP Oracle](./pattern-twap-oracle.md) — manipulation-resistant alternative
- [Multi-Source Validation](./pattern-multi-source-validation.md) — use spot as one input
- [Chainlink Integration](./pattern-chainlink-integration.md) — off-chain alternative

## References

- [Uniswap V3 slot0](https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolState#slot0)
- [Flash Loan Attacks Explained](https://blog.chain.link/flash-loans/)
- [MEV and Oracle Manipulation](https://writings.flashbots.net/)

