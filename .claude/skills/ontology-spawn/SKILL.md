---
name: ontology-spawn
description: Convert a folder of heterogeneous documents (PDFs, images, markdown, CSV, TTL, spreadsheets, anything) into a KebGraph semantic model (.ttl). Point it at a folder, it reads everything, extracts building knowledge, and writes a Turtle RDF file. Use when the user wants to create a knowledge graph from raw building documents.
---

# Ontology Spawn

Turn a folder of raw documents into a KebGraph semantic model.

## How it works

1. User gives you a folder path
2. You read every file in it — PDFs, images, markdown, CSV, TTL, text, whatever is there
3. You extract building knowledge: systems, sensors, equipment, spaces, relationships, operating parameters
4. You write a KebGraph TTL file in the same folder

The LLM (you) is the parser. No format-specific tooling needed — just read and understand.

## Step 1: Discover

Glob the folder for all files. Read them all. For large folders, prioritize:
- PDFs and markdown first (richest context)
- Images (floor plans, system diagrams, P&ID, photos)
- Existing TTL/RDF files (prior models to extend or incorporate)
- CSV/spreadsheet data (sensor lists, equipment registers, point lists)
- Any other text files

Use the Read tool for everything — it handles PDFs, images, and text natively.

For very large PDFs (>10 pages), read in chunks using the `pages` parameter.

## Step 2: Extract

As you read, identify:

**Sets** (logical groupings):
- The building itself (top-level Set)
- Floors, wings, zones
- Rooms and spaces
- HVAC systems (ventilation, heating, cooling, DHW)
- Subsystems (duct branches, pipe loops, circuits)

**Actors** (data points and controllable equipment):
- Sensors: temperature, humidity, CO2, pressure, flow, power, occupancy
- Valves: heating, cooling, control valves
- Dampers: air dampers, fire dampers
- Fans: supply, exhaust, fan coil units
- Meters: energy, water, electricity
- Alarms and setpoints

**Captions** (rich context for each node):
- Purpose and function
- Operating ranges, setpoints, deadbands
- Database IDs, BACnet addresses, file paths to data
- Control sequences and dependencies
- Physical location details

**Only model what is monitored or controlled.** Passive infrastructure (pipes, ducts, walls) becomes context in Captions, not separate nodes.

## Step 3: Build the namespace

Derive the building namespace from the building name:

```
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/{BuildingName}#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

Use a short, ASCII-safe building prefix (e.g., `rio10`, `ct42`, `axg32`).

## Step 4: Write the TTL

Write the file directly using the Write tool. KebGraph TTL is simple enough to write by hand — no Python script needed.

Output file: `{folder}/{building_name}.ttl`

### TTL structure

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/BuildingName#> .
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Building (top-level Set)
bldg:BuildingName a keb:Set ;
    keb:cnx bldg:Floor1,
        bldg:VS01 ;
    keb:hasCaption """Building name and address.
Built: year. Type: office/residential/etc.
Key systems: heating, cooling, ventilation.
Summary of what's in the documents."""^^xsd:string .

# Floor (Set)
bldg:Floor1 a keb:Set ;
    keb:cnx bldg:Room_01_A1 ;
    keb:hasCaption "1st floor description from documents."^^xsd:string .

# Room (Set with Actors)
bldg:Room_01_A1 a keb:Set ;
    keb:hasActor bldg:Room_01_A1_GT11,
        bldg:Room_01_A1_SV2x ;
    keb:hasCaption "Room details from documents."^^xsd:string .

# Temperature sensor (Actor)
bldg:Room_01_A1_GT11 a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption "Sensor details. Setpoint: 22C. Database ID: xxx."^^xsd:string .

# Heating valve (Actor)
bldg:Room_01_A1_SV2x a keb:Actor,
        brick:Control_Valve ;
    keb:hasCaption "Valve details from documents."^^xsd:string .
```

### KebGraph rules

- **4 edge types only**: `rdf:type`, `keb:cnx` (Set→Set), `keb:hasActor` (Set→Actor), `keb:hasCaption` (any→Literal)
- **No Actor-to-Actor edges.** Actors are always grouped through Sets.
- **Actors must be real data points** — things you can query or control. Not passive equipment.
- **Captions carry the detail** — operating ranges, flow direction, control sequences, database IDs. When in doubt, put it in a Caption.
- **Sets provide hierarchy** — Building → Floor → Room, or Building → System → Subsystem.
- **Dual-type entities** are allowed — something can be both a Set and an Actor (e.g., a heat exchanger that has sub-sensors AND generates its own data).

### Common Brick types

| What you find | Brick class |
|---|---|
| Temperature sensor | `brick:Temperature_Sensor` |
| Humidity sensor | `brick:Humidity_Sensor` |
| CO2 sensor | `brick:CO2_Sensor` |
| Pressure sensor | `brick:Pressure_Sensor` |
| Flow sensor | `brick:Flow_Sensor` |
| Power meter | `brick:Thermal_Power_Sensor` or `brick:Electric_Power_Sensor` |
| Control valve | `brick:Control_Valve` |
| General valve | `brick:Valve` |
| Air damper | `brick:Damper` |
| Fan | `brick:Fan` |
| Exhaust fan | `brick:Exhaust_Fan` |
| Heat exchanger | `brick:Heat_Exchanger` |
| Radiator (if monitored) | `brick:Radiator` |
| Smoke detector | `brick:Smoke_Detector` |

## Step 5: Summarize

After writing the TTL, tell the user:
- How many Sets and Actors were created
- What source documents contributed most
- What was ambiguous or unclear in the source material
- What could be improved with more data (e.g., "no database IDs found — Captions use placeholder xxx")

## Tips

- **Floor plans and P&ID images** are gold — they show spatial layout, system topology, and sensor placement. Read them carefully.
- **BMS point lists** (often CSV or Excel) map directly to Actors. Each row is typically one sensor or actuator.
- **Control descriptions** go into Set Captions as control sequences.
- **If an existing TTL file is in the folder**, read it first — you may be extending an existing model rather than starting from scratch.
- **Swedish HVAC naming**: GT=temp sensor, GQ=CO2, GH=humidity, GP=pressure, SV=valve, ST=damper, TF=supply fan, FF=exhaust fan, VVX=heat exchanger, VS=heating system, KB=cooling system.
- **When information conflicts** between documents, note the conflict in the relevant Caption rather than guessing which is correct.
- **Database IDs**: if point lists include database identifiers, BACnet addresses, or Modbus registers, always include them in Actor Captions. These are the ground-truth anchors.
