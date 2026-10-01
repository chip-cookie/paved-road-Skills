# Contributor guide for agents

This repository is a portable skill pack. The same `skills/` folder is loaded by
Claude Code (`.claude-plugin/`), Codex CLI (`.codex-plugin/` + `.agents/plugins/`), and
Gemini CLI (`gemini-extension.json`), or copied into skill folders by `scripts/install.sh`.

## Rules for editing skills

- One skill = one folder `skills/<name>/` with a `SKILL.md`.
- `SKILL.md` must start with YAML frontmatter containing only `name` and `description`
  (other keys are not portable across agents).
- `name` must equal the folder name: lowercase letters, digits, hyphens, max 64 chars.
- `description` starts with "Use when ..." and says when to trigger, max 1024 chars,
  no angle brackets.
- Keep `SKILL.md` under ~200 lines. Put long examples in `references/` and runnable
  code in `scripts/`, and reference them by relative path.
- Skills are generic. Do not reference a specific company's internal systems.
- Update the skill list in `README.md`, `README.ko.md`, and `GEMINI.md` when adding a skill.
- Bump `version` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`,
  `.codex-plugin/plugin.json`, and `gemini-extension.json` (validate.py checks they match).

## Before committing

```bash
python3 scripts/validate.py
```
