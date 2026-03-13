# KebGraph Detailed Reference

## Philosophy

KebGraph is an **LLM-native** semantic modeling approach for buildings. Unlike traditional ontologies (Brick, REC, S223) that model complete physical topology with detailed port-level connections, KebGraph focuses on:

1. **Operational relevance** — Only model what generates data or receives control
2. **Compact graphs** — Use Sets for grouping instead of verbose topology
3. **Natural language preservation** — Captions carry rich context without formal relationships
4. **Interoperability** — Reuse Brick/REC/S223 types via `rdf:type`

## Namespace

```
keb:  <https://KebnekaisePlayground.org/KebGraph#>
brick: <https://brickschema.org/schema/Brick#>
xsd:  <http://www.w3.org/2001/XMLSchema#>
```

Building-specific namespaces follow the pattern:
```
https://KebnekaisePlayground.org/KebTown/{BuildingName}#
```

## Core Concepts Deep Dive

### Actors

**Definition**: Components that either produce data or receive control commands.

**Two categories**:
1. **Data generators**: sensors, meters, fan efficiency readings, valve positions, alarms
2. **Control receivers**: actuators, control valves, dampers, setpoints

**What IS an Actor**:
| Category | Examples |
|----------|---------|
| Sensors | Temperature, humidity, CO2, pressure, flow, power, occupancy |
| Valves | Heating control valves (SV2x), cooling control valves (SV4x), main circuit valves |
| Dampers | Air dampers (ST4x), outdoor dampers, exhaust dampers |
| Meters | Energy meters, flow meters, thermal power sensors |
| Fans | Supply fans, exhaust fans, fan coil unit fans (when data-generating) |
| Setpoints | Temperature setpoints, pressure setpoints |
| Alarms | High-temp alarms, filter alarms, fire alarms |

**What is NOT an Actor**:
| Category | Examples |
|----------|---------|
| Locations | Rooms, floors, zones, buildings → these are **Sets** |
| Passive assets | Pipes, ducts, walls, windows, roofs |
| Non-monitored equipment | Radiators (unless metered), tanks, batteries |
| Storage | Water tanks, thermal storage, batteries |

**Exception**: Radiators CAN be Actors when they have monitoring data (e.g., `brick:Radiator` with a Database ID in their Caption). The rule is: **only model what is actually monitored or controlled**.

**Why Actors matter**:
- Anchor the model to ground-truth data sources (database IDs, BACnet addresses, file paths)
- Improve retrieval accuracy and reduce LLM hallucinations
- Scope the model to operational reality

### Sets

**Definition**: Logical groupings of Actors and other Sets.

**Use cases**:
- **Spatial**: building, floor, room, zone
- **Subsystem**: radiator loop, AHU branch, chilled-water circuit, inlet air duct
- **Conceptual**: HVAC system, heating system, cooling system

**Key advantage**: Provides topology and scope through simple grouping. When ordering and flow direction matter, use Captions instead of modeling individual connections.

**No Actor-to-Actor edges**: Actors are always grouped through Sets. This keeps the graph flat and queryable.

### Captions

**Definition**: Natural-language text nodes attached to Actors and Sets via `keb:hasCaption`.

**Status**: First-class nodes in the graph — not comments or annotations.

**What to include in Captions**:
1. Purpose and function of the component/system
2. Component ordering and flow direction (for duct/pipe Sets)
3. Data location: database ID, file path, IP address, BACnet object
4. Operating ranges: setpoints, deadbands, limits
5. Control sequences and dependencies
6. Physical context: location description, solar exposure, occupancy

**Caption examples**:

Actor caption (sensor):
```
"Room 02-A1 temperature sensor. Setpoint: 22C. Deadzone economy: 4C.
Deadzone comfort: 2C. Database ID: sensor_12345. Unit: Celsius."
```

Actor caption (valve):
```
"Room 02-A1 SV2x heating control valve for radiator.
Database ID: valve_67890. Unit: %."
```

Set caption (room):
```
"Room ID: 02-A1, Room type: 301 (Standard office).
Climate controlled with heating, cooling, and ventilation. Seats 2-4 people."
```

Set caption (system):
```
"VS01 - Heating system for radiators. District heating connection
provides hot water to radiators throughout the building."
```

Set caption (duct with flow direction):
```
"Inlet air duct for the AHU fresh-air branch. Flow medium: air.
Flow direction: Outdoor intake → Temperature sensor → Air filter →
Modulating damper → Supply fan → Heat exchanger.
Exposed points: temperature (°C), damper position (%), fan speed (%)."
```

Set caption (room with control sequence):
```
"Room ID: 02-C3, Room type: 301C (Office with fan coil).
Has CAKx fan and SV40x cooling actuator for enhanced cooling.
Control sequence: CAKx varies down -> SV40x closes -> SV4x closes ->
ST4x to min -> SV2x opens for heat.
Reversed for cooling demand. Corner office with extra solar load."
```

## Edge Types

| Edge | Purpose | Domain → Range |
|------|---------|----------------|
| `rdf:type` | Classification (reuses Brick/REC/S223 types) | Entity → Class |
| `keb:cnx` | System linking / hierarchy | Set → Set |
| `keb:hasActor` | Actor membership | Set → Actor |
| `keb:hasCaption` | Natural-language context | Actor or Set → xsd:string Literal |

**Design rationale**: Limited edges reduce modeling effort, simplify maintenance, and make graphs easy to query with SPARQL or direct traversal.

## Common Brick Types for Actors

| Domain | Brick Class |
|--------|------------|
| Temperature | `brick:Temperature_Sensor` |
| Humidity | `brick:Humidity_Sensor` |
| CO2 | `brick:CO2_Sensor` |
| Pressure | `brick:Pressure_Sensor` |
| Flow | `brick:Flow_Sensor` |
| Power | `brick:Thermal_Power_Sensor`, `brick:Electric_Power_Sensor` |
| Valves | `brick:Control_Valve`, `brick:Valve` |
| Dampers | `brick:Damper`, `brick:Outside_Damper`, `brick:Exhaust_Damper` |
| Fans | `brick:Fan`, `brick:Outside_Fan`, `brick:Exhaust_Fan` |
| Radiators | `brick:Radiator` (only when monitored) |
| Heat exchangers | `brick:Heat_Exchanger` |
| Safety | `brick:Smoke_Detector`, `brick:Fire_Alarm` |

## Design Patterns

### 1. Dual-Type Entities

Some components are both a Set (grouping other Actors) and an Actor (generating data themselves). Example: a heat exchanger with an efficiency sensor.

```python
g.add((BLDG.VVX, RDF.type, KEB.Set))
g.add((BLDG.VVX, RDF.type, KEB.Actor))
g.add((BLDG.VVX, RDF.type, BRICK.Heat_Exchanger))
g.add((BLDG.VVX, KEB.hasCaption, Literal(
    "VVX heat recovery unit. Efficiency: ~75%. "
    "Has inlet/outlet temp sensors.", datatype=XSD.string)))
# As a Set, it contains child Actors
g.add((BLDG.VVX, KEB.hasActor, BLDG.VVX_GT_Inlet))
# As part of hierarchy
g.add((BLDG.FTX, KEB.cnx, BLDG.VVX))
```

### 2. Room Climate Control Pattern

Standard room with heating, cooling, and ventilation:

```python
# Room as Set
g.add((BLDG.Room_02_A1, RDF.type, KEB.Set))
g.add((BLDG.Room_02_A1, KEB.hasCaption, Literal(
    "Room ID: 02-A1, Room type: 301 (Standard office). "
    "Climate controlled with heating, cooling, and ventilation. "
    "Seats 2-4 people.", datatype=XSD.string)))

# Temperature sensor
g.add((BLDG.Room_02_A1_GT11, RDF.type, KEB.Actor))
g.add((BLDG.Room_02_A1_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room_02_A1_GT11, KEB.hasCaption, Literal(
    "Room 02-A1 temperature sensor. Setpoint: 22C. "
    "Deadzone economy: 4C. Deadzone comfort: 2C. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, KEB.hasActor, BLDG.Room_02_A1_GT11))

# CO2 sensor
g.add((BLDG.Room_02_A1_GQ41, RDF.type, KEB.Actor))
g.add((BLDG.Room_02_A1_GQ41, RDF.type, BRICK.CO2_Sensor))
g.add((BLDG.Room_02_A1_GQ41, KEB.hasCaption, Literal(
    "Room 02-A1 CO2 sensor. Lower limit: 600ppm. "
    "Upper limit: 800ppm. High CO2: >1000ppm. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, KEB.hasActor, BLDG.Room_02_A1_GQ41))

# Heating valve
g.add((BLDG.Room_02_A1_SV2x, RDF.type, KEB.Actor))
g.add((BLDG.Room_02_A1_SV2x, RDF.type, BRICK.Control_Valve))
g.add((BLDG.Room_02_A1_SV2x, KEB.hasCaption, Literal(
    "Room 02-A1 SV2x heating control valve for radiator. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, KEB.hasActor, BLDG.Room_02_A1_SV2x))

# Cooling valve
g.add((BLDG.Room_02_A1_SV4x, RDF.type, KEB.Actor))
g.add((BLDG.Room_02_A1_SV4x, RDF.type, BRICK.Control_Valve))
g.add((BLDG.Room_02_A1_SV4x, KEB.hasCaption, Literal(
    "Room 02-A1 SV4x cooling control valve. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, KEB.hasActor, BLDG.Room_02_A1_SV4x))

# Air damper
g.add((BLDG.Room_02_A1_ST4x, RDF.type, KEB.Actor))
g.add((BLDG.Room_02_A1_ST4x, RDF.type, BRICK.Damper))
g.add((BLDG.Room_02_A1_ST4x, KEB.hasCaption, Literal(
    "Room 02-A1 air damper. Controls airflow 0-100%. "
    "Deviation limit: +-15%. Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, KEB.hasActor, BLDG.Room_02_A1_ST4x))
```

### 3. System Set Pattern (Heating/Cooling)

Central plant systems with their own monitoring points:

```python
# Heating system
g.add((BLDG.VS01, RDF.type, KEB.Set))
g.add((BLDG.VS01, KEB.hasCaption, Literal(
    "VS01 - Heating system for radiators. District heating connection "
    "provides hot water to radiators throughout the building.",
    datatype=XSD.string)))
g.add((BLDG.Building, KEB.cnx, BLDG.VS01))

# System-level sensors
g.add((BLDG.VS01_SupplyTemp, RDF.type, KEB.Actor))
g.add((BLDG.VS01_SupplyTemp, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.VS01_SupplyTemp, KEB.hasCaption, Literal(
    "VS01 heating system supply temperature. Unit: Celsius. "
    "Log interval: 10 min. Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.VS01, KEB.hasActor, BLDG.VS01_SupplyTemp))

g.add((BLDG.VS01_Flow, RDF.type, KEB.Actor))
g.add((BLDG.VS01_Flow, RDF.type, BRICK.Flow_Sensor))
g.add((BLDG.VS01_Flow, KEB.hasCaption, Literal(
    "VS01 heating system flow sensor. Unit: L/s. "
    "Log interval: 10 min. Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.VS01, KEB.hasActor, BLDG.VS01_Flow))

g.add((BLDG.VS01_Power, RDF.type, KEB.Actor))
g.add((BLDG.VS01_Power, RDF.type, BRICK.Thermal_Power_Sensor))
g.add((BLDG.VS01_Power, KEB.hasCaption, Literal(
    "VS01 heating system thermal power. Unit: W. "
    "Log interval: 10 min. Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.VS01, KEB.hasActor, BLDG.VS01_Power))
```

### 4. AHU / Ventilation Pattern

Air handling units with duct subsystems:

```python
# AHU as top-level system Set
g.add((BLDG.FTX, RDF.type, KEB.Set))
g.add((BLDG.FTX, KEB.hasCaption, Literal(
    "FTX ventilation system with heat recovery. "
    "Serves all floors.", datatype=XSD.string)))
g.add((BLDG.Building, KEB.cnx, BLDG.FTX))

# Inlet air duct (subsystem Set)
g.add((BLDG.InletAirDuct, RDF.type, KEB.Set))
g.add((BLDG.InletAirDuct, KEB.hasCaption, Literal(
    "Inlet air duct for the AHU fresh-air branch. "
    "Flow medium: air. "
    "Flow direction: Outdoor intake → Temperature sensor → "
    "Air filter → Modulating damper → Supply fan → Heat exchanger. "
    "Exposed points: temperature (°C), damper position (%), "
    "fan speed (%).", datatype=XSD.string)))
g.add((BLDG.FTX, KEB.cnx, BLDG.InletAirDuct))

# Actors in the inlet duct
g.add((BLDG.GT41, RDF.type, KEB.Actor))
g.add((BLDG.GT41, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.GT41, KEB.hasCaption, Literal(
    "Inlet air temperature sensor. Measures air temp after filter, "
    "before heat exchanger. Range: -40 to 50C. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.InletAirDuct, KEB.hasActor, BLDG.GT41))
```

### 5. Naming Conventions

Swedish HVAC naming codes commonly found in KebGraph models:

| Code | Meaning | Brick Type |
|------|---------|-----------|
| GT | Temperature sensor (givare temperatur) | `brick:Temperature_Sensor` |
| GQ | CO2 sensor (givare kvalitet) | `brick:CO2_Sensor` |
| GH | Humidity sensor (givare hygrometer) | `brick:Humidity_Sensor` |
| GP | Pressure sensor (givare tryck) | `brick:Pressure_Sensor` |
| GF | Flow sensor (givare flöde) | `brick:Flow_Sensor` |
| SV | Control valve (styrventil) | `brick:Control_Valve` |
| ST | Damper/actuator (ställdon) | `brick:Damper` |
| TF | Fan (tilluftsfläkt) | `brick:Fan` |
| FF | Exhaust fan (frånluftsfläkt) | `brick:Exhaust_Fan` |
| VVX | Heat exchanger (värmeväxlare) | `brick:Heat_Exchanger` |
| CAK | Fan coil unit (kylbaffel) | `brick:Fan` |
| VS | Heating system (värmesystem) | Set |
| KB | Cooling system (kylbaffel) | Set |
| FTX | Ventilation with heat recovery | Set |

Number suffixes indicate position/instance: GT**11** = first temp sensor in subsystem 1, SV**2x** = valve in circuit 2, ST**4x** = damper in subsystem 4.

## Complete Example: Office Building TTL

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/ExampleOffice#> .
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:ExampleOffice a keb:Set ;
    keb:cnx bldg:Floor1,
        bldg:VS01,
        bldg:KB01 ;
    keb:hasCaption """Example Office Building
Address: Exempelvägen 1, Stockholm
Built: 2020
Office: 200 m2
A small office with 1 floor, 2 rooms. District heating and cooling."""^^xsd:string .

bldg:Floor1 a keb:Set ;
    keb:cnx bldg:Room_01_A1,
        bldg:Room_01_B2 ;
    keb:hasCaption "1st Floor - 2 office rooms with individual climate control."^^xsd:string .

bldg:Room_01_A1 a keb:Set ;
    keb:hasActor bldg:Room_01_A1_GT11,
        bldg:Room_01_A1_GQ41,
        bldg:Room_01_A1_SV2x ;
    keb:hasCaption "Room 01-A1, standard office. Heated by radiator. Seats 2."^^xsd:string .

bldg:Room_01_A1_GT11 a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption "Room 01-A1 temperature sensor. Setpoint: 22C. Database ID: t_01a1"^^xsd:string .

bldg:Room_01_A1_GQ41 a keb:Actor,
        brick:CO2_Sensor ;
    keb:hasCaption "Room 01-A1 CO2 sensor. Upper limit: 800ppm. Database ID: co2_01a1"^^xsd:string .

bldg:Room_01_A1_SV2x a keb:Actor,
        brick:Control_Valve ;
    keb:hasCaption "Room 01-A1 heating control valve. Database ID: sv_01a1"^^xsd:string .

bldg:Room_01_B2 a keb:Set ;
    keb:hasActor bldg:Room_01_B2_GT11,
        bldg:Room_01_B2_SV2x,
        bldg:Room_01_B2_SV4x ;
    keb:hasCaption "Room 01-B2, meeting room. Heating and cooling. Seats 6."^^xsd:string .

bldg:Room_01_B2_GT11 a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption "Room 01-B2 temperature sensor. Setpoint: 22C. Database ID: t_01b2"^^xsd:string .

bldg:Room_01_B2_SV2x a keb:Actor,
        brick:Control_Valve ;
    keb:hasCaption "Room 01-B2 heating control valve. Database ID: sv2_01b2"^^xsd:string .

bldg:Room_01_B2_SV4x a keb:Actor,
        brick:Control_Valve ;
    keb:hasCaption "Room 01-B2 cooling control valve. Database ID: sv4_01b2"^^xsd:string .

bldg:VS01 a keb:Set ;
    keb:hasActor bldg:VS01_SupplyTemp,
        bldg:VS01_Flow ;
    keb:hasCaption "VS01 - Heating system. District heating to radiators."^^xsd:string .

bldg:VS01_SupplyTemp a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption "VS01 supply temperature. Unit: Celsius. Database ID: vs01_st"^^xsd:string .

bldg:VS01_Flow a keb:Actor,
        brick:Flow_Sensor ;
    keb:hasCaption "VS01 flow sensor. Unit: L/s. Database ID: vs01_flow"^^xsd:string .

bldg:KB01 a keb:Set ;
    keb:hasActor bldg:KB01_SupplyTemp ;
    keb:hasCaption "KB01 - Cooling system. Chilled water for cooling baffles."^^xsd:string .

bldg:KB01_SupplyTemp a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption "KB01 supply temperature. Unit: Celsius. Database ID: kb01_st"^^xsd:string .
```

## SPARQL Query Patterns

### Find all Actors in a specific room
```sparql
SELECT ?actor ?type ?caption WHERE {
    <room-uri> keb:hasActor ?actor .
    ?actor a ?type .
    FILTER(?type != keb:Actor)
    OPTIONAL { ?actor keb:hasCaption ?caption }
}
```

### Get full building topology
```sparql
SELECT ?parent ?child ?caption WHERE {
    ?parent keb:cnx ?child .
    ?parent a keb:Set .
    ?child a keb:Set .
    OPTIONAL { ?child keb:hasCaption ?caption }
}
```

### Find all sensors of a specific type
```sparql
SELECT ?actor ?set ?caption WHERE {
    ?actor a brick:Temperature_Sensor .
    ?set keb:hasActor ?actor .
    OPTIONAL { ?actor keb:hasCaption ?caption }
}
```

### Find Actors with specific database IDs
```sparql
SELECT ?actor ?caption WHERE {
    ?actor a keb:Actor .
    ?actor keb:hasCaption ?caption .
    FILTER(CONTAINS(?caption, "Database ID"))
}
```

### Find which Set an Actor belongs to
```sparql
SELECT ?set ?set_caption WHERE {
    ?set keb:hasActor <actor-uri> .
    OPTIONAL { ?set keb:hasCaption ?set_caption }
}
```

### Count Actors per Set
```sparql
SELECT ?set ?caption (COUNT(?actor) AS ?num_actors) WHERE {
    ?set a keb:Set .
    ?set keb:hasActor ?actor .
    OPTIONAL { ?set keb:hasCaption ?caption }
} GROUP BY ?set ?caption
ORDER BY DESC(?num_actors)
```

### Find rooms with specific equipment
```sparql
SELECT ?room ?room_caption ?actor ?actor_caption WHERE {
    ?room a keb:Set .
    ?room keb:hasCaption ?room_caption .
    FILTER(CONTAINS(?room_caption, "Room"))
    ?room keb:hasActor ?actor .
    ?actor a brick:Control_Valve .
    OPTIONAL { ?actor keb:hasCaption ?actor_caption }
}
```

## Using ontology_tool.py with KebGraph

The ontology tool from the ontology skill works with KebGraph TTL files:

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"

# Parse and summarize a KebGraph model
python3 "$ONTOOL" parse model.ttl

# List all Sets and Actors
python3 "$ONTOOL" list-classes model.ttl

# Show topology (Set-to-Set connections)
python3 "$ONTOOL" topology model.ttl

# Run SPARQL queries
python3 "$ONTOOL" query model.ttl "SELECT ?s ?caption WHERE { ?s keb:hasCaption ?caption }"

# Describe a specific entity
python3 "$ONTOOL" describe model.ttl "https://KebnekaisePlayground.org/KebTown/Building#Room_01_A1"

# Validate structure
python3 "$ONTOOL" validate model.ttl
```

## Comparison with Other Ontologies

| Aspect | Brick | S223 | KebGraph |
|--------|-------|------|----------|
| Focus | Equipment + Point taxonomy | System topology + ports | Operational data points |
| Topology | `feeds`, `hasPart`, `isLocationOf` | ConnectionPoints + Connections | `cnx` (Set→Set) + `hasActor` (Set→Actor) |
| Detail level | Medium (class hierarchy) | High (port-level) | Low (grouping only) |
| Natural language | Labels only | Labels only | First-class Captions |
| Edge count | Many relationship types | Many (inferred via SHACL) | 4 edge types total |
| LLM readability | Moderate | Low | High (designed for it) |
| Modeling effort | Medium | High | Low |
| Interop | Native | Cross-walks to Brick | Uses Brick types via rdf:type |
