# Brick Reference

## Contents

1. What Brick is
2. Core concepts
3. Core class hierarchy
4. Relationship decision table
5. A practical modeling workflow
6. Minimal modeling patterns
7. SPARQL snippets
8. BMS point mapping guide
9. Common pitfalls
10. Modeling checklist

## What Brick is

Brick is an ontology-based metadata schema for buildings. It represents the physical, logical, and virtual entities in buildings and the relationships among them. Brick is designed for machine-readable building metadata that can support portable analytics, controls, and operations workflows.

Use Brick when the task needs more than ad hoc labels. Brick is strongest when the goal is portable software, reusable queries, maintainable metadata, and integration across vendors or subsystems.

## Core concepts

### Entity

An entity is a physical, logical, or virtual thing in a building.

- Physical entities: buildings, floors, rooms, AHUs, VAVs, fans, meters, thermostats
- Virtual entities: sensors, commands, setpoints, status points, computed points
- Logical entities: HVAC zones, lighting zones, collections defined by rules

### Class

A class gives an entity its type. Prefer classes as the primary type system.

Examples:

- `brick:AHU`
- `brick:VAV`
- `brick:Room`
- `brick:Supply_Air_Temperature_Sensor`
- `brick:Zone_Air_Cooling_Temperature_Setpoint`

### Tag

Tags are annotations. They are useful for search and discovery, but they are not the primary typing mechanism. Do not replace explicit classes with loose tag bundles.

### Relationship

Relationships give the model its operational meaning. In practice, a good Brick model is often more about correct relationships than about squeezing every entity into the most specific possible class.

## Core class hierarchy

### Equipment
```
Equipment
├── HVAC_Equipment
│   ├── AHU (Air Handling Unit)
│   ├── VAV (Variable Air Volume Box)
│   ├── FCU (Fan Coil Unit)
│   ├── CRAC (Computer Room Air Conditioning)
│   ├── Fan (Supply_Fan, Return_Fan, Exhaust_Fan, Relief_Fan)
│   ├── Pump (Chilled_Water_Pump, Hot_Water_Pump, Condenser_Water_Pump)
│   ├── Chiller (Centrifugal_Chiller, Absorption_Chiller)
│   ├── Boiler (Gas_Boiler, Electric_Boiler)
│   ├── Heat_Exchanger (Condenser, Evaporator)
│   ├── Cooling_Tower
│   ├── Damper (Supply_Damper, Return_Damper, Exhaust_Damper, Outside_Damper)
│   ├── Valve (Chilled_Water_Valve, Hot_Water_Valve, Bypass_Valve)
│   ├── Coil (Cooling_Coil, Heating_Coil)
│   ├── Compressor
│   ├── Filter
│   ├── Humidifier / Dehumidifier
│   ├── Heat_Pump
│   ├── Terminal_Unit
│   └── HRV / ERV (Heat/Energy Recovery Ventilator)
├── Electrical_Equipment
│   ├── Transformer
│   ├── Switchgear
│   ├── Inverter (Solar_Inverter)
│   ├── Battery / Energy_Storage
│   └── EV_Charging_Station
├── Lighting_Equipment
│   ├── Luminaire
│   └── Lighting_Driver
├── Meter
│   ├── Electrical_Meter (Building_Electrical_Meter, Panel_Electrical_Meter)
│   ├── Gas_Meter
│   ├── Water_Meter (Chilled_Water_Meter, Hot_Water_Meter)
│   └── Thermal_Power_Meter
├── Solar_Panel
├── Water_Heater (Electric_Water_Heater, Gas_Water_Heater)
└── ICT_Equipment (Server, Controller, Gateway)
```

### Point (data points — sensors, commands, setpoints)
```
Point
├── Sensor
│   ├── Temperature_Sensor
│   │   ├── Air_Temperature_Sensor (Zone_Air_Temperature_Sensor, Supply_Air_Temperature_Sensor,
│   │   │   Return_Air_Temperature_Sensor, Outside_Air_Temperature_Sensor,
│   │   │   Discharge_Air_Temperature_Sensor, Mixed_Air_Temperature_Sensor)
│   │   ├── Water_Temperature_Sensor (Chilled_Water_Temperature_Sensor,
│   │   │   Hot_Water_Temperature_Sensor, Entering/Leaving_Water_Temperature_Sensor)
│   │   └── Soil_Temperature_Sensor
│   ├── Humidity_Sensor (Relative_Humidity_Sensor, Zone/Outside/Return/Supply_Air_Humidity_Sensor)
│   ├── Pressure_Sensor (Static_Pressure_Sensor, Differential_Pressure_Sensor)
│   ├── Flow_Sensor (Air_Flow_Sensor, Water_Flow_Sensor, Supply/Return_Air_Flow_Sensor)
│   ├── CO2_Sensor (Zone_CO2_Sensor)
│   ├── Occupancy_Sensor / People_Count_Sensor
│   ├── Power_Sensor / Energy_Sensor
│   ├── Voltage_Sensor / Current_Sensor
│   ├── Speed_Sensor
│   └── Illuminance_Sensor
├── Setpoint
│   ├── Temperature_Setpoint (Zone_Air_Temperature_Setpoint, Cooling/Heating_Temperature_Setpoint,
│   │   Supply_Air_Temperature_Setpoint, Occupied/Unoccupied/Standby_*_Setpoint)
│   ├── Pressure_Setpoint (Static_Pressure_Setpoint)
│   ├── Flow_Setpoint (Supply_Air_Flow_Setpoint)
│   ├── Humidity_Setpoint
│   └── Speed_Setpoint
├── Command
│   ├── On_Off_Command (Fan_On_Off_Command, Pump_On_Off_Command)
│   ├── Frequency_Command
│   ├── Speed_Command (Fan_Speed_Command)
│   ├── Position_Command (Damper_Position_Command, Valve_Position_Command)
│   ├── Mode_Command (Cooling/Heating/Occupied_Mode_Command)
│   └── Enable_Command / Disable_Command
├── Status
│   ├── On_Off_Status (Fan_On_Off_Status, Pump_On_Off_Status)
│   ├── Mode_Status (Occupancy_Mode_Status, Cooling/Heating_Mode_Status)
│   ├── Fault_Status
│   ├── Run_Status
│   └── Speed_Status
├── Alarm
│   ├── Temperature_Alarm (High/Low_Temperature_Alarm)
│   ├── Pressure_Alarm
│   ├── Humidity_Alarm
│   └── CO2_Alarm
└── Parameter
    ├── Delay_Parameter
    ├── Deadband_Parameter
    ├── Proportional_Band_Parameter
    └── Integral_Time_Parameter
```

### Location (spatial hierarchy)
```
Location
├── Site
├── Building
├── Floor (Basement, Roof)
├── Room (Office, Conference_Room, Laboratory, Server_Room, Mechanical_Room, Electrical_Room)
├── Space
├── Wing
├── Zone (HVAC_Zone, Lighting_Zone, Fire_Zone)
└── Outdoor_Area
```

## Relationship decision table

| If the meaning is... | Prefer | Inverse | Example |
| --- | --- | --- | --- |
| telemetry or command belongs to equipment or a space | `brick:hasPoint` | `brick:isPointOf` | VAV hasPoint damper position command |
| physical placement | `brick:hasLocation` | `brick:isLocationOf` | thermostat hasLocation room |
| composition or containment that defines the subject | `brick:hasPart` | `brick:isPartOf` | AHU hasPart supply fan |
| distribution or downstream flow | `brick:feeds` | `brick:isFedBy` | AHU feeds VAV |
| metering | `brick:meters` | `brick:isMeteredBy` | Meter meters Equipment |
| meter hierarchy | `brick:hasSubMeter` | `brick:isSubMeterOf` | Building meter hasSubMeter panel meter |
| control | `brick:controls` | `brick:isControlledBy` | Controller controls Equipment |

### Fast rule of thumb

- Ask "Is this thing part of the definition of the parent?" If yes, use `hasPart`.
- Ask "Is this thing merely located somewhere?" If yes, use `hasLocation`.
- Ask "Is this telemetry or control data about something?" If yes, use `hasPoint` or `isPointOf`.
- Ask "Does air, water, power, or another distributed resource go from A to B?" If yes, use `feeds`.

## A practical modeling workflow

### 1. Start from the application

Use the minimum metadata needed to answer the user's query or power the target application. This is the semantic sufficiency mindset: the model is finished when it supports the desired workflows well enough.

### 2. Model spaces first

For most building use cases, model:

- building
- floor
- room
- zone, if the application reasons about zones rather than only rooms

### 3. Add major equipment

Start with major equipment classes and only add subcomponents when required by the task.

Examples:

- `brick:AHU`
- `brick:VAV`
- `brick:Thermostat`
- `brick:Electric_Meter`

### 4. Add the points the application actually uses

Model the points needed for control logic, fault detection, energy analysis, or the query at hand.

### 5. Connect with the right relationships

Most useful Brick queries depend on a small set of relationships used consistently.

### 6. Validate

Check syntax, then validate against Brick shapes or a Brick-aware tool such as `brickschema` or BuildingMOTIF.

## Minimal modeling patterns

### Pattern A: room and thermostat

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix ex: <urn:demo#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:bldg a brick:Building .
ex:f1 a brick:Floor ;
    brick:isPartOf ex:bldg .
ex:r101 a brick:Room ;
    brick:isPartOf ex:f1 .

ex:tstat1 a brick:Thermostat ;
    brick:hasLocation ex:r101 .

ex:zat1 a brick:Zone_Air_Temperature_Sensor ;
    brick:isPointOf ex:tstat1 .

ex:csp1 a brick:Zone_Air_Cooling_Temperature_Setpoint ;
    brick:isPointOf ex:tstat1 .
```

### Pattern B: AHU, VAV, and HVAC zone

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix ex: <urn:demo#> .

ex:ahu1 a brick:AHU .
ex:vav1 a brick:VAV .
ex:zone1 a brick:HVAC_Zone .

ex:ahu1 brick:feeds ex:vav1 .
ex:vav1 brick:feeds ex:zone1 .

ex:sat1 a brick:Supply_Air_Temperature_Sensor ;
    brick:isPointOf ex:ahu1 .

ex:afs1 a brick:Air_Flow_Sensor ;
    brick:isPointOf ex:vav1 .
```

### Pattern C: composition vs location

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix ex: <urn:demo#> .

ex:vav1 a brick:VAV ;
    brick:hasPart ex:damper1 ;
    brick:hasLocation ex:r101 .

ex:damper1 a brick:Damper .
ex:r101 a brick:Room .
```

Here, the damper is part of the VAV. The VAV is located in the room. The room is not part of the VAV.

## SPARQL snippets

### Equipment and points

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?equip ?equipType ?point ?pointType WHERE {
  ?equip brick:hasPoint ?point .
  ?equip rdf:type ?equipType .
  ?point rdf:type ?pointType .
  FILTER(STRSTARTS(STR(?equipType), STR(brick:)))
  FILTER(STRSTARTS(STR(?pointType), STR(brick:)))
}
ORDER BY ?equip ?point
```

### Full feed chain (what feeds what)

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?upstream ?downstream WHERE {
  ?upstream brick:feeds+ ?downstream .
}
```

### All sensors in a zone with their equipment

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?zone ?equip ?sensor ?sensorType WHERE {
  ?zone a brick:HVAC_Zone .
  ?equip brick:feeds ?zone .
  ?equip brick:hasPoint ?sensor .
  ?sensor a ?sensorType .
  ?sensorType rdfs:subClassOf* brick:Sensor .
}
```

### Spatial hierarchy

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?building ?floor ?room WHERE {
  ?room a brick:Room .
  ?room brick:isPartOf ?floor .
  ?floor a brick:Floor .
  ?floor brick:isPartOf ?building .
  ?building a brick:Building .
}
```

### Equipment in a specific location

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?equip ?equipType WHERE {
  ?equip a ?equipType .
  ?equipType rdfs:subClassOf* brick:Equipment .
  ?equip brick:hasLocation ?loc .
  ?loc a brick:Mechanical_Room .
}
```

### Temperature sensors with their measurement context

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?sensor ?sensorType ?equip WHERE {
  ?sensor a ?sensorType .
  ?sensorType rdfs:subClassOf* brick:Temperature_Sensor .
  ?sensor brick:isPointOf ?equip .
}
```

### All meters and what they measure

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?meter ?meterType ?target ?targetType WHERE {
  ?meter a ?meterType .
  ?meterType rdfs:subClassOf* brick:Meter .
  ?meter brick:meters ?target .
  ?target a ?targetType .
}
```

### Type counts

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?type (COUNT(?entity) AS ?count) WHERE {
  ?entity rdf:type ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
```

## BMS point mapping guide

When mapping BMS/BAS point names to Brick classes, use this pattern:

| BMS Pattern | Brick Class |
|-------------|-------------|
| `SAT`, `SupplyAirTemp` | `Supply_Air_Temperature_Sensor` |
| `RAT`, `ReturnAirTemp` | `Return_Air_Temperature_Sensor` |
| `OAT`, `OutsideAirTemp` | `Outside_Air_Temperature_Sensor` |
| `DAT`, `DischargeAirTemp` | `Discharge_Air_Temperature_Sensor` |
| `MAT`, `MixedAirTemp` | `Mixed_Air_Temperature_Sensor` |
| `ZAT`, `ZoneTemp`, `RoomTemp` | `Zone_Air_Temperature_Sensor` |
| `RH`, `Humidity` | `Relative_Humidity_Sensor` |
| `CO2` | `CO2_Sensor` |
| `SAF`, `SupplyAirFlow` | `Supply_Air_Flow_Sensor` |
| `SP`, `StaticPressure` | `Static_Pressure_Sensor` |
| `DmprCmd`, `DamperPos` | `Damper_Position_Command` |
| `VlvCmd`, `ValvePos` | `Valve_Position_Command` |
| `FanSpd`, `FanSpeed` | `Fan_Speed_Command` |
| `FanStatus`, `FanSts` | `Fan_On_Off_Status` |
| `CoolingSP`, `ClgSP` | `Cooling_Temperature_Setpoint` |
| `HeatingSP`, `HtgSP` | `Heating_Temperature_Setpoint` |
| `OccSts`, `Occupancy` | `Occupancy_Status` |
| `kW`, `Power` | `Power_Sensor` |
| `kWh`, `Energy` | `Energy_Sensor` |

## Common pitfalls

### 1. Using tags as the type system

Do not say an entity is a supply air temperature sensor only because it has words like supply, air, temperature, and sensor attached informally. Assign an explicit class.

### 2. Confusing location with composition

- Room contains thermostat by location
- AHU contains fan by composition

Those are different semantics.

### 3. Over-specializing before the evidence exists

If the source label is only `SAT`, you may know it is a temperature sensor but not yet whether it is supply air, discharge air, or mixed air. Use the safest defensible class and explain what would let you specialize it.

### 4. Leaving points unattached

A point with a class but no `isPointOf` or inverse `hasPoint` is often much less useful operationally.

### 5. Modeling everything in one pass

For real projects, iterate. Start with semantically sufficient coverage, validate, run the target queries, then enrich.

## Modeling checklist

Before returning a Brick answer or graph, verify:

- every important entity has an explicit class
- points are attached to equipment or spaces
- spaces are connected into a spatial hierarchy when relevant
- `hasPart` is not being used where `hasLocation` should be used
- `feeds` is only used where actual distribution semantics exist
- the graph parses successfully
- if possible, the graph validates against Brick shapes
