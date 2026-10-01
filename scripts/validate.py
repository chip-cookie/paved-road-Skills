#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md for cross-agent portability. Stdlib only."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description"}
errors = []


def parse_frontmatter(text, where):
    if not text.startswith("---\n"):
        errors.append(f"{where}: must start with '---' frontmatter on line 1")
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{where}: unterminated frontmatter")
        return {}
    fm = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"{where}: bad frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
for skill in skills:
    md = skill / "SKILL.md"
    where = str(md.relative_to(ROOT))
    if not md.exists():
        errors.append(f"{skill.name}: missing SKILL.md")
        continue
    text = md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text, where)
    name, desc = fm.get("name", ""), fm.get("description", "")
    if extra := set(fm) - ALLOWED_KEYS:
        errors.append(f"{where}: non-portable frontmatter keys {sorted(extra)}")
    if name != skill.name:
        errors.append(f"{where}: name '{name}' must equal folder '{skill.name}'")
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{where}: invalid name '{name}'")
    if not desc:
        errors.append(f"{where}: missing description")
    elif len(desc) > 1024 or "<" in desc or ">" in desc:
        errors.append(f"{where}: description too long or contains angle brackets")
    elif not desc.startswith("Use when"):
        errors.append(f"{where}: description should start with 'Use when'")
    if text.count("\n") > 250:
        errors.append(f"{where}: over 250 lines; move detail into references/")
    for ref in re.findall(r"`((?:references|scripts)/[^`\s]+)`", text):
        if not (skill / ref).exists():
            errors.append(f"{where}: references missing file {ref}")

versions = {}
for manifest in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                 ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json",
                 "gemini-extension.json"):
    try:
        data = json.loads((ROOT / manifest).read_text(encoding="utf-8"))
        if "version" in data:
            versions[manifest] = data["version"]
        for entry in data.get("plugins", []):
            if "version" in entry:
                versions[manifest + " plugins[]"] = entry["version"]
    except Exception as e:  # noqa: BLE001
        errors.append(f"{manifest}: {e}")
if len(set(versions.values())) > 1:
    errors.append(f"version mismatch: {versions}")

for doc in ("README.md", "README.ko.md", "GEMINI.md"):
    text = (ROOT / doc).read_text(encoding="utf-8") if (ROOT / doc).exists() else ""
    for skill in skills:
        if skill.name not in text:
            errors.append(f"{doc}: skill '{skill.name}' not listed")

if errors:
    print("\n".join(f"FAIL {e}" for e in errors))
    sys.exit(1)
print(f"OK  {len(skills)} skills valid: {', '.join(s.name for s in skills)}")
