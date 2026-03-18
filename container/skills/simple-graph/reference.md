# Simple Building Graph — Reference

## Overview

A simple convention for modeling building systems as RDF graphs. Uses Brick Schema types for classification and organizes data into Sets (groupings), Actors (data/control points), and Captions (natural-language context).

## Namespace

```
sg:    <https://opennekaise.com/SimpleGraph#>
brick: <https://brickschema.org/schema/Brick#>
xsd:   <http://www.w3.org/2001/XMLSchema#>
```

Building-specific namespaces follow the pattern:
```
https://opennekaise.com/buildings/{BuildingName}#
```

## Core Concepts

### Actors

**Definition**: Components that either produce data or receive control commands.

**Two categories**:
1. **Data generators**: sensors, meters, fan efficiency readings, valve positions, alarms
2. **Control receivers**: actuators, control valves, dampers, setpoints

**What IS an Actor**:
| Category | Examples |
|----------|---------|
| Sensors | Temperature, humidity, CO2, pressure, flow, power, occupancy |
| Valves | Heating control valves, cooling control valves, main circuit valves |
| Dampers | Air dampers, outdoor dampers, exhaust dampers |
| Meters | Energy meters, flow meters, thermal power sensors |
| Fans | Supply fans, exhaust fans (when data-generating) |
| Setpoints | Temperature setpoints, pressure setpoints |
| Alarms | High-temp alarms, filter alarms, fire alarms |

**What is NOT an Actor**:
| Category | Examples |
|----------|---------|
| Locations | Rooms, floors, zones, buildings → these are **Sets** |
| Passive assets | Pipes, ducts, walls, windows, roofs |
| Non-monitored equipment | Radiators (unless metered), tanks, batteries |

**Exception**: Radiators CAN be Actors when they have monitoring data. The rule is: **only model what is actually monitored or controlled**.

### Sets

**Definition**: Logical groupings of Actors and other Sets.

**Use cases**:
- **Spatial**: building, floor, room, zone
- **Subsystem**: radiator loop, AHU branch, chilled-water circuit, inlet air duct
- **Conceptual**: HVAC system, heating system, cooling system

**No Actor-to-Actor edges**: Actors are always grouped through Sets.

### Captions

**Definition**: Natural-language text nodes attached to Actors and Sets via `sg:hasCaption`.

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

Set caption (room):
```
"Room ID: 02-A1, Room type: 301 (Standard office).
Climate controlled with heating, cooling, and ventilation. Seats 2-4 people."
```

Set caption (duct with flow direction):
```
"Inlet air duct for the AHU fresh-air branch. Flow medium: air.
Flow direction: Outdoor intake → Temperature sensor → Air filter →
Modulating damper → Supply fan → Heat exchanger.
Exposed points: temperature (°C), damper position (%), fan speed (%)."
```

## Edge Types

| Edge | Purpose | Domain → Range |
|------|---------|----------------|
| `rdf:type` | Classification (reuses Brick types) | Entity → Class |
| `sg:cnx` | System linking / hierarchy | Set → Set |
| `sg:hasActor` | Actor membership | Set → Actor |
| `sg:hasCaption` | Natural-language context | Actor or Set → xsd:string Literal |

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
g.add((BLDG.VVX, RDF.type, SG.Set))
g.add((BLDG.VVX, RDF.type, SG.Actor))
g.add((BLDG.VVX, RDF.type, BRICK.Heat_Exchanger))
g.add((BLDG.VVX, SG.hasCaption, Literal(
    "VVX heat recovery unit. Efficiency: ~75%. "
    "Has inlet/outlet temp sensors.", datatype=XSD.string)))
g.add((BLDG.VVX, SG.hasActor, BLDG.VVX_GT_Inlet))
g.add((BLDG.FTX, SG.cnx, BLDG.VVX))
```

### 2. Room Climate Control Pattern

```python
# Room as Set
g.add((BLDG.Room_02_A1, RDF.type, SG.Set))
g.add((BLDG.Room_02_A1, SG.hasCaption, Literal(
    "Room ID: 02-A1, Room type: 301 (Standard office). "
    "Climate controlled. Seats 2-4.", datatype=XSD.string)))

# Temperature sensor
g.add((BLDG.Room_02_A1_GT11, RDF.type, SG.Actor))
g.add((BLDG.Room_02_A1_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room_02_A1_GT11, SG.hasCaption, Literal(
    "Room 02-A1 temperature sensor. Setpoint: 22C. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, SG.hasActor, BLDG.Room_02_A1_GT11))

# Heating valve
g.add((BLDG.Room_02_A1_SV2x, RDF.type, SG.Actor))
g.add((BLDG.Room_02_A1_SV2x, RDF.type, BRICK.Control_Valve))
g.add((BLDG.Room_02_A1_SV2x, SG.hasCaption, Literal(
    "Room 02-A1 heating control valve. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, SG.hasActor, BLDG.Room_02_A1_SV2x))
```

### 3. System Set Pattern

```python
g.add((BLDG.VS01, RDF.type, SG.Set))
g.add((BLDG.VS01, SG.hasCaption, Literal(
    "VS01 - Heating system for radiators. District heating connection.",
    datatype=XSD.string)))
g.add((BLDG.Building, SG.cnx, BLDG.VS01))

g.add((BLDG.VS01_SupplyTemp, RDF.type, SG.Actor))
g.add((BLDG.VS01_SupplyTemp, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.VS01_SupplyTemp, SG.hasCaption, Literal(
    "VS01 supply temperature. Unit: Celsius. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.VS01, SG.hasActor, BLDG.VS01_SupplyTemp))
```

## Complete Example TTL

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://opennekaise.com/buildings/ExampleOffice#> .
@prefix sg: <https://opennekaise.com/SimpleGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:ExampleOffice a sg:Set ;
    sg:cnx bldg:Floor1,
        bldg:VS01,
        bldg:KB01 ;
    sg:hasCaption """Example Office Building
Address: Exempelvägen 1, Stockholm
Built: 2020
Office: 200 m2
A small office with 1 floor, 2 rooms. District heating and cooling."""^^xsd:string .

bldg:Floor1 a sg:Set ;
    sg:cnx bldg:Room_01_A1,
        bldg:Room_01_B2 ;
    sg:hasCaption "1st Floor - 2 office rooms with individual climate control."^^xsd:string .

bldg:Room_01_A1 a sg:Set ;
    sg:hasActor bldg:Room_01_A1_GT11,
        bldg:Room_01_A1_GQ41,
        bldg:Room_01_A1_SV2x ;
    sg:hasCaption "Room 01-A1, standard office. Heated by radiator. Seats 2."^^xsd:string .

bldg:Room_01_A1_GT11 a sg:Actor,
        brick:Temperature_Sensor ;
    sg:hasCaption "Room 01-A1 temperature sensor. Setpoint: 22C. Database ID: t_01a1"^^xsd:string .

bldg:Room_01_A1_GQ41 a sg:Actor,
        brick:CO2_Sensor ;
    sg:hasCaption "Room 01-A1 CO2 sensor. Upper limit: 800ppm. Database ID: co2_01a1"^^xsd:string .

bldg:Room_01_A1_SV2x a sg:Actor,
        brick:Control_Valve ;
    sg:hasCaption "Room 01-A1 heating control valve. Database ID: sv_01a1"^^xsd:string .

bldg:Room_01_B2 a sg:Set ;
    sg:hasActor bldg:Room_01_B2_GT11,
        bldg:Room_01_B2_SV2x,
        bldg:Room_01_B2_SV4x ;
    sg:hasCaption "Room 01-B2, meeting room. Heating and cooling. Seats 6."^^xsd:string .

bldg:Room_01_B2_GT11 a sg:Actor,
        brick:Temperature_Sensor ;
    sg:hasCaption "Room 01-B2 temperature sensor. Setpoint: 22C. Database ID: t_01b2"^^xsd:string .

bldg:Room_01_B2_SV2x a sg:Actor,
        brick:Control_Valve ;
    sg:hasCaption "Room 01-B2 heating control valve. Database ID: sv2_01b2"^^xsd:string .

bldg:Room_01_B2_SV4x a sg:Actor,
        brick:Control_Valve ;
    sg:hasCaption "Room 01-B2 cooling control valve. Database ID: sv4_01b2"^^xsd:string .

bldg:VS01 a sg:Set ;
    sg:hasActor bldg:VS01_SupplyTemp,
        bldg:VS01_Flow ;
    sg:hasCaption "VS01 - Heating system. District heating to radiators."^^xsd:string .

bldg:VS01_SupplyTemp a sg:Actor,
        brick:Temperature_Sensor ;
    sg:hasCaption "VS01 supply temperature. Unit: Celsius. Database ID: vs01_st"^^xsd:string .

bldg:VS01_Flow a sg:Actor,
        brick:Flow_Sensor ;
    sg:hasCaption "VS01 flow sensor. Unit: L/s. Database ID: vs01_flow"^^xsd:string .

bldg:KB01 a sg:Set ;
    sg:hasActor bldg:KB01_SupplyTemp ;
    sg:hasCaption "KB01 - Cooling system. Chilled water for cooling baffles."^^xsd:string .

bldg:KB01_SupplyTemp a sg:Actor,
        brick:Temperature_Sensor ;
    sg:hasCaption "KB01 supply temperature. Unit: Celsius. Database ID: kb01_st"^^xsd:string .
```

## SPARQL Query Patterns

### Find all Actors in a specific room
```sparql
SELECT ?actor ?type ?caption WHERE {
    <room-uri> sg:hasActor ?actor .
    ?actor a ?type .
    FILTER(?type != sg:Actor)
    OPTIONAL { ?actor sg:hasCaption ?caption }
}
```

### Get full building topology
```sparql
SELECT ?parent ?child ?caption WHERE {
    ?parent sg:cnx ?child .
    ?parent a sg:Set .
    ?child a sg:Set .
    OPTIONAL { ?child sg:hasCaption ?caption }
}
```

### Find all sensors of a specific type
```sparql
SELECT ?actor ?set ?caption WHERE {
    ?actor a brick:Temperature_Sensor .
    ?set sg:hasActor ?actor .
    OPTIONAL { ?actor sg:hasCaption ?caption }
}
```

### Count Actors per Set
```sparql
SELECT ?set ?caption (COUNT(?actor) AS ?num_actors) WHERE {
    ?set a sg:Set .
    ?set sg:hasActor ?actor .
    OPTIONAL { ?set sg:hasCaption ?caption }
} GROUP BY ?set ?caption
ORDER BY DESC(?num_actors)
```

## Using ontology_tool.py

The ontology tool from the ontology skill works with these TTL files:

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"

# Parse and summarize a model
python3 "$ONTOOL" parse model.ttl

# List all Sets and Actors
python3 "$ONTOOL" list-classes model.ttl

# Show topology (Set-to-Set connections)
python3 "$ONTOOL" topology model.ttl

# Run SPARQL queries
python3 "$ONTOOL" query model.ttl "SELECT ?s ?caption WHERE { ?s sg:hasCaption ?caption }"

# Validate structure
python3 "$ONTOOL" validate model.ttl
```
