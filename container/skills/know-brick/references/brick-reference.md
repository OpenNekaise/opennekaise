# Brick Reference

## Contents

1. What Brick is
2. Core concepts
3. Relationship decision table
4. A practical modeling workflow
5. Minimal modeling patterns
6. SPARQL snippets
7. Common pitfalls
8. Modeling checklist

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

## Relationship decision table

| If the meaning is... | Prefer | Inverse | Example |
| --- | --- | --- | --- |
| telemetry or command belongs to equipment or a space | `brick:hasPoint` | `brick:isPointOf` | VAV hasPoint damper position command |
| physical placement | `brick:hasLocation` | `brick:isLocationOf` | thermostat hasLocation room |
| composition or containment that defines the subject | `brick:hasPart` | `brick:isPartOf` | AHU hasPart supply fan |
| distribution or downstream flow | `brick:feeds` | `brick:isFedBy` | AHU feeds VAV |

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

SELECT ?equip ?equipType ?point ?pointType WHERE {
  ?equip brick:hasPoint ?point .
  ?equip rdf:type ?equipType .
  ?point rdf:type ?pointType .
  FILTER(STRSTARTS(STR(?equipType), STR(brick:)))
  FILTER(STRSTARTS(STR(?pointType), STR(brick:)))
}
ORDER BY ?equip ?point
```

### Physical locations

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?entity ?location WHERE {
  ?entity brick:hasLocation ?location .
}
ORDER BY ?entity
```

### Downstream feeds graph

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?upstream ?downstream WHERE {
  ?upstream brick:feeds ?downstream .
}
ORDER BY ?upstream ?downstream
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

