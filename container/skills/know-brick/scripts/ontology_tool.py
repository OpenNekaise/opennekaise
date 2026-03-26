#!/usr/bin/env python3
"""
Building ontology tool for Nekaise Agent.

Handles RDF/TTL parsing, SPARQL queries, model creation, validation,
and topology analysis for Brick Schema and ASHRAE 223P ontologies.

Self-bootstrapping: installs rdflib into a persistent venv on first use.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def _resolve_dir(primary, fallback):
    """Use primary path if its parent exists, otherwise fallback."""
    p = Path(primary)
    if p.parent.exists():
        return p
    return Path(fallback)

VENV_DIR = _resolve_dir("/workspace/group/.ontology-venv", Path.home() / ".ontology-venv")
CACHE_DIR = _resolve_dir("/workspace/group/.ontology-cache", Path.home() / ".ontology-cache")

BRICK_NS = "https://brickschema.org/schema/Brick#"
S223_NS = "http://data.ashrae.org/standard223#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
QUDT_NS = "http://qudt.org/schema/qudt/"
UNIT_NS = "http://qudt.org/vocab/unit/"
QK_NS = "http://qudt.org/vocab/quantitykind/"

BRICK_URL = "https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl"
S223_URL = "https://open223.info/223p.ttl"


def ensure_rdflib():
    """Install rdflib into a persistent venv if not already available."""
    try:
        import rdflib  # noqa: F401
        return
    except ImportError:
        pass

    venv_python = VENV_DIR / "bin" / "python3"
    if venv_python.exists():
        # Venv exists but we're not running from it — re-exec
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)

    print(f"Installing rdflib into {VENV_DIR}...", file=sys.stderr)
    subprocess.check_call(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    pip = str(VENV_DIR / "bin" / "pip")
    subprocess.check_call(
        [pip, "install", "--quiet", "rdflib"],
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    print("rdflib installed successfully.", file=sys.stderr)
    # Re-exec with the venv python
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)


ensure_rdflib()

from rdflib import Graph, Namespace, URIRef, Literal, BNode  # noqa: E402
from rdflib.namespace import RDF, RDFS, OWL, XSD  # noqa: E402

BRICK = Namespace(BRICK_NS)
S223 = Namespace(S223_NS)
QUDT = Namespace(QUDT_NS)
UNIT = Namespace(UNIT_NS)
QK = Namespace(QK_NS)


def shorten(uri, g=None):
    """Shorten a URI to prefix:local form."""
    if isinstance(uri, BNode):
        return f"_:{uri}"
    if isinstance(uri, Literal):
        return f'"{uri}"'
    uri_str = str(uri)
    prefixes = {
        BRICK_NS: "brick:",
        S223_NS: "s223:",
        RDF_NS: "rdf:",
        RDFS_NS: "rdfs:",
        OWL_NS: "owl:",
        QUDT_NS: "qudt:",
        UNIT_NS: "unit:",
        QK_NS: "qk:",
        "http://www.w3.org/ns/shacl#": "sh:",
        "http://www.w3.org/2004/02/skos/core#": "skos:",
    }
    if g:
        for prefix, ns in g.namespaces():
            ns_str = str(ns)
            if uri_str.startswith(ns_str):
                return f"{prefix}:{uri_str[len(ns_str):]}"
    for ns, prefix in prefixes.items():
        if uri_str.startswith(ns):
            return f"{prefix}{uri_str[len(ns):]}"
    return uri_str


def load_graph(file_path):
    """Load an RDF graph from file, auto-detecting format."""
    g = Graph()
    g.bind("brick", BRICK)
    g.bind("s223", S223)
    g.bind("qudt", QUDT)
    g.bind("unit", UNIT)
    g.bind("qk", QK)

    path = Path(file_path)
    fmt = None
    suffix = path.suffix.lower()
    if suffix in (".ttl", ".turtle"):
        fmt = "turtle"
    elif suffix in (".rdf", ".xml", ".owl"):
        fmt = "xml"
    elif suffix in (".jsonld", ".json"):
        fmt = "json-ld"
    elif suffix in (".n3",):
        fmt = "n3"
    elif suffix in (".nt",):
        fmt = "nt"

    g.parse(str(path), format=fmt)
    return g


def cmd_parse(args):
    """Parse and summarize an RDF file."""
    if len(args) < 1:
        print("Usage: ontology_tool.py parse <file>")
        sys.exit(1)

    g = load_graph(args[0])
    total_triples = len(g)

    # Collect namespaces used
    namespaces = sorted(set(f"{p}: {n}" for p, n in g.namespaces() if p))

    # Count classes (types used as objects of rdf:type)
    classes = set()
    for s, p, o in g.triples((None, RDF.type, None)):
        if isinstance(o, URIRef):
            classes.add(o)

    # Count instances per class (top 20)
    class_counts = {}
    for cls in classes:
        count = len(list(g.triples((None, RDF.type, cls))))
        class_counts[shorten(cls, g)] = count
    top_classes = sorted(class_counts.items(), key=lambda x: -x[1])[:20]

    # Count predicates used
    predicates = {}
    for s, p, o in g:
        pk = shorten(p, g)
        predicates[pk] = predicates.get(pk, 0) + 1
    top_preds = sorted(predicates.items(), key=lambda x: -x[1])[:15]

    # Detect ontology type
    ontology_type = []
    for cls in classes:
        cls_str = str(cls)
        if cls_str.startswith(BRICK_NS):
            ontology_type.append("Brick Schema")
            break
    for cls in classes:
        cls_str = str(cls)
        if cls_str.startswith(S223_NS):
            ontology_type.append("ASHRAE 223P")
            break
    if not ontology_type:
        ontology_type.append("Generic RDF")

    print(f"=== RDF Model Summary: {args[0]} ===")
    print(f"Ontology type: {', '.join(ontology_type)}")
    print(f"Total triples: {total_triples}")
    print(f"Distinct classes: {len(classes)}")
    print(f"Distinct predicates: {len(predicates)}")
    print()
    print("Namespaces:")
    for ns in namespaces[:15]:
        print(f"  {ns}")
    print()
    print("Top classes (by instance count):")
    for cls, count in top_classes:
        print(f"  {cls}: {count}")
    print()
    print("Top predicates (by usage):")
    for pred, count in top_preds:
        print(f"  {pred}: {count}")


def cmd_query(args):
    """Run a SPARQL query against an RDF file."""
    if len(args) < 2:
        print("Usage: ontology_tool.py query <file> <sparql>")
        sys.exit(1)

    g = load_graph(args[0])
    sparql = args[1]

    # If the query doesn't contain PREFIX declarations, add common ones
    if "PREFIX" not in sparql.upper():
        prefixes = "\n".join(
            f"PREFIX {p}: <{n}>"
            for p, n in g.namespaces()
            if p
        )
        # Add standard prefixes not in graph
        for p, n in [("brick", BRICK_NS), ("s223", S223_NS), ("qudt", QUDT_NS),
                      ("unit", UNIT_NS), ("qk", QK_NS)]:
            if f"PREFIX {p}:" not in prefixes:
                prefixes += f"\nPREFIX {p}: <{n}>"
        sparql = prefixes + "\n" + sparql

    results = g.query(sparql)

    if hasattr(results, "vars") and results.vars:
        # SELECT query
        headers = [str(v) for v in results.vars]
        print("\t".join(headers))
        print("\t".join("-" * len(h) for h in headers))
        for row in results:
            values = []
            for v in row:
                if v is None:
                    values.append("")
                else:
                    values.append(shorten(v, g))
            print("\t".join(values))
        print(f"\n({len(results)} results)")
    elif hasattr(results, "askAnswer"):
        print(f"ASK result: {results.askAnswer}")
    else:
        print(f"CONSTRUCT/DESCRIBE returned {len(results)} triples")
        for s, p, o in results:
            print(f"  {shorten(s, g)} {shorten(p, g)} {shorten(o, g)}")


def cmd_describe(args):
    """Describe an entity: all its properties and relationships."""
    if len(args) < 2:
        print("Usage: ontology_tool.py describe <file> <uri>")
        sys.exit(1)

    g = load_graph(args[0])
    uri = URIRef(args[1])

    # Outgoing triples (entity as subject)
    outgoing = list(g.triples((uri, None, None)))
    # Incoming triples (entity as object)
    incoming = list(g.triples((None, None, uri)))

    if not outgoing and not incoming:
        print(f"Entity not found: {args[1]}")
        print("\nDid you mean one of these?")
        # Fuzzy match
        target = args[1].rsplit("#", 1)[-1].rsplit("/", 1)[-1].lower()
        matches = []
        seen = set()
        for s, p, o in g:
            for term in [s, o]:
                if isinstance(term, URIRef) and term not in seen:
                    seen.add(term)
                    local = str(term).rsplit("#", 1)[-1].rsplit("/", 1)[-1].lower()
                    if target in local or local in target:
                        matches.append(str(term))
        for m in matches[:10]:
            print(f"  {m}")
        return

    print(f"=== {shorten(uri, g)} ===")
    print(f"Full URI: {uri}")

    if outgoing:
        print(f"\nOutgoing ({len(outgoing)} triples):")
        # Group by predicate
        by_pred = {}
        for s, p, o in outgoing:
            pk = shorten(p, g)
            by_pred.setdefault(pk, []).append(shorten(o, g))
        for pred, objects in sorted(by_pred.items()):
            for obj in objects:
                print(f"  {pred} → {obj}")

    if incoming:
        print(f"\nIncoming ({len(incoming)} triples):")
        by_pred = {}
        for s, p, o in incoming:
            pk = shorten(p, g)
            by_pred.setdefault(pk, []).append(shorten(s, g))
        for pred, subjects in sorted(by_pred.items()):
            for subj in subjects:
                print(f"  {subj} ← {pred}")


def cmd_list_classes(args):
    """List all classes used in a model."""
    if len(args) < 1:
        print("Usage: ontology_tool.py list-classes <file>")
        sys.exit(1)

    g = load_graph(args[0])

    classes = {}
    for s, p, o in g.triples((None, RDF.type, None)):
        if isinstance(o, URIRef):
            key = shorten(o, g)
            classes[key] = classes.get(key, 0) + 1

    print("Classes (with instance counts):")
    for cls, count in sorted(classes.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {cls}: {count}")
    print(f"\nTotal: {len(classes)} classes")


def cmd_list_instances(args):
    """List instances, optionally filtered by class."""
    if len(args) < 1:
        print("Usage: ontology_tool.py list-instances <file> [class-uri]")
        sys.exit(1)

    g = load_graph(args[0])
    class_filter = URIRef(args[1]) if len(args) > 1 else None

    instances = []
    if class_filter:
        for s, p, o in g.triples((None, RDF.type, class_filter)):
            if isinstance(s, URIRef):
                label = ""
                for _, _, lbl in g.triples((s, RDFS.label, None)):
                    label = f" ({lbl})"
                    break
                instances.append(f"  {shorten(s, g)}{label}")
    else:
        seen = set()
        for s, p, o in g.triples((None, RDF.type, None)):
            if isinstance(s, URIRef) and s not in seen:
                seen.add(s)
                types = [shorten(t, g) for _, _, t in g.triples((s, RDF.type, None))
                         if isinstance(t, URIRef) and str(t) != OWL_NS + "NamedIndividual"]
                label = ""
                for _, _, lbl in g.triples((s, RDFS.label, None)):
                    label = f" ({lbl})"
                    break
                instances.append(f"  {shorten(s, g)}{label} [{', '.join(types)}]")

    for inst in sorted(instances):
        print(inst)
    print(f"\nTotal: {len(instances)} instances")


def cmd_topology(args):
    """Show equipment connectivity (Brick feeds and 223P cnx chains)."""
    if len(args) < 1:
        print("Usage: ontology_tool.py topology <file>")
        sys.exit(1)

    g = load_graph(args[0])

    print("=== Equipment Topology ===\n")

    # Brick feeds relationships
    feeds_query = """
    SELECT ?upstream ?downstream WHERE {
        ?upstream <https://brickschema.org/schema/Brick#feeds> ?downstream .
    }
    """
    feeds = list(g.query(feeds_query))
    if feeds:
        print("Brick feeds chains:")
        for row in feeds:
            up = shorten(row[0], g)
            down = shorten(row[1], g)
            print(f"  {up} → {down}")
        print()

    # 223P cnx connections
    cnx_query = """
    SELECT ?a ?b WHERE {
        ?a <http://data.ashrae.org/standard223#cnx> ?b .
    }
    """
    cnx = list(g.query(cnx_query))
    if cnx:
        print("223P cnx connections:")
        for row in cnx:
            a = shorten(row[0], g)
            b = shorten(row[1], g)
            print(f"  {a} ↔ {b}")
        print()

    # hasPoint relationships
    points_query = """
    SELECT ?equip ?point WHERE {
        { ?equip <https://brickschema.org/schema/Brick#hasPoint> ?point }
        UNION
        { ?equip <http://data.ashrae.org/standard223#hasProperty> ?point }
    }
    """
    points = list(g.query(points_query))
    if points:
        print("Equipment → Points/Properties:")
        by_equip = {}
        for row in points:
            eq = shorten(row[0], g)
            pt = shorten(row[1], g)
            by_equip.setdefault(eq, []).append(pt)
        for equip, pts in sorted(by_equip.items()):
            print(f"  {equip}:")
            for pt in pts:
                print(f"    • {pt}")
        print()

    # Containment
    contains_query = """
    SELECT ?parent ?child WHERE {
        { ?parent <https://brickschema.org/schema/Brick#hasPart> ?child }
        UNION
        { ?parent <http://data.ashrae.org/standard223#contains> ?child }
    }
    """
    contains = list(g.query(contains_query))
    if contains:
        print("Containment hierarchy:")
        for row in contains:
            parent = shorten(row[0], g)
            child = shorten(row[1], g)
            print(f"  {parent} contains {child}")
        print()

    # Location hierarchy
    location_query = """
    SELECT ?child ?parent WHERE {
        ?child <https://brickschema.org/schema/Brick#isPartOf> ?parent .
    }
    """
    locations = list(g.query(location_query))
    if locations:
        print("Spatial hierarchy (isPartOf):")
        for row in locations:
            child = shorten(row[0], g)
            parent = shorten(row[1], g)
            print(f"  {child} ⊂ {parent}")
        print()

    if not feeds and not cnx and not points and not contains and not locations:
        print("No topology relationships found in this model.")
        print("Expected relationships: brick:feeds, s223:cnx, brick:hasPoint, brick:isPartOf, s223:contains")


def cmd_validate(args):
    """Validate a model against Brick SHACL shapes."""
    if len(args) < 1:
        print("Usage: ontology_tool.py validate <file>")
        sys.exit(1)

    g = load_graph(args[0])

    # Try using brickschema library if available
    try:
        import brickschema
        bg = brickschema.Graph(load_brick=True)
        for triple in g:
            bg.add(triple)
        valid, _, report = bg.validate()
        print(f"Validation result: {'PASS' if valid else 'FAIL'}")
        print()
        print(report)
        return
    except ImportError:
        pass

    # Fallback: basic structural validation
    print("Note: brickschema package not installed. Running basic structural checks.")
    print("Install with: pip install brickschema (for full SHACL validation)")
    print()

    issues = []
    warnings = []

    # Check that typed entities have reasonable types
    for s, p, o in g.triples((None, RDF.type, None)):
        if isinstance(o, URIRef):
            o_str = str(o)
            # Check for abstract 223P classes that shouldn't be instantiated
            if o_str == S223_NS + "Equipment":
                issues.append(f"{shorten(s, g)} typed as abstract s223:Equipment — use a specific subclass")
            if o_str == S223_NS + "ConnectionPoint":
                issues.append(f"{shorten(s, g)} typed as abstract s223:ConnectionPoint — use Inlet/Outlet/Bidirectional")

    # Check Brick hasPoint targets are Points
    brick_has_point = URIRef(BRICK_NS + "hasPoint")
    for s, p, o in g.triples((None, brick_has_point, None)):
        types = [str(t) for _, _, t in g.triples((o, RDF.type, None))]
        point_types = [t for t in types if "Sensor" in t or "Setpoint" in t or
                       "Command" in t or "Status" in t or "Alarm" in t or "Parameter" in t or
                       "Point" in t]
        if not point_types and types:
            warnings.append(f"{shorten(o, g)} is target of hasPoint but doesn't look like a Point type")

    # Check 223P connection points have medium
    has_medium = URIRef(S223_NS + "hasMedium")
    for cp_type in ["InletConnectionPoint", "OutletConnectionPoint", "BidirectionalConnectionPoint"]:
        for s, p, o in g.triples((None, RDF.type, URIRef(S223_NS + cp_type))):
            mediums = list(g.triples((s, has_medium, None)))
            if not mediums:
                warnings.append(f"{shorten(s, g)} ({cp_type}) has no hasMedium declaration")

    # Check for dangling references
    all_subjects = set(s for s, p, o in g if isinstance(s, URIRef))
    for s, p, o in g:
        if isinstance(o, URIRef) and not isinstance(o, BNode):
            o_str = str(o)
            # Skip namespace/ontology URIs
            if any(o_str.startswith(ns) for ns in [BRICK_NS, S223_NS, RDF_NS, RDFS_NS, OWL_NS, QUDT_NS, UNIT_NS, QK_NS,
                                                     "http://www.w3.org/ns/shacl#", "http://www.w3.org/2004/02/skos/core#"]):
                continue
            if o not in all_subjects and p != RDF.type:
                # Check if it's a known external reference
                if not any(o_str.startswith(ns) for ns in ["http://www.w3.org/", "http://purl.org/"]):
                    warnings.append(f"Possible dangling reference: {shorten(s, g)} {shorten(p, g)} → {shorten(o, g)}")

    if issues:
        print(f"ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  ✗ {issue}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings[:20]:
            print(f"  ! {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")
        print()

    if not issues and not warnings:
        print("No issues found (basic structural checks passed).")
    elif not issues:
        print("No structural issues found, but warnings present.")


def cmd_add_triple(args):
    """Add a triple to an existing model."""
    if len(args) < 4:
        print("Usage: ontology_tool.py add-triple <file> <subject> <predicate> <object>")
        sys.exit(1)

    file_path = args[0]
    g = load_graph(file_path)

    subj = URIRef(args[1])
    pred = URIRef(args[2])
    # Object can be URI or literal
    obj_str = args[3]
    if obj_str.startswith('"') and obj_str.endswith('"'):
        obj = Literal(obj_str[1:-1])
    elif obj_str.startswith("http://") or obj_str.startswith("https://"):
        obj = URIRef(obj_str)
    else:
        obj = Literal(obj_str)

    g.add((subj, pred, obj))
    g.serialize(file_path, format="turtle")
    print(f"Added: {shorten(subj, g)} {shorten(pred, g)} {shorten(obj, g)}")
    print(f"Model saved: {file_path} ({len(g)} triples)")


def cmd_export(args):
    """Export a model to a different format."""
    if len(args) < 3:
        print("Usage: ontology_tool.py export <input-file> <format> <output-file>")
        print("Formats: turtle, xml, json-ld, n3, nt")
        sys.exit(1)

    g = load_graph(args[0])
    fmt = args[1]
    output = args[2]

    fmt_map = {
        "turtle": "turtle", "ttl": "turtle",
        "xml": "xml", "rdf": "xml", "rdfxml": "xml",
        "json-ld": "json-ld", "jsonld": "json-ld",
        "n3": "n3",
        "nt": "nt", "ntriples": "nt",
    }
    actual_fmt = fmt_map.get(fmt.lower(), fmt)
    g.serialize(output, format=actual_fmt)
    print(f"Exported {len(g)} triples to {output} ({actual_fmt})")


def cmd_fetch_brick(args):
    """Download and cache the Brick ontology."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "Brick.ttl"

    if cache_file.exists() and "--force" not in args:
        print(f"Brick ontology already cached at {cache_file}")
        print("Use --force to re-download.")
        # Print summary
        g = load_graph(str(cache_file))
        print(f"Contains {len(g)} triples")
        return

    print(f"Downloading Brick ontology from {BRICK_URL}...")
    import urllib.request
    urllib.request.urlretrieve(BRICK_URL, str(cache_file))
    g = load_graph(str(cache_file))
    print(f"Cached at {cache_file} ({len(g)} triples)")


def cmd_fetch_223p(args):
    """Download and cache the 223P ontology."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "223p.ttl"

    if cache_file.exists() and "--force" not in args:
        print(f"223P ontology already cached at {cache_file}")
        print("Use --force to re-download.")
        g = load_graph(str(cache_file))
        print(f"Contains {len(g)} triples")
        return

    print(f"Downloading 223P ontology from {S223_URL}...")
    import urllib.request
    urllib.request.urlretrieve(S223_URL, str(cache_file))
    g = load_graph(str(cache_file))
    print(f"Cached at {cache_file} ({len(g)} triples)")


COMMANDS = {
    "parse": cmd_parse,
    "query": cmd_query,
    "describe": cmd_describe,
    "list-classes": cmd_list_classes,
    "list-instances": cmd_list_instances,
    "topology": cmd_topology,
    "validate": cmd_validate,
    "add-triple": cmd_add_triple,
    "export": cmd_export,
    "fetch-brick": cmd_fetch_brick,
    "fetch-223p": cmd_fetch_223p,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("Usage: ontology_tool.py <command> [args...]")
        print()
        print("Commands:")
        print("  parse <file>                          Parse and summarize an RDF file")
        print("  query <file> <sparql>                 Run SPARQL query")
        print("  describe <file> <uri>                 Describe an entity")
        print("  list-classes <file>                   List all classes")
        print("  list-instances <file> [class-uri]     List instances")
        print("  topology <file>                       Show equipment connectivity")
        print("  validate <file>                       Validate model")
        print("  add-triple <file> <s> <p> <o>         Add a triple")
        print("  export <file> <format> <output>       Export to format")
        print("  fetch-brick                           Download Brick ontology")
        print("  fetch-223p                            Download 223P ontology")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
