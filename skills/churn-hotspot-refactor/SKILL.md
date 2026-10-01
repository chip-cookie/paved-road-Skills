---
name: churn-hotspot-refactor
description: Use when a long-lived codebase feels harder to change, before planning a refactor, or when asked where technical debt is. Finds files that change often AND are complex using git history, then plans small refactors that stop complexity from growing there.
---

# Churn Hotspot Refactor

## Overview

Complexity only costs money where people keep changing the code. A messy file nobody
touches is cheap; a messy file edited every week is where bugs and slowdowns come from.
Rank files by **churn x complexity**, then refactor the top few - not the whole codebase.

## When to Use

- "Where should we refactor?" / "Where is our tech debt?"
- A platform has been maintained for years and changes are getting slower
- Before adding a feature to an area with a history of incidents

## Process

1. **Measure.** From the repository root run the bundled script (path is relative to
   this skill's directory):

   ```bash
   python3 scripts/hotspots.py --repo <repo> --since "12 months ago" --top 20 \
     --exclude "vendor/*,node_modules/*,*_test.go,tests/*"
   ```

   It prints a markdown table: hotspot score (0-1), commits, lines changed, authors,
   LOC, branch count, max nesting depth. Use `--json` for machine-readable output.
   If the script cannot run, do the same with
   `git log --since="12 months ago" --name-only --format= | sort | uniq -c | sort -rn | head -30`
   and read the top files to judge complexity.
2. **Sanity-check the top 10.** Drop generated files, fixtures, and changelogs. For each
   remaining file, read it and note *why* it churns: many features land there, unclear
   ownership, bug fixes, or config that should be data.
3. **Look for coupling.** Files that always change together point at a missing
   abstraction. For each top file, count which other files appear in the same commits:

   ```bash
   for c in $(git log --since="12 months ago" --format=%H -- <file>); do
     git show --name-only --format= "$c"
   done | sort | uniq -c | sort -rn | head
   ```
4. **Pick at most three targets.** Highest hotspot score with a clear reason to churn.
5. **Plan small, safe refactors** for each target:
   - Add characterization tests around current behavior first
   - Extract the part that changes most into its own unit (module, table, config)
   - Replace conditionals-by-customer/service with data (context, lookup tables)
   - Reduce nesting with guard clauses; split functions over ~50 lines
   - Each step is a separate, reviewable PR with no behavior change
6. **Set a ratchet.** Add a lint/complexity threshold (e.g. cyclomatic complexity per
   function) to CI for the target files so complexity cannot grow back silently.
7. **Re-measure** after a few months and compare.

## Output Format

```markdown
## Hotspot report: <repo> (<window>)
<table from script, filtered>

### Targets
1. `<file>` - why it churns - refactor plan (steps) - ratchet
```

## Red Flags

- Proposing a full rewrite instead of targeted extraction
- Refactoring files with low churn because they "look ugly"
- Refactoring without tests that pin current behavior

## Common Mistakes

- Using all-time history; old churn is less relevant. Default to 6-12 months.
- Counting lines changed only: one giant formatting commit dominates. Commits count
  is the primary signal; lines changed is secondary.
