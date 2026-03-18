---
name: update-ontology
description: Update the building's ontology with confirmed facts from conversation or daily sweep. Reads the existing ONTOLOGY.ttl, applies changes, writes the full file back. Only persists verified building facts — never speculation or plans.
---

# Update Ontology

## Purpose

Keep the building's ontology current as a living information representation. The ontology is the structured source of truth for the building — equipment, sensors, setpoints, control sequences, topology. When the agent learns a confirmed building fact, it belongs in the ontology.

## When to run

You are triggered in two ways:

- **After a conversation** — you already have the conversation in context. Ask yourself: "did this conversation contain a confirmed building fact that changes or adds to the ontology?" If yes, update. If it was just a question, a greeting, or speculation, skip.
- **Daily sweep (2 am)** — read today's messages from `/workspace/ipc/messages_history.json` and compare against the current ontology. Consolidate any confirmed facts that were missed.

## What counts as an ontology update

**Update the ontology when:**
- A setpoint was changed ("we set the supply temp to 35°C")
- Equipment was installed, replaced, or decommissioned
- A sensor was recalibrated, renamed, or its unit changed
- A control sequence was modified
- An alarm threshold was changed
- A new zone, circuit, or system was commissioned
- A serving area changed (system now covers a different floor/wing)
- An operational fact was confirmed by a technician or verified from data

**Do NOT update the ontology when:**
- Someone asked a question (no new fact)
- Someone speculated or planned ("we should probably change the setpoint")
- Someone discussed options that haven't been decided
- You inferred something that wasn't confirmed
- The conversation was about non-building topics
- The fact is already in the ontology and unchanged

## The test

Before writing any change, ask: **"Did a person confirm this as a fact about the building's current state, or did I observe it directly from building data?"**

If the answer is no, do not update.

## Steps

1. Read existing ontology:
   ```bash
   cat /workspace/group/ONTOLOGY.ttl 2>/dev/null || echo "No ontology."
   ```

2. If no ontology exists, skip. The ontology must first be created via `/ontology-spawn` on the host.

3. Get the conversation to process:
   - If you already have a conversation in context (auto-trigger after a chat), use that.
   - If running as a scheduled task, read the messages history:
     ```bash
     cat /workspace/ipc/messages_history.json 2>/dev/null || echo "[]"
     ```
   - If both are empty, skip.

4. Identify confirmed building facts that are new or different from what the ontology currently says. Compare carefully — do not "update" something that already matches.

5. If there are changes, read the full ontology, apply the changes, and write the entire file back:
   ```bash
   cat > /workspace/group/ONTOLOGY.ttl << 'ONTOLOGY_EOF'
   [full updated TTL content]
   ONTOLOGY_EOF
   ```

## What changes look like

### Caption updates (most common)
A setpoint changed, an alarm was added, an operational note was confirmed. Find the relevant Actor or Set and rewrite its `sg:hasCaption` with the updated information. Keep all existing information in the Caption that is still valid — only change what actually changed.

### New Actors
A sensor or actuator was installed. Add it as a new `sg:Actor` with the correct Brick type, a full Caption, and a `sg:hasActor` edge from its parent Set.

### New Sets
A new system or subsystem was commissioned. Add it as a `sg:Set` with a comprehensive Caption, connected to its parent via `sg:cnx`.

### Removals
Equipment was decommissioned. Remove the Actor or Set entirely. Do not leave stubs or "decommissioned" markers — if it's gone, it's gone from the graph.

## Graph rules (must follow)

- **4 edge types only**: `rdf:type`, `sg:cnx` (Set to Set), `sg:hasActor` (Set to Actor), `sg:hasCaption` (any to Literal)
- **No Actor-to-Actor edges.** Actors are grouped through Sets.
- **Captions ARE the knowledge.** Not pointers. Not summaries. The actual information with exact numbers.
- **Sets provide hierarchy.** Building, System, Subsystem.
- **Full rewrite.** Always write the complete file. Never attempt partial patches.

## Quality rules

- Never add speculative information. Only confirmed facts.
- Never weaken a Caption. If you update a setpoint, keep all other information in the Caption intact.
- Never remove information from a Caption unless it was explicitly corrected or the equipment was decommissioned.
- If you are unsure whether something is confirmed, do not update. Err on the side of not changing.
- Include the date of change in the Caption when updating operational values (e.g., "Supply setpoint: 35°C (changed 2026-03-17, was 32°C)").

## Output

After writing (or deciding to skip), wrap your entire response in `<internal>` tags so it is not sent to the user. Include a brief note of what changed (or "No ontology changes") for logging.
