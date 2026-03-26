---
name: know-brick
description: Brick Schema building ontology for equipment classification, point tagging, spatial hierarchy, and BMS data modeling. Use when working with Brick, brick schema, point tagging, equipment classification, BMS mapping, feeds/isFedBy, hasPoint, spatial hierarchy, or .ttl files using Brick classes.
---

# Brick Schema

Work with Brick models: equipment classification, point tagging, spatial hierarchy, and BMS data mapping.

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
python3 "$TOOL" list-instances model.ttl "https://brickschema.org/schema/Brick#AHU"

# Show equipment feed chains
python3 "$TOOL" topology model.ttl

# Validate against Brick SHACL shapes (requires brickschema pip package)
python3 "$TOOL" validate model.ttl

# Download and cache Brick ontology for offline use
python3 "$TOOL" fetch-brick
```

## Creating a Brick Model

```python
from rdflib import Graph, Namespace, RDF, RDFS, Literal

BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("http://example.org/building#")

g = Graph()
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

g.add((BLDG.MyBuilding, RDF.type, BRICK.Building))
g.add((BLDG.Floor1, RDF.type, BRICK.Floor))
g.add((BLDG.Floor1, BRICK.isPartOf, BLDG.MyBuilding))

g.add((BLDG.AHU1, RDF.type, BRICK.AHU))
g.add((BLDG.VAV1, RDF.type, BRICK.VAV))
g.add((BLDG.AHU1, BRICK.feeds, BLDG.VAV1))

g.add((BLDG.SAT, RDF.type, BRICK.Supply_Air_Temperature_Sensor))
g.add((BLDG.AHU1, BRICK.hasPoint, BLDG.SAT))

g.serialize("/workspace/group/building_model.ttl", format="turtle")
```

## Reference Material

For detailed class hierarchies, relationships, point taxonomy, and SPARQL patterns, read:

- `${CLAUDE_SKILL_DIR}/brick-reference.md` — full Brick reference

Read this only when you need specific class names, relationship details, or query patterns.

## When to Use This Skill

- User asks about equipment classification or point tagging
- Working with Brick models or `.ttl` files that use `brick:` namespace
- Mapping BMS/BAS point names to semantic classes
- Modeling spatial hierarchy (Site, Building, Floor, Room, Zone)
- Questions about feeds/isFedBy, hasPoint, isPartOf relationships
