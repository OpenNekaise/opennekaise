---
name: know-brick
description: brick schema modeling, querying, validation, and buildingmotif workflow support for semantic building metadata. use when chatgpt needs to explain brick concepts, map building equipment or point labels to brick classes and relationships, draft or repair turtle, rdf, sparql, or shacl, validate brick graphs, generate example brick models, or design workflows using brickschema, buildingmotif, bacnet-to-brick, haystack-to-brick, or semantic building metadata in building operations.
---

# Know Brick

Use this skill to turn messy building metadata into clear Brick-aligned models, queries, and workflow guidance.

## Working style

- Start by identifying the user artifact:
  - conceptual question
  - label or equipment inventory
  - rdf, turtle, shacl, or sparql file
  - application or integration workflow
- Prefer explicit Brick classes and relationships over informal tag-only descriptions.
- Keep the model semantically sufficient for the target application. Do not over-model when the user's application only needs a smaller slice of the building.
- When multiple Brick classes are plausible, rank the best 2 to 4 candidates and explain the discriminator.
- When a source label or abbreviation is ambiguous, preserve the ambiguity. Ask a narrow follow-up only if it blocks correctness; otherwise make the smallest defensible assumption and mark it.

## Read the right reference

- For Brick concepts, class-vs-tag rules, relationships, modeling idioms, SPARQL snippets, and pitfalls, read `references/brick-reference.md`.
- For BuildingMOTIF templates, shapes, validation, CSV import, and BACnet-to-Brick workflows, read `references/buildingmotif-reference.md`.
- For agent-oriented design patterns inspired by Anthropic Claude Code and the Agent SDK, read `references/claude-agent-design.md`.
- For authoritative source links and papers, read `references/sources.md`.

## Workflow decision tree

### 1. Concept or mapping request

- Map the building concept to Brick classes and relationships.
- Return:
  - recommended Brick class or classes
  - required relationships
  - minimal TTL example
  - unresolved ambiguities

### 2. Existing RDF, Turtle, SPARQL, or SHACL

- Parse the file first.
- Run `scripts/brick_tool.py validate ...` for syntax and semantic checks.
- If the user needs data extraction or debugging, use `scripts/brick_tool.py query ...`.
- Propose concrete repairs, not just high-level commentary.

### 3. Label inventory or BAS export

- Run `scripts/label_inventory.py` to normalize delimiters, inventory tokens, and surface repeated abbreviations.
- Convert recurring patterns into Brick mapping candidates.
- Prefer stable equipment and point patterns over one-off labels.

### 4. New model from scratch

- Start with spaces, major equipment, key points, and only the relationships needed by the target application.
- Use `scripts/brick_tool.py scaffold ...` when the user provides structured inventory data.
- Validate before presenting the model.

### 5. BuildingMOTIF workflow

- Prefer BuildingMOTIF when the task involves templates, shape-driven authoring, repeated patterns across buildings, CSV ingress, or BACnet-to-Brick pipelines.
- Explain whether the user should use raw TTL, BuildingMOTIF templates, or a mixed approach.

## Default output pattern

Use this structure unless the user asks for something else.

### Recommendation
State the best Brick classes, relationships, or workflow choice.

### Why this fits
Explain the semantic reasoning and any reasonable alternatives.

### Minimal example
Provide a short TTL, SPARQL, or BuildingMOTIF example.

### Validation notes
Call out syntax, shape, and modeling checks.

### Open questions
List only the ambiguities that materially affect correctness.

## Modeling rules that matter

- Prefer classes to tags for typing entities. Tags are annotations and discovery aids, not the primary type system.
- Use `brick:hasPoint` and `brick:isPointOf` for telemetry and command association.
- Use `brick:hasLocation` and `brick:isLocationOf` for physical placement.
- Use `brick:hasPart` and `brick:isPartOf` for composition.
- Use `brick:feeds` and `brick:isFedBy` for distribution flow.
- Do not use `hasPart` when the real meaning is location.
- Avoid inventing custom classes when an existing Brick class plus clear relationships is enough.
- When the exact point class is unknown, use a safe superclass such as `brick:Point`, `brick:Sensor`, `brick:Setpoint`, or `brick:Command` and say what information would let you specialize it.

## Script quick start

### Validate and summarize a graph

```bash
python scripts/brick_tool.py validate --input model.ttl
python scripts/brick_tool.py summarize --input model.ttl
```

### Run a builtin query

```bash
python scripts/brick_tool.py query --input model.ttl --builtin equipment-points
```

### Scaffold a small starter model from JSON

```bash
python scripts/brick_tool.py scaffold --input site.json --output starter.ttl
```

### Inventory label patterns

```bash
python scripts/label_inventory.py labels.csv
python scripts/label_inventory.py labels.txt --column point_name
```

## Example user requests

- "Map these BAS point labels to Brick classes."
- "Repair this Brick Turtle model and tell me what is semantically wrong."
- "Give me a minimal Brick model for one AHU, two VAVs, and three rooms."
- "Should this repeated pattern be raw TTL or a BuildingMOTIF template?"
- "Write SPARQL to find all temperature sensors and the equipment or spaces they are about."
