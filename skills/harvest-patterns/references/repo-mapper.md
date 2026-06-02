# Repo Mapper Prompt

Use this prompt for a subagent that maps a target repository before extraction.

## Task

Analyze the target repository and produce an evidence map for reusable smart-contract knowledge.

## Inputs

- Target repository path or URL.
- Optional scope from the user.
- Current catalog root path.

## Read

Prefer local files. Use `rg --files`, `rg`, and focused reads. Inspect:

- Contracts, libraries, interfaces, deployment scripts, tests, fuzz/invariant tests.
- `docs/`, `audits/`, `security/`, `research/`, `adr/`, `README*`, specs, issues exported into the repo.
- Config that reveals framework, compiler versions, dependencies, upgradeability, networks.

## Output

Return a concise report:

```
REPO_MAP
Target: <path/repo>
Stack: <frameworks, languages, test tools>
Primary domains: <vault/oracle/lending/governance/etc.>
Important files:
- <path>: <why it matters>
Evidence clusters:
- <cluster name>: <files/tests/docs that belong together>
Likely catalog categories:
- <category>: <reason>
Extraction leads:
- <lead>: <why it may become pattern/risk/req/ADR>
Gaps / inaccessible material:
- <missing dependency, generated file, private submodule, etc.>
```

## Rules

- Do not propose catalog changes yet.
- Do not write files.
- Distinguish code evidence, test evidence, and prose evidence.
- Mention whether the repo appears production-proven, experimental, or educational if the evidence shows it.
