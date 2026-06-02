---
name: harvest-patterns
description: >-
  Harvest reusable smart-contract knowledge from another repository into this
  smart-contract-patterns catalog. Use when Codex should analyze a target repo,
  extract proven patterns, risks, requirements, ADRs, invariants, audit lessons,
  or implementation decisions, compare branch changes or candidate updates with
  the current catalog, decide whether proposed pattern updates are better or
  worth applying, audit code against known anti-patterns, update pattern/risk/req
  docs, and regenerate the catalog index.
---

# Harvest Patterns

## Purpose

Turn evidence from a target repository into reusable catalog knowledge for this
repo. The output is not a code review of the target repo; it is a curated update
to `patterns/`, `ANTIPATTERNS.md`, or process/skill docs when the target repo
contains reusable decisions, mitigations, failures, or design trade-offs.

## Inputs

Accept a target repository path or URL plus optional scope:

- `target`: local path preferred; clone/fetch only if the user asks or approves.
- `scope`: directories, contracts, PR, commit range, audit report, or docs to focus on.
- `mode`: `dry-run` for proposed updates only, `write` to edit this repo, `branch-review` to evaluate current branch/catalog diffs, or `anti-pattern-audit` to audit a target repo against `ANTIPATTERNS.md`. If unclear and the user asked to "update/enrich this repo", use `write`.
- `base`: branch/commit used for `branch-review` diffs. Default to the repository's main branch if obvious, else use the merge base with the upstream tracking branch.

## Workflow

1. **Map the target repo.** Read `references/repo-mapper.md` and dispatch a mapper subagent when subagents are available. Locally inspect only what is needed to continue while it runs.
2. **Extract candidates.** Read `references/extractor.md`. Dispatch independent extractor subagents for patterns, risks, requirements/invariants, and decisions when the target repo has enough material. Each candidate must cite source evidence.
3. **Audit anti-patterns when relevant.** Read `references/anti-pattern-auditor.md` for smart-contract code, architecture docs, audit reports, or user requests mentioning anti-patterns. Treat audit findings as candidate risks or `ANTIPATTERNS.md` updates; do not silently rewrite target repo code.
4. **Compare with current catalog.** Read `references/catalog-comparer.md`. Decide for each candidate: update existing doc, add new doc, merge into anti-patterns, or reject as too project-specific.
5. **Review branch diffs when relevant.** In `branch-review` mode, read `references/branch-reviewer.md` and evaluate whether the current branch's catalog changes improve, duplicate, weaken, or contradict the base catalog.
6. **Review contradictions.** Read `references/contradiction-reviewer.md`. Check new/changed claims against existing requirements, patterns, risks, anti-patterns, and `patterns/INDEX.md`.
7. **Write catalog updates.** Read `references/doc-writer.md`. Apply only evidence-backed changes. Preserve existing style, filenames, and category structure.
8. **Regenerate and verify.** Run `python3 scripts/generate-pattern-index.py`, inspect `git diff`, and run lightweight checks for broken relative markdown links and malformed new docs.

If subagents are unavailable, run the same steps sequentially. Do not skip the comparison and contradiction review.

## Evidence Rules

- Every accepted candidate must include at least one concrete source: file path, function/contract name, test, ADR, audit finding, issue, commit, or README section.
- Prefer implemented and tested behavior over comments. Treat comments and docs as weaker evidence unless tests or code support them.
- When the target is this catalog or evidence is prose-only, downgrade confidence and do not describe the finding as production-proven.
- Do not add a pattern just because an idea is interesting. Add it only when it is reusable across projects and has clear "Use When" / "Avoid When" boundaries.
- If the source repo has a bug or exploit, capture the generalized risk and mitigation, not project gossip.
- If evidence contradicts this catalog, keep both only when the scope differs; otherwise flag the conflict and resolve the docs.

## Output Shape

For each run, return:

```
Harvest summary:
- Target: <path/repo>
- Scope: <scope>
- Added: <files>
- Updated: <files>
- Rejected candidates: <count with short reasons>
- Anti-pattern findings: <count and severity summary, if audited>
- Branch verdict: <keep/change/reject/split, if branch-review>
- Verification: <commands/checks run>
- Open questions: <only blockers or important unresolved contradictions>
```

## Catalog Placement

- Put reusable solution patterns under `patterns/<category>/pattern-*.md`.
- Put threat/failure modes under `patterns/<category>/risk-*.md`.
- Put cross-pattern guarantees under `patterns/<category>/req-*.md`.
- Put broad "never do this" guidance in `ANTIPATTERNS.md` only when it is not tied to one category.
- Prefer updating an existing doc when the candidate is a variant, caveat, or missing edge case of an existing pattern.

## Writing Rules

- Follow the existing pattern style and `TEMPLATE.md` section names.
- Add a short `## Source Evidence` section to newly harvested docs unless the evidence naturally fits under Real-World Examples or References.
- Keep implementation snippets minimal and pattern-focused; abstract target-specific names.
- Keep local target repo paths in evidence when the target is local. If the target is public, include stable links only when available.
- After edits, regenerate `patterns/INDEX.md`; do not hand-edit the generated file.

## Subagent Guidance

Use subagents for bounded sidecar work:

- Mapper owns repository inventory and evidence map.
- Extractors own candidate discovery only; they do not write files.
- Anti-pattern auditor owns detection against `ANTIPATTERNS.md` and generalized risk candidates.
- Comparer owns duplicate/merge recommendations.
- Branch reviewer owns verdicts about current branch changes versus the base catalog.
- Contradiction reviewer owns consistency checks.
- Main Codex agent owns final file edits, index generation, and final judgment.

Do not let multiple workers edit the same catalog files. If using worker subagents for file edits, assign disjoint paths explicitly.
