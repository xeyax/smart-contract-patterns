# DeFi Smart Contract Patterns

A curated catalog of smart contract design patterns for DeFi applications. Designed for AI agents to select optimal patterns based on requirements.

## How to Use This Catalog

### For AI Agents
1. Read this index to understand available patterns
2. Match user requirements against "Use When" criteria in each pattern
3. Consider "Avoid When" and "Trade-offs" for informed decisions
4. Follow links to detailed pattern descriptions

### File Naming Convention
- `req-*.md` — requirements (what must be satisfied)
- `pattern-*.md` — patterns (solutions/implementations)
- `risk-*.md` — risks (problems/vulnerabilities)

### Adding New Documents
1. Use appropriate prefix (`req-`, `pattern-`, `risk-`)
2. For patterns: fill in all sections (Metadata, Use When, Avoid When, Trade-offs, Implementation)
3. Link to relevant requirements (which R1-Rn does it satisfy or violate?)
4. Add entry to Quick Reference table and category section below

### Code Style Guidelines
- **Focus on the pattern itself** — show only the code that illustrates the core concept
- **Abstract away unrelated details** — use descriptive function names like `_acceptDeposit()`, `_processWithdrawal()`, `_calculateNav()` instead of implementation details (transfers, oracle calls, etc.)
- **Keep examples minimal** — vault-specific, protocol-specific, or standard boilerplate code should be abstracted

## Pattern Categories

### token-standards
Token implementations and extensions (ERC20, ERC721, ERC1155 variants, custom mechanics).

### access-control
Permission management patterns (Ownable, Role-Based Access Control, Multisig, Timelock).

### upgradeability
Contract upgrade mechanisms (Transparent Proxy, UUPS, Diamond/EIP-2535).

### liquidity
DEX and liquidity provision patterns (AMMs, order books, concentrated liquidity).

### lending
Lending protocol patterns (overcollateralized loans, flash loans, interest rate models).

### vaults
Vault patterns (ERC4626, share accounting methods, withdrawal mechanisms, fee structures).

### yield
Yield generation patterns (staking, liquidity mining, reward distribution).

### oracles
Price feed and data oracle patterns (TWAP, Chainlink integration, oracle aggregation).

### governance
DAO and governance patterns (token voting, timelocks, veToken models).

### security
Security patterns and guards (reentrancy protection, pausable, rate limiting).

---

## Quick Reference

| Document | Type | Description |
|----------|------|-------------|
| [Vault Fairness Requirements](patterns/vaults/req-vault-fairness.md) | req | Core requirements for vault deposit/withdraw |
| [Delta NAV Share Accounting](patterns/vaults/pattern-delta-nav.md) | pattern | Standard share calculation based on NAV change |
| [Proportional Deposit/Withdrawal](patterns/vaults/pattern-proportional-deposit.md) | pattern | Multi-asset without oracles |
| [Premium Buffer](patterns/vaults/pattern-premium-buffer.md) | pattern | Entry/exit fees to cover oracle deviation |
| [Dynamic Premium](patterns/vaults/pattern-dynamic-premium.md) | pattern | Adaptive fees based on drift/volatility |
| [Async Deposit/Withdrawal](patterns/vaults/pattern-async-deposit.md) | pattern | Delayed settlement eliminates timing advantage |
| [Timelock on Shares](patterns/vaults/pattern-timelock-shares.md) | pattern | Lock shares after mint to prevent flash loans |
| [Circuit Breaker](patterns/vaults/pattern-circuit-breaker.md) | pattern | Pause operations on oracle deviation |
| [Oracle Arbitrage Risk](patterns/vaults/risk-oracle-arbitrage.md) | risk | Timing arbitrage from stale oracle prices |

---

## Patterns by Category

### token-standards
*No patterns yet*

### access-control
*No patterns yet*

### upgradeability
*No patterns yet*

### liquidity
*No patterns yet*

### lending
*No patterns yet*

### vaults

**Requirements:**
- [req-vault-fairness](patterns/vaults/req-vault-fairness.md) — core fairness requirements (R1-R4)

**Patterns:**
- [pattern-delta-nav](patterns/vaults/pattern-delta-nav.md) — share calculation based on NAV change
- [pattern-proportional-deposit](patterns/vaults/pattern-proportional-deposit.md) — multi-asset without oracles
- [pattern-premium-buffer](patterns/vaults/pattern-premium-buffer.md) — entry/exit fees (satisfies R1, R3)
- [pattern-dynamic-premium](patterns/vaults/pattern-dynamic-premium.md) — adaptive fees based on drift/volatility (satisfies R1)
- [pattern-async-deposit](patterns/vaults/pattern-async-deposit.md) — delayed settlement (satisfies R4)
- [pattern-timelock-shares](patterns/vaults/pattern-timelock-shares.md) — lock shares after mint (partially satisfies R4)
- [pattern-circuit-breaker](patterns/vaults/pattern-circuit-breaker.md) — pause on oracle deviation (satisfies R4)

**Risks:**
- [risk-oracle-arbitrage](patterns/vaults/risk-oracle-arbitrage.md) — timing arbitrage (violates R1, R2, R4)

### yield
*No patterns yet*

### oracles
*No patterns yet*

### governance
*No patterns yet*

### security
*No patterns yet*
