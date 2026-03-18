# Simple Building Graph — Reference

## Overview

A simple convention for modeling building systems as RDF graphs. Uses Brick Schema types for classification and organizes data into Points (sensors/actuators), Groups (logical groupings), and Descriptions (natural-language context).

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

### Points

Components that either produce data or receive control commands.

| Category | Examples |
|----------|---------|
| Sensors | Temperature, humidity, CO2, pressure, flow, power, occupancy |
| Valves | Heating control valves, cooling control valves |
| Dampers | Air dampers, outdoor dampers, exhaust dampers |
| Meters | Energy meters, flow meters, thermal power sensors |
| Fans | Supply fans, exhaust fans (when data-generating) |
| Setpoints | Temperature setpoints, pressure setpoints |
| Alarms | High-temp alarms, filter alarms, fire alarms |

**Not Points**: Locations (→ Groups), passive assets (pipes, ducts, walls), non-monitored equipment.

Only model what is actually monitored or controlled.

### Groups

Logical groupings of Points and other Groups.

- **Spatial**: building, floor, room, zone
- **Subsystem**: radiator loop, AHU branch, inlet air duct
- **Conceptual**: HVAC system, heating system, cooling system

Points are always accessed through Groups — no direct Point-to-Point edges.

### Descriptions

Natural-language text attached to Points and Groups via `sg:hasDescription`.

Include: purpose, operating ranges, setpoints, database IDs, control sequences, flow direction, physical context.

**Examples:**

Point description:
```
"Room 02-A1 temperature sensor. Setpoint: 22C.
Database ID: sensor_12345. Unit: Celsius."
```

Group description (room):
```
"Room 02-A1, standard office. Climate controlled. Seats 2-4."
```

Group description (duct with flow direction):
```
"Inlet air duct. Flow: Outdoor intake → Filter →
Damper → Supply fan → Heat exchanger."
```

## Edge Types

| Edge | Purpose | Domain → Range |
|------|---------|----------------|
| `rdf:type` | Classification (Brick types) | Entity → Class |
| `sg:contains` | Hierarchy / linking | Group → Group |
| `sg:hasPoint` | Point membership | Group → Point |
| `sg:hasDescription` | Text context | Any → xsd:string Literal |

## Common Brick Types

| Domain | Brick Class |
|--------|------------|
| Temperature | `brick:Temperature_Sensor` |
| Humidity | `brick:Humidity_Sensor` |
| CO2 | `brick:CO2_Sensor` |
| Pressure | `brick:Pressure_Sensor` |
| Flow | `brick:Flow_Sensor` |
| Power | `brick:Thermal_Power_Sensor`, `brick:Electric_Power_Sensor` |
| Valves | `brick:Control_Valve`, `brick:Valve` |
| Dampers | `brick:Damper`, `brick:Outside_Damper` |
| Fans | `brick:Fan`, `brick:Exhaust_Fan` |
| Heat exchangers | `brick:Heat_Exchanger` |
| Safety | `brick:Smoke_Detector`, `brick:Fire_Alarm` |

## Design Patterns

### Dual-Type Entities

Some components are both a Group and a Point — e.g., a heat exchanger that contains child sensors but also generates data itself.

```python
g.add((BLDG.VVX, RDF.type, SG.Group))
g.add((BLDG.VVX, RDF.type, SG.Point))
g.add((BLDG.VVX, RDF.type, BRICK.Heat_Exchanger))
g.add((BLDG.VVX, SG.hasDescription, Literal(
    "VVX heat recovery unit. Efficiency: ~75%.",
    datatype=XSD.string)))
g.add((BLDG.VVX, SG.hasPoint, BLDG.VVX_GT_Inlet))
g.add((BLDG.FTX, SG.contains, BLDG.VVX))
```

### Room Pattern

```python
g.add((BLDG.Room_02_A1, RDF.type, SG.Group))
g.add((BLDG.Room_02_A1, SG.hasDescription, Literal(
    "Room 02-A1, standard office. Seats 2-4.",
    datatype=XSD.string)))

g.add((BLDG.Room_02_A1_GT11, RDF.type, SG.Point))
g.add((BLDG.Room_02_A1_GT11, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.Room_02_A1_GT11, SG.hasDescription, Literal(
    "Room 02-A1 temperature sensor. Setpoint: 22C. "
    "Database ID: xxx", datatype=XSD.string)))
g.add((BLDG.Room_02_A1, SG.hasPoint, BLDG.Room_02_A1_GT11))
```

### System Pattern

```python
g.add((BLDG.VS01, RDF.type, SG.Group))
g.add((BLDG.VS01, SG.hasDescription, Literal(
    "VS01 - Heating system. District heating to radiators.",
    datatype=XSD.string)))
g.add((BLDG.Building, SG.contains, BLDG.VS01))

g.add((BLDG.VS01_SupplyTemp, RDF.type, SG.Point))
g.add((BLDG.VS01_SupplyTemp, RDF.type, BRICK.Temperature_Sensor))
g.add((BLDG.VS01_SupplyTemp, SG.hasDescription, Literal(
    "VS01 supply temperature. Unit: Celsius. Database ID: xxx",
    datatype=XSD.string)))
g.add((BLDG.VS01, SG.hasPoint, BLDG.VS01_SupplyTemp))
```

## Complete Example TTL

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://opennekaise.com/buildings/ExampleOffice#> .
@prefix sg: <https://opennekaise.com/SimpleGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:ExampleOffice a sg:Group ;
    sg:contains bldg:Floor1,
        bldg:VS01,
        bldg:KB01 ;
    sg:hasDescription """Example Office Building
Address: Exempelvägen 1, Stockholm
Built: 2020. 1 floor, 2 rooms. District heating and cooling."""^^xsd:string .

bldg:Floor1 a sg:Group ;
    sg:contains bldg:Room_01_A1,
        bldg:Room_01_B2 ;
    sg:hasDescription "1st Floor - 2 office rooms."^^xsd:string .

bldg:Room_01_A1 a sg:Group ;
    sg:hasPoint bldg:Room_01_A1_GT11,
        bldg:Room_01_A1_GQ41,
        bldg:Room_01_A1_SV2x ;
    sg:hasDescription "Room 01-A1, standard office. Heated by radiator."^^xsd:string .

bldg:Room_01_A1_GT11 a sg:Point,
        brick:Temperature_Sensor ;
    sg:hasDescription "Room 01-A1 temperature sensor. Setpoint: 22C. Database ID: t_01a1"^^xsd:string .

bldg:Room_01_A1_GQ41 a sg:Point,
        brick:CO2_Sensor ;
    sg:hasDescription "Room 01-A1 CO2 sensor. Upper limit: 800ppm. Database ID: co2_01a1"^^xsd:string .

bldg:Room_01_A1_SV2x a sg:Point,
        brick:Control_Valve ;
    sg:hasDescription "Room 01-A1 heating control valve. Database ID: sv_01a1"^^xsd:string .

bldg:Room_01_B2 a sg:Group ;
    sg:hasPoint bldg:Room_01_B2_GT11,
        bldg:Room_01_B2_SV2x ;
    sg:hasDescription "Room 01-B2, meeting room. Heating and cooling."^^xsd:string .

bldg:Room_01_B2_GT11 a sg:Point,
        brick:Temperature_Sensor ;
    sg:hasDescription "Room 01-B2 temperature sensor. Setpoint: 22C. Database ID: t_01b2"^^xsd:string .

bldg:Room_01_B2_SV2x a sg:Point,
        brick:Control_Valve ;
    sg:hasDescription "Room 01-B2 heating control valve. Database ID: sv2_01b2"^^xsd:string .

bldg:VS01 a sg:Group ;
    sg:hasPoint bldg:VS01_SupplyTemp,
        bldg:VS01_Flow ;
    sg:hasDescription "VS01 - Heating system. District heating to radiators."^^xsd:string .

bldg:VS01_SupplyTemp a sg:Point,
        brick:Temperature_Sensor ;
    sg:hasDescription "VS01 supply temperature. Database ID: vs01_st"^^xsd:string .

bldg:VS01_Flow a sg:Point,
        brick:Flow_Sensor ;
    sg:hasDescription "VS01 flow sensor. Database ID: vs01_flow"^^xsd:string .

bldg:KB01 a sg:Group ;
    sg:hasPoint bldg:KB01_SupplyTemp ;
    sg:hasDescription "KB01 - Cooling system."^^xsd:string .

bldg:KB01_SupplyTemp a sg:Point,
        brick:Temperature_Sensor ;
    sg:hasDescription "KB01 supply temperature. Database ID: kb01_st"^^xsd:string .
```

## SPARQL Query Patterns

### Find all Points in a room
```sparql
SELECT ?point ?type ?desc WHERE {
    <room-uri> sg:hasPoint ?point .
    ?point a ?type .
    FILTER(?type != sg:Point)
    OPTIONAL { ?point sg:hasDescription ?desc }
}
```

### Get building topology
```sparql
SELECT ?parent ?child ?desc WHERE {
    ?parent sg:contains ?child .
    ?parent a sg:Group .
    ?child a sg:Group .
    OPTIONAL { ?child sg:hasDescription ?desc }
}
```

### Find sensors by type
```sparql
SELECT ?point ?group ?desc WHERE {
    ?point a brick:Temperature_Sensor .
    ?group sg:hasPoint ?point .
    OPTIONAL { ?point sg:hasDescription ?desc }
}
```

### Count Points per Group
```sparql
SELECT ?group ?desc (COUNT(?point) AS ?num_points) WHERE {
    ?group a sg:Group .
    ?group sg:hasPoint ?point .
    OPTIONAL { ?group sg:hasDescription ?desc }
} GROUP BY ?group ?desc
ORDER BY DESC(?num_points)
```

## Using ontology_tool.py

```bash
ONTOOL="${CLAUDE_SKILL_DIR}/../ontology/scripts/ontology_tool.py"

python3 "$ONTOOL" parse model.ttl
python3 "$ONTOOL" list-classes model.ttl
python3 "$ONTOOL" topology model.ttl
python3 "$ONTOOL" query model.ttl "SELECT ?s ?desc WHERE { ?s sg:hasDescription ?desc }"
python3 "$ONTOOL" validate model.ttl
```
