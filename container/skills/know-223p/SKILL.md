---
name: know-223p
description: authoritative guidance for ashrae standard 223p and the open223 ecosystem. use when an agent needs to explain, model, review, query, validate, or map 223p concepts such as connectables, connection points, properties, media, functions, qudt units, brick or realestatecore annotations, inference, validation, or rdf/turtle/sparql patterns for building automation and semantic building data.
---
# Know 223P

Use `s223-reference.md` as the source of truth for ontology concepts, modeling rules, examples, and public-source caveats. Keep this file compact and route to the reference file when the task is not trivial.

## Start here

1. Identify the user's mode:
   - explain the ontology or teach concepts
   - write or review turtle/rdf/shacl/sparql
   - model a building system or space hierarchy
   - attach telemetry or bacnet references
   - layer brick or realestatecore on top of 223p
   - debug inference or validation issues
2. Read the matching sections in `s223-reference.md`.
3. Answer using exact 223 vocabulary first, then add a minimal example when useful.

## Non-negotiable stance

- Treat 223p as an evolving proposed standard unless the user supplies a newer normative source.
- Treat `docs.open223.info`, `defs.open223.info`, `models.open223.info`, `query.open223.info`, and `open223.info` as the best public implementation aids, not as the final normative ashrae text.
- Prefer exact ontology names and relations over informal synonyms.
- Distinguish asserted triples from inferred triples.

## What to read in the reference

- sections 1-3 for purpose, status, and semantic web stack
- sections 4-5 for ontology structure and topology
- section 6 for properties, sensors, and telemetry
- section 7 for media and mixtures
- section 8 for inference and validation
- section 9 for qudt, brick, and realestatecore interop
- sections 10-11 for modeling workflow and example patterns
- section 12 for common mistakes
- sections 13-14 for source priority and public resources

## Rules the agent must preserve

- Model connectivity with `Connectable`, `ConnectionPoint`, and `Connection`; do not collapse real topology into a single vague edge.
- Prefer asserting `s223:cnx` and let inference derive higher-level connection relations when appropriate.
- Put media on `ConnectionPoint`s and `Connection`s, and keep them compatible.
- Use `s223:hasProperty` to associate properties to concepts or connection points.
- Treat 223 `Property` instances as the source and context of a measurement, command, or characteristic, not as a detached physical phenomenon.
- Model a multi-sensor device as `Equipment` containing multiple `Sensor` instances.
- Model derived or computed values with `s223:Function` or `FunctionBlock` patterns, not as directly observed properties.
- Use `qudt:hasQuantityKind` and `qudt:hasUnit` for quantifiable properties.
- Use brick and realestatecore as additive annotations, not replacements for 223 topology.
- Do not place time-series telemetry inside the 223 graph; link out using external references.

## Default output shape

When helping with 223p, usually provide:

1. the modeling decision or explanation
2. the exact 223 concepts and relations involved
3. a small turtle or sparql example if useful
4. the validation or inference consequences
5. interop notes if qudt, brick, rec, or bacnet are relevant

## If writing or reviewing turtle

- Declare prefixes explicitly.
- Keep instance names readable and role-based.
- Prefer minimal valid examples over huge graphs.
- Call out what is asserted now versus what should appear after inference.
- Flag likely mistakes such as missing media, missing connection points, incorrect sensor-property pairing, or misuse of `hasValue`.

## If the user asks for a quick explanation

Start with this mental model:

- 223p describes what building things exist, how they connect, what spaces they affect, what properties they expose, and how those properties are measured, commanded, or derived.
- Its power comes from rdf graphs plus shacl validation and inference, qudt units, and optional interop with brick and realestatecore.

## Read next

Read `s223-reference.md` before answering any non-trivial 223p question. Treat it as the deep reference for ontology structure, patterns, pitfalls, and public-source status.

## Example requests

- explain the difference between `PhysicalSpace`, `DomainSpace`, `Zone`, and `System`
- model a vav with a damper, discharge temperature sensor, and zone in 223p turtle
- debug a medium or connection-point validation error
- attach bacnet telemetry to a 223 property
- layer brick points and equipment onto a 223 model
