# ASHRAE Standard 223P Reference

Namespace: `http://data.ashrae.org/standard223#` | Prefix: `s223:`
Ontology file: `https://open223.info/223p.ttl`

## Core Modeling Pattern

223P models building systems as **connected topology graphs**. The fundamental pattern:

```
Equipment → OutletConnectionPoint → Connection → InletConnectionPoint → Equipment
```

You only need to assert `s223:cnx` between entities. All other connectivity predicates
(`hasConnectionPoint`, `connectedTo`, `connectedThrough`, etc.) are **inferred by SHACL rules**.

## Key Classes

### Connectable (anything that connects)
```
Connectable
├── Equipment
│   ├── AirHandlingUnit
│   ├── Fan
│   ├── Damper
│   ├── Valve
│   ├── Coil (CoolingCoil, HeatingCoil)
│   ├── Chiller
│   ├── Boiler
│   ├── HeatPump (AirToAirHeatPump)
│   ├── CoolingTower
│   ├── Compressor
│   ├── Filter
│   ├── Pump
│   ├── FanCoilUnit
│   ├── SingleDuctTerminal
│   ├── DualDuctTerminal
│   ├── FanPoweredTerminal
│   ├── ChilledBeam
│   ├── Sensor (ConcentrationSensor, LightSensor, ...)
│   ├── Actuator
│   ├── Controller
│   ├── ElectricityMeter
│   ├── Battery
│   ├── ElectricEnergyTransformer / Inverter / Converter
│   ├── ElectricityBreaker
│   └── EthernetSwitch / EthernetPort
├── Junction (branching points within connections)
└── DomainSpace (spatial zone for a building service domain)
```

### Function (control logic / computed values — NOT a Connectable)
```
Function           # has hasInput/hasOutput → Property
                   # Must have ≥1 hasInput or hasOutput
                   # A Property can be output of at most 1 Function
                   # Maps to CDL Blocks in ASHRAE 231P
```

### ConnectionPoint (ports on equipment)
```
ConnectionPoint
├── InletConnectionPoint      # receives medium
├── OutletConnectionPoint     # sends medium
└── BidirectionalConnectionPoint  # either direction
```

### Connection (physical medium carriers)
```
Connection
├── Duct           # air
├── Pipe           # water/fluid
├── Conductor      # electricity
├── EthernetCable  # network
├── FiberOpticCable
└── CoaxialCable
```

### Property (telemetry points)
```
Property
├── ObservableProperty (sensor readings)
│   ├── QuantifiableObservableProperty  # numeric (temperature, flow)
│   └── EnumeratedObservableProperty    # enumerated (on/off, mode)
├── ActuatableProperty (control outputs)
│   ├── QuantifiableActuatableProperty  # numeric (damper % command)
│   └── EnumeratedActuatableProperty    # enumerated (enable/disable)
└── (inferred from sensors/actuators)
```

### Spatial
```
PhysicalSpace     # physical room/area
DomainSpace       # zone served by a domain (HVAC, Lighting, etc.)
Zone              # groups DomainSpaces with similar service
ZoneGroup         # groups Zones
```

## Key Predicates

| Predicate | Domain → Range | Purpose |
|-----------|---------------|---------|
| `s223:cnx` | Connectable ↔ ConnectionPoint ↔ Connection | **The one relation you assert** — everything else is inferred |
| `s223:contains` | Equipment/Zone → Equipment/DomainSpace | Composition hierarchy |
| `s223:hasMedium` | ConnectionPoint/Connection → Medium | What substance flows |
| `s223:hasProperty` | Concept → Property | General property association (telemetry, setpoints) |
| `s223:observes` | Sensor → ObservableProperty (exactly 1) | What a sensor reads |
| `s223:actuates` | Actuator → Equipment (0+) | What equipment an actuator controls |
| `s223:actuatedByProperty` | Actuator → ActuatableProperty (1+); Equipment → ActuatableProperty (0+) | Command point association. Actuators require ≥1. Equipment uses it optionally. |
| `s223:hasInput` | Function → Property (0+) | Control logic input. Function must have ≥1 hasInput or hasOutput. |
| `s223:hasOutput` | Function → Property (0+) | Control logic output. A Property can be hasOutput of at most 1 Function. |
| `s223:mapsTo` | ConnectionPoint → ConnectionPoint | Maps outer port to inner port (containment) |
| `s223:hasDomain` | DomainSpace/Zone → Domain | Building service domain |
| `s223:encloses` | PhysicalSpace → DomainSpace | Space-to-domain mapping |
| `s223:hasRole` | ConnectionPoint → Role | Functional role (cooling, heating, supply, return) |
| `s223:hasAspect` | Property → Aspect | Contextual qualifier (delta, setpoint) |

### Inferred Predicates (never assert these — they come from SHACL rules)
- `s223:connected`, `s223:connectedTo`, `s223:connectedFrom`
- `s223:connectedThrough`
- `s223:hasConnectionPoint`, `s223:isConnectionPointOf`
- `s223:connectsAt`, `s223:connectsFrom`, `s223:connectsTo`

## Enumerations

### Medium (what flows through connections)
| Medium | Use |
|--------|-----|
| `s223:Fluid-Air` | Air ducts |
| `s223:Fluid-Water` | Pipes (chilled, hot, condenser water) |
| `s223:Fluid-Steam` | Steam pipes |
| `s223:Fluid-RefrigerantR410A` | Refrigerant lines |
| `s223:Electricity-AC` | AC power conductors |
| `s223:Electricity-DC` | DC power conductors |
| `s223:Signal-WiredEthernet` | Network cables |
| `s223:Medium-Mix` | Mixed media (use `composedOf` + `ofConstituent`) |

### Domain (building service categories)
`s223:Domain-HVAC`, `s223:Domain-Lighting`, `s223:Domain-Electrical`,
`s223:Domain-Fire`, `s223:Domain-Plumbing`, `s223:Domain-Refrigeration`

### Role (functional roles)
`s223:Role-Cooling`, `s223:Role-Heating`, `s223:Role-Supply`, `s223:Role-Return`,
`s223:Role-Discharge`, `s223:Role-HeatTransfer`, `s223:Role-Exhaust`, `s223:Role-Relief`

## Units and Quantities (via QUDT)

```turtle
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .

# Temperature
myProp qudt:hasQuantityKind qk:Temperature ;
       qudt:hasUnit unit:DEG_C .

# Flow rate
myProp qudt:hasQuantityKind qk:VolumeFlowRate ;
       qudt:hasUnit unit:L-PER-SEC .

# Power
myProp qudt:hasQuantityKind qk:Power ;
       qudt:hasUnit unit:KiloW .

# Percentage (damper position, valve command)
myProp qudt:hasQuantityKind qk:DimensionlessRatio ;
       qudt:hasUnit unit:PERCENT .

# Pressure
myProp qudt:hasQuantityKind qk:Pressure ;
       qudt:hasUnit unit:PA .

# Concentration (CO2 ppm)
myProp qudt:hasQuantityKind qk:MoleFraction ;
       qudt:hasUnit unit:PPM .
```

## Example: Minimal VAV Model

```turtle
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix qk:   <http://qudt.org/vocab/quantitykind/> .
@prefix ex:   <http://example.org/building#> .

# VAV terminal unit containing a damper
ex:VAV1 a s223:SingleDuctTerminal ;
    s223:cnx ex:VAV1-in, ex:VAV1-out ;
    s223:contains ex:VAV1-damper ;
    s223:hasProperty ex:zone-temp .

# Damper inside the VAV
ex:VAV1-damper a s223:Damper ;
    s223:cnx ex:damper-in, ex:damper-out ;
    s223:hasProperty ex:damper-cmd .

# Connection points
ex:VAV1-in a s223:InletConnectionPoint ;
    s223:hasMedium s223:Fluid-Air ;
    s223:mapsTo ex:damper-in .

ex:VAV1-out a s223:OutletConnectionPoint ;
    s223:hasMedium s223:Fluid-Air .

ex:damper-in a s223:InletConnectionPoint ;
    s223:hasMedium s223:Fluid-Air .

ex:damper-out a s223:OutletConnectionPoint ;
    s223:hasMedium s223:Fluid-Air .

# Supply duct to VAV
ex:supply-duct a s223:Connection, s223:Duct ;
    s223:hasMedium s223:Fluid-Air ;
    s223:cnx ex:VAV1-in .

# Properties (telemetry points)
ex:damper-cmd a s223:QuantifiableActuatableProperty ;
    qudt:hasQuantityKind qk:DimensionlessRatio ;
    qudt:hasUnit unit:PERCENT .

ex:zone-temp a s223:QuantifiableObservableProperty ;
    qudt:hasQuantityKind qk:Temperature ;
    qudt:hasUnit unit:DEG_C .

# Zone
ex:Zone1 a s223:Zone ;
    s223:hasDomain s223:Domain-HVAC ;
    s223:hasDomainSpace ex:Zone1-hvac .

ex:Zone1-hvac a s223:DomainSpace ;
    s223:hasDomain s223:Domain-HVAC .

ex:Room101 a s223:PhysicalSpace ;
    s223:encloses ex:Zone1-hvac .
```

## Common SPARQL Queries

### All equipment and their types
```sparql
SELECT ?equip ?type WHERE {
    ?equip a ?type .
    ?type rdfs:subClassOf* s223:Equipment .
    FILTER(?type != s223:Equipment)
}
```

### Connection topology (what connects to what)
```sparql
SELECT ?from ?connection ?to WHERE {
    ?from a ?from_type .
    ?from_type rdfs:subClassOf* s223:Equipment .
    ?from s223:cnx ?from_cp .
    ?from_cp a s223:OutletConnectionPoint .
    ?connection s223:cnx ?from_cp .
    ?connection a ?conn_type .
    ?conn_type rdfs:subClassOf* s223:Connection .
    ?connection s223:cnx ?to_cp .
    ?to_cp a s223:InletConnectionPoint .
    ?to s223:cnx ?to_cp .
    ?to a ?to_type .
    ?to_type rdfs:subClassOf* s223:Equipment .
}
```

### All sensors and what they observe
```sparql
SELECT ?sensor ?property ?unit ?quantity WHERE {
    ?sensor a/rdfs:subClassOf* s223:Sensor .
    ?sensor s223:observes ?property .
    OPTIONAL { ?property qudt:hasUnit ?unit }
    OPTIONAL { ?property qudt:hasQuantityKind ?quantity }
}
```

### Equipment containment hierarchy
```sparql
SELECT ?parent ?child WHERE {
    ?parent s223:contains ?child .
    ?parent a/rdfs:subClassOf* s223:Equipment .
    ?child a/rdfs:subClassOf* s223:Equipment .
}
```

### Medium flow paths
```sparql
SELECT ?connection ?medium WHERE {
    ?connection a/rdfs:subClassOf* s223:Connection .
    ?connection s223:hasMedium ?medium .
}
```

### Zones and their domain spaces
```sparql
SELECT ?zone ?domain ?space ?physical WHERE {
    ?zone a s223:Zone .
    ?zone s223:hasDomain ?domain .
    ?zone s223:hasDomainSpace ?space .
    OPTIONAL { ?physical s223:encloses ?space }
}
```

## Dual-Typing: Brick + 223P Together

Entities can carry both Brick and 223P types for maximum interoperability:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix s223:  <http://data.ashrae.org/standard223#> .

ex:VAV1 a s223:SingleDuctTerminal, brick:VAV ;
    s223:cnx ex:VAV1-in, ex:VAV1-out ;
    brick:feeds ex:Zone1 ;
    brick:hasPoint ex:zone-temp-sensor .

ex:zone-temp-sensor a brick:Zone_Air_Temperature_Sensor ;
    s223:observes ex:zone-temp-prop .
```

## Resources

| Resource | URL |
|----------|-----|
| Documentation | https://docs.open223.info/ |
| Ontology TTL | https://open223.info/223p.ttl |
| Class explorer | https://explore.open223.info/ |
| SPARQL query tool | https://query.open223.info/ |
| Example models | https://models.open223.info/ |
