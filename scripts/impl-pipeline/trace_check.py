#!/usr/bin/env python3
"""Check agent 2's traceability table covers every spec scenario, exactly once.

Table format (one row per scenario; markdown pipe table, header and `---`
separator rows optional and ignored):

    | Scenario | Layer | Target |
    | --- | --- | --- |
    | Rejects an expired token | acceptance | tests/acceptance/auth_test.py::test_expired_token |
    | Counts distinct tags | unit | src/tags_test.py::test_distinct |
    | Empty input yields empty output | existing | tests/unit/parse_test.py::test_empty |

Layer is one of: acceptance, unit, existing. Target must be `<file>::<test_name>`.
Scenario text must match the spec's `### Scenario:` heading exactly.

Python 3.8+ stdlib only. Orchestrator tooling; imposes no toolchain on the
target project.
"""
import argparse
import sys

from scenarios import parse_scenarios

LAYERS = ("acceptance", "unit", "existing")


def parse_table(text):
    """-> (rows, malformed) where rows is [(scenario, layer, target, lineno)]."""
    rows, malformed = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) < 3:
            malformed.append((lineno, line, "expected 3 columns"))
            continue
        scenario, layer, target = cells[0], cells[1].lower(), cells[2]
        if scenario.lower() in ("scenario", "scenarios"):
            continue
        target = target.strip("`")
        rows.append((scenario, layer, target, lineno))
    return rows, malformed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to the spec markdown file")
    ap.add_argument("table", help="path to the traceability table, or - for stdin")
    args = ap.parse_args()

    try:
        with open(args.spec, encoding="utf-8") as f:
            scenarios = parse_scenarios(f.read())
        table_text = sys.stdin.read() if args.table == "-" else \
            open(args.table, encoding="utf-8").read()
    except OSError as e:
        print(f"trace_check: {e}", file=sys.stderr)
        return 2

    if not scenarios:
        print(f"trace_check: no '### Scenario:' headings in {args.spec}", file=sys.stderr)
        return 2

    rows, malformed = parse_table(table_text)
    problems = [f"line {n}: {why}: {line}" for n, line, why in malformed]

    seen = {}
    for scenario, layer, target, lineno in rows:
        seen.setdefault(scenario, []).append(lineno)
        if layer not in LAYERS:
            problems.append(f"line {lineno}: layer must be one of {'/'.join(LAYERS)}, got '{layer}'")
        if "::" not in target or target.startswith("::") or target.endswith("::"):
            problems.append(f"line {lineno}: target must be <file>::<test_name>, got '{target}'")

    for s in scenarios:
        if s not in seen:
            problems.append(f"scenario not traced to any test: {s}")
        elif len(seen[s]) > 1:
            problems.append(f"scenario traced more than once (lines {seen[s]}): {s}")
    for s in seen:
        if s not in scenarios:
            problems.append(f"table row matches no spec scenario (typo or stale?): {s}")

    if problems:
        for p in problems:
            print(f"trace_check: {p}", file=sys.stderr)
        return 1

    print(f"trace_check: ok ({len(scenarios)} scenario(s) traced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
