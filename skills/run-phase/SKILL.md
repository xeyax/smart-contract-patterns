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

1. **Scoper (initial)** — delegate to a subagent with 04-adr-scoper.md (initial run prompt). Result: constraints, grouped decisions, research needs, execution order. Save to scoping file.

2. **STOP** — present the scoping result to the user with these guiding questions:
   - "Are the extracted constraints correct? Anything missing?" (e.g., target network, protocol compatibility, budget)
   - "Are there decisions you've already made? State them and I'll record as ADRs without a full cycle."
   - "Are there decisions where you have a strong preference or inputs for the team?"
   - "Anything missing from the list? Anything that should be removed?"
   - "Which decisions feel unclear — where do you want research help? Any hints on where to look?"
   Wait for response.

3. **Scoper (refinement)** — delegate to a subagent with 04-adr-scoper.md (refinement run prompt). Pass the current scoping file + user feedback. Result: updated scope with statuses (DECIDED / NEEDS RESEARCH / READY FOR ADR / REMOVED) and directions for each DT. **Overwrites the scoping file.**

4. **Process by status** (in the execution order from the refined scope):

   Naming: DT-001 → `ADR-001.md` + `ADR-001-analysis.md`, etc.

   The creator produces two files per ADR:
   - `ADR-{NNN}.md` — compact decision (summary, decision, consequences)
   - `ADR-{NNN}-analysis.md` — full reasoning (context, options, rationale)

   By status:
   - **DECIDED** → write as ADR decision file directly from the scope (no analysis file, no cycle needed)
   - **NEEDS RESEARCH** → run research cycle (03-research-creator.md + 03-research-reviewer.md), passing the research directions from the scope.
   - **NEEDS RESEARCH / READY FOR ADR** → create ADR (both files) via 04-adr-creator.md, passing developer input and research findings from the scope.

5. **Review by group** — the scoper groups related decisions into clusters. Review follows the same grouping:

   - **Single-DT group** → review immediately after creating that ADR.
   - **Multi-DT group** → create ALL ADRs in the group first, then run ONE review covering all of them together. The reviewer checks each ADR individually AND cross-checks consistency between them.

   Pass all ADR files (both decision and analysis) in the group to the reviewer. The reviewer writes a single review file per group to `docs/adr/.reviews/` (e.g., `docs/adr/.reviews/review-group-1-v1.md`).

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

Review files: save to a `.reviews/` subdirectory next to the artifact (e.g., `docs/.reviews/review-vision-v1.md`, `docs/adr/.reviews/review-ADR-001-v1.md`).

## Developer interaction by phase

Before running the creator and after receiving reviewer feedback, ask the user targeted questions to improve artifact quality and avoid wasted iterations.

### Vision

**Before creator** (after receiving the idea):
- "Who are the main users? What situation are they in?"
- "What solutions do they use now? What's wrong with them?"
- "How would you measure success?"
- "What should definitely NOT be in scope?"

Incorporate answers into `{{IDEA}}` before passing to the creator.

**After reviewer** (if NEEDS REVISION):
- Present the reviewer's REMOVE/REWRITE suggestions and ask: "Do you agree with these cuts, or is something important being removed?"

### Requirements

**Before creator** (after vision is accepted):
- "Any hard technical constraints?" (target chain, gas limits, must integrate with protocol X)
- "Any specific security concerns beyond the standard?" (multisig, timelock, specific attack vectors you worry about)
- "Is there an MVP scope — what must be in v1 vs. can wait?"

Pass answers as additional context to the creator alongside `{{VISION_DOC}}`.

**After reviewer** (if NEEDS REVISION):
- Present the reviewer's KEEP/REWRITE/REMOVE/DEFER categorization and ask: "Do you agree with the REMOVE and DEFER items?"

### ADR

No additional questions before creator — the scoper pause already gathers all necessary input from the developer.

### Plan, Implementation

No phase-specific questions — the standard cycle is sufficient.

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
| adr | artifact path | Where to save each ADR decision | `docs/adr/ADR-{NNN}.md` (e.g., `ADR-001.md`) |
| adr | analysis path | Where to save each ADR analysis | `docs/adr/ADR-{NNN}-analysis.md` |
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
