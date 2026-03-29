# Requirements YAML Format

Unified item list. All types (FR, NFR, C, R) in one flat list. Validators and generators understand this format natively.

## Structure

```yaml
project: "Vault Fee Wrapper"
version: 1
date: 2026-03-28

purpose: >
  ERC-4626 wrapper over existing vault. Issues own shares, charges
  performance fee on gains, tracks referrals for off-chain distribution.
  Two contracts: Wrapper (core) and FeeReceiver (distribution).

scope:
  in_scope:
    - Wrapper deposit/redeem
    - Performance fee
    - Referral tracking
    - Fee distribution
    - Emergency pause
    - Admin governance
  out_of_scope:
    - Base vault implementation
    - Off-chain referral reward calculation
    - Deployment scripts
    - UI/frontend

glossary:
  - term: PPS
    definition: Price per share — ratio of total assets to total share supply
  - term: Fee peak
    definition: Highest PPS at which fees were last accrued
  - term: Heartbeat
    definition: Public function that triggers fee accrual without deposit or redeem
  - term: FeeReceiver
    definition: Separate contract that accumulates fee shares and supports batch distribution

items:
  # --- Core Flows ---
  - id: FR-001
    type: FR
    group: Core Flows
    status: ✓
    priority: Must
    text: "Users can deposit assets and receive proportional share of wrapper ownership"
    rationale: "Core vault functionality, ERC-4626 standard"
    source: "q-tree: Wrapper architecture"
    verification: Test
    risks: [R-001]
    children:
      - type: acceptance
        text: "Ownership share proportional to deposit relative to total assets"
      - type: edge_case
        text: "First depositor receives shares at 1:1 rate"
      - type: negative
        text: "Deposit when paused → reverts"
      - type: negative
        text: "Deposit below minimum → reverts"

  # --- Risks (mixed in with FRs) ---
  - id: R-001
    type: R
    status: ✓
    priority: Must
    text: "Dust griefing — many tiny deposits bloat storage"
    mitigation: "Minimum deposit threshold"
    mitigated_by: [FR-012]

  # --- Constraints ---
  - id: C-001
    type: C
    status: ✓
    priority: Must
    text: "Ethereum mainnet deployment"

  # --- NFR ---
  - id: NFR-001
    type: NFR
    status: ✓
    priority: Must
    text: "Standard deposit/redeem interface is fully ERC-4626 compliant"
    rationale: "Composability with aggregators and DeFi protocols"
    verification: Test
    children:
      - type: acceptance
        text: "All required ERC-4626 functions implemented"
      - type: acceptance
        text: "Unsupported functions (withdraw, mint) return 0 for max and revert on call"
```

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | yes | Project name |
| `version` | number | no | Document version |
| `date` | string | no | Last updated |
| `purpose` | string | yes | What the system is — one paragraph |
| `scope.in_scope` | string[] | yes | What's included |
| `scope.out_of_scope` | string[] | yes | What's explicitly excluded |
| `glossary` | list | no | Term definitions: `term` + `definition` |
| `items` | list | yes | All items (FR, NFR, C, R) in one list |

## Item Fields

### Required

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique: FR-NNN, NFR-NNN, C-NNN, R-NNN |
| `type` | enum | FR, NFR, C (constraint), R (risk) |
| `status` | marker | ✓ / → / ? |
| `priority` | enum | Must / Should / Could |
| `text` | string | The statement. WHAT, not HOW. Singular, verifiable. |

### Optional

| Field | Type | Description |
|-------|------|-------------|
| `group` | string | Logical grouping (Core Flows, Performance Fee, etc.) |
| `rationale` | string | Why this exists |
| `source` | string | Origin: stakeholder, standard, threat analysis |
| `verification` | enum | Test / Analysis / Demonstration / Inspection (IADT) |
| `risks` | id[] | Risks this mitigates |
| `depends_on` | id[] | Dependencies |
| `conflicts_with` | id[] | Explicit conflicts |
| `attack_surface` | string | What attacks this prevents |
| `gas_budget` | string | Gas constraint |
| `mitigation` | string | For risks: how mitigated (or "accepted") |
| `mitigated_by` | id[] | For risks: which FRs mitigate this |

### Children (acceptance criteria)

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | acceptance / edge_case / negative / performance |
| `text` | string | Observable pass/fail condition. WHAT, not HOW. |

## Grouping

Items can be grouped by `group` field. Recommended order (core → periphery):

1. **Purpose & Initialization** — system identity, deployment
2. **Core Flows** — deposit, redeem, total assets
3. **Performance Fee** — fee model, accrual, governance
4. **Referral System** — tracking, guards, whitelist
5. **FeeReceiver** — distribution, extraction
6. **Admin & Operations** — pause, min deposit
7. **ERC-4626 Views** — preview, max functions

Items of all types (FR, NFR, C, R) can appear in any group. A risk next to the FR it relates to is better than all risks at the bottom.

## Notes

- All types in one list. Proposer generates mixed batches (FR + R + C together).
- Requirements describe WHAT, not HOW. Test: "could this be implemented differently?" If yes — it's HOW.
- Each item should be singular. "and" → consider splitting.
- Detail files (`details/{id}.md`) for long rationale/rejected/assumptions.
- Glossary should cover all domain-specific terms used in item texts.
