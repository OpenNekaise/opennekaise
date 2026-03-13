---
name: ontology
description: Work with building ontologies (Brick Schema, ASHRAE 223P) and semantic knowledge graphs. Parse, query, create, validate, and reason over RDF/TTL models. Use when users mention ontology, semantic model, knowledge graph, Brick, 223P, RDF, TTL, SPARQL, building topology, equipment classification, point tagging, or when working with .ttl/.rdf/.jsonld files.
allowed-tools: Bash(python3 *), Bash(chmod *), Bash(cat *)
---

# Building Ontology Skill

Work with RDF-based building ontologies: **Brick Schema** (equipment/point classification, spatial hierarchy) and **ASHRAE Standard 223P** (connection topology, medium flow, port-based modeling).

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

# Show equipment connectivity (feeds/cnx chains)
python3 "$TOOL" topology model.ttl

# Validate against Brick SHACL shapes (requires brickschema pip package)
python3 "$TOOL" validate model.ttl

# Add a triple
python3 "$TOOL" add-triple model.ttl "http://example.org/b#Room1" "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" "https://brickschema.org/schema/Brick#Room"

# Export to another format (xml, n3, json-ld, turtle)
python3 "$TOOL" export model.ttl json-ld output.jsonld

# Download and cache ontologies for offline use
python3 "$TOOL" fetch-brick
python3 "$TOOL" fetch-223p
```

## When to Use This Skill

- **User uploads a .ttl, .rdf, or .jsonld file** — parse it, summarize contents, answer questions about it
- **User asks about building topology** — query or create a semantic model showing how equipment connects
- **User asks about equipment classification** — use Brick taxonomy to properly classify sensors, equipment, spaces
- **User wants to map BMS points** — use Brick Point classes (Sensor, Setpoint, Command, Status, Alarm) to tag data points semantically
- **User asks about ontology, RDF, SPARQL, knowledge graph** — use this skill's tools and reference material
- **Creating a digital twin or building model** — build a Brick or 223P model from available data

## Creating a New Brick Model

When creating a building model from scratch or from data the user provides:

```python
# Write directly with Python — no special tool needed
from rdflib import Graph, Namespace, RDF, RDFS, Literal

BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("http://example.org/building#")

g = Graph()
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

# Add building structure
g.add((BLDG.MyBuilding, RDF.type, BRICK.Building))
g.add((BLDG.Floor1, RDF.type, BRICK.Floor))
g.add((BLDG.Floor1, BRICK.isPartOf, BLDG.MyBuilding))

# Add equipment
g.add((BLDG.AHU1, RDF.type, BRICK.AHU))
g.add((BLDG.VAV1, RDF.type, BRICK.VAV))
g.add((BLDG.AHU1, BRICK.feeds, BLDG.VAV1))

# Add points
g.add((BLDG.SAT, RDF.type, BRICK.Supply_Air_Temperature_Sensor))
g.add((BLDG.AHU1, BRICK.hasPoint, BLDG.SAT))

g.serialize("/workspace/group/building_model.ttl", format="turtle")
```

## Reference Material

For detailed class hierarchies, relationships, and SPARQL patterns, read these files from the skill directory:

- `${CLAUDE_SKILL_DIR}/brick-reference.md` — Brick Schema classes, relationships, point taxonomy, common SPARQL
- `${CLAUDE_SKILL_DIR}/s223-reference.md` — ASHRAE 223P classes, connection topology, medium modeling, SPARQL

Read these only when you need specific class names, relationship details, or query patterns — not on every invocation.

## Key Concepts Summary

### Brick Schema (classification-focused)
- **Equipment**: AHU, VAV, Chiller, Boiler, Fan, Pump, Damper, Valve, Meter...
- **Point**: Sensor, Setpoint, Command, Status, Alarm, Parameter (each with substance+quantity subtypes like Air_Temperature_Sensor)
- **Location**: Site > Building > Floor > Room > Zone
- **Relationships**: `feeds/isFedBy`, `hasPoint/isPointOf`, `isPartOf/hasPart`, `isLocationOf/hasLocation`, `controls`, `meters`
- **Namespace**: `https://brickschema.org/schema/Brick#`

### ASHRAE 223P (topology-focused)
- **Equipment**: Same types but with port-based connections
- **Connection pattern**: Equipment → OutletConnectionPoint → Connection (Duct/Pipe/Conductor) → InletConnectionPoint → Equipment
- **Medium**: What flows through connections (Fluid-Air, Fluid-Water, Electricity-AC)
- **Properties**: ObservableProperty (sensors), ActuatableProperty (commands)
- **Key predicate**: `s223:cnx` — all other connectivity is inferred from this
- **Namespace**: `http://data.ashrae.org/standard223#`

### When to Use Which
- **Brick** — asset classification, point tagging, spatial hierarchy, "what is this and what does it measure?"
- **223P** — physical topology, flow paths, port connections, "how does air/water/electricity flow through the building?"
- **Both together** — dual-type entities for comprehensive modeling
