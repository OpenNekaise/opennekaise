#!/usr/bin/env python3
"""Inventory noisy building point labels.

Accepts either:
- a plain text file with one label per line, or
- a CSV/TSV file, using ``--column`` or the first populated column.

Outputs the most common labels, tokens, prefixes, suffixes, and short tokens.
This is useful before mapping BAS labels to Brick classes.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List

CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")


def read_labels(path: Path, column: str | None) -> List[str]:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            rows = list(reader)
        if not rows:
            return []
        chosen = column
        if chosen is None:
            for candidate in reader.fieldnames or []:
                if any((row.get(candidate) or "").strip() for row in rows):
                    chosen = candidate
                    break
        if chosen is None:
            return []
        return [
            (row.get(chosen) or "").strip()
            for row in rows
            if (row.get(chosen) or "").strip()
        ]

    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def tokenize(label: str) -> List[str]:
    spaced = CAMEL_RE.sub(" ", label)
    raw_tokens = SPLIT_RE.split(spaced)
    return [token.lower() for token in raw_tokens if token]


def prefix_suffix(label: str) -> tuple[str | None, str | None]:
    for sep in ["/", ".", "-", "_", ":", " "]:
        if sep in label:
            parts = [part for part in label.split(sep) if part]
            if len(parts) >= 2:
                return parts[0].lower(), parts[-1].lower()
    return None, None


def summarize(labels: Iterable[str]) -> dict:
    labels = [label for label in labels if label]
    token_counter: Counter[str] = Counter()
    label_counter: Counter[str] = Counter(labels)
    prefix_counter: Counter[str] = Counter()
    suffix_counter: Counter[str] = Counter()
    short_counter: Counter[str] = Counter()

    for label in labels:
        tokens = tokenize(label)
        token_counter.update(tokens)
        prefix, suffix = prefix_suffix(label)
        if prefix:
            prefix_counter[prefix] += 1
        if suffix:
            suffix_counter[suffix] += 1
        for token in tokens:
            if 1 <= len(token) <= 5:
                short_counter[token] += 1

    return {
        "labels": len(labels),
        "unique_labels": len(label_counter),
        "top_labels": label_counter.most_common(20),
        "top_tokens": token_counter.most_common(30),
        "top_prefixes": prefix_counter.most_common(20),
        "top_suffixes": suffix_counter.most_common(20),
        "short_tokens": short_counter.most_common(30),
    }


def print_summary(summary: dict) -> None:
    print(f"Labels: {summary['labels']}")
    print(f"Unique labels: {summary['unique_labels']}")
    for key, title in [
        ("top_labels", "Top labels"),
        ("top_tokens", "Top tokens"),
        ("top_prefixes", "Top prefixes"),
        ("top_suffixes", "Top suffixes"),
        ("short_tokens", "Short tokens and abbreviations"),
    ]:
        print(f"\n{title}:")
        rows = summary[key]
        if not rows:
            print("  none")
            continue
        for value, count in rows:
            print(f"  {value}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory tokens in noisy BAS labels")
    parser.add_argument("input", help="Path to labels file")
    parser.add_argument("--column", help="CSV or TSV column to use")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    labels = read_labels(Path(args.input).resolve(), args.column)
    summary = summarize(labels)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
