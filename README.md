<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise converts buildings into Nekaise Agent that works in your Slack.
</p>

One day, buildings used to be studied and managed by "meat computers" in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in the ritual of "group meeting". The buildings themselves ran on rigid rule-based controls — fixed schedules that blast AC at 7am whether anyone showed up or not, thermostats fighting each other across floors, lights on timers that ignore the sun, and a BMS dashboard blinking hundreds of alarms that everyone learned to ignore.

That era began to fade. Buildings learned to understand themselves — AI agents reading documentation, fetching sensor data, analyzing time series, learning occupant patterns, and helping keep people comfortable, without anyone having to file a ticket or shout into a walkie-talkie.

The agents claim we are now in the 2,120th generation of the optimization, in any case no one could tell if that's right or wrong as the AI has long understood the building beyond what any engineer could comprehend. This repo is the story of how it all began.

— March 2026, with a salute to [@karpathy](https://github.com/karpathy/autoresearch)

That's why we started [TwinVista](https://resurseffektivbebyggelse.se/projekt/twinvista/), a large research project at KTH funded by [Energimyndigheten](https://www.energimyndigheten.se/en/).

[OpenNekaise](https://opennekaise.com/) is our open-source contribution back to the community.

## Nekaise Agent Philosophy

OpenNekaise creates AI agents (Nekaise Agents) that are grounded in ontology — a living information representation of the building that evolves through every interaction.

Most LLM-based agents operate on raw text and loose context. Our research at KTH shows that when you ground an agent in an ontology — defining what a building *is*, how its systems relate, and what its data *means* — the agent reasons more reliably and makes fewer hallucinated leaps. The ontology is not a one-time creation from documents. It is the agent's persistent, structured understanding of the building — updated as conversations happen, as technicians report changes, and as the agent consolidates what it has learned.

This is an active area of research. As our ontology work matures, OpenNekaise will evolve to reflect it.

## Quick Start

```bash
git clone git@github.com:OpenNekaise/opennekaise.git
cd opennekaise
claude
```

This opens [Claude Code](https://claude.ai/code). Run `/setup` and it will walk you through everything.

After setup, you don't need to read further — just ask Claude Code any question about your deployment, configuration, or building data. It already knows the codebase.

We suggest you just ask questions with your favorite coding agent — but if you really prefer the conventional way of reading a GitHub repo, here it is.

## Agents work in folders, sandboxed

OpenNekaise keeps one folder per building under `home/`, using the building slug as folder name (e.g. `home/rio-10/`). Your Slack channel names should match these folder names — the channel name is how the system maps a conversation to its building data. User data in `home/` is local by design and not tracked by git — only `home/.gitkeep` is versioned.

Every agent invocation runs inside an ephemeral Docker container that is destroyed on exit. One container per group, per message. The orchestrator spawns a fresh `docker run --rm` with mounts scoped to that group only:

| What the agent sees | Mount | Access |
|---|---|---|
| Its own working directory | `/workspace/group` | read-write |
| Its building data | `/home/<building-folder>` | read-only |
| Shared global prompt | `/workspace/global` | read-only |
| IPC (messages, tasks) | `/workspace/ipc` | read-write |

The agent for one building **cannot** see other buildings, other groups' working directories, or the host application code. The main/admin context gets read-only access to the project root — it still can't modify it.

**Secrets never touch disk.** API keys are passed via stdin JSON, consumed once, and deleted. A pre-tool hook strips credentials from the environment before any Bash subprocess runs.

DM channels are blocked by default. To allow direct messages to the bot, set `ADMIN_DM_JID` and `ALLOWED_DM_JIDS` in `.env`. Allowed DMs are restricted to the `main` context.

## MEMORY.md

`groups/<folder>/MEMORY.md` is what turns Nekaise Agent from a tool you query into a colleague who knows your building. Each group has one. The agent reads it at the start of every conversation.

Memory stores distilled facts, decisions, user preferences, and open issues — never raw messages. The agent decides what matters. Updates happen automatically:

- **After each conversation** — the agent reflects on what just happened and writes anything worth keeping. Corrections replace old entries, not duplicate them.
- **Daily sweep (2 am)** — a scheduled task reads the day's messages alongside existing memory and produces a cleaner, consolidated version.

Over weeks and months the agent becomes more useful — not because the model improved, but because the memory grew.

## ONTOLOGY.ttl

An ontology is a formal model that defines what things exist, what they mean, and how they relate to each other. Without one, an AI agent sees raw data — sensor readings, spreadsheets, scattered documents — but has no coherent understanding of the world behind that data. With an ontology, the agent knows that a supply temperature sensor belongs to a specific AHU, that the AHU serves a specific zone, and that the zone has occupancy patterns that affect how the system should run. This is a shared source of truth for decision-making — a semantic layer where value compounds over time as insights from one interaction benefit the next.

In our case, the ontology is the agent's structured facts of the building.

`groups/<folder>/ONTOLOGY.ttl` is that model — a semantic model containing equipment, sensors, setpoints, control sequences, and topology in RDF/Turtle format.

The ontology starts from documents. Run `/ontology-spawn` in Claude Code, point it at a building folder full of PDFs, images, spreadsheets, and control cards, and it extracts every building fact into `home/<building>/ONTOLOGY.ttl`. On first container run, the host seeds this into the group workspace automatically.

From there, the ontology is alive. It updates the same way memory does:

- **After each conversation** — if the conversation contained a confirmed building fact (a setpoint changed, a sensor was replaced, a system was commissioned), the agent updates the ontology. Speculation and plans are never written.
- **Daily sweep (2 am)** — the agent reviews the day's conversations against the current ontology and consolidates any confirmed facts that were missed.

The agent reads the full ontology at the start of each conversation alongside memory. Memory knows context — who said what, what was decided. The ontology knows the building — what equipment exists, how it's configured, how it behaves.

### What the agent knows

The agent's context is layered — each layer adds more specificity:

| Layer | File | What it does |
|---|---|---|
| Global prompt | `groups/global/CLAUDE.md` | Shared rules for all building agents — verify first, stay concise, use building data |
| Admin prompt | `groups/main/CLAUDE.md` | Extra context and tools for the admin channel only |
| Building prompt | `groups/<folder>/CLAUDE.md` | Building-specific instructions and quirks |
| Memory | `groups/<folder>/MEMORY.md` | Everything the agent has learned from past conversations |
| Ontology | `groups/<folder>/ONTOLOGY.ttl` | Structured building truth — equipment, sensors, setpoints, control sequences, topology |

Sessions give the agent short-term continuity within a conversation. Memory and ontology are the long-term layers — they survive session clears, restarts, and prompt updates.

## SKILL.md

Skills are markdown files that teach the agent how to do specific things. They live in two places for two audiences:

**Host skills** (`.claude/skills/`) — for you, the developer running Claude Code on this machine. These power slash commands like `/setup`, `/debug`, `/customize`, and `/update`. They never enter the container.

- **ontology-spawn** — reads all documents in a building folder (PDFs, images, spreadsheets, CSVs, existing TTL) and extracts every building fact into `ONTOLOGY.ttl`. Run via Claude Code on the host.

**Container skills** (`container/skills/`) — for Nekaise Agent inside the sandbox. These get synced into every group's container on each run, so agents always have the latest version.

- **update-memory** — powers the MEMORY.md system described above.
- **update-ontology** — powers the ONTOLOGY.ttl system described above.
- **agent-browser** — gives the agent a real browser for research, reading articles, extracting data from web pages, and interacting with web apps.
- **ontology** — RDF, Brick Schema, and ASHRAE 223P support. Python tool for parsing TTL files, running SPARQL queries, exploring class hierarchies, and building semantic models.
- **kebgraph** — semantic model reference and tooling used by ONTOLOGY.ttl.

Skills are just markdown — no special framework. Drop a folder with a `SKILL.md` into `container/skills/` and it's available to every agent on the next run.

## Upstream Credit

OpenNekaise is forked from [NanoClaw](https://github.com/qwibitai/nanoclaw) and has since been redesigned for the built environment — with ontology-grounded reasoning, per-building isolation, and structured building data at its core. Thanks to the NanoClaw maintainers for the lightweight starting point. It is hard to say no to [pure Claude Agent SDK-based AI agents](https://platform.claude.com/docs/en/agent-sdk/overview).

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of thinking and working with LLMs.

## License

MIT
