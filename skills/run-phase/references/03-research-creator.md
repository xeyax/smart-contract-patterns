# Research -- Researcher

```
Conduct technical research and document findings in docs/research/{{FILENAME}}.md.

Question: {{RESEARCH_QUESTION}}
Context (requirements): {{REQUIREMENTS_DOC}}

Sections:

## Question
Specific formulation of what needs to be determined.

## Sources
What was studied (documentation, code, transactions) -- with links.

## Findings
Each finding:
- Statement (one sentence)
- Proof (link to code, tx hash, quote, fork test)
- Confidence level: CONFIRMED / FROM DOCUMENTATION / ASSUMPTION

## Limitations and Edge Cases
## Open Questions
## Conclusions for the Project
Specifically: update Requirements? need an ADR? are there blockers?

RULES:
- Each finding = proof + confidence level. No proof -> "ASSUMPTION"
- Don't guess -- couldn't find it -> "Open Questions"
- A real transaction is more valuable than documentation
- Contradiction between docs and code -> record both versions
- Write in English
```
