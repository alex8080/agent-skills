#!/usr/bin/env python3
"""Assert a pipeline stage stayed inside its lane.

Checks, against the repo at --repo (default: cwd):
  1. HEAD still equals --baseline-sha  (the "do NOT commit" rule)
  2. every changed path matches at least one --allow glob   (if any given)
  3. no changed path matches any --deny glob                (if any given)

"Changed" = working-tree changes (staged, unstaged, untracked) UNION anything
committed since --baseline-sha, so an agent cannot hide a lane violation by
committing it.

Globs are fnmatch patterns over slash-separated repo-relative paths; `*` spans
directory separators (so `tests/acceptance/*` matches nested files).

Python 3.8+ stdlib only. Orchestrator tooling; imposes no toolchain on the
target project.
"""
import argparse
import fnmatch
import subprocess
import sys


def git(repo, *args):
    p = subprocess.run(
        ("git", "-C", repo) + args, capture_output=True, text=True
    )
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def porcelain_paths(repo):
    """Paths from `git status --porcelain -z`, including rename sources."""
    out = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    fields = out.split("\0")
    paths, i = set(), 0
    while i < len(fields):
        rec = fields[i]
        i += 1
        if not rec:
            continue
        status, path = rec[:2], rec[3:]
        paths.add(path)
        if "R" in status or "C" in status:
            if i < len(fields) and fields[i]:
                paths.add(fields[i])
            i += 1
    return paths


def matches_any(path, globs):
    return any(fnmatch.fnmatchcase(path, g) for g in globs)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline-sha", required=True,
                    help="HEAD sha captured before the stage was launched")
    ap.add_argument("--allow", action="append", default=[], metavar="GLOB",
                    help="changed paths must all match one of these (repeatable)")
    ap.add_argument("--deny", action="append", default=[], metavar="GLOB",
                    help="no changed path may match these (repeatable)")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--label", default="stage", help="name used in messages")
    args = ap.parse_args()

    try:
        head = git(args.repo, "rev-parse", "HEAD").strip()
        baseline = git(args.repo, "rev-parse", args.baseline_sha).strip()
        changed = porcelain_paths(args.repo)
        if head != baseline:
            changed |= {
                p for p in git(
                    args.repo, "diff", "--name-only", f"{baseline}..{head}"
                ).splitlines() if p
            }
    except RuntimeError as e:
        print(f"stage_guard[{args.label}]: {e}", file=sys.stderr)
        return 2

    violations = []
    if head != baseline:
        violations.append(
            f"committed during the stage: HEAD {head[:12]} != baseline {baseline[:12]} "
            "(pipeline rule: leave changes in the working tree)"
        )
    for path in sorted(changed):
        if args.allow and not matches_any(path, args.allow):
            violations.append(f"outside this stage's lane: {path}")
        if args.deny and matches_any(path, args.deny):
            violations.append(f"forbidden for this stage: {path}")

    if violations:
        for v in violations:
            print(f"stage_guard[{args.label}]: {v}", file=sys.stderr)
        return 1

    print(f"stage_guard[{args.label}]: ok ({len(changed)} changed path(s), no commits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
