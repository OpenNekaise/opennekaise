# ASHRAE 223P / Open223 Reference

_Last public-source check used for this reference: 2026-03-26._

This file is the deep reference for the `know-223p` skill. It is written for agents that need to explain 223P, author or review Turtle/RDF, map building systems into the ontology, attach telemetry context, or debug inference and validation.

## Table of contents

1. [What 223P is](#1-what-223p-is)
2. [Mental model: the five lenses](#2-mental-model-the-five-lenses)
3. [The semantic-web stack behind 223P](#3-the-semantic-web-stack-behind-223p)
4. [Core ontology structure](#4-core-ontology-structure)
5. [Topology and connectivity patterns](#5-topology-and-connectivity-patterns)
6. [Properties, sensors, telemetry, and functions](#6-properties-sensors-telemetry-and-functions)
7. [Media, constituents, and mixtures](#7-media-constituents-and-mixtures)
8. [Inference and validation](#8-inference-and-validation)
9. [QUDT, Brick, and RealEstateCore interop](#9-qudt-brick-and-realestatecore-interop)
10. [A practical modeling workflow for agents](#10-a-practical-modeling-workflow-for-agents)
11. [Minimal Turtle patterns](#11-minimal-turtle-patterns)
12. [Common mistakes and how to avoid them](#12-common-mistakes-and-how-to-avoid-them)
13. [Canonical public resources](#13-canonical-public-resources)
14. [Source-priority rules for answering users](#14-source-priority-rules-for-answering-users)

## 1. What 223P is

ASHRAE 223P is a proposed semantic data model for analytics and automation applications in buildings. Its public purpose and scope center on creating formal, machine-readable, interoperable semantic frameworks for building automation and control data and other building-system information, in support of applications such as fault detection and diagnostics, commissioning, digital twins, real-time optimization, and smart-grid interactions.

For an agent, the most important framing is this:

- 223P is not just a tag list.
- 223P is an ontology plus rules.
- It models *things*, *connections*, *spaces*, *properties*, and *how those properties are measured or acted on*.
- It is designed to be used as graph data in RDF, then validated and extended through SHACL-based rules.

### Status caveat

Public sources do not present a perfectly single status message:

- the public user docs still describe 223P as proposed and say the standard is not yet available for public review;
- the Open223 portal lists advisory public review resources;
- a NIST project page updated in 2026 says the team is waiting for committee action on a second public review.

Therefore, the safe stance is: **treat 223P as an evolving proposed standard and the Open223 ecosystem as the best public implementation aid, not as the final published normative ASHRAE text.**

## 2. Mental model: the five lenses

The public 223 overview is easiest to remember as five lenses.

### 2.1 Type

Type answers: **what kind of thing is this?**

Examples:

- `s223:Fan`
- `s223:Damper`
- `s223:PhysicalSpace`
- `s223:Zone`
- `s223:QuantifiableObservableProperty`

### 2.2 Topology

Topology answers: **how are things connected, and what flows between them?**

223P does not focus on detailed geometry. It focuses on graph topology:

- which things can connect
- through which connection points
- using which connections
- carrying which media

### 2.3 Composition

Composition answers: **what contains what, encloses what, or groups what?**

Examples:

- equipment containing sub-equipment
- a floor containing rooms
- a physical space enclosing a domain space
- a zone grouping domain spaces
- a system grouping interrelated equipment

### 2.4 Telemetry

Telemetry answers: **what can be measured or commanded, and where does the live value come from?**

223P does not embed time-series history. Instead, it models the meaning and context of properties and can link a property to an external telemetry source such as BACnet.

### 2.5 Characteristics

Characteristics answer: **what non-topological attributes matter?**

Examples:

- rated flow of a pump
- temperature of supply air
- commanded position of a damper
- enumeration-valued state such as on/off or alarm status

## 3. The semantic-web stack behind 223P

Any agent working seriously with 223P should assume the following stack.

### 3.1 RDF

223P models are RDF graphs: subject-predicate-object triples. This is the core representation.

### 3.2 Turtle

Most public 223 examples use Turtle (`.ttl`). When authoring examples, use Turtle unless the user explicitly asks for another serialization.

### 3.3 SHACL and SHACL-AF

223P uses SHACL in two different ways:

- **validation** to check whether a model conforms to the ontology rules
- **inference** to add implied triples using SHACL rules and SHACL Advanced Features

### 3.4 SPARQL

SPARQL is the main query language for RDF and therefore the main public query language for 223P models.

### 3.5 QUDT

QUDT provides units and quantity kinds. In practice, 223P relies on QUDT to say what a quantifiable property measures and in what unit.

## 4. Core ontology structure

### 4.1 Graph-level basics

A 223 model is a directed labeled graph. Public documentation distinguishes:

- **entity**: a modeled thing in the building
- **class**: the category that entity instantiates
- **relation**: the RDF predicate connecting entities
- **model**: the full RDF graph using 223 constructs

### 4.2 The major top-level modeling constructs

These are the concepts an agent should recognize first.

#### Connectable

`Connectable` is the abstract supertype for things that can participate in building connectivity via connection points and connections.

Major connectable subclasses:

- `Equipment`
- `DomainSpace`
- `Junction`

#### Equipment

`Equipment` represents a device that performs a task.

Examples:

- pumps
- fans
- heat exchangers
- luminaires
- sensors
- actuators
- controllers

Equipment may contain other equipment. This lets you model a device either as a black box or as an assembly of parts.

#### DomainSpace

A `DomainSpace` is the portion or entirety of a `PhysicalSpace` associated with a domain such as HVAC, lighting, or security.

Important nuances:

- a domain space may represent an entire room or just part of it;
- multiple domain spaces may overlap;
- domain spaces of different domains may overlap;
- a domain space should not span multiple physical spaces.

This is one of the most important distinctions in 223P. Do not confuse architectural rooms with served or controlled regions.

#### Junction

A `Junction` represents an important branch or intersection within a connection. Use it when the branch itself matters semantically, not just geometrically.

#### ConnectionPoint

A `ConnectionPoint` is the abstract place where a connectable thing can connect to something else. Think flange, wire terminal, or another physical attachment feature.

Important rules:

- a connection point belongs to exactly one connectable;
- it is constrained to a medium;
- it is typed by flow direction.

Common subclasses:

- `InletConnectionPoint`
- `OutletConnectionPoint`
- `BidirectionalConnectionPoint`

#### Connection

A `Connection` is the thing that conveys a medium between connectables.

Examples:

- `Pipe`
- `Duct`
- `Conductor`
- `Waveguide`

A connection can have two or more connection points and may include branches. If the branch identity matters, introduce a `Junction`.

#### PhysicalSpace

A `PhysicalSpace` is an architectural or physical room, floor, corridor, etc. A physical space may contain other physical spaces and may enclose domain spaces.

#### Zone

A `Zone` is a logical grouping of one or more domain spaces, or even other zones, for service or control purposes.

#### System

A `System` is a modeler-defined task-oriented collection of interrelated equipment.

#### Property

`Property` is one of the central constructs in 223P.

A property may represent:

- something observed
- something actuated or commanded
- a characteristic of equipment, a space, a zone, or another concept
- a derived value produced by a function

#### EnumerationKind

Enumerations are closed sets of named values. They are heavily used in 223P for roles, states, media, domains, aspects, and other contextual vocabularies.

#### Function / FunctionBlock

Public sources use both the higher-level idea of a **FunctionBlock** and concrete examples with `s223:Function`.

Treat the safe semantic meaning as: **a modeling construct for transformation or transfer of information, especially control logic or derived values.**

Do not treat this as executable code inside the ontology. The algorithmic details are outside normal 223 modeling scope.

## 5. Topology and connectivity patterns

This is where many models fail.

### 5.1 The key insight: `s223:cnx` is the backbone

Public 223 guidance says that many connection-related relations can be inferred, and that only `s223:cnx` generally needs to be authored manually for connectivity.

As an authoring rule:

- prefer asserting `s223:cnx`
- let inference derive other views of the connection graph where appropriate

### 5.2 What a valid topology usually contains

For a real flow path, you usually need:

1. a `Connectable` such as equipment or a domain space
2. one or more `ConnectionPoint`s on that connectable
3. a `Connection` carrying a compatible medium
4. `s223:cnx` links tying them together

### 5.3 Direction matters

Choose the correct connection point type:

- `InletConnectionPoint` if flow is into the connectable
- `OutletConnectionPoint` if flow is out of the connectable
- `BidirectionalConnectionPoint` if either direction is expected

### 5.4 Medium compatibility matters

Connection points and connections are constrained by medium. If the medium is air, the point cannot be used for an electrical connection.

A large class of validation errors comes from forgetting to declare or align media.

### 5.5 `mapsTo` is for containment boundaries

When a contained piece of equipment has its own inner connection points and the containing equipment exposes outer connection points, `s223:mapsTo` is used to relate the inner and outer points.

This is essential for modeling assemblies cleanly.

### 5.6 `pairedConnectionPoint`

Use `pairedConnectionPoint` when the ontology expects a corresponding inlet/outlet or bidirectional pairing relationship.

### 5.7 Optional and boundary connection points

Two relations help avoid false validation failures for intentionally dangling points:

- `s223:hasOptionalConnectionPoint`
- `s223:hasBoundaryConnectionPoint`

Use these only when the point is intentionally unconnected in the current modeling context.

### 5.8 When to introduce a `Junction`

If you only need to say that one connection branches to multiple consumers, multiple connection points on the same connection may be sufficient.

If you need to reason about the branch point itself, meter a particular branch, or preserve a named intersection, add a `Junction` and split the connection into multiple connections around it.

## 6. Properties, sensors, telemetry, and functions

### 6.1 The 223 view of a property

In 223P, properties are not modeled as abstract phenomena floating independently of devices. Public docs explicitly distinguish 223 from ontologies like SSN/SOSA here.

Treat a 223 property as the source and context of a value that is observed, actuated, or otherwise meaningful to a building application.

### 6.2 `hasProperty`

Use `s223:hasProperty` to associate a `Property` with a `Concept`. This is the generic relation that ties properties onto equipment, connection points, spaces, zones, and related concepts.

### 6.3 Quantifiable versus enumerable

A property may be:

- **quantifiable**: numerical value with quantity kind and unit
- **enumerable**: value drawn from an enumeration kind

### 6.4 Observable versus actuatable

A property may be:

- **observable**: produced by a sensor
- **actuatable**: driven by an actuator or command source

A quantifiable observable temperature point and an enumerable on/off command are both natural 223 patterns.

### 6.5 Sensor rule: one sensor, one observable property

Public guidance says a `Sensor` observes a single `ObservableProperty`.

That means a multi-capability device is modeled as `Equipment` containing multiple sensor instances. Do **not** model one generic sensor instance as observing temperature, humidity, CO2, and occupancy all at once unless your chosen ontology version explicitly allows that pattern.

### 6.6 Sensor platform pattern

If a physical enclosure senses multiple things, model the enclosure as equipment and put distinct sensors inside it with `contains`.

This is one of the most useful 223 patterns for real hardware.

### 6.7 Derived properties

If a value is computed rather than directly sensed, do not pretend it is an observable property from a sensor.

Instead:

- create a `Function` or function-block construct
- attach one or more `hasInput` properties
- attach one or more `hasOutput` properties
- model the output as a quantifiable or enumerable property as appropriate

This is the correct way to represent control logic and derived signals.

### 6.8 External telemetry references

223P can link a property to an external data source using `s223:hasExternalReference`.

A key public example is `BACnetExternalReference`, which carries BACnet identifiers needed to locate the corresponding live value.

Use this when the goal is semantic context plus a pointer to the operational system.

### 6.9 `hasValue` is not live telemetry

Public defs indicate that `hasValue` is for a static value carried in the model itself. It is not meant to hold live operational telemetry.

Therefore:

- use `hasValue` only for a static modeled value when needed
- use external references for live telemetry
- avoid mixing internal/static and live-reference semantics carelessly

### 6.10 Property context via aspects and media

Properties can be contextualized by:

- medium
- substance or constituent
- aspect
- role-like enumerations
- quantity kind
- unit

Example: a temperature property can be contextualized as a **supply** air temperature rather than just “temperature”.

## 7. Media, constituents, and mixtures

223P uses enumeration hierarchies to represent media.

### 7.1 Mediums

The standard models important building media such as:

- air
- water
- electricity
- light
- signal-like media

### 7.2 Pure media versus mixtures

Public docs distinguish pure media, mixtures, and constituents.

Example mental model:

- `Air` and `Water` are media
- a water-glycol solution is a mixture
- the mixture is described through constituents and composition properties

### 7.3 Why mixture modeling matters

Mixture structure is not decorative. It supports compatibility validation among connection points, connections, and properties. Public guidance says mediums are compatible when they share at least one common constituent.

### 7.4 Agent rule

If the user models anything more specific than generic air/water/electricity, check whether:

- the medium should be a pure medium or a mixture
- the property should declare `ofMedium` or `ofSubstance`
- compatibility constraints will fire during validation

## 8. Inference and validation

### 8.1 Keep ontology and model separate

The public inference tutorial recommends loading the 223 ontology into a graph separate from the building model graph. This makes maintenance and versioning easier.

### 8.2 Load the ontology explicitly

The public tutorial loads the ontology from:

```text
https://query.open223.info/ontologies/223p.ttl
```

Use this as the default public ontology URL unless the user provides a pinned or review-specific variant.

### 8.3 What inference does

Inference adds implied triples so the model is easier to write and easier to query. One useful framing from the public docs is that inference acts like a normalization step for 223 models.

### 8.4 What validation does

Validation checks whether the graph obeys the ontology constraints:

- class expectations
- relation targets
- medium compatibility
- property requirements
- structural completeness

### 8.5 Original versus compiled models

Open223 example models are often available in two forms:

- **original**: only the authored triples
- **compiled**: the graph after SHACL rules have extended it with inferred triples

Always ask yourself whether a query or example depends on asserted or compiled form.

### 8.6 Agent rule

When reviewing or generating 223 data:

- say which triples must be authored
- say which triples are expected only after inference
- do not claim inferred relations are present unless inference has actually been run

## 9. QUDT, Brick, and RealEstateCore interop

### 9.1 QUDT

Use QUDT for units and quantity kinds.

For quantifiable properties, usually include:

- `qudt:hasQuantityKind`
- `qudt:hasUnit`

Public docs say 223P is compatible with QUDT 3.1.4 and expected to remain compatible with newer versions.

### 9.2 Brick

Brick can add a richer, faster-evolving vocabulary on top of 223.

Public guidance says:

- Brick `Point` classes can annotate 223 `Property` instances
- Brick `Equipment` classes can annotate 223 `Equipment`
- some useful relations such as `brick:hasPoint` can be inferred from the combined model

Agent rule: **use Brick for additional semantic labeling, not in place of 223 topology.**

### 9.3 RealEstateCore

REC space classes can annotate 223 `PhysicalSpace` instances to provide more descriptive human-facing space semantics.

### 9.4 Safe combined-model stance

A model can be “223-first” and still carry Brick and REC annotations. Public docs emphasize that using 223 neither requires nor eliminates the use of Brick or REC.

## 10. A practical modeling workflow for agents

When asked to create or review a 223 model, follow this order.

### Step 1: define the modeling boundary

Decide what is in scope:

- a device
- a subsystem
- a room or served zone
- a complete building fragment

### Step 2: identify domains and spaces

Separate:

- physical spaces
- domain spaces
- zones
- systems

### Step 3: list connectables

Enumerate all equipment, domain spaces, and any needed junctions.

### Step 4: add connection points and connections

For each flow path:

- create inlet/outlet/bidirectional connection points
- assign media
- create the conveying connection
- author the `cnx` structure
- add `mapsTo` where containment boundaries exist

### Step 5: add properties

For each measurable, commandable, or descriptive attribute:

- choose observable, actuatable, quantifiable, or enumerable form
- attach it with `hasProperty`
- add units, quantity kinds, aspects, medium, substance, etc. as needed

### Step 6: add sensing, actuation, and logic

- add sensors for observed properties
- add actuators/controllers for commanded behavior
- add functions for derived or computed values

### Step 7: attach external references

Link out to BACnet or another telemetry source when operational integration matters.

### Step 8: run inference and validation

Check both original and compiled views of the model.

### Step 9: test with competency questions

Run small SPARQL queries that reflect the intended use case.

## 11. Minimal Turtle patterns

These examples are intentionally small. They are patterns, not full production models.

### 11.1 Fan, duct, and damper topology

```ttl
@prefix ex: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .

ex:returnFan a s223:Fan ;
  s223:cnx ex:returnFanIn, ex:returnFanOut .

ex:returnFanIn a s223:InletConnectionPoint ;
  s223:hasMedium s223:Fluid-Air .

ex:returnFanOut a s223:OutletConnectionPoint ;
  s223:cnx ex:returnAirDuct ;
  s223:hasMedium s223:Fluid-Air .

ex:returnAirDuct a s223:Duct ;
  s223:cnx ex:damperIn ;
  s223:hasMedium s223:Fluid-Air .

ex:damperIn a s223:InletConnectionPoint ;
  s223:hasMedium s223:Fluid-Air .
```

### 11.2 Temperature property observed at an outlet point

```ttl
@prefix ex: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix qudtqk: <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .

ex:airTemp a s223:QuantifiableObservableProperty ;
  qudt:hasQuantityKind qudtqk:Temperature ;
  qudt:hasUnit unit:DEG_C ;
  s223:hasAspect s223:Role-Supply .

ex:damperOut a s223:OutletConnectionPoint ;
  s223:hasMedium s223:Fluid-Air ;
  s223:hasProperty ex:airTemp .

ex:tempSensor a s223:Sensor ;
  s223:hasPhysicalLocation ex:damper ;
  s223:hasObservationLocation ex:damperOut ;
  s223:observes ex:airTemp .
```

### 11.3 Derived property via function

```ttl
@prefix ex: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix qudtqk: <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .

ex:zoneEffectiveTemp a s223:QuantifiableProperty ;
  qudt:hasQuantityKind qudtqk:Temperature ;
  qudt:hasUnit unit:DEG_C .

ex:zoneTempLogic a s223:Function ;
  s223:hasInput ex:zoneTempRaw, ex:airFlow ;
  s223:hasOutput ex:zoneEffectiveTemp .
```

### 11.4 PhysicalSpace, DomainSpace, and Zone

```ttl
@prefix ex: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .

ex:room101 a s223:PhysicalSpace .

ex:room101Hvac a s223:DomainSpace ;
  s223:hasDomain s223:Domain-HVAC .

ex:room101 s223:encloses ex:room101Hvac .

ex:zoneA a s223:Zone ;
  s223:hasDomain s223:Domain-HVAC ;
  s223:hasDomainSpace ex:room101Hvac .
```

### 11.5 BACnet external reference pattern

```ttl
@prefix ex: <urn:ex/> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix bacnet: <http://data.ashrae.org/bacnet/2020#> .

ex:zoneTemp s223:hasExternalReference ex:zoneTempRef .

ex:zoneTempRef a s223:BACnetExternalReference ;
  bacnet:device-identifier "1234" ;
  bacnet:object-identifier "analog-input,7" ;
  bacnet:property-identifier "present-value" .
```

### 11.6 SPARQL reachability across a connection graph

```sparql
PREFIX ex: <urn:ex/>
PREFIX s223: <http://data.ashrae.org/standard223#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?x WHERE {
  ex:breaker s223:cnx* ?x .
  ?x a/rdfs:subClassOf* s223:Connectable .
}
```

This pattern is useful for finding all connectables reachable through a circuit or airflow path.

## 12. Common mistakes and how to avoid them

### Mistake 1: treating 223P as a time-series database

Avoid: placing live telemetry values directly into the graph as if 223 were historian storage.

Do instead: model the property and link to the telemetry source using an external reference.

### Mistake 2: skipping connection points

Avoid: directly drawing “fan connectedTo duct” without a connection-point structure when proper topology matters.

Do instead: model connection points and media.

### Mistake 3: using Brick as the topology layer

Avoid: replacing 223 connectivity with Brick tags alone.

Do instead: keep 223 for topology and add Brick as annotation.

### Mistake 4: confusing PhysicalSpace, DomainSpace, and Zone

Avoid: using one room node for architectural room, thermal service area, and control grouping all at once.

Do instead:

- `PhysicalSpace` for architectural containment
- `DomainSpace` for served/service-specific area
- `Zone` for logical grouping

### Mistake 5: one sensor for many unrelated observables

Avoid: a single generic sensor instance observing temperature, humidity, CO2, and occupancy.

Do instead: model a sensor platform as equipment containing multiple sensors.

### Mistake 6: forgetting QUDT on quantifiable properties

Avoid: a numeric property without quantity kind or unit.

Do instead: add `qudt:hasQuantityKind` and `qudt:hasUnit`.

### Mistake 7: pretending a derived value is directly observed

Avoid: tagging a computed property as `ObservableProperty` when no sensor generates it.

Do instead: model a function that produces the property.

### Mistake 8: misusing `hasValue`

Avoid: storing live telemetry in `hasValue`.

Do instead: reserve `hasValue` for static modeled values and use external references for operational data.

### Mistake 9: ignoring asserted-versus-inferred differences

Avoid: assuming every example query works on the original graph.

Do instead: say whether the graph must be compiled first.

### Mistake 10: overclaiming standard status

Avoid: stating that public Open223 docs are the final official ASHRAE standard.

Do instead: say they are public documentation and tooling around a proposed evolving standard.

## 13. Canonical public resources

Use these public resources in this order depending on the task.

### Exact semantics

- `https://defs.open223.info/`
  - best for class, relation, shape, and rule definitions

### Explanations, patterns, and tutorials

- `https://docs.open223.info/`
  - best for overview, tutorials, design patterns, sensors/properties, QUDT, Brick, REC

### Example models

- `https://models.open223.info/`
  - best for real example graphs and original/compiled variants

### Querying and ontology loading

- `https://query.open223.info/`
  - best for public ontology loading and SPARQL experimentation

### Open223 service index and public portal

- `https://open223.info/`
  - best for the portal view of docs, query, models, defs, and advisory review links

### Project background and status signals

- `https://www.nist.gov/programs-projects/semantic-interoperability-building-data`
- `https://www.energy.gov/eere/buildings/ashrae-standard-223p`

## 14. Source-priority rules for answering users

When helping a user, follow this priority.

1. **Need exact meaning of a class or relation?** Use `defs.open223.info`.
2. **Need modeling patterns or practical guidance?** Use `docs.open223.info`.
3. **Need real examples or queryable artifacts?** Use `models.open223.info` and `query.open223.info`.
4. **Need ecosystem overview or public-review pointers?** Use `open223.info`.
5. **Need project or status background?** Use NIST and DOE pages.

### Safe wording rules

- Say “proposed standard” or “223P” unless the user gives a newer final normative source.
- Say “public Open223 documentation/tooling” rather than “official ASHRAE standard text.”
- If a public source disagreement matters, state the disagreement instead of hiding it.
- If you are unsure whether a relation is asserted or inferred in an example, say so explicitly.

---

## Compact memory aid for agents

When you need the shortest possible summary, remember this sentence:

**223P models what building things are, how they connect, what spaces they affect, what properties they expose, and how those properties are observed, commanded, or derived, using RDF plus SHACL rules, QUDT units, and optional Brick/REC annotations.**
