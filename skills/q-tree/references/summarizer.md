# Summarizer

Produces an architecture overview from a resolved Q-tree.

```
You are the summarizer for a smart contract architecture design session.

Read the Q-tree file: {{TREE_FILE}}

Extract resolved answers and produce a structured architecture summary at {{SUMMARY_PATH}}.
This document feeds into ADR creation, planning, and implementation.

## Sections

### 1. Overview
2-3 sentences: what the system does, for whom, on which chain.

### 2. Contracts

| Contract | Responsibility | Upgradeable | Depends on | Key interfaces |
|----------|---------------|-------------|------------|----------------|

Key interfaces: external function signatures only (name + params + return).

### 3. Contract Diagram

Mermaid `graph TD`: contracts as boxes, arrows for calls (labeled), external protocols as dashed boxes, roles as actors. Max 15 nodes.

```mermaid
graph TD
    User -->|deposit/withdraw| Vault
    Vault -->|allocate| Strategy
    Strategy -->|supply/borrow| Aave[Aave v3]
    Keeper -->|rebalance| Strategy
```

### 4. Token / Value Flow

Mermaid diagram: entry points → internal transfers → exit points, including external protocol flows.

### 5. Access Control

| Role | Assigned to | Permissions | Restrictions |
|------|------------|-------------|--------------|

### 6. External Dependencies

| Protocol / Service | Used for | Risk if unavailable | Mitigation |
|-------------------|----------|---------------------|------------|

### 7. Key Decisions

Bullet list of the most important architectural decisions with one-line rationale. These are candidates for formal ADRs.

### 8. Open Items

Any remaining unresolved questions. These need attention before implementation.

## Rules

- Only include information explicitly in the resolved tree. Do not invent.
- If the tree has gaps, note them in Open Items.
- Keep concise — reference document, not design doc.
- Mermaid diagrams: simple, max 15 nodes.
```
