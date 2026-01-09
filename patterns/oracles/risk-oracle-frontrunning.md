# Oracle Frontrunning Risk

> Attackers exploit predictable oracle updates to front-run price changes and extract value.

## Metadata

| Property | Value |
|----------|-------|
| Category | oracles |
| Tags | oracle, frontrunning, mev, timing, arbitrage, risk |
| Type | Risk Description |

## Problem Description

Oracle updates are visible in the mempool before being included in a block. Attackers can:
- See pending price updates
- Front-run with profitable transactions
- Extract value from protocols using the oracle

This is a form of MEV (Maximal Extractable Value) specific to oracle-dependent protocols.

## Requirements Violated

This risk violates [Oracle Reliability Requirements](./req-oracle-reliability.md):
- **R1: Freshness** — exploits timing of updates
- **R2: Accuracy** — price transitions are exploitable

## Attack Vectors

### 1. Chainlink Update Frontrunning

```
┌─────────────────────────────────────────────────────────────┐
│                    Attack Timeline                          │
├─────────────────────────────────────────────────────────────┤
│ T+0: Current Chainlink price: ETH = $2000                   │
│                                                             │
│ T+1: Attacker sees pending Chainlink update in mempool      │
│      New price: ETH = $2100 (+5%)                           │
│                                                             │
│ T+2: Attacker front-runs with higher gas:                   │
│      - Deposit $1M into vault at $2000 NAV                  │
│      - Or: Borrow max against ETH collateral                │
│                                                             │
│ T+3: Chainlink update included in same block                │
│      Price now $2100                                        │
│                                                             │
│ T+4: Attacker's position worth more / can withdraw profit   │
└─────────────────────────────────────────────────────────────┘
```

### 2. TWAP Manipulation + Frontrun

```
1. Attacker calculates when TWAP window will shift
2. Makes trades to influence new TWAP value
3. Submits transaction that will be profitable at new TWAP
4. Times everything to execute atomically
```

### 3. Predictable Update Schedule

Some oracles update at predictable times:

```
Oracle updates every hour at :00
At :59:50, attacker prepares transactions
At :00:01, attacker's tx executes right after update

Attacker knows direction of update from:
- Pending mempool transactions
- Observing CEX prices
- Prior block's DEX prices
```

### 4. Liquidation Frontrunning

```
Borrower position close to liquidation threshold
Oracle price drop pending in mempool

Attacker:
1. Sees pending price update that will trigger liquidation
2. Front-runs with their own liquidation call
3. Captures liquidation bonus
4. Original liquidator's tx fails or gets worse execution
```

## MEV Searcher Behavior

Professional MEV searchers:

```
1. Monitor mempool for Chainlink transmit() calls
2. Decode pending price update
3. Calculate profitable opportunities:
   - Vault deposits/withdrawals
   - Lending positions
   - Liquidations
4. Bundle frontrun + oracle update + backrun
5. Submit via Flashbots (private mempool)
```

## Conditions That Increase Risk

| Factor | Higher Risk | Lower Risk |
|--------|-------------|------------|
| Update frequency | Low (predictable timing) | High (unpredictable) |
| Price deviation threshold | High (large jumps) | Low (small jumps) |
| Mempool visibility | Public | Private/Flashbots |
| Protocol TVL | High (profitable to attack) | Low |
| Block time | Long (more time to frontrun) | Short |

## Impact Calculation

```
Frontrun Profit = Position Size × Price Change - Gas Cost

Example:
- Pending update: +2% price increase
- Attacker deposits $5M before update
- Position gains: 2% × $5M = $100K
- Gas cost: ~$500 (high priority)
- Net profit: ~$99.5K
```

## Mitigations

| Pattern | How It Helps | Trade-off |
|---------|--------------|-----------|
| Commit-reveal | Hide operation until after oracle update | Complex UX, 2 transactions |
| Async settlement | Settlement price unknown at commit time | Delayed execution |
| Private mempool | Updates not visible to attackers | Centralization |
| Time-weighted execution | Average price over window | Slower settlement |

### Implementation: Async Deposit

```solidity
contract AsyncVault {
    struct DepositRequest {
        address user;
        uint256 amount;
        uint256 requestBlock;
    }

    mapping(bytes32 => DepositRequest) public requests;
    uint256 public settlementDelay = 1;  // blocks

    function requestDeposit(uint256 amount) external {
        // Just record intent, don't use current price
        bytes32 id = keccak256(abi.encode(msg.sender, block.number));
        requests[id] = DepositRequest(msg.sender, amount, block.number);
        _transferIn(amount);
    }

    function settleDeposit(bytes32 id) external {
        DepositRequest memory req = requests[id];
        require(block.number > req.requestBlock + settlementDelay, "Too soon");

        // Price determined AFTER request, can't be frontrun
        uint256 price = getCurrentPrice();
        uint256 shares = req.amount * 1e18 / price;
        _mint(req.user, shares);

        delete requests[id];
    }
}
```

### Implementation: Commit-Reveal

```solidity
contract CommitRevealVault {
    mapping(address => bytes32) public commits;
    mapping(address => uint256) public commitBlocks;

    function commit(bytes32 hash) external {
        commits[msg.sender] = hash;
        commitBlocks[msg.sender] = block.number;
    }

    function reveal(uint256 amount, bytes32 salt) external {
        require(block.number > commitBlocks[msg.sender] + 1, "Wait for next block");
        require(
            keccak256(abi.encode(msg.sender, amount, salt)) == commits[msg.sender],
            "Invalid reveal"
        );

        // Execute deposit with current (post-commit) price
        _deposit(msg.sender, amount);

        delete commits[msg.sender];
    }
}
```

### Implementation: Time-Weighted Average Execution

```solidity
contract TWAXVault {
    function deposit(uint256 amount) external {
        // Use TWAP that spans the recent window
        // Even if attacker knows pending update,
        // TWAP smooths out the impact
        uint256 twapPrice = getTWAP(30 minutes);
        uint256 shares = amount * 1e18 / twapPrice;
        _mint(msg.sender, shares);
    }
}
```

## Detection

### On-Chain Indicators

```solidity
// Detect if tx was likely frontrunning an oracle update
// by checking if oracle updated in same block
function wasOracleUpdatedThisBlock() internal view returns (bool) {
    (, , , uint256 updatedAt, ) = priceFeed.latestRoundData();
    return updatedAt == block.timestamp;
}
```

### Off-Chain Monitoring

- Track transactions that consistently precede oracle updates
- Monitor for unusual activity around predictable update times
- Analyze MEV extraction patterns

## Real-World Examples

- **Flashbots MEV Bundles** — routinely include oracle frontrunning
- **Yearn Harvest Frontrunning** — bots frontrun yield harvests
- **Liquidation MEV** — significant value extracted from lending protocols

## Related Patterns

- [Async Deposit/Withdrawal](../vaults/pattern-async-deposit.md) — primary defense
- [TWAP Oracle](./pattern-twap-oracle.md) — smooths price transitions
- [Multi-Source Validation](./pattern-multi-source-validation.md) — adds uncertainty

## Related Risks

- [Oracle Staleness Risk](./risk-oracle-staleness.md) — staleness creates frontrun window
- [Price Manipulation Risk](./risk-price-manipulation.md) — different attack vector

## References

- [Flashbots Documentation](https://docs.flashbots.net/)
- [MEV Explore](https://explore.flashbots.net/)
- [Chainlink Off-Chain Reporting](https://docs.chain.link/architecture-overview/off-chain-reporting)
- [Oracle Frontrunning Analysis](https://www.paradigm.xyz/2020/08/ethereum-is-a-dark-forest)

