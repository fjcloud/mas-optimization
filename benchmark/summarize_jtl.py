#!/usr/bin/env python3
"""Quick summary of a JMeter .jtl (CSV) result file."""

from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from typing import Dict, List


def pct(vals: List[float], p: float) -> float:
    s = sorted(vals)
    return s[min(len(s) - 1, int(len(s) * p))]


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("usage: summarize_jtl.py <file.jtl>", file=sys.stderr)
        sys.exit(2)

    by_label: Dict[str, List[float]] = defaultdict(list)
    ok = fail = 0
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("label") or row.get("Label") or "?"
            try:
                elapsed = float(row.get("elapsed") or row.get("Elapsed") or 0)
            except ValueError:
                continue
            success = (row.get("success") or row.get("Success") or "true").lower() == "true"
            if success:
                ok += 1
                by_label[label].append(elapsed)
            else:
                fail += 1
                by_label[label].append(elapsed)

    print(f"samples ok={ok} fail={fail} total={ok+fail}")
    print(f"{'label':48} {'n':>6} {'p50':>8} {'p95':>8} {'max':>8}")
    rows = []
    for label, vals in by_label.items():
        rows.append(
            (
                len(vals),
                label,
                statistics.median(vals),
                pct(vals, 0.95),
                max(vals),
            )
        )
    for n, label, p50, p95, mx in sorted(rows, key=lambda r: -r[0])[:40]:
        print(f"{label[:48]:48} {n:6} {p50:8.0f} {p95:8.0f} {mx:8.0f}")


if __name__ == "__main__":
    main()
