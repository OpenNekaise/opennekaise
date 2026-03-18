---
name: simple-graph
description: Work with simple building graphs based on Brick Schema. Organizes building data into Points (sensors/actuators), Groups (logical groupings), and Descriptions (natural-language metadata). Use when working with building knowledge graphs, TTL files, finding sensors/equipment in a building model, or creating building semantic models.
---

# Simple Building Graph

A lightweight convention for representing building systems as RDF graphs, built on Brick Schema.

## Elements

### Points
Sensors, meters, valves, dampers, actuators — anything that generates data or receives control.

### Groups
Logical groupings of Points and other Groups — rooms, floors, buildings, HVAC subsystems.

### Descriptions
Natural-language text attached to Points and Groups via `sg:hasDescription`. Carries operational context: setpoints, database IDs, control sequences, flow direction, etc.

## Edge Types

| Edge | Purpose | Connects |
|------|---------|----------|
| `rdf:type` | Classification (Brick types) | Entity → Class |
| `sg:contains` | Hierarchy / linking | Group → Group |
| `sg:hasPoint` | Point membership | Group → Point |
| `sg:hasDescription` | Text context | Any → Literal |

## Namespace

```
sg:    <https://opennekaise.com/SimpleGraph#>
brick: <https://brickschema.org/schema/Brick#>
```

## Reading a Model

Models are Turtle (.ttl) files. Use the ontology tool for parsing:

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"
python3 "$ONTOOL" parse model.ttl
```

### How to Navigate

1. **Find the top-level Group** (the building) — look for `a sg:Group` with no parent
2. **Follow `sg:contains`** to find child Groups (floors, systems)
3. **Follow `sg:hasPoint`** to find Points within a Group
4. **Read `sg:hasDescription`** on any node for context
5. **Check `rdf:type`** for the Brick class (e.g., `brick:Temperature_Sensor`)

### Key Queries

**Find all Points in a room:**
```sparql
SELECT ?point ?type ?desc WHERE {
    <room-uri> sg:hasPoint ?point .
    ?point a ?type .
    FILTER(?type != sg:Point)
    OPTIONAL { ?point sg:hasDescription ?desc }
}
```

**Find all Groups (topology):**
```sparql
SELECT ?parent ?child ?desc WHERE {
    ?parent sg:contains ?child .
    ?parent a sg:Group .
    ?child a sg:Group .
    OPTIONAL { ?child sg:hasDescription ?desc }
}
```

**Find all temperature sensors:**
```sparql
SELECT ?point ?desc WHERE {
    ?point a brick:Temperature_Sensor .
    ?point sg:hasDescription ?desc .
}
```

**Find which Group a Point belongs to:**
```sparql
SELECT ?group ?desc WHERE {
    ?group sg:hasPoint <point-uri> .
    OPTIONAL { ?group sg:hasDescription ?desc }
}
```

## Creating a Model

```python
from rdflib import Graph, Namespace, RDF, Literal, XSD

g = Graph()
SG = Namespace("https://opennekaise.com/SimpleGraph#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("http://example.org/building#")

g.bind("sg", SG)
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

# Building (top-level Group)
g.add((BLDG.MyBuilding, RDF.type, SG.Group))
g.add((BLDG.MyBuilding, SG.hasDescription, Literal(
    "MyBuilding. District heating, radiators. 3 floors.",
    datatype=XSD.string)))

# Floor (child Group)
g.add((BLDG.Floor1, RDF.type, SG.Group))
g.add((BLDG.Floor1, SG.hasDescription, Literal(
    "1st floor. 4 office rooms.", datatype=XSD.string)))
g.add((BLDG.MyBuilding, SG.contains, BLDG.Floor1))

# Room (child Group)
g.add((BLDG.Room101, RDF.type, SG.Group))
g.add((BLDG.Room101, SG.hasDescription, Literal(
    "Room 101, standard office. Heated by radiator.",
    datatype=XSD.string)))
g.add((BLDG.Floor1, SG.contains, BLDG.Room101))

# Temperature sensor (Point)
g.add((BLDG.Room101_GT11, RDF.type, SG.Point))
g.add((BLDG.Room101_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room101_GT11, SG.hasDescription, Literal(
    "Room 101 temperature sensor. Setpoint: 22C. "
    "Database ID: abc123. Unit: Celsius.",
    datatype=XSD.string)))
g.add((BLDG.Room101, SG.hasPoint, BLDG.Room101_GT11))

# Heating system (Group)
g.add((BLDG.VS01, RDF.type, SG.Group))
g.add((BLDG.VS01, SG.hasDescription, Literal(
    "VS01 - Heating system. District heating to radiators.",
    datatype=XSD.string)))
g.add((BLDG.MyBuilding, SG.contains, BLDG.VS01))

g.serialize("/workspace/group/building_model.ttl", format="turtle")
```

## Hierarchy Pattern

```
Building (Group)
├── Floor1 (Group)
│   ├── Room_01_A1 (Group)
│   │   ├── GT11 (Point) — temperature sensor
│   │   ├── GQ41 (Point) — CO2 sensor
│   │   └── SV2x (Point) — heating valve
│   └── Room_01_B2 (Group)
├── FTX (Group) — ventilation system
│   ├── InletAirDuct (Group)
│   │   ├── GT41 (Point) — inlet temp sensor
│   │   └── TF (Point) — fan
│   └── VVX (Group+Point) — heat exchanger
├── VS01 (Group) — heating system
└── KB01 (Group) — cooling system
```

## Reference

For detailed patterns and a complete example, read:
`${CLAUDE_SKILL_DIR}/reference.md`
