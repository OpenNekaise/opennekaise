---
name: simple-graph
description: Work with simple building graphs based on Brick Schema. Organizes building context through Actors (data/control points), Sets (logical groupings), and Captions (natural-language metadata). Use when working with building knowledge graphs, TTL files, finding sensors/equipment in a building model, or creating building semantic models.
---

# Simple Building Graph

A lightweight approach for representing building systems as RDF graphs. Reuses Brick Schema types for classification and organizes everything into three simple elements.

## The Three Elements

### Actors
Components that generate data or receive control — sensors, meters, valves, dampers, actuators, setpoints, alarms, fans (when data-generating).

**Not Actors**: Locations, passive assets (pipes, ducts, walls, windows), non-monitored equipment.

### Sets
Logical groupings of Actors and other Sets. They represent spatial locations (room, floor, building), subsystems (radiator loop, AHU branch), or conceptual systems (HVAC system).

### Captions
Natural-language text nodes attached to Actors and Sets via `sg:hasCaption`. They carry purpose, component ordering, flow direction, operating ranges, control sequences, database IDs, and links to external resources.

## Edge Types

| Edge | Purpose | Connects |
|------|---------|----------|
| `rdf:type` | Classification (reuses Brick types) | Entity → Class |
| `sg:cnx` | System linking | Set → Set |
| `sg:hasActor` | Actor membership in a Set | Set → Actor |
| `sg:hasCaption` | Natural-language context | Actor or Set → Caption literal |

**No Actor-to-Actor edges.** Actors are always grouped through Sets.

## Namespace

```
sg: <https://opennekaise.com/SimpleGraph#>
```

Uses Brick types for classification:
```
brick: <https://brickschema.org/schema/Brick#>
```

## Reading a Model

Models are Turtle (.ttl) files. Use the ontology tool for parsing:

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"
python3 "$ONTOOL" parse model.ttl
```

Or read the TTL directly — it's designed to be human-readable.

### How to Navigate

1. **Find the top-level Set** (the building) — look for `a sg:Set` with no parent
2. **Follow `sg:cnx`** to find child Sets (floors, systems)
3. **Follow `sg:hasActor`** to find Actors within a Set
4. **Read `sg:hasCaption`** on any node for rich context
5. **Check `rdf:type`** to know what Brick class an Actor is (e.g., `brick:Temperature_Sensor`)

### Key Queries

**Find all Actors in a room/set:**
```sparql
SELECT ?actor ?type ?caption WHERE {
    <room-uri> sg:hasActor ?actor .
    ?actor a ?type .
    FILTER(?type != sg:Actor)
    OPTIONAL { ?actor sg:hasCaption ?caption }
}
```

**Find all Sets (topology):**
```sparql
SELECT ?parent ?child ?caption WHERE {
    ?parent sg:cnx ?child .
    ?parent a sg:Set .
    ?child a sg:Set .
    OPTIONAL { ?child sg:hasCaption ?caption }
}
```

**Find all temperature sensors in the building:**
```sparql
SELECT ?actor ?caption WHERE {
    ?actor a brick:Temperature_Sensor .
    ?actor sg:hasCaption ?caption .
}
```

**Find which Set an Actor belongs to:**
```sparql
SELECT ?set ?set_caption WHERE {
    ?set sg:hasActor <actor-uri> .
    OPTIONAL { ?set sg:hasCaption ?set_caption }
}
```

**Get database IDs from Captions:**
```sparql
SELECT ?actor ?caption WHERE {
    ?actor a sg:Actor .
    ?actor sg:hasCaption ?caption .
    FILTER(CONTAINS(?caption, "Database ID"))
}
```

## Creating a Model

```python
from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD

g = Graph()
SG = Namespace("https://opennekaise.com/SimpleGraph#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("http://example.org/building#")

g.bind("sg", SG)
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

# 1. Define the building (top-level Set)
g.add((BLDG.MyBuilding, RDF.type, SG.Set))
g.add((BLDG.MyBuilding, SG.hasCaption, Literal(
    "MyBuilding. Address: ... Built: ... "
    "HVAC: district heating, radiators. 3 floors.",
    datatype=XSD.string)))

# 2. Define child Sets (floors, systems)
g.add((BLDG.Floor1, RDF.type, SG.Set))
g.add((BLDG.Floor1, SG.hasCaption, Literal(
    "1st floor. 4 office rooms with individual climate control.",
    datatype=XSD.string)))
g.add((BLDG.MyBuilding, SG.cnx, BLDG.Floor1))

# 3. Define rooms as Sets
g.add((BLDG.Room101, RDF.type, SG.Set))
g.add((BLDG.Room101, SG.hasCaption, Literal(
    "Room 101, type: standard office. Heated by radiator, "
    "cooled by chilled beam. Seats 2-4.",
    datatype=XSD.string)))
g.add((BLDG.Floor1, SG.cnx, BLDG.Room101))

# 4. Define Actors (sensors, valves, etc.)
g.add((BLDG.Room101_GT11, RDF.type, SG.Actor))
g.add((BLDG.Room101_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room101_GT11, SG.hasCaption, Literal(
    "Room 101 temperature sensor. Setpoint: 22C. "
    "Database ID: abc123. Unit: Celsius.",
    datatype=XSD.string)))
g.add((BLDG.Room101, SG.hasActor, BLDG.Room101_GT11))

# 5. Define system Sets
g.add((BLDG.VS01, RDF.type, SG.Set))
g.add((BLDG.VS01, SG.hasCaption, Literal(
    "VS01 - Heating system. District heating supplies hot water "
    "to radiators throughout the building.",
    datatype=XSD.string)))
g.add((BLDG.MyBuilding, SG.cnx, BLDG.VS01))

# 6. Export
g.serialize("/workspace/group/building_model.ttl", format="turtle")
```

## Hierarchy Pattern

```
Building (Set)
├── Floor1 (Set)
│   ├── Room_01_A1 (Set)
│   │   ├── GT11 (Actor) — temperature sensor
│   │   ├── GQ41 (Actor) — CO2 sensor
│   │   ├── ST4x (Actor) — air damper
│   │   └── SV2x (Actor) — heating valve
│   └── Room_01_B2 (Set)
│       └── ...
├── FTX (Set) — ventilation system
│   ├── InletAirDuct (Set)
│   │   ├── GT41 (Actor) — inlet temp sensor
│   │   ├── TF (Actor) — fan
│   │   └── ST2:1 (Actor) — damper
│   ├── ExhaustAirDuct (Set)
│   └── VVX (Set+Actor) — heat exchanger
├── VS01 (Set) — heating system
│   ├── Flow (Actor) — flow sensor
│   └── SupplyTemp (Actor) — supply temp sensor
└── KB01 (Set) — cooling system
```

## Caption Best Practices

Captions should include concrete, verifiable information:

```
"Room 101 temperature sensor. Setpoint: 22C. Deadzone comfort: 2C.
Deadzone economy: 4C. Database ID: sensor_12345. Unit: Celsius.
Log interval: 15 min."
```

```
"VS01 - Heating system for radiators. District heating connection.
Supply temp range: 40-60C. Flow sensor and power meter installed.
Control sequence: outdoor temp compensation curve."
```

## Reference

For detailed patterns and a complete example model, read:
`${CLAUDE_SKILL_DIR}/reference.md`
