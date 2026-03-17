---
name: kebgraph
description: Work with KebGraph, a lightweight LLM-native semantic model for buildings. KebGraph organizes building context through Actors (data/control points), Sets (logical groupings), and Captions (natural-language metadata). Use when working with building knowledge graphs, KebGraph TTL files, finding sensors/equipment in a building model, creating building semantic models, or when users mention KebGraph, actors, sets, captions in a building context.
---

# KebGraph Skill

KebGraph is an LLM-native semantic modeling approach for buildings. It reuses vocabularies from Brick Schema, RealEstateCore, and ASHRAE 223P, reorganized into three compact elements designed for AI processing.

## The Three Elements

### Actors
**What they are**: Components that generate data or receive control — sensors, meters, valves, dampers, actuators, setpoints, alarms, fans (when data-generating).

**What they are NOT**: Locations, passive assets (pipes, ducts, walls, windows), non-monitored equipment.

**Why they matter**: Actors anchor the model to ground-truth sources (database IDs, BACnet addresses, file paths). Every Actor is something you can actually query data from or send a command to.

### Sets
**What they are**: Logical groupings of Actors and other Sets. They represent spatial locations (room, floor, building), subsystems (radiator loop, AHU branch), or conceptual systems (HVAC system).

**Why they matter**: Sets provide topology through grouping instead of detailed port-level connections. They mirror how practitioners think: Building → Floor → Room, or AHU → Inlet Duct → [sensors, damper, fan].

### Captions
**What they are**: Natural-language text nodes attached to Actors and Sets via `keb:hasCaption`. They carry purpose, component ordering, flow direction, operating ranges, control sequences, database IDs, and links to external resources.

**Why they matter**: Captions preserve rich context without adding formal topology. They're how KebGraph stays compact yet informative — the LLM reads Captions directly.

## Edge Types (Minimal by Design)

| Edge | Purpose | Connects |
|------|---------|----------|
| `rdf:type` | Classification (reuses Brick/REC/S223 types) | Entity → Class |
| `keb:cnx` | System linking | Set → Set |
| `keb:hasActor` | Actor membership in a Set | Set → Actor |
| `keb:hasCaption` | Natural-language context | Actor or Set → Caption literal |

**No Actor-to-Actor edges.** Actors are always grouped through Sets.

## Namespace

```
keb: <https://opennekaise.com/KebGraph#>
```

KebGraph uses Brick types for classification:
```
brick: <https://brickschema.org/schema/Brick#>
```

## Reading a KebGraph Model

KebGraph models are Turtle (.ttl) files. Use the ontology tool for parsing:

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"
python3 "$ONTOOL" parse model.ttl
```

Or read the TTL directly — it's designed to be human/LLM-readable.

### How to Navigate a KebGraph

1. **Find the top-level Set** (the building) — look for `a keb:Set` with no parent
2. **Follow `keb:cnx`** to find child Sets (floors, systems)
3. **Follow `keb:hasActor`** to find Actors within a Set
4. **Read `keb:hasCaption`** on any node for rich context
5. **Check `rdf:type`** to know what Brick class an Actor is (e.g., `brick:Temperature_Sensor`)

### Key Queries

**Find all Actors in a room/set:**
```sparql
SELECT ?actor ?type ?caption WHERE {
    <room-uri> keb:hasActor ?actor .
    ?actor a ?type .
    FILTER(?type != keb:Actor)
    OPTIONAL { ?actor keb:hasCaption ?caption }
}
```

**Find all Sets (topology):**
```sparql
SELECT ?parent ?child ?caption WHERE {
    ?parent keb:cnx ?child .
    ?parent a keb:Set .
    ?child a keb:Set .
    OPTIONAL { ?child keb:hasCaption ?caption }
}
```

**Find all temperature sensors in the building:**
```sparql
SELECT ?actor ?caption WHERE {
    ?actor a brick:Temperature_Sensor .
    ?actor keb:hasCaption ?caption .
}
```

**Find which Set an Actor belongs to:**
```sparql
SELECT ?set ?set_caption WHERE {
    ?set keb:hasActor <actor-uri> .
    OPTIONAL { ?set keb:hasCaption ?set_caption }
}
```

**Get database IDs from Captions** — search Caption text for "Database ID:" patterns:
```sparql
SELECT ?actor ?caption WHERE {
    ?actor a keb:Actor .
    ?actor keb:hasCaption ?caption .
    FILTER(CONTAINS(?caption, "Database ID"))
}
```

## Creating a KebGraph Model

When creating a model for a building, follow this pattern:

```python
from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD

g = Graph()
KEB = Namespace("https://opennekaise.com/KebGraph#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
BLDG = Namespace("http://example.org/building#")

g.bind("keb", KEB)
g.bind("brick", BRICK)
g.bind("bldg", BLDG)

# 1. Define the building (top-level Set)
g.add((BLDG.MyBuilding, RDF.type, KEB.Set))
g.add((BLDG.MyBuilding, KEB.hasCaption, Literal(
    "MyBuilding. Address: ... Built: ... "
    "HVAC: district heating, radiators. 3 floors.",
    datatype=XSD.string)))

# 2. Define child Sets (floors, systems)
g.add((BLDG.Floor1, RDF.type, KEB.Set))
g.add((BLDG.Floor1, KEB.hasCaption, Literal(
    "1st floor. 4 office rooms with individual climate control.",
    datatype=XSD.string)))
g.add((BLDG.MyBuilding, KEB.cnx, BLDG.Floor1))

# 3. Define rooms as Sets
g.add((BLDG.Room101, RDF.type, KEB.Set))
g.add((BLDG.Room101, KEB.hasCaption, Literal(
    "Room 101, type: standard office. Heated by radiator, "
    "cooled by chilled beam. Seats 2-4.",
    datatype=XSD.string)))
g.add((BLDG.Floor1, KEB.cnx, BLDG.Room101))

# 4. Define Actors (sensors, valves, etc.)
g.add((BLDG.Room101_GT11, RDF.type, KEB.Actor))
g.add((BLDG.Room101_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room101_GT11, KEB.hasCaption, Literal(
    "Room 101 temperature sensor. Setpoint: 22C. "
    "Database ID: abc123. Unit: Celsius.",
    datatype=XSD.string)))
g.add((BLDG.Room101, KEB.hasActor, BLDG.Room101_GT11))

g.add((BLDG.Room101_SV2x, RDF.type, KEB.Actor))
g.add((BLDG.Room101_SV2x, RDF.type, BRICK.Control_Valve))
g.add((BLDG.Room101_SV2x, KEB.hasCaption, Literal(
    "Room 101 heating control valve for radiator. "
    "Database ID: def456. Unit: %.",
    datatype=XSD.string)))
g.add((BLDG.Room101, KEB.hasActor, BLDG.Room101_SV2x))

# 5. Define system Sets
g.add((BLDG.VS01, RDF.type, KEB.Set))
g.add((BLDG.VS01, KEB.hasCaption, Literal(
    "VS01 - Heating system. District heating supplies hot water "
    "to radiators throughout the building.",
    datatype=XSD.string)))
g.add((BLDG.MyBuilding, KEB.cnx, BLDG.VS01))

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

```
"Inlet air duct for the AHU fresh-air branch.
Flow medium: air.
Flow direction: Outdoor intake → Temperature sensor → Air filter →
Modulating damper → Supply fan → Heat exchanger.
Exposed points: temperature (°C), damper position (%), fan speed (%)."
```

## Reference

For detailed patterns, design rationale, and a complete example model, read:
`${CLAUDE_SKILL_DIR}/kebgraph-reference.md`
