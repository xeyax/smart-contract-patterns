# Oracle Centralization Risk

> Relying on a single oracle source creates single points of failure and trust assumptions.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, centralization, trust, availability, risk |
| Type | Risk Description |

## Problem Description

Centralized oracle dependencies create risks:
- Single point of failure (oracle downtime = protocol downtime)
- Trust in oracle operators (who could manipulate or be compromised)
- Regulatory/legal risk (operators could be forced to censor)
- No fallback when primary source fails

## Requirements Violated

This risk violates [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R4: Availability** — single source can fail

## Attack Vectors

### 1. Oracle Downtime

```
Scenario: Chainlink feed goes offline (maintenance, bug, attack)

Impact:
- Protocol cannot determine prices
- Deposits/withdrawals blocked
- Liquidations cannot execute
- Positions may become undercollateralized without intervention
```

### 2. Operator Compromise

```
Scenario: Oracle operator keys compromised

Impact:
- Attacker can submit false prices
- Protocol acts on manipulated data
- Massive value extraction possible before detection
```

### 3. Coordinated Operator Manipulation

```
Scenario: Majority of Chainlink nodes collude or are compromised

Impact:
- Median price is attacker-controlled
- Threshold signatures can be forged
- Protocol cannot distinguish real from fake prices
```

### 4. Regulatory Pressure

```
Scenario: Government forces oracle operator to:
- Stop serving certain protocols
- Report user transactions
- Censor specific addresses

Impact:
- Protocol loses price feed
- Users cannot interact
- Potential legal exposure for protocol
```

### 5. Economic Attack on Oracle Network

```
Scenario: Attacker bribes/coerces oracle nodes

Cost calculation:
- Chainlink node bond: varies
- Potential profit from manipulation: can be billions
- If profit > cost to corrupt nodes: economically viable
```

## Trust Assumptions

### Chainlink

| Trust Point | Assumption |
|-------------|------------|
| Node operators | Act honestly, keys not compromised |
| Chainlink Labs | Won't censor, maintains network |
| Data sources | Report accurate prices |
| Network consensus | 2/3 honest nodes |

### On-Chain Oracles (Uniswap TWAP)

| Trust Point | Assumption |
|-------------|------------|
| Pool liquidity | Sufficient to resist manipulation |
| Block producers | Don't censor oracle queries |
| Ethereum network | Continues operating |

## Centralization Spectrum

```
Most Centralized ◄────────────────────────► Most Decentralized

Single EOA       Multisig      Chainlink      Uniswap TWAP
Feed            Controlled     Network        (on-chain)
     │              │              │              │
     ▼              ▼              ▼              ▼
  1 trust        N/M trust     ~15 nodes      No external
   point          points       consensus       trust
```

## Impact Scenarios

### Scenario A: Primary Oracle Offline

```
Chainlink ETH/USD stops updating for 2 hours

Protocol behavior:
- Staleness check triggers → deposits blocked
- No fallback → complete freeze
- Users cannot exit positions
- Liquidations paused → bad debt risk
```

### Scenario B: Oracle Returns Wrong Price

```
Bug in Chainlink aggregator returns ETH = $0

Protocol behavior (without bounds check):
- All ETH collateral valued at $0
- Mass liquidations triggered
- Protocol insolvent in minutes
```

### Scenario C: Gradual Drift Attack

```
Compromised node slowly drifts reported price
Over days, 10% deviation from reality

Protocol behavior:
- No circuit breaker triggers (within deviation bounds)
- Arbitrageurs extract value slowly
- By detection, significant loss incurred
```

## Mitigations

| Pattern | How It Helps | Trade-off |
|---------|--------------|-----------|
| [Multi-Source Validation](./pattern-multi-source-validation.md) | No single source dependency | Higher gas, complexity |
| Fallback Oracles | Alternative when primary fails | Need multiple integrations |
| [Historical Bounds](./pattern-historical-bounds.md) | Reject extreme outliers | May reject legitimate prices |
| Governance Override | Manual intervention for emergencies | Introduces different centralization |

### Implementation: Fallback Oracle Chain

```solidity
contract FallbackOracleChain {
    address[] public oracles;  // Ordered by preference

    function getPrice() public view returns (uint256) {
        for (uint i = 0; i < oracles.length; i++) {
            try IOracle(oracles[i]).getPrice() returns (uint256 price) {
                if (_isValid(price)) {
                    return price;
                }
            } catch {
                // Try next oracle
                continue;
            }
        }
        revert("All oracles failed");
    }

    function _isValid(uint256 price) internal view returns (bool) {
        // Sanity checks
        return price > 0 && price < type(uint128).max;
    }
}
```

### Implementation: Multi-Oracle Median

```solidity
contract MedianOracle {
    address[] public oracles;
    uint256 public minResponses = 3;

    function getPrice() public view returns (uint256) {
        uint256[] memory prices = new uint256[](oracles.length);
        uint256 validCount = 0;

        for (uint i = 0; i < oracles.length; i++) {
            try IOracle(oracles[i]).getPrice() returns (uint256 price) {
                if (price > 0) {
                    prices[validCount] = price;
                    validCount++;
                }
            } catch {}
        }

        require(validCount >= minResponses, "Insufficient oracle responses");

        // Sort and return median
        _sort(prices, validCount);
        return prices[validCount / 2];
    }
}
```

### Implementation: On-Chain Fallback

```solidity
contract ChainlinkWithTWAPFallback {
    AggregatorV3Interface public chainlink;
    address public uniswapPool;
    uint256 public maxStaleness;

    function getPrice() public view returns (uint256) {
        // Try Chainlink first
        try this.getChainlinkPrice() returns (uint256 price) {
            return price;
        } catch {
            // Fall back to Uniswap TWAP
            return getTWAP(uniswapPool, 30 minutes);
        }
    }

    function getChainlinkPrice() external view returns (uint256) {
        (, int256 price, , uint256 updatedAt, ) = chainlink.latestRoundData();
        require(block.timestamp - updatedAt <= maxStaleness, "Stale");
        require(price > 0, "Invalid");
        return uint256(price);
    }
}
```

## Decentralization Strategies

### 1. Hybrid Approach

```
Primary: Chainlink (fast, reliable, covered by insurance)
Secondary: Uniswap TWAP (decentralized fallback)
Tertiary: Governance median (emergency only)
```

### 2. Cross-Chain Verification

```
Read price from multiple chains
If Ethereum Chainlink differs from Arbitrum Chainlink:
Something is wrong, pause operations
```

### 3. Optimistic Oracle

```
Anyone can submit price
Challenge period allows disputes
Staked collateral deters bad actors
Example: UMA's optimistic oracle
```

## Real-World Incidents

- **Synthetix (2019)** — $1B in erroneous trades due to oracle misconfig
- **Compound (2020)** — DAI price spike caused $89M in liquidations
- **LUNA/UST (2022)** — Chainlink paused price feeds during collapse

## Related Patterns

- [Multi-Source Validation](./pattern-multi-source-validation.md) — reduce centralization
- [Chainlink Integration](./pattern-chainlink-integration.md) — understand trust model
- [TWAP Oracle](./pattern-twap-oracle.md) — on-chain alternative

## Related Risks

- [Oracle Staleness Risk](./risk-oracle-staleness.md) — centralized oracle may become stale
- [Oracle Frontrunning Risk](./risk-oracle-frontrunning.md) — centralized updates are predictable

## References

- [Chainlink Architecture](https://docs.chain.link/architecture-overview/architecture-overview)
- [UMA Optimistic Oracle](https://docs.umaproject.org/oracle/optimistic-oracle)
- [Decentralizing DeFi Oracles](https://blog.chain.link/levels-of-data-aggregation-in-chainlink-price-feeds/)

