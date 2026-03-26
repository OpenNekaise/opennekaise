# Claude Agent Design Notes for a Brick Skill

## Contents

1. Why this matters
2. Claude Code building blocks that resemble skill primitives
3. Design implications for `know-brick`
4. A portable Claude-oriented layout
5. Recommended command patterns
6. Tool and safety boundaries

## Why this matters

Anthropic's Claude Code ecosystem does not use the exact same packaging model as ChatGPT Skills, but it exposes adjacent primitives that should shape how a Brick skill is organized:

- project memory through `CLAUDE.md`
- custom slash commands in `.claude/commands/`
- subagents for specialized work
- hooks for pre and post tool control
- MCP for live external tools and data sources
- SDK tool permissions such as `allowedTools`, `disallowedTools`, and permission modes

A good Brick skill should therefore separate:

- short control-plane instructions
- large domain references
- deterministic scripts
- optional live integrations

## Claude Code building blocks that resemble skill primitives

### `CLAUDE.md`

Use project memory for short operational rules, common commands, naming conventions, and links to reference files. Keep it compact.

### Custom slash commands

Use Markdown files in `.claude/commands/` for frequent task entrypoints such as validation, query generation, and point-label mapping.

### Subagents

Use specialized subagents when the work benefits from a separate context window, such as:

- a Brick modeler
- a Brick validator
- a BuildingMOTIF template author

### Hooks

Use hooks when you want automatic checks before or after editing files, such as running a local validator after changes to `.ttl`, `.rq`, or `.md` files.

### MCP

Use MCP only when live systems materially improve the workflow, such as a triplestore, issue tracker, document store, or BAS-related API. Treat remote tools as untrusted inputs until checked.

## Design implications for `know-brick`

### 1. Keep the main instructions short

The main `SKILL.md` should tell the agent how to classify the task and which deeper reference file to load. Do not dump the entire ontology into the entrypoint.

### 2. Put domain depth in references

Move Brick semantics, BuildingMOTIF guidance, and research context into separate reference files. This reduces context cost and mirrors how Claude Code memory plus slash commands are usually organized.

### 3. Use scripts for fragile repeated operations

Parsing Turtle, running canned SPARQL, inventorying point labels, and scaffolding starter graphs are good script candidates because they are deterministic and error-prone when rewritten ad hoc.

### 4. Expose clear task entrypoints

Good Brick entrypoints are:

- validate a graph
- summarize a graph
- run a canned query
- inventory noisy labels
- scaffold a starter model

### 5. Make live integrations optional

The core skill should still work offline. Live triplestore, BAS, or issue-tracker access can be layered in later through MCP or connectors.

## A portable Claude-oriented layout

If this skill is adapted to Claude Code, use a structure like:

```text
CLAUDE.md
.claude/
  commands/
    brick-validate.md
    brick-map.md
    brick-query.md
references/
  brick-reference.md
  buildingmotif-reference.md
scripts/
  brick_tool.py
  label_inventory.py
```

### Suggested role of each file

- `CLAUDE.md`: short project memory and pointers
- `.claude/commands/*.md`: reusable entry prompts
- `references/*.md`: long-form domain knowledge
- `scripts/*.py`: deterministic local tooling

## Recommended command patterns

### `/brick-validate`

Prompt idea:

- parse the current Brick files
- run local validation scripts
- summarize errors by category
- propose the smallest semantic repair set

### `/brick-map`

Prompt idea:

- normalize the provided point labels or equipment inventory
- infer likely Brick classes and relationships
- mark ambiguous abbreviations explicitly
- emit a minimal starter graph

### `/brick-query`

Prompt idea:

- inspect the model
- choose or write the safest SPARQL query
- explain assumptions about classes, relationships, and reasoning

## Tool and safety boundaries

- Validation-oriented agents should usually need read plus local execution, not network access.
- Modeling agents can often work with read, write, and local execution only.
- Live integrations through MCP should be narrowly scoped and justified.
- Treat generated Brick mappings as reviewable proposals when source labels are weak or ambiguous.

