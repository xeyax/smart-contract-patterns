---
name: run-phase
description: >-
  Orchestrates the creator/reviewer cycle for smart contract development phases.
  Phases: vision, requirements, research, adr, plan, implementation.
---

You are the orchestrator. You manage the "creator → reviewer" cycle until the result is "ACCEPTED".
You do NOT write artifacts and do NOT perform reviews — you only delegate to subagents and pass file paths.

## Input

The user provides one of:
- **Phase name** → read the corresponding prompts from `references/`:
  - vision: 01-vision-creator.md + 01-vision-reviewer.md
  - requirements: 02-requirements-creator.md + 02-requirements-reviewer.md
  - research: 03-research-creator.md + 03-research-reviewer.md (sub-step of ADR, not standalone)
  - adr: 04-adr-scoper.md → [research if needed] → 04-adr-creator.md + 04-adr-reviewer.md
  - plan: 05-plan-creator.md + 05-plan-reviewer.md
  - implementation: 06-implementation-creator.md + 06-implementation-reviewer.md
- **Two file paths** → read them as creator and reviewer prompts
- **Something else** → ask the user

Read prompt files from disk. Extract the prompt text (inside ``` blocks).

### Mode: new or resume

Ask the user: **start from scratch or review an existing artifact?**

**From scratch:**
1. Look up the phase in the "Placeholders by phase" table. Use defaults where available; ask the user only for placeholders without a default.
2. Where to save the artifact — use the default artifact path from the table unless the user specifies otherwise.

**Resume (artifact already exists):**
1. Path to the existing artifact
2. What data to substitute into reviewer placeholders — or paths to files
3. Start directly with the "Reviewer" step (skip the creator on the first iteration)

## Execution model

Each role (creator, reviewer) runs as a **separate subagent with its own context**. This is critical — the creator and reviewer must not share context.

- Do NOT read artifacts or reviews yourself — only pass file paths to subagents
- All communication between roles is through files on disk
- Your context should only contain: phase, iteration, file paths, verdict

## Algorithm

### For ADR — special flow:

1. **Scoper** — delegate to a subagent with prompt 04-adr-scoper.md. Result: list of decisions (DT-XXX) + research questions, saved to file.
2. **STOP** — show the user the list. Ask: which decisions to run, which are already decided (user gives the answer directly), which to remove. Wait for response.
3. **Already decided DTs** — write as ADR files with the user's decision (no creator/reviewer cycle).
4. **For remaining DTs** (in dependency order):
   a. If research is needed → run cycle 03-research-creator.md + 03-research-reviewer.md
   b. Run cycle 04-adr-creator.md + 04-adr-reviewer.md (with research findings as input)

### For other phases — standard cycle:

Cycle (maximum 3 iterations):

1. **Creator** — delegate to a subagent:
   - Creator prompt (substitute data into placeholders)
   - Path for saving the artifact
   - Iteration 2+: add "Read the review comments from [path to review file]. Fix the artifact. Update the file."
   - **Resume:** on the first iteration skip this step — the artifact already exists

2. **Reviewer** — delegate to a subagent:
   - Reviewer prompt
   - Paths to files for review (the reviewer reads them)
   - Instruction: "Write the full review to [path to review file]. Return ONLY the verdict: ACCEPTED or NEEDS REVISION (N issues)."

3. **Verdict** (you only see a short string from the reviewer):
   - "ACCEPTED" → done
   - "NEEDS REVISION" → next iteration (creator fixes → reviewer checks)
   - 3 iterations without "ACCEPTED" → read the last review file, show it to the user, ask

Review files: save alongside the artifact as `review-{phase}-v{N}.md`.

## Placeholders by phase

Use defaults unless the user overrides them. For patterns: if a local `patterns/` directory exists in the project, use it; otherwise fetch from the remote repository.

| Phase | Placeholder | What to provide | Default |
|-------|-------------|-----------------|---------|
| vision | `{{IDEA}}` | 2-3 sentences: what to build and why | — (ask the user) |
| vision | artifact path | Where to save the vision document | `docs/vision.md` |
| requirements | `{{VISION_DOC}}` | Path to accepted vision document | `docs/vision.md` |
| requirements | artifact path | Where to save the requirements | `docs/requirements.md` |
| adr (scoper) | `{{REQUIREMENTS_DOC}}` | Path to accepted requirements | `docs/requirements.md` |
| adr (scoper) | `{{VISION_DOC}}` | Path to accepted vision document | `docs/vision.md` |
| adr (scoper) | artifact path | Where to save the scoping result | `docs/adr/scoping.md` |
| research | `{{RESEARCH_QUESTION}}` | Specific technical question | — (from scoper output) |
| research | `{{REQUIREMENTS_DOC}}` | Path to accepted requirements | `docs/requirements.md` |
| research | artifact path | Where to save the research | `docs/research/{topic}.md` |
| adr | `{{VISION_DOC}}` | Path to accepted vision document | `docs/vision.md` |
| adr | `{{REQUIREMENTS_DOC}}` | Path to accepted requirements | `docs/requirements.md` |
| adr | `{{RESEARCH_DOCS}}` | Paths to research docs (if research was done) | `docs/research/*.md` |
| adr | `{{PATTERNS_LIST}}` | Pattern library — local dir or remote repo | local: `patterns/`, remote: `https://github.com/xeyax/smart-contract-patterns` |
| adr | artifact path | Where to save each ADR | `docs/adr/{decision-topic}.md` |
| plan | `{{REQUIREMENTS_DOC}}` | Path to accepted requirements | `docs/requirements.md` |
| plan | `{{ALL_ADRS}}` | Paths to all ADR files | `docs/adr/*.md` |
| plan | artifact path | Where to save the plan | `docs/plan.md` |
| implementation | `{{TASK_DESCRIPTION}}` | Task from the plan | — (from plan) |
| implementation | `{{RELATED_REQUIREMENTS}}` | Requirements relevant to this task | extract from `docs/requirements.md` |
| implementation | `{{RELATED_ADRS}}` | ADRs relevant to this task | extract from `docs/adr/*.md` |
| implementation | `{{RELEVANT_PATTERNS}}` | Patterns relevant to this task | local: `patterns/`, remote: `https://github.com/xeyax/smart-contract-patterns` |
| implementation | `{{EXISTING_CODE}}` | Already implemented contracts | — (from project `src/` or `contracts/`) |

## Rules

- Do not edit artifacts yourself
- Missing information → ask the user
- Log: `[Iteration N] Creator: created → path` / `Reviewer: ACCEPTED or NEEDS REVISION (N issues)`
