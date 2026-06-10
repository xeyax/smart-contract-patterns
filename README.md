# DeFi Smart Contract Patterns

A curated catalog of smart contract design patterns for DeFi applications, harvested from production protocols with source evidence. Designed for AI agents to select optimal patterns based on requirements.

## How to Use This Catalog

### For AI Agents

1. Fetch [`patterns/INDEX.md`](patterns/INDEX.md) — a one-file index of every document with description and "Use When" criteria
2. Match user requirements against "Use When" / "Avoid When" criteria
3. Fetch only the pattern files that match; weigh "Trade-offs" and "Key Points" for informed decisions
4. Check the category's `risk-*` and `req-*` files for what the chosen patterns must satisfy or defend against

### File Naming Convention

- `req-*.md` — requirements (what must be satisfied)
- `pattern-*.md` — patterns (solutions/implementations)
- `risk-*.md` — risks (problems/vulnerabilities)

### Adding New Documents

1. Use the appropriate prefix (`req-`, `pattern-`, `risk-`) and follow [TEMPLATE.md](TEMPLATE.md)
2. Cite source evidence as GitHub permalinks pinned to a commit — never local paths
3. Link relevant requirements (which R1–Rn does it satisfy or violate?) and related patterns
4. Regenerate the index: `python3 scripts/generate-pattern-index.py`
5. Validate: `python3 scripts/validate-patterns.py`

### Code Style Guidelines

- **Focus on the pattern itself** — show only the code that illustrates the core concept
- **Abstract away unrelated details** — use descriptive function names like `_acceptDeposit()`, `_processWithdrawal()`, `_calculateNav()` instead of implementation details (transfers, oracle calls, etc.)
- **Keep examples minimal** — vault-specific, protocol-specific, or standard boilerplate code should be abstracted

## Pattern Categories

The table below is auto-generated — edit `CATEGORY_DESCRIPTIONS` in `scripts/generate-pattern-index.py`, not the table.

<!-- BEGIN GENERATED:CATEGORIES -->
| Category | Docs | Scope |
|----------|------|-------|
| [access-control](patterns/access-control/) | 26 (26 patterns) | Roles, authority handoff, scoped permissions, rate-limited privileges. |
| [automation](patterns/automation/) | 6 (6 patterns) | Keeper/bot execution, triggers, cranks, permissionless maintenance. |
| [cross-chain](patterns/cross-chain/) | 42 (38 patterns, 1 risks, 3 reqs) | Bridges, cross-chain messaging, rollup exits, custody, finality. |
| [governance](patterns/governance/) | 16 (12 patterns, 3 risks, 1 reqs) | Voting, timelocks, parameter changes, emergency powers. |
| [lending](patterns/lending/) | 48 (45 patterns, 3 reqs) | Collateral, interest-rate models, liquidations, bad-debt handling. |
| [liquidity](patterns/liquidity/) | 39 (32 patterns, 3 risks, 4 reqs) | AMMs, concentrated liquidity, pool fees, LP accounting. |
| [math](patterns/math/) | 2 (2 patterns) | Fixed-point arithmetic, rounding, numerical safety. |
| [monitoring](patterns/monitoring/) | 6 (6 patterns) | On-chain risk monitors, circuit breakers, invariant checks. |
| [oracles](patterns/oracles/) | 20 (14 patterns, 5 risks, 1 reqs) | Price feeds, TWAP, staleness, manipulation resistance. |
| [perps](patterns/perps/) | 12 (11 patterns, 1 reqs) | Perpetual futures: funding, margin, position settlement. |
| [rewards](patterns/rewards/) | 17 (16 patterns, 1 risks) | Staking rewards, emissions, distribution accounting. |
| [routing](patterns/routing/) | 8 (7 patterns, 1 risks) | Swap routing, order settlement, aggregation. |
| [token-integration](patterns/token-integration/) | 5 (5 patterns) | Safely consuming external or non-standard tokens. |
| [tokens](patterns/tokens/) | 11 (11 patterns) | Token implementations and transfer mechanics. |
| [upgrades](patterns/upgrades/) | 6 (5 patterns, 1 risks) | Proxies, migrations, versioning. |
| [vaults](patterns/vaults/) | 41 (33 patterns, 3 risks, 5 reqs) | Share accounting, deposits/withdrawals, NAV, vault fees. |
| [zero-knowledge](patterns/zero-knowledge/) | 3 (2 patterns, 1 reqs) | ZK proof verification and integration. |
<!-- END GENERATED:CATEGORIES -->

See [`patterns/INDEX.md`](patterns/INDEX.md) for the full per-document index, and [ANTIPATTERNS.md](ANTIPATTERNS.md) for known-bad architectural decisions.

## Development Process

A formalized workflow for building smart contracts using LLM agents with creator/reviewer cycles. Each phase produces a specific artifact, reviewed by a separate agent before proceeding.

```
Idea → Vision → Requirements → ADR (+ Research) → Plan → Implementation
```

See [process/README.md](process/README.md) for the full process description and prompts.

## Knowledge Harvesting

Use the `harvest-patterns` skill to analyze another repository and extract reusable patterns, risks, requirements, and decisions back into this catalog. The skill is evidence-first: each accepted addition must cite source code, tests, ADRs, audit notes, or docs from the analyzed repo, then compare against the existing catalog before writing updates. Harvest session records live in [harvests/](harvests/).
