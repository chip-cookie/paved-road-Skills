#!/usr/bin/env python3
"""Rank files by churn x complexity using git history. Stdlib only.

Usage:
  python3 hotspots.py [--repo .] [--since "12 months ago"] [--top 20]
                      [--include "*.py,*.go"] [--exclude "tests/*,vendor/*"] [--json]

Churn      = number of commits touching the file in the window (plus lines changed).
Complexity = branching keywords + indentation depth, a language-agnostic proxy.
Score      = churn_rank_pct * complexity_rank_pct  (0..1, higher = hotter)
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

BRANCH_RE = re.compile(
    r"\b(?:if|elif|for|foreach|while|case|when|catch|except|switch|match|unless)\b|&&|\|\||\band\b|\bor\b"
)
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".lock", ".min.js",
            ".map", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".json", ".md", ".txt"}


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"git error: {out.stderr.strip()}")
    return out.stdout


def churn(repo, since):
    commits = defaultdict(int)
    lines = defaultdict(int)
    authors = defaultdict(set)
    log = git(repo, "log", f"--since={since}", "--no-merges", "--numstat",
              "--format=@@%an")
    author = None
    for row in log.splitlines():
        if row.startswith("@@"):
            author = row[2:]
            continue
        parts = row.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if "=>" in path:  # rename: keep the new path
            path = re.sub(r"\{.*? => (.*?)\}", r"\1", path).split(" => ")[-1]
        commits[path] += 1
        if added.isdigit() and deleted.isdigit():
            lines[path] += int(added) + int(deleted)
        authors[path].add(author)
    return commits, lines, authors


def complexity(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            src = f.readlines()
    except OSError:
        return None
    branches = 0
    max_indent = 0
    total_indent = 0
    code_lines = 0
    for line in src:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "*", "/*")):
            continue
        code_lines += 1
        expanded = line.expandtabs(4)
        indent = (len(expanded) - len(expanded.lstrip())) // 4
        max_indent = max(max_indent, indent)
        total_indent += indent
        branches += len(BRANCH_RE.findall(stripped))
    if code_lines == 0:
        return None
    return {"loc": code_lines, "branches": branches, "max_depth": max_indent,
            "score": branches + total_indent / 4}


def pct_rank(values):
    ordered = sorted(values)
    n = len(ordered)
    return {v: (ordered.index(v) + 1) / n for v in set(values)} if n else {}


def matches(path, patterns):
    return any(fnmatch.fnmatch(path, p.strip()) for p in patterns if p.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--since", default="12 months ago")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--include", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = git(a.repo, "rev-parse", "--show-toplevel").strip()
    commits, lines, authors = churn(root, a.since)
    inc = a.include.split(",") if a.include else []
    exc = a.exclude.split(",") if a.exclude else []

    rows = []
    for path, n in commits.items():
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            continue  # deleted since
        if any(path.endswith(e) for e in SKIP_EXT):
            continue
        if inc and not matches(path, inc):
            continue
        if exc and matches(path, exc):
            continue
        c = complexity(full)
        if c is None:
            continue
        rows.append({"path": path, "commits": n, "lines_changed": lines[path],
                     "authors": len(authors[path]), **c})

    if not rows:
        sys.exit("no candidate files found (check --since / --include)")

    churn_pct = pct_rank([r["commits"] for r in rows])
    cx_pct = pct_rank([r["score"] for r in rows])
    for r in rows:
        r["hotspot"] = round(churn_pct[r["commits"]] * cx_pct[r["score"]], 3)
    rows.sort(key=lambda r: (r["hotspot"], r["commits"]), reverse=True)
    rows = rows[: a.top]

    if a.json:
        print(json.dumps(rows, indent=2))
        return
    print(f"# Churn x complexity hotspots (since {a.since})\n")
    print("| # | file | hotspot | commits | lines changed | authors | LOC | branches | max depth |")
    print("|---|------|---------|---------|---------------|---------|-----|----------|-----------|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | `{r['path']}` | {r['hotspot']} | {r['commits']} | {r['lines_changed']} "
              f"| {r['authors']} | {r['loc']} | {r['branches']} | {r['max_depth']} |")


if __name__ == "__main__":
    main()
