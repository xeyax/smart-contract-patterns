# ambiguity-report.md formatting rules

## Forbidden vague words

`flexible`, `easy`, `adequate`, `sufficient`, `fast`, `reliable`, `scalable`, `intuitive`, `user-friendly`, `safe`, `robust`, `efficient`, `seamless`, `appropriate`, `reasonable`, `minimal`, `optimal`, `modern`, `simple`, `clean`, `when appropriate`, `if needed`, `under normal conditions`, `as needed`.

Profile may extend this list.

## Structure

```markdown
# Ambiguity Report

## 1. Vague wording

- FR-003: "...handles errors gracefully..."
  Suggestion: replace with quantified condition (specific behavior on each error type).
  [GAP]: vague wording in FR-003

- NFR-002: "Response time should be fast"
  Suggestion: replace with specific number (e.g. "< 200ms p95").
  [GAP]: vague wording in NFR-002

## 2. Insufficient acceptance criteria

- FR-005: "Process payment"
  Has 1 AC; missing: refund/decline edge cases.
  [GAP]: FR-005 has insufficient acceptance criteria for edge cases

## 3. Unquantified NFRs / constraints

- NFR-004: "High availability"
  Suggestion: add specific uptime % (e.g. "99.9% monthly").
  [GAP]: NFR-004 uses unquantified term
```

## Rules

- Three sections, always present (use "No findings." if a section is empty).
- One bullet per finding.
- Don't suggest specific numbers — only the kind of quantification needed.
- An item may appear in multiple sections.
- Don't flag invariant-style FRs (one criterion fully covers them) for "insufficient AC".
