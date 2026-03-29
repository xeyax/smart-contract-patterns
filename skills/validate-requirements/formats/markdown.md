# Requirements Markdown Format

Human-friendly format. Validators parse by section structure. All item types can appear in any group.

## Structure

```markdown
# Requirements: Vault Fee Wrapper

## Purpose

The system is an ERC-4626 wrapper over an existing vault. Issues own shares,
charges performance fee on gains, tracks referrals for off-chain distribution.

## Scope

**In scope:** deposit/redeem, performance fee, referral tracking, fee distribution, emergency pause.

**Out of scope:** base vault implementation, off-chain reward calculation, UI.

## Glossary

- **PPS** — price per share, ratio of total assets to total share supply.
- **Fee peak** — highest PPS at which fees were last accrued.

## Core Flows

### FR-001: Proportional deposit [Must] ✓
Users can deposit assets and receive proportional share of wrapper ownership.

**Rationale:** Core vault functionality, ERC-4626 standard.
**Risks:** R-001

**Acceptance criteria:**
- Ownership share proportional to deposit relative to total assets
- First depositor receives shares at 1:1 rate
- Deposit when paused → reverts
- Deposit below minimum → reverts

### R-001: Dust griefing [Must] ✓
Attacker makes many tiny deposits to bloat storage.
**Mitigation:** FR-012 (minimum deposit threshold)
**Mitigated by:** FR-012

### C-001: Ethereum mainnet [Must] ✓
System deploys on Ethereum mainnet.

## Performance Fee

### FR-003: Fee on net new gains only [Must] ✓
System charges a performance fee only on gains above the previous fee peak.
...
```

## Key Differences from YAML

- Grouping via `##` headings instead of `group:` field
- Item type inferred from ID prefix (FR-, NFR-, C-, R-)
- Status marker at end of heading line (✓ / → / ?)
- Priority in brackets: `[Must]`, `[Should]`, `[Could]`
- All types can appear in any group section (risks next to related FRs)

## Parsing Rules

1. **`## Section`** = group (Core Flows, Performance Fee, Admin, etc.)
2. **`### ID: Title [Priority] Status`** = item. ID prefix determines type.
3. **First paragraph** after heading = item text
4. **`**Field:**`** = metadata (Rationale, Source, Risks, Mitigation, Mitigated by)
5. **`**Acceptance criteria:**`** followed by bullet list = children
6. **`## Purpose`**, **`## Scope`**, **`## Glossary`** = special sections (parsed as metadata, not items)

## Notes

- Human-friendly — write requirements by hand in this format.
- All item types (FR, NFR, C, R) can appear in any `##` section.
- Not every field needs to be present — validators flag missing fields as warnings.
- For machine-to-machine exchange, prefer yaml format.
- Mixed formatting OK — some items have full metadata, others just text + acceptance criteria.
