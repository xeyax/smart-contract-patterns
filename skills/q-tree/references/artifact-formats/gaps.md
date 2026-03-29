# Gaps Formatting Rules

Rules for `gaps.md` artifact.

## Structure

```markdown
# Gaps

| # | Type | Artifact | Description | Parent | Suggested q-tree question |
|---|------|----------|-------------|--------|--------------------------|
| 1 | GAP | invariants | No invariants for Strategy | d:strategy-sep | ? What must always be true for Strategy state? |
| 2 | CHOICE | contracts | Oracle logic placed in Strategy | d:oracle | ? Where does oracle integration live? |
```

## Rules

- Type: `GAP` (information missing) or `CHOICE` (ambiguity, summarizer picked one interpretation).
- Parent: `[d:tag]` of the nearest existing node where the question belongs. `—` if no natural parent.
- Only created if there are `[GAP]` or `[CHOICE]` entries in other artifacts.
