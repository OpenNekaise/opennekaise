---
name: ontology-spawn
description: Convert a folder of heterogeneous documents (PDFs, images, markdown, CSV, TTL, spreadsheets, anything) into a KebGraph semantic model (.ttl). Point it at a folder, it reads everything, extracts building knowledge, and writes a Turtle RDF file. Use when the user wants to create a knowledge graph from raw building documents.
---

# Ontology Spawn

Turn a folder of raw documents into a KebGraph semantic model.

## How it works

1. User gives you a folder path
2. You read every file in it — PDFs, images, markdown, CSV, TTL, text, whatever is there
3. You extract building knowledge: systems, sensors, equipment, spaces, control logic, alarms, setpoints
4. You write a KebGraph TTL file in the same folder

The LLM (you) is the parser. No format-specific tooling needed — just read and understand.

## Step 1: Discover

Glob the folder for all files. Read them all. For large folders, prioritize:
- PDFs first — control cards (driftkort), operating manuals, commissioning docs are the richest source
- Images — P&ID flow diagrams, distribution schematics, floor plans
- Existing TTL/RDF files — prior models to extend or incorporate
- CSV/spreadsheet data — sensor lists, equipment registers, BMS point exports
- Markdown and text files — any supporting documentation

Use the Read tool for everything — it handles PDFs, images, and text natively.

For very large PDFs (>10 pages), read in chunks using the `pages` parameter.

## Step 2: Understand the document types

### Control cards (Driftkort)

Control cards are the single most valuable document type for building graphs. They are typically PDFs organized per system, each containing multiple pages:

**Page 1: P&ID flow diagram** — a schematic showing every sensor and actuator in position, with color-coded flows (supply air, exhaust air, hot water, cold water). Read these images carefully — they show which sensors belong to which duct/pipe branch and how the system is connected.

**Page 2+: Text pages** with structured sections:

- **General** (Allmänt) — equipment cabinet ID, system name, location served, investment area
- **Control** (Styrning/Reglering) — how the system is controlled: which sensor drives which valve/damper, setpoint shift logic, outdoor compensation curves
- **Startup sequence** — what happens when the unit starts (damper opens, fan delay, valve preheating)
- **Shutdown/failure** — what closes or stops on power failure or unit stop
- **Interlocks** (Förregling) — fan cross-interlocks, pump-fan dependencies
- **Fire protection** (Brand) — smoke detector responses per zone, which dampers close, override logic, alarm hierarchy
- **Freeze protection** (Frysskydd) — guard sensor threshold, what happens when triggered, manual reset requirements
- **Defrost function** (Avfrostning) — differential pressure triggers, bypass behavior, exhaust temp limits
- **Alarm table** (Larm) — every alarm object with type, priority (A/B), and communication channel
- **Measurement table** (Mätningar) — every sensor/meter with type description, unit, and communication protocol
- **Setting values** (Börvärden) — setpoint tables with specific numeric values
- **Control curves** — outdoor temp vs supply temp breakpoint tables (typically 9 breakpoints)

### Distribution diagrams

For systems serving multiple areas (staircases, zones), separate diagrams show damper and smoke detector placement per zone. These map spatial structure to system topology.

### BMS point lists

CSV or spreadsheet exports from the building management system. Each row = one data point. Usually contain: point name, description, unit, protocol address.

### Other documents

Floor plans, energy declarations, commissioning reports, maintenance logs, tenant handbooks — all contain useful context for Captions even if they don't define new Actors.

## Step 3: Extract

Build the graph from what you found. Think in systems, not pages.

### Building (top-level Set)
One Set for the whole building. Caption includes: name, address, building type, year built, certifications, total area, number of floors, key systems present.

### Systems as Sets
Each control card typically describes one system. Each system becomes a Set connected to the building via `keb:cnx`. Common systems:

- **Ventilation units** (LB04, LB05, LB07, LB10, LB11...) — each AHU is a Set
- **Heating system** (VS01, VS02...) — radiator circuits, district heating connection
- **Cooling system** (KB01...) — chilled water, cooling baffles
- **Domestic hot water** (VV, VVC...) — DHW production and circulation
- **Garage ventilation** — exhaust fans with CO/CO2 control
- **Alarm & control** (AS201...) — central system for lighting, metering, elevator alarms

### Subsystem Sets
When a system has clear internal branches, create child Sets:
- **Inlet air duct** / **Exhaust air duct** / **Supply air duct** / **Outlet air duct** — for AHU branches
- **Distribution zones** — when dampers serve specific staircases or floors
- **Heat exchanger** (VVX) — often dual-type (Set + Actor) since it groups sub-sensors and generates efficiency data

### Actors from measurement tables
Every row in a measurement table becomes an Actor:
- Temperature sensors (GT11, GT41, GT42, GT43, GT44, GT81...)
- Pressure sensors (GP11, GP12, GP41, GP61, GP62...)
- Flow sensors (GF41, GF42...)
- Smoke detectors (GX71, GX72, GX73, GX74...)
- Dampers (ST21, ST22, ST31, ST71, ST72, ST73...)
- Fans (TF01, FF01...)
- Control valves (SV21...)
- Pumps (P1...)
- Electricity meters (EL, via EcoG protocol)
- Lux sensors, occupancy sensors

### Actors from alarm tables
Alarms themselves are not separate Actors — they describe fault conditions on existing Actors. Include alarm type and priority in the Actor's Caption.

### What goes into Captions — this is where the real value is

**Actor Captions** should include:
- What it measures/controls and its unit
- Setpoint value (from setting values table)
- Alarm conditions and priorities
- Communication protocol (DUC, EcoG, FO01, HD1-5)
- Control error thresholds (e.g., "alarm if ±4°C for >30min")
- Database ID or BMS address if known

**System Set Captions** should include:
- Equipment cabinet ID (AS201, AS202...)
- Serving area (which addresses/staircases)
- Full startup sequence
- Full control strategy (which sensor controls which valve/damper)
- Setpoint shift logic (outdoor compensation with breakpoint table)
- Heating sequence (damper opens for heat recovery → valve opens for heat → reverse when demand drops)
- Interlock logic
- Fire protection sequence (per smoke detector zone: what closes, what overrides what)
- Freeze protection threshold and behavior
- Defrost trigger conditions

**This is the most important part of the skill.** Control cards contain operational intelligence that no other document has. Every control sequence, every interlock, every fire response — capture it in Captions. An LLM reading these Captions later should understand how the system behaves without needing the original PDF.

### Shared sensors
Some sensors appear on every system card (e.g., outdoor temperature sensor UTE-GT31). Create this Actor once and attach it to the building-level Set, not to individual systems. Reference it in system Captions by name.

### Electricity meters and sub-meters
Buildings often have hierarchical metering: total → property → apartments → garage → EV charging → heat pump, etc. Each meter is an Actor. Group them in a metering Set. Note the hierarchy in Captions.

## Step 4: Build the namespace

Derive the building namespace from the building name:

```
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/{BuildingName}#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

Use a short, ASCII-safe building prefix (e.g., `rio10`, `ct42`, `vv17c`).

## Step 5: Write the TTL

Write the file directly using the Write tool. KebGraph TTL is simple enough to write by hand.

Output file: `{folder}/{building_name}.ttl`

### TTL structure

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/BuildingName#> .
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Building (top-level Set)
bldg:BuildingName a keb:Set ;
    keb:cnx bldg:LB04,
        bldg:VS01,
        bldg:KB01,
        bldg:AlarmControl ;
    keb:hasCaption """Building name and address.
Built: year. Rebuilt: year. Type: residential/office.
Certification: if any. Area: X m2. Floors: N.
Systems: ventilation (LB04, LB05...), heating (VS01),
cooling (KB01), domestic hot water (VV01).
Shared outdoor temp sensor: UTE-GT31."""^^xsd:string .

# Ventilation unit (Set) — one per AHU
bldg:LB04 a keb:Set ;
    keb:cnx bldg:LB04_InletDuct,
        bldg:LB04_ExhaustDuct,
        bldg:LB04_VVX ;
    keb:hasActor bldg:LB04_TF01,
        bldg:LB04_FF01,
        bldg:LB04_SV21,
        bldg:LB04_P1 ;
    keb:hasCaption """LB04 ventilation unit. Cabinet: AS202.
Location: fan room. Serving: [address].
Control: GT11 controls SV21 and ST31 in sequence.
Setpoint shift via UTE-GT31 with 9-breakpoint curve.
Heating sequence: ST31 opens for heat recovery →
SV21 opens for heat. Reverse when demand drops.
Startup: ST22 opens → FF01 starts after delay →
SV21 opens max to preheat (at <+5°C outdoor) →
ST21 opens → TF01 starts after delay → SV21 to regulated.
Interlocks: TF01/FF01 cross-interlocked. P1 interlocks TF01 in winter.
On stop/power failure: ST21 closes on spring.
Freeze protection: GT81 takes over SV21 control,
stops unit if battery temp falls below threshold.
Defrost: GP41 pressure triggers ST31 bypass for ~10 min.
Fire (GX71): unit stops, outdoor damper closes.
Fire (GX72): bypass ST71 opens, unit speeds up.
GX72 overrides GX71."""^^xsd:string .

# Inlet air duct subsystem
bldg:LB04_InletDuct a keb:Set ;
    keb:hasActor bldg:LB04_GT41,
        bldg:LB04_GP61,
        bldg:LB04_ST21 ;
    keb:hasCaption """Inlet air duct. Flow: outdoor →
GT41 (temp) → filter (GP61 guard) → ST21 (damper) →
TF01 (supply fan) → VVX heat exchanger."""^^xsd:string .

# Actor examples
bldg:LB04_GT11 a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption """Supply air temperature sensor.
Unit: °C. Via: DUC. Setpoint: per control curve.
Alarm: control error (±4°C for >30min), priority B."""^^xsd:string .

bldg:LB04_GT81 a keb:Actor,
        brick:Temperature_Sensor ;
    keb:hasCaption """Freeze guard sensor on heating battery.
Unit: °C. Via: DUC. Threshold: 7°C.
Takes over SV21 control on freeze risk.
Stops unit if temp falls below threshold."""^^xsd:string .

bldg:LB04_GX71 a keb:Actor,
        brick:Smoke_Detector ;
    keb:hasCaption """Supply air duct smoke detector.
Fire: stops unit, closes outdoor damper.
Service alarm priority B. Fire alarm priority A.
Via: HD1."""^^xsd:string .

# VVX as dual-type (Set + Actor)
bldg:LB04_VVX a keb:Set,
        keb:Actor,
        brick:Heat_Exchanger ;
    keb:hasActor bldg:LB04_GT42 ;
    keb:hasCaption """Plate heat exchanger for heat recovery.
Efficiency measurement via DUC.
Low efficiency alarm, priority B.
ST31 bypass damper controls heat recovery."""^^xsd:string .
```

### KebGraph rules

- **4 edge types only**: `rdf:type`, `keb:cnx` (Set→Set), `keb:hasActor` (Set→Actor), `keb:hasCaption` (any→Literal)
- **No Actor-to-Actor edges.** Actors are always grouped through Sets.
- **Actors must be real data points** — things listed in measurement or alarm tables. Not passive equipment.
- **Captions carry the operational intelligence** — control sequences, interlocks, fire logic, setpoints, alarm thresholds. This is the most valuable part of the graph.
- **Sets provide hierarchy** — Building → System → Subsystem, or Building → Floor → Room.
- **Dual-type entities** are allowed — VVX heat exchangers are commonly both Set and Actor.

### Common Brick types

| What you find | Brick class |
|---|---|
| Temperature sensor (GT) | `brick:Temperature_Sensor` |
| Humidity sensor (GH) | `brick:Humidity_Sensor` |
| CO2 sensor (GQ) | `brick:CO2_Sensor` |
| CO sensor (GQ, in garages) | `brick:CO2_Sensor` |
| Pressure sensor (GP) | `brick:Pressure_Sensor` |
| Flow sensor (GF) | `brick:Flow_Sensor` |
| Lux sensor (GX31) | `brick:Luminance_Sensor` |
| Electricity meter | `brick:Electrical_Meter` |
| Thermal power meter | `brick:Thermal_Power_Sensor` |
| Control valve (SV) | `brick:Control_Valve` |
| General valve | `brick:Valve` |
| Air damper (ST) | `brick:Damper` |
| Fire damper (DK, brandspjäll) | `brick:Damper` |
| Supply fan (TF) | `brick:Fan` |
| Exhaust fan (FF) | `brick:Exhaust_Fan` |
| Heat exchanger (VVX) | `brick:Heat_Exchanger` |
| Smoke detector (GX7x) | `brick:Smoke_Detector` |
| Pump (P) | `brick:Pump` |
| Radiator (if monitored) | `brick:Radiator` |

### Communication protocols in Captions

| Code | Meaning |
|---|---|
| DUC | Direct Digital Control (DDC) — BMS native |
| EcoG | Energy metering protocol (electricity sub-meters) |
| FO01 | Frequency converter fault relay |
| HD1-HD5 | Hardwired digital inputs (fire, smoke) |

## Step 6: Summarize

After writing the TTL, tell the user:
- How many Sets and Actors were created
- Which systems were modeled (list system IDs)
- What control strategies were captured in Captions
- What was ambiguous or missing (e.g., "measurement tables had no database IDs — using placeholder xxx")
- What additional documents would improve the model (e.g., "BMS point export would add real database IDs")

## Reading P&ID diagrams

P&ID flow diagrams in control cards use color-coded lines and standardized symbols:

- **Trace the flow path** — follow arrows and color bands to identify inlet, supply, exhaust, outlet branches
- **Identify every labeled component** — each label (GT41, ST21, SV21, etc.) on the diagram is a potential Actor
- **Note component positions** — which sensor is before/after the heat exchanger, which damper is on which branch
- **Look for branch points** — where ducts split to serve different zones (staircases, floors, rooms)
- **Fire/safety components** — smoke detectors (triangle symbols), fire dampers (DK), often at zone boundaries
- **Identify shared sensors** — outdoor temperature sensor (UTE-GT31) typically shown at the top of every diagram

Use the flow topology to structure your Sets (duct branches) and to write accurate flow-direction Captions.

## Swedish HVAC naming conventions

| Code | Swedish | Meaning | Creates |
|---|---|---|---|
| GT | Givare Temperatur | Temperature sensor | Actor |
| GP | Givare Tryck | Pressure sensor | Actor |
| GQ | Givare Kvalitet | CO2/air quality sensor | Actor |
| GH | Givare Hygrometer | Humidity sensor | Actor |
| GF | Givare Flöde | Flow sensor | Actor |
| GX | Givare övrigt | Other sensor (smoke, lux) | Actor |
| SV | Styrventil | Control valve | Actor |
| ST | Ställdon/Spjäll | Damper actuator | Actor |
| TF | Tilluftsfläkt | Supply fan | Actor |
| FF | Frånluftsfläkt | Exhaust fan | Actor |
| VVX | Värmeväxlare | Heat exchanger | Set + Actor |
| P | Pump | Circulation pump | Actor |
| DK | Brandspjäll | Fire damper | Actor |
| LB | Luftbehandling | Air handling unit | Set |
| VS | Värmesystem | Heating system | Set |
| KB | Kylbatteri/system | Cooling system | Set |
| VV/VVC | Varmvatten/cirkulation | DHW system | Set |
| UTE | Utomhus | Outdoor (shared sensor) | Actor |
| AS | Apparatskåp | Equipment cabinet | metadata in Caption |

Number suffixes: GT**11** = first temp sensor in subsystem 1, GT**41** = temp sensor in subsystem 4, GP**61** = pressure in subsystem 6.
System prefixes: **LB04**-GT11 = GT11 belonging to ventilation unit LB04.

## Tips

- **Control cards are the priority** — one control card PDF can contain more graph-worthy information than 10 other documents combined.
- **Capture control logic verbatim in Captions** — startup sequences, heating/cooling cascades, fire overrides, interlock dependencies. These are the operational brain of the building.
- **Control curves (breakpoint tables)** are extremely valuable — include them in system Captions. They define how the building responds to weather.
- **Alarm priorities matter** — Priority A = critical (fire, safety). Priority B = service/maintenance. Include both priority and type in Actor Captions.
- **One building, many systems** — a residential complex might have 8+ ventilation units, each with its own control card. Model each as a separate Set.
- **Shared sensors** — outdoor temperature (UTE-GT31) appears on every ventilation card. Create it once at building level.
- **When information conflicts** between documents, note the conflict in the relevant Caption.
- **Database IDs**: if BMS point exports include database identifiers, BACnet addresses, or Modbus registers, always include them in Actor Captions. These are the ground-truth data anchors.
- **Don't skip the small details** — freeze protection thresholds, filter guard pressures, defrost triggers. These are exactly what an engineer needs when debugging a system at 2 AM.
