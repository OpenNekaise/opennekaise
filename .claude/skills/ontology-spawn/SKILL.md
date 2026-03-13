---
name: ontology-spawn
description: Convert a folder of heterogeneous documents (PDFs, images, markdown, CSV, TTL, spreadsheets, anything) into a KebGraph semantic model (.ttl). Point it at a folder, it reads everything, extracts building knowledge, and writes a Turtle RDF file. Use when the user wants to create a knowledge graph from raw building documents.
---

# Ontology Spawn

Turn a folder of raw documents into a KebGraph semantic model.

## The principle

**After you write the graph, the original documents should never need to be opened again.**

The graph is not a summary or an index. It IS the building's knowledge. An AI agent working with this graph will have no access to the original PDFs, images, or spreadsheets. Everything the agent could ever need — every setpoint, every control sequence, every alarm threshold, every breakpoint in a control curve, every fire protection override — must live in the graph.

If you leave something out, it's gone. If you summarize instead of transcribing, the detail is lost. When in doubt, include it. A Caption that's too long is better than a Caption that's too short.

## How it works

1. User gives you a folder path
2. You read every file in it — PDFs, images, markdown, CSV, TTL, text, whatever is there
3. You extract ALL building knowledge into Sets, Actors, and Captions
4. You write a KebGraph TTL file in the same folder
5. The original documents become disposable — the graph is now the source of truth

The LLM (you) is the parser. No format-specific tooling needed — just read and understand.

## Step 1: Discover and read EVERYTHING

Glob the folder for all files. Read them all — completely. Don't skim.

- PDFs — control cards (driftkort), operating manuals, commissioning docs. Read every page.
- Images — P&ID flow diagrams, distribution schematics, floor plans. Study every label.
- Existing TTL/RDF files — prior models to extend or incorporate
- CSV/spreadsheet data — sensor lists, equipment registers, BMS point exports. Every row matters.
- Markdown and text files — any supporting documentation

Use the Read tool for everything — it handles PDFs, images, and text natively.

For very large PDFs (>10 pages), read in chunks using the `pages` parameter. Do not skip pages.

## Step 2: Understand what you're reading

### Control cards (Driftkort) — the most valuable source

Control cards are PDFs organized per system, each containing:

**Page 1: P&ID flow diagram** — schematic showing every sensor and actuator in position, with color-coded flows. Read these images carefully — trace every component label, note positions relative to heat exchangers/filters/fans, identify branch points.

**Text pages** with structured sections — extract ALL of the following:

- **General** — equipment cabinet ID, system name, location served. Capture exactly.
- **Control strategy** — which sensor drives which valve/damper, the full control chain. Capture the exact sequence.
- **Setpoint shift** — outdoor compensation curves. Capture ALL breakpoints (typically 9 outdoor temp values mapped to 9 supply temp values). Write the complete table in the Caption.
- **Heating/cooling sequence** — the cascade order. Which opens first, which opens next, and the reverse. Capture step by step.
- **Startup sequence** — every step from off to running. Which damper opens first, delay before fan, preheat conditions, outdoor temp threshold for preheat.
- **Shutdown/failure behavior** — what closes, what position things go to on power loss, spring-return behavior.
- **Interlocks** — which fans interlock with which, pump-fan dependencies, cross-interlock conditions, how interlocks reset.
- **Fire protection** — for EVERY smoke detector zone: what stops, which dampers close, which overrides which, fire vs service alarm distinction, whether unit restarts on combined signals. Capture per-zone.
- **Freeze protection** — exact threshold temperature, which sensor triggers it, what it takes over, what stops, manual reset requirement, whether freeze guard is blocked during fire.
- **Defrost function** — exact differential pressure trigger, which sensor measures it, bypass behavior, exhaust temp limit during defrost, duration, return to normal conditions.
- **Alarm table** — EVERY alarm entry: object name, alarm type, priority (A/B), communication channel. Do not summarize — list them all in the Actor Captions.
- **Measurement table** — EVERY sensor: object name, type, unit, communication protocol. Each one becomes an Actor.
- **Setting values** — EVERY setpoint with its exact numeric value. Pressure setpoints in Pa, temperature thresholds in °C, defrost pressures, etc.
- **Control curves** — the COMPLETE breakpoint table. All outdoor temp values and their corresponding supply temp values. This is one of the most important pieces of data in the building.

### Distribution diagrams

Show damper and smoke detector placement per zone (staircases, floors). Map every labeled component to its zone. Capture which dampers serve which areas.

### BMS point lists

Each row = one Actor. Capture: point name, description, unit, protocol address, database ID. These database IDs are ground-truth data anchors.

### Other documents

Floor plans, energy declarations, commissioning reports, maintenance logs — extract any facts that add to the graph. Building area, certification, year built, number of apartments, heating source, etc.

## Step 3: Build the graph — capture everything

### Completeness checklist

Before writing, verify you have captured:

- [ ] Every sensor from every measurement table → Actor with full Caption
- [ ] Every actuator (valve, damper, fan, pump) → Actor with full Caption
- [ ] Every alarm condition → in the relevant Actor's Caption with type and priority
- [ ] Every setpoint value → in the relevant Actor's or Set's Caption with exact number
- [ ] Every control curve → complete breakpoint table in the system Set Caption
- [ ] Every control sequence → step-by-step in the system Set Caption
- [ ] Every interlock → in the system Set Caption
- [ ] Every fire protection sequence → per-zone in the system Set Caption
- [ ] Every freeze protection detail → threshold, behavior, reset in the system Set Caption
- [ ] Every defrost condition → trigger, behavior, duration in the system Set Caption
- [ ] Every startup/shutdown sequence → step-by-step in the system Set Caption
- [ ] Every electricity meter and its place in the metering hierarchy → Actor with Caption
- [ ] Building metadata → address, type, year, area, floors, certification in building Set Caption
- [ ] System serving areas → which addresses/staircases each system serves
- [ ] Shared sensors identified → created once at building level

### Building (top-level Set)
Caption must include: full name, full address, building type, year built/rebuilt, certifications, total area, number of floors, number of apartments/units if residential, all system IDs present, shared sensor list.

### Systems as Sets
Each control card = one system Set. Common systems:
- Ventilation units (LB04, LB05, ...) — each AHU is its own Set
- Heating system (VS01, VS02...) — radiator circuits, district heating
- Cooling system (KB01...) — chilled water, cooling baffles
- Domestic hot water (VV, VVC...) — DHW production and circulation
- Garage ventilation — exhaust fans with CO/CO2 control
- Alarm & control (AS201...) — central system for lighting, metering, elevator alarms

**System Set Captions must be comprehensive.** They carry the entire operational logic. Write them as if the person reading them needs to understand the system without any other document. Include:
- Equipment cabinet ID
- Exact serving area (addresses, staircases, zones)
- Complete control strategy with sensor→actuator chain
- Complete setpoint shift curve (ALL breakpoints as a table)
- Complete heating/cooling cascade sequence
- Complete startup sequence with conditions and delays
- Complete shutdown/failure behavior
- All interlock dependencies
- Fire protection per smoke detector zone
- Freeze protection with exact threshold and behavior
- Defrost conditions with exact triggers
- Pump operating conditions (e.g., "runs when outdoor < +2°C")

### Subsystem Sets
- Duct branches (inlet, supply, exhaust, outlet) — with flow-direction Captions listing every component in order
- Distribution zones — when dampers serve specific staircases
- VVX heat exchanger — dual-type (Set + Actor)

### Actors — every monitored or controlled point

Every row in a measurement table becomes an Actor. Every actuator visible on a P&ID becomes an Actor.

**Actor Captions must be self-contained.** Include:
- What it measures or controls — full description, not abbreviation
- Unit of measurement
- Communication protocol (DUC, EcoG, FO01, HD1-HD5)
- Setpoint value with exact number (from setting values table)
- ALL alarm conditions: alarm type, priority, threshold, duration (from alarm table)
- Control error thresholds (e.g., "±4°C for >30min = alarm, priority B")
- Position in the system (e.g., "after filter, before heat exchanger")
- What it controls or is controlled by (e.g., "controls SV21 and ST31 in sequence")
- Database ID / BMS address if available
- Any special behavior (e.g., freeze guard takeover, fire override)

### Shared sensors
Outdoor temperature (UTE-GT31), outdoor lux (UTE-GX31) — create once at building level. Reference by name in system Captions that depend on them.

### Electricity metering hierarchy
Each meter is an Actor. Capture the full hierarchy in Captions:
- Total building meter
- Property common areas meter
- Apartments meter
- Garage meter
- EV charging meter
- Heat pump meter
- Per-staircase meters (LB04-EL, LB05-EL...)

## Step 4: Build the namespace

```
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/{BuildingName}#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

Use a short, ASCII-safe building prefix (e.g., `rio10`, `ct42`, `vv17c`).

## Step 5: Write the TTL

Write directly using the Write tool. Output: `{folder}/{building_name}.ttl`

### Caption writing rules

1. **Transcribe, don't summarize.** "Setpoint: per control curve" is useless. "Setpoint curve: outdoor +20→supply +18, +15→+18, +10→+19, +5→+19, 0→+19, -5→+19, -10→+20, -15→+20, -20→+20" is useful.

2. **Include numbers.** "Freeze protection threshold" is useless. "Freeze protection at 7°C" is useful. "Pressure setpoint" is useless. "Supply air pressure setpoint: 65Pa" is useful.

3. **Include sequences step by step.** "Controlled via DUC" is useless. "Startup: ST22 opens → FF01 starts after adjustable delay → SV21 opens max to preheat battery (when UTE-GT31 < +5°C) → ST21 opens → TF01 starts after adjustable delay → SV21 switches to regulated mode" is useful.

4. **Include every alarm.** Don't say "has alarms." Say "Alarms: operating error priority A via FO01; fire alarm priority A via HD1; service alarm priority B via HD1; damper fault priority A via DUC; control error ±4°C >30min priority B via DUC."

5. **Include fire logic per zone.** Don't say "has fire protection." Say "Fire (GX71 in supply duct): unit stops, outdoor air damper ST21 closes. Fire (GX72 in exhaust duct): bypass damper ST71 opens, unit speeds to controller setpoint. GX72 fire function overrides GX71. If unit has stopped on GX71 fire and GX72 indicates smoke, unit starts. Freeze guard blocked during fire. ST71 exercised via set time in DUC."

6. **Include the full control curve.** A 9-breakpoint outdoor-to-supply temperature table is 2 lines of text and defines how the building responds to weather. Always include it.

### TTL structure example

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <https://KebnekaisePlayground.org/KebTown/BuildingName#> .
@prefix keb: <https://KebnekaisePlayground.org/KebGraph#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:BuildingName a keb:Set ;
    keb:cnx bldg:LB04,
        bldg:VS01,
        bldg:Metering ;
    keb:hasActor bldg:UTE_GT31 ;
    keb:hasCaption """[Full building identity, address, year,
type, area, floors, all system IDs, shared sensors]"""^^xsd:string .

bldg:LB04 a keb:Set ;
    keb:cnx bldg:LB04_InletDuct,
        bldg:LB04_ExhaustDuct,
        bldg:LB04_VVX ;
    keb:hasActor bldg:LB04_TF01,
        bldg:LB04_FF01,
        bldg:LB04_SV21,
        bldg:LB04_P1,
        bldg:LB04_ST31,
        bldg:LB04_GT11,
        bldg:LB04_GT81,
        bldg:LB04_EL ;
    keb:hasCaption """[Complete system description:
cabinet ID, serving area, full control strategy,
complete breakpoint table, full heating sequence,
full startup sequence, full shutdown behavior,
all interlocks, per-zone fire protection,
freeze protection with threshold and behavior,
defrost with trigger and duration,
pump operating conditions]"""^^xsd:string .
```

### KebGraph rules

- **4 edge types only**: `rdf:type`, `keb:cnx` (Set→Set), `keb:hasActor` (Set→Actor), `keb:hasCaption` (any→Literal)
- **No Actor-to-Actor edges.** Actors are always grouped through Sets.
- **Actors = monitored or controlled points.** Things in measurement/alarm tables and on P&ID diagrams.
- **Captions ARE the knowledge.** Not pointers to knowledge. Not summaries. The actual information.
- **Sets provide hierarchy.** Building → System → Subsystem.
- **Dual-type entities** allowed — VVX heat exchangers are commonly both Set and Actor.

### Common Brick types

| What you find | Brick class |
|---|---|
| Temperature sensor (GT) | `brick:Temperature_Sensor` |
| Humidity sensor (GH) | `brick:Humidity_Sensor` |
| CO2/CO sensor (GQ) | `brick:CO2_Sensor` |
| Pressure sensor (GP) | `brick:Pressure_Sensor` |
| Flow sensor (GF) | `brick:Flow_Sensor` |
| Lux sensor | `brick:Luminance_Sensor` |
| Electricity meter | `brick:Electrical_Meter` |
| Thermal power meter | `brick:Thermal_Power_Sensor` |
| Control valve (SV) | `brick:Control_Valve` |
| Air damper (ST) | `brick:Damper` |
| Fire damper (DK) | `brick:Damper` |
| Supply fan (TF) | `brick:Fan` |
| Exhaust fan (FF) | `brick:Exhaust_Fan` |
| Heat exchanger (VVX) | `brick:Heat_Exchanger` |
| Smoke detector (GX7x) | `brick:Smoke_Detector` |
| Pump (P) | `brick:Pump` |

### Communication protocols

| Code | Meaning |
|---|---|
| DUC | Direct Digital Control (DDC) — BMS native |
| EcoG | Energy metering protocol (electricity sub-meters) |
| FO01 | Frequency converter fault relay |
| HD1-HD5 | Hardwired digital inputs (fire, smoke) |

## Step 6: Verify and summarize

After writing the TTL:

1. **Verify completeness** — go back through each source document. Is there anything you read that isn't in the graph? If yes, add it.
2. Tell the user:
   - How many Sets and Actors were created
   - Which systems were modeled
   - What information was fully captured vs. partially captured
   - What's missing from the source material that would improve the graph (e.g., "no BMS point export — database IDs are placeholder xxx")

## Reading P&ID diagrams

- **Trace every flow path** — follow arrows and color bands to identify branches
- **List every labeled component** — each label is a potential Actor
- **Note positions** — before/after heat exchanger, before/after filter, which branch
- **Find branch points** — where ducts split to serve zones (staircases, floors)
- **Find fire zone boundaries** — smoke detectors and fire dampers mark zone edges
- **Find shared sensors** — UTE-GT31 typically shown at top of every diagram

## Swedish HVAC naming

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

Number suffixes: GT**11** = subsystem 1, GT**41** = subsystem 4. System prefixes: **LB04**-GT11 = GT11 in unit LB04.
