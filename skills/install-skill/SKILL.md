---
name: install-skill
description: >-
  Install skills from this project globally for Cursor and Claude Code.
  Optionally specify skill name(s) to install specific skills.
---

Install skills from this repository using the `skills` CLI.

## Input

The user optionally provides:
- **Skill name(s)** — one or more skill names to install (e.g. `q-tree`, `ddd run-phase`). If not specified, install all skills from this project.

## Algorithm

Run the following command:

```bash
npx skills add . -g -a cursor claude-code {{SKILL_SELECT}} -y
```

Where `{{SKILL_SELECT}}`:
- If skill name(s) provided: `-s name1 -s name2` (one `-s` flag per skill)
- If no skill names: omit (installs all skills)

## After install

Report which skills were installed and where.
