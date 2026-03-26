#!/usr/bin/env python3
"""Utility script for small Brick workflows.

Subcommands:
  validate   Parse a graph and, when possible, run Brick-aware validation
  summarize  Print a compact summary of triples, types, and relationships
  query      Run a builtin or user-provided SPARQL query
  scaffold   Generate a small starter Brick model from JSON inventory

The script intentionally works with standard Python plus rdflib.
If the optional ``brickschema`` package is installed, ``validate`` can also
run Brick-aware validation.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Optional

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

BRICK = Namespace("https://brickschema.org/schema/Brick#")

BUILTIN_QUERIES = {
    "equipment-points": """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?equip ?equipType ?point ?pointType WHERE {
  ?equip brick:hasPoint ?point .
  ?equip rdf:type ?equipType .
  ?point rdf:type ?pointType .
}
ORDER BY ?equip ?point
""",
    "locations": """
PREFIX brick: <https://brickschema.org/schema/Brick#>
SELECT ?entity ?location WHERE {
  ?entity brick:hasLocation ?location .
}
ORDER BY ?entity
""",
    "feeds": """
PREFIX brick: <https://brickschema.org/schema/Brick#>
SELECT ?upstream ?downstream WHERE {
  ?upstream brick:feeds ?downstream .
}
ORDER BY ?upstream ?downstream
""",
    "types": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?type (COUNT(?entity) AS ?count) WHERE {
  ?entity rdf:type ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
""",
}

COMMON_RELATIONSHIPS = [
    BRICK.hasPoint,
    BRICK.isPointOf,
    BRICK.hasLocation,
    BRICK.isLocationOf,
    BRICK.hasPart,
    BRICK.isPartOf,
    BRICK.feeds,
    BRICK.isFedBy,
]


def infer_format(path: Path, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    suffix = path.suffix.lower()
    if suffix in {".ttl", ".turtle"}:
        return "turtle"
    if suffix == ".nt":
        return "nt"
    if suffix == ".n3":
        return "n3"
    if suffix == ".xml":
        return "xml"
    if suffix == ".jsonld":
        return "json-ld"
    return "turtle"


def load_graph(path: Path, fmt: Optional[str]) -> Graph:
    graph = Graph()
    graph.parse(path.as_posix(), format=infer_format(path, fmt))
    return graph


def short(uri) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text:
        return text.rstrip("/").rsplit("/", 1)[-1]
    return text


def summarize_graph(graph: Graph) -> dict:
    type_counter: Counter[str] = Counter()
    rel_counter: Counter[str] = Counter()
    untyped_subjects = set()
    typed_subjects = set(graph.subjects(RDF.type, None))

    for _, _, obj in graph.triples((None, RDF.type, None)):
        type_counter[short(obj)] += 1

    for rel in COMMON_RELATIONSHIPS:
        rel_counter[short(rel)] = sum(1 for _ in graph.triples((None, rel, None)))

    subjects = set(graph.subjects())
    for subj in subjects:
        if (subj, RDF.type, None) not in graph:
            untyped_subjects.add(subj)

    return {
        "triples": len(graph),
        "typed_subjects": len(typed_subjects),
        "untyped_subjects": len(untyped_subjects),
        "top_types": type_counter.most_common(15),
        "relationships": {name: count for name, count in rel_counter.items() if count},
    }


def print_summary(summary: dict) -> None:
    print(f"Triples: {summary['triples']}")
    print(f"Typed subjects: {summary['typed_subjects']}")
    print(f"Untyped subjects: {summary['untyped_subjects']}")
    print("\nTop types:")
    if summary["top_types"]:
        for name, count in summary["top_types"]:
            print(f"  {name}: {count}")
    else:
        print("  none")
    print("\nBrick relationships present:")
    if summary["relationships"]:
        for name, count in summary["relationships"].items():
            print(f"  {name}: {count}")
    else:
        print("  none")


def lint_graph(graph: Graph) -> list[str]:
    warnings: list[str] = []

    pointish = set(graph.subjects(RDF.type, BRICK.Point))
    sensorish = set(graph.subjects(RDF.type, BRICK.Sensor))
    commandish = set(graph.subjects(RDF.type, BRICK.Command))
    setpointish = set(graph.subjects(RDF.type, BRICK.Setpoint))
    interesting_points = pointish | sensorish | commandish | setpointish

    for entity in sorted(interesting_points, key=str):
        has_up = (entity, BRICK.isPointOf, None) in graph
        has_down = (None, BRICK.hasPoint, entity) in graph
        if not (has_up or has_down):
            warnings.append(
                f"Point-like entity without hasPoint/isPointOf linkage: {entity}"
            )

    for subj, _, obj in graph.triples((None, BRICK.hasLocation, None)):
        if (obj, RDF.type, BRICK.Equipment) in graph:
            warnings.append(
                f"Entity {subj} hasLocation equipment {obj}; check whether this should be hasPart or isPartOf instead"
            )

    for subj in set(graph.subjects()) | set(graph.objects()):
        if isinstance(subj, URIRef) and (subj, RDF.type, None) not in graph:
            if any((subj, rel, None) in graph or (None, rel, subj) in graph for rel in COMMON_RELATIONSHIPS):
                warnings.append(f"Entity participates in Brick relationships but has no explicit rdf:type: {subj}")

    return sorted(set(warnings))


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve()
    graph = load_graph(path, args.format)
    print(f"Parsed graph successfully: {path}")
    print(f"Triples: {len(graph)}")

    warnings = lint_graph(graph)
    if warnings:
        print("\nHeuristic warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\nHeuristic warnings: none")

    try:
        import brickschema  # type: ignore
    except Exception:
        print(
            "\nBrick-aware validation: unavailable (optional package 'brickschema' is not installed)."
        )
        return 0

    try:
        bgraph = brickschema.Graph(load_brick=True)
        bgraph.parse(path.as_posix(), format=infer_format(path, args.format))
        valid, _, results_text = bgraph.validate()
        print(f"\nBrick-aware validation: {'valid' if valid else 'invalid'}")
        if results_text:
            print(results_text)
        return 0 if valid else 2
    except Exception as exc:
        print(f"\nBrick-aware validation failed to run: {exc}")
        return 1


def cmd_summarize(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve()
    graph = load_graph(path, args.format)
    summary = summarize_graph(graph)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_summary(summary)
    return 0


def format_cell(value) -> str:
    if value is None:
        return ""
    return str(value)


def cmd_query(args: argparse.Namespace) -> int:
    path = Path(args.input).resolve()
    graph = load_graph(path, args.format)

    if args.builtin:
        query_text = BUILTIN_QUERIES[args.builtin]
    elif args.query_file:
        query_text = Path(args.query_file).read_text()
    elif args.query:
        query_text = args.query
    else:
        raise ValueError("Provide --builtin, --query-file, or --query")

    results = list(graph.query(query_text))
    print(f"Rows: {len(results)}")
    for row in results:
        print("\t".join(format_cell(item) for item in row))
    return 0


def sanitize_identifier(text: str) -> str:
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch == "_":
            cleaned.append(ch)
        elif ch in {"-", ".", "/", " ", ":"}:
            cleaned.append("_")
    out = "".join(cleaned).strip("_")
    return out or "entity"


def ttl_line(subject: str, predicate: str, obj: str, end: str = " .") -> str:
    return f"{subject} {predicate} {obj}{end}"


def scaffold_ttl(spec: dict) -> str:
    namespace = spec.get("namespace", "urn:site#")
    if not namespace.endswith(("#", "/")):
        namespace = namespace + "#"

    lines = [
        "@prefix brick: <https://brickschema.org/schema/Brick#> .",
        "@prefix site: <" + namespace + "> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "",
    ]

    def ref(name: str) -> str:
        return "site:" + sanitize_identifier(name)

    building = spec.get("building")
    if building:
        lines.append(ttl_line(ref(building), "a", f"brick:{spec.get('building_class', 'Building')}"))
        lines.append("")

    for space in spec.get("spaces", []):
        sid = ref(space["id"])
        sclass = space.get("class", "Room")
        lines.append(ttl_line(sid, "a", f"brick:{sclass}"))
        parent = space.get("part_of")
        if parent:
            lines.append(ttl_line(sid, "brick:isPartOf", ref(parent)))
        lines.append("")

    for equip in spec.get("equipment", []):
        eid = ref(equip["id"])
        eclass = equip.get("class", "Equipment")
        lines.append(ttl_line(eid, "a", f"brick:{eclass}"))
        if equip.get("location"):
            lines.append(ttl_line(eid, "brick:hasLocation", ref(equip["location"])))
        for downstream in equip.get("feeds", []):
            lines.append(ttl_line(eid, "brick:feeds", ref(downstream)))

        for part in equip.get("parts", []):
            pid = ref(part["id"])
            pclass = part.get("class", "Equipment")
            lines.append(ttl_line(pid, "a", f"brick:{pclass}"))
            lines.append(ttl_line(eid, "brick:hasPart", pid))

        for point in equip.get("points", []):
            pid = ref(point["id"])
            pclass = point.get("class", "Point")
            lines.append(ttl_line(pid, "a", f"brick:{pclass}"))
            lines.append(ttl_line(eid, "brick:hasPoint", pid))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def cmd_scaffold(args: argparse.Namespace) -> int:
    spec = json.loads(Path(args.input).read_text())
    ttl = scaffold_ttl(spec)
    if args.output:
        Path(args.output).write_text(ttl)
        print(f"Wrote scaffold to {args.output}")
    else:
        print(ttl)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Brick helper utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--input", required=True, help="Path to input file")
    common.add_argument("--format", default=None, help="RDF format override")

    p_validate = sub.add_parser("validate", parents=[common], help="Parse and validate a Brick graph")
    p_validate.set_defaults(func=cmd_validate)

    p_summarize = sub.add_parser("summarize", parents=[common], help="Summarize a Brick graph")
    p_summarize.add_argument("--json", action="store_true", help="Emit JSON")
    p_summarize.set_defaults(func=cmd_summarize)

    p_query = sub.add_parser("query", parents=[common], help="Run SPARQL against a graph")
    p_query.add_argument("--builtin", choices=sorted(BUILTIN_QUERIES), help="Builtin query name")
    p_query.add_argument("--query-file", help="Path to a SPARQL query file")
    p_query.add_argument("--query", help="Inline SPARQL query text")
    p_query.set_defaults(func=cmd_query)

    p_scaffold = sub.add_parser("scaffold", help="Create a starter Brick model from JSON inventory")
    p_scaffold.add_argument("--input", required=True, help="Path to JSON spec")
    p_scaffold.add_argument("--output", help="Optional output TTL path")
    p_scaffold.set_defaults(func=cmd_scaffold)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
