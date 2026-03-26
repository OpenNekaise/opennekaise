# BuildingMOTIF Reference

## Contents

1. When to use BuildingMOTIF
2. Core concepts
3. Practical workflows
4. Templates vs shapes
5. Choosing raw TTL vs BuildingMOTIF
6. Common pitfalls

## When to use BuildingMOTIF

Choose BuildingMOTIF when the task has repeated structure, validation requirements, or ingestion from existing metadata sources.

BuildingMOTIF is especially useful for:

- authoring repeated building patterns as templates
- validating models against Brick or custom SHACL constraints
- CSV-driven generation of repeated equipment and point structures
- BACnet-to-Brick or other ingress pipelines that need enrichment after import
- maintaining reusable libraries instead of copying large TTL fragments by hand

## Core concepts

### BuildingMOTIF instance

This is the main application object. It manages models, libraries, templates, shapes, and storage.

### Model

A model is the building graph you are creating or editing.

### Library

A library is a reusable bundle of ontology content, templates, and shapes. A Brick library gives you Brick classes and shapes. A custom library can encode local patterns.

### Template

A template is a reusable graph-generating pattern. Use templates when the same structural motif appears many times, such as many thermostats, VAVs, or similar room packages.

### Shape collection

A shape collection is a set of SHACL constraints used for validation.

### Ingress

Ingress modules pull data from another source and turn it into graph fragments or records. Examples include CSV ingress and BACnet ingress.

## Practical workflows

### Workflow A: model creation with reusable templates

Use this when the user has repeated, structured equipment patterns.

1. Create a BuildingMOTIF instance.
2. Create a model namespace for the site.
3. Load the Brick library.
4. Load or author a custom template library.
5. Evaluate templates to generate graph fragments.
6. Validate the resulting model.
7. Export the model to Turtle.

### Workflow B: validate an existing model

Use this when the user already has a Brick model and wants confidence checks.

1. Load the model.
2. Load the Brick library or shape collection.
3. Run validation.
4. Report which constraints fail and propose the minimum repairs.

### Workflow C: CSV import for repeated structures

Use this when the source data is tabular and the repeated building pattern is known.

1. Encode the pattern as a template.
2. Generate or define the expected CSV columns.
3. Fill CSV rows for each repeated instance.
4. Run a CSV ingress through the template.
5. Validate the produced graph.

### Workflow D: BACnet to Brick then enrich

Use this when the raw BACnet import gives shallow or generic point types.

1. Pull device and object metadata from BACnet.
2. Convert the network into an initial Brick graph.
3. Enrich the graph with label parsing, local naming conventions, or template-driven structure.
4. Validate and iterate.

## Templates vs shapes

These are related but not the same.

- A template generates graph structure.
- A shape constrains graph structure.

A useful mental model is:

- template = what to create
- shape = what must be true

When a pattern is repeated and should be created many times, use a template.
When a rule must hold regardless of how the graph was created, use a shape.

## Choosing raw TTL vs BuildingMOTIF

### Prefer raw TTL when

- the example is tiny
- the user needs a one-off snippet
- the task is debugging a small local graph
- no repeated pattern or ingestion flow exists

### Prefer BuildingMOTIF when

- a pattern repeats many times
- the user wants reusable authoring assets
- validation is part of the expected workflow
- ingestion from CSV or BACnet matters
- the project needs a maintainable template library rather than copied snippets

### Mixed approach

Often the best answer is hybrid:

- sketch the semantics in a small TTL example for clarity
- recommend a template or ingress workflow for production

## Common pitfalls

### 1. Encoding one-off detail as a template too early

If the user only has a single example and no evidence of repetition, stay simple.

### 2. Treating validation as optional

BuildingMOTIF is especially valuable when the team wants repeatable correctness, not just graph generation.

### 3. Importing source data and assuming it is semantically complete

BACnet or CSV imports often need enrichment before the model is operationally useful.

### 4. Mixing local naming conventions directly into ontology design

Keep local naming rules in templates, ingestion logic, or conventions. Do not let them distort the semantic model.

