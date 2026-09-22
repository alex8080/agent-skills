#!/usr/bin/env python3
"""List the `### Scenario:` headings in a spec, in document order.

Python 3.8+ stdlib only. Orchestrator tooling; imposes no toolchain on the
target project.
"""
import argparse
import json
import re
import sys

SCENARIO_RE = re.compile(r"^###\s+Scenario:\s*(\S.*?)\s*$")


def parse_scenarios(text):
    return [m.group(1) for m in (SCENARIO_RE.match(l) for l in text.splitlines()) if m]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", help="path to the spec markdown file")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    args = ap.parse_args()

    try:
        with open(args.spec, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"scenarios: cannot read spec: {e}", file=sys.stderr)
        return 2

    scenarios = parse_scenarios(text)
    if not scenarios:
        print(
            f"scenarios: no '### Scenario:' headings found in {args.spec} "
            "(wrong file, or spec does not follow the scenario convention)",
            file=sys.stderr,
        )
        return 1

    dupes = sorted({s for s in scenarios if scenarios.count(s) > 1})
    if dupes:
        for d in dupes:
            print(f"scenarios: duplicate scenario title: {d}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(scenarios, indent=2))
    else:
        for s in scenarios:
            print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
