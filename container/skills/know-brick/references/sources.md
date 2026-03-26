# Sources and Research Notes

This file collects the primary sources used to shape this skill. Treat these as the first places to re-check when the ecosystem changes.

## Official Brick sources

- Brick homepage: https://brickschema.org/
- Brick ontology documentation: https://docs.brickschema.org/
- Brick relationships: https://docs.brickschema.org/brick/relationships.html
- Brick design principles: https://docs.brickschema.org/brick/overview.html
- Brick core concepts: https://docs.brickschema.org/brick/concepts.html
- Brick tags: https://docs.brickschema.org/metadata/tags.html
- Brick model creation guidance: https://docs.brickschema.org/lifecycle/creation.html
- Brick tools, downloads, and publication list: https://brickschema.org/resources/
- Brick source repository: https://github.com/BrickSchema/Brick

## Tooling around Brick

### brickschema Python package

- PyPI: https://pypi.org/project/brickschema/
- Purpose: parsing, reasoning, validation, querying, and serving Brick-aware graphs

### BuildingMOTIF

- PyPI: https://pypi.org/project/buildingmotif/
- Documentation: https://nrel.github.io/BuildingMOTIF/
- Model creation tutorial: https://nrel.github.io/BuildingMOTIF/tutorials/model_creation.html
- Model validation tutorial: https://nrel.github.io/BuildingMOTIF/tutorials/model_validation.html
- Shapes and templates: https://nrel.github.io/BuildingMOTIF/explanations/shapes-and-templates.html
- CSV import guide: https://nrel.github.io/BuildingMOTIF/guides/csv-import.html
- BACnet to Brick guide: https://nrel.github.io/BuildingMOTIF/guides/ingress-bacnet-to-brick.html
- Bibliography: https://nrel.github.io/BuildingMOTIF/bibliography.html

## Anthropic Claude Code and Agent SDK sources

- Claude Code SDK overview: https://docs.anthropic.com/en/docs/claude-code/sdk
- Claude memory: https://docs.anthropic.com/en/docs/claude-code/memory
- Claude slash commands: https://docs.anthropic.com/en/docs/claude-code/slash-commands
- Claude subagents: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Claude hooks: https://docs.anthropic.com/en/docs/claude-code/hooks
- Claude MCP: https://docs.anthropic.com/en/docs/claude-code/mcp
- Claude SDK MCP: https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-mcp

## Brick papers and adjacent research

### Foundational Brick papers

- Brick: Towards a Unified Metadata Schema for Buildings. BuildSys 2016.
- Brick: Metadata Schema for Portable Smart Building Applications. Applied Energy, 2018. DOI: 10.1016/j.apenergy.2018.02.091
- Beyond a House of Sticks: Formalizing Metadata Tags with Brick. BuildSys 2019.

### Lifecycle and integration

- Shepherding Metadata Through the Building Lifecycle. BuildSys 2020. DOI: 10.1145/3408308.3427627
- Interactive Metadata Integration with Brick. BuildSys 2020 demo. DOI: 10.1145/3408308.3431125

### Review and scope expansion

- Metadata Schemas and Ontologies for Building Energy Applications: A Critical Review and Use Case Analysis. Authors include Marco Pritoni, Michael Poplawski, Avijit Saha, Joel Bender. Review article on interoperability and use cases.
- Extending the Brick Schema to Represent Metadata of Occupants. Automation in Construction, 2022. DOI: 10.1016/j.autcon.2022.104307

### BuildingMOTIF and semantic sufficiency

- Application-Driven Creation of Building Metadata Models with Semantic Sufficiency. BuildSys 2022. DOI: 10.1145/3563357.3564083

## Snapshot checked while authoring this skill

Verified on 2026-03-26:

- Brick stable release visible on the Brick tools page: 1.4.4
- `brickschema` release visible on PyPI: 0.7.9
- `buildingmotif` release visible on PyPI: 0.4.0

Because these tools evolve, re-check the official sources above before pinning versions in production instructions.

