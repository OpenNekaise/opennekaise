---
name: know-223p
description: ASHRAE Standard 223P building topology ontology. Connection patterns, equipment ports, medium flow, properties, functions, SPARQL queries, and RDF/TTL modeling. Use when working with 223P, s223, connection topology, ConnectionPoint, cnx, medium flow, Function, ActuatableProperty, ObservableProperty, or .ttl files using 223P classes.
---

# ASHRAE Standard 223P

Work with 223P topology models: equipment connections, port-based modeling, medium flow, properties, and control functions.

## Quick Start

The `ontology_tool.py` script handles all RDF operations. It self-bootstraps (installs `rdflib` on first use).

```bash
TOOL="${CLAUDE_SKILL_DIR}/scripts/ontology_tool.py"
python3 "$TOOL" <command> [args...]
```

### Core Commands

```bash
# Parse and summarize an RDF file
python3 "$TOOL" parse model.ttl

# Run a SPARQL query
python3 "$TOOL" query model.ttl "SELECT ?s ?type WHERE { ?s a ?type } LIMIT 20"

# Describe a specific entity (all properties and relationships)
python3 "$TOOL" describe model.ttl "http://example.org/building#AHU1"

# List all classes used in a model
python3 "$TOOL" list-classes model.ttl

# List instances, optionally filtered by class
python3 "$TOOL" list-instances model.ttl
python3 "$TOOL" list-instances model.ttl "http://data.ashrae.org/standard223#Equipment"

# Show equipment connectivity (cnx chains)
python3 "$TOOL" topology model.ttl

# Download and cache 223P ontology for offline use
python3 "$TOOL" fetch-223p
```

## Reference Material

For detailed class hierarchies, predicates, enumerations, and SPARQL patterns, read:

- `${CLAUDE_SKILL_DIR}/s223-reference.md` — full 223P reference

Read this only when you need specific class names, predicate details, or query patterns.

## When to Use This Skill

- User asks about building topology, connection patterns, or medium flow
- Working with 223P models or `.ttl` files that use `s223:` namespace
- Creating or querying port-based equipment models
- Mapping control functions (`s223:Function`) to properties
- Modeling how air, water, or electricity flows through equipment
