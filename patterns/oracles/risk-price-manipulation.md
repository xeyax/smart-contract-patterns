# Price Manipulation Risk

> Attackers manipulate on-chain price sources to exploit protocols that rely on them.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, manipulation, flash-loan, sandwich, mev, risk |
| Type | Risk Description |

## Problem Description

On-chain price sources (DEX spot prices, low-liquidity pools) can be manipulated within a single transaction or block. Attackers exploit this to:
- Borrow more than collateral is worth
- Trigger unfair liquidations
- Extract value through deposit/withdrawal arbitrage

## Requirements Violated

This risk violates [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R3: Manipulation Resistance** — price can be artificially moved

## Attack Vectors

### 1. Flash Loan Price Manipulation

Most common attack pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Transaction                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Borrow 10,000 ETH via flash loan                         │
│ 2. Swap all ETH → USDC on target pool                       │
│    Pool price: ETH drops from $2000 to $500                 │
│ 3. Protocol reads manipulated spot price ($500)             │
│ 4. Attacker deposits USDC, gets shares at wrong price       │
│ 5. Swap USDC → ETH (restore price)                          │
│ 6. Repay flash loan                                         │
│ 7. Profit from mispriced shares                             │
└─────────────────────────────────────────────────────────────┘
```

**Cost to attacker:** Flash loan fee (0.09%) + swap fees + gas
**Potential profit:** Can be millions if protocol uses spot price

### 2. Sandwich Attack

MEV bots sandwich user transactions:

```
1. Victim submits swap: Buy ETH
2. Attacker front-runs: Buy ETH (price goes up)
3. Victim's tx executes at worse price
4. Attacker back-runs: Sell ETH at higher price

If protocol reads price between steps 2-3:
Protocol sees manipulated price
```

### 3. Multi-Block Manipulation

More expensive but harder to detect:

```
Block N:   Attacker accumulates position, moves price 5%
Block N+1: Attacker maintains manipulation
Block N+2: Protocol reads "stable" (but fake) TWAP
Block N+3: Attacker unwinds, profits
```

**Cost:** High (capital locked across blocks, slippage)
**Defense:** Longer TWAP windows, higher liquidity requirements

### 4. Low Liquidity Pool Exploitation

```
Obscure token with $100K liquidity
$10K swap moves price 20%

Attacker:
1. Swap $10K to move price
2. Use manipulated price in lending protocol
3. Borrow more than fair value
4. Default on loan, keep extra borrowed assets
```

## Vulnerable Patterns

| Price Source | Vulnerability | Attack Cost |
|--------------|---------------|-------------|
| DEX Spot (slot0) | Trivial single-tx manipulation | Very low |
| Short TWAP (<5 min) | Flash loan + multi-block | Low |
| Low liquidity pool | Simple swap | Very low |
| Uniswap V2 reserves | Flash loan manipulation | Low |

## Safe Patterns

| Price Source | Why Safer | Trade-off |
|--------------|-----------|-----------|
| Long TWAP (30+ min) | Requires sustained manipulation | Lags during volatility |
| High liquidity pools | Expensive to move | May not exist for all tokens |
| Chainlink | Off-chain, manipulation-resistant | Centralization, staleness |
| Multi-source validation | Requires manipulating multiple sources | Higher gas |

## Impact Calculation

```
Manipulation Profit = (Price Impact × Position Size) - Attack Cost

Attack Cost = Flash Loan Fee + Swap Slippage + Gas

Example:
- Move price 10% with $1M flash loan
- Flash loan fee: 0.09% = $900
- Swap slippage: 0.3% × 2 = $6,000
- Gas: $500
- Total cost: ~$7,400
- Potential profit: 10% × victim_position_size
- Break-even if victim position > $74,000
```

## Mitigations

| Pattern | How It Helps | Trade-off |
|---------|--------------|-----------|
| [TWAP Oracle](./pattern-twap-oracle.md) | Time-weighting defeats single-block attacks | Lags during volatility |
| [Multi-Source Validation](./pattern-multi-source-validation.md) | Requires manipulating multiple sources | Higher gas |
| [Chainlink Integration](./pattern-chainlink-integration.md) | Off-chain aggregation | Centralization, staleness |
| Liquidity Requirements | Reject prices from low-liquidity pools | May exclude valid tokens |

### Implementation: TWAP Protection

```solidity
// Use 30-minute TWAP instead of spot
function getManipulationResistantPrice() internal view returns (uint256) {
    (int24 tick, ) = OracleLibrary.consult(pool, 30 minutes);
    return tickToPrice(tick);
}
```

### Implementation: Liquidity Check

```solidity
function validateLiquidity(address pool) internal view returns (bool) {
    uint128 liquidity = IUniswapV3Pool(pool).liquidity();
    return liquidity >= MIN_LIQUIDITY_THRESHOLD;
}
```

### Implementation: Multi-Source Check

```solidity
function validatePrice(uint256 oraclePrice) internal view returns (bool) {
    uint256 twapPrice = getTWAP(30 minutes);
    uint256 deviation = calculateDeviation(oraclePrice, twapPrice);

    // Reject if oracle and TWAP differ too much
    return deviation <= MAX_DEVIATION_BPS;
}
```

## Detection

### On-Chain Indicators

```solidity
// Large deviation between spot and TWAP indicates possible manipulation
function isSpotManipulated() public view returns (bool) {
    uint256 spotPrice = getSpotPrice();
    uint256 twapPrice = getTWAP(30 minutes);

    uint256 deviation = calculateDeviation(spotPrice, twapPrice);
    return deviation > MANIPULATION_THRESHOLD;
}
```

### Off-Chain Monitoring

- Sudden liquidity changes in target pools
- Large flash loan transactions
- Unusual price deviations from centralized exchanges

## Real-World Incidents

- **bZx (2020)** — $8M stolen via flash loan + oracle manipulation
- **Harvest Finance (2020)** — $34M via USDC/USDT pool manipulation
- **Cream Finance (2021)** — Multiple attacks using oracle manipulation
- **Mango Markets (2022)** — $114M via MNGO token price manipulation

## Related Patterns

- [TWAP Oracle](./pattern-twap-oracle.md) — primary defense
- [Multi-Source Validation](./pattern-multi-source-validation.md) — detect manipulation
- [DEX Spot Price](./pattern-dex-spot-price.md) — understand what NOT to use alone

## Related Risks

- [Oracle Staleness Risk](./risk-oracle-staleness.md) — different vector, similar impact
- [Oracle Frontrunning Risk](./risk-oracle-frontrunning.md) — exploits update timing

## References

- [Flash Loan Attacks](https://blog.chain.link/flash-loans/)
- [DeFi Oracle Manipulation](https://samczsun.com/so-you-want-to-use-a-price-oracle/)
- [MEV and Sandwich Attacks](https://writings.flashbots.net/)

