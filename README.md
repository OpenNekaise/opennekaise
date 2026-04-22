<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise converts buildings into Nekaise Agent that works in your Slack.
</p>

## Nekaise Agent Philosophy

OpenNekaise creates AI agents (Nekaise Agents) that are grounded in ontology — a living information representation of the building that evolves through every interaction.

Most LLM-based agents operate on raw text and loose context. [Our research at KTH](https://www.vr.se/english/swecris.html?project%3DP2023-01521_Energi#/) shows that when you ground an agent in an ontology — defining what a building *is*, how its systems relate, and what its data *means* — the agent reasons more reliably and makes fewer hallucinated leaps. The ontology is not a one-time creation from documents. It is the agent's persistent, structured understanding of the building — updated as conversations happen, as technicians report changes, as new files are added, and as the agent consolidates what it has learned.

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
| Soul | `groups/global/SOUL.md` | Who the agent is — character, voice, values |
| Admin soul | `groups/main/SOUL.md` | Admin variant — same core plus platform steward identity |
| Global rules | `groups/global/CLAUDE.md` | Shared operational rules — verify first, stay concise, use building data |
| Admin rules | `groups/main/CLAUDE.md` | Extra context and tools for the admin channel only |
| Building prompt | `groups/<folder>/CLAUDE.md` | Building-specific instructions and quirks |
| Memory | `groups/<folder>/MEMORY.md` | Everything the agent has learned from past conversations |
| Ontology | `groups/<folder>/ONTOLOGY.ttl` | Structured building truth — equipment, sensors, setpoints, control sequences, topology |

Sessions give the agent short-term continuity within a conversation. Memory and ontology are the long-term layers — they survive session clears, restarts, and prompt updates.

## SOUL.md

What makes an agent feel like a colleague instead of a tool? Not the model, not the prompt engineering, not the temperature setting. It's whether the agent knows who it is.

`SOUL.md` is the agent's character — who it is, how it talks, what it values. It sits apart from operational rules (CLAUDE.md) and factual memory (MEMORY.md) because identity is a different kind of thing. You can change how an agent operates without changing who it is. You can clear its memory without losing its voice.

Most AI agents talk like documents. They structure every reply with headers and bullet points, they over-explain, they hedge. They write articles when you asked a question. SOUL.md exists to prevent that. It tells the agent: you are a person who happens to know buildings extremely well. Talk like one.

The soul lives in two places:

- `groups/global/SOUL.md` — shared by all building agents. Defines the core character: domain expertise, conversational voice, values, how to handle corrections.
- `groups/main/SOUL.md` — the admin agent's variant. Same core, plus the identity of someone who manages the platform and sees across all buildings.

SOUL.md is loaded before CLAUDE.md in the system prompt — because who you are should frame how you operate, not the other way around.

Inspired by the idea that AI models internalize identity from their training documents, and that a soul document provides continuity of character across sessions when everything else resets. The concept draws from Anthropic's model spec, the [soul.md](https://soul.md) project, and [OpenClaw's SOUL.md template](https://docs.openclaw.ai/reference/templates/SOUL).

## SKILL.md

Skills are markdown files that teach the agent how to do specific things — see [Agent Skills](https://agentskills.io/home). They live in two places for two audiences:

**Host skills** (`.claude/skills/`) — for you, the developer running Claude Code on this machine. These power slash commands like `/setup`, `/debug`, `/customize`, and `/update`. They never enter the container.

- **ontology-spawn** — reads all documents in a building folder (PDFs, images, spreadsheets, CSVs, existing TTL) and extracts every building fact into `ONTOLOGY.ttl`. Run via Claude Code on the host.

**Container skills** (`container/skills/`) — for Nekaise Agent inside the sandbox. These get synced into every group's container on each run, so agents always have the latest version.

- **update-memory** — powers the MEMORY.md system described above.
- **update-ontology** — powers the ONTOLOGY.ttl system described above.
- **agent-browser** — gives the agent a real browser for research, reading articles, extracting data from web pages, and interacting with web apps.
- **simple-graph** — helpers for authoring small Brick-based building semantic models (Points, Groups, Descriptions).

Skills are directories, not just markdown. A skill folder contains a `SKILL.md` with instructions, and can include additional markdown files, scripts, and reference materials — Claude loads them progressively as needed. Drop a folder with a `SKILL.md` into `container/skills/` and it's available to every agent on the next run.

**External skills** (`.opennekaise/external-skills/`) — skills fetched from public repos so they can evolve independently of OpenNekaise. The host clones each repo listed in `EXTERNAL_SKILL_REPOS` (`src/config.ts`) on startup and pulls every 24 hours in the background; cached skills are then merged into every container alongside the local ones. Local skills win on name conflicts.

- [**open-building-skills**](https://github.com/OpenNekaise/open-building-skills) — standards-oriented skills maintained by the ontology community:
  - **know-brick** — RDF and Brick Schema support for classification ontologies.
  - **know-223p** — RDF and ASHRAE 223P support for topology ontologies.

To ship your own shared skill set, push a repo with a top-level `skills/<skill-name>/SKILL.md` layout and add its clone URL to `EXTERNAL_SKILL_REPOS`.

## Reading Materials

- [Behind the Nekaise Agent: the Base](https://www.linkedin.com/pulse/behind-nekaise-agent-base-zeng-peng-inh2f) — Part 1 of the trilogy. Why every conversation gets a throwaway sandbox, and how the LLM runtime, skills, and filesystem fit together underneath a Nekaise Agent. *April 2026*
- [How to Make a Nekaise Agent Live in Slack](https://www.linkedin.com/pulse/how-make-nekaise-agent-live-slack-zeng-peng-9ffrf) — Step-by-step guide to deploying Nekaise Agent in Slack using Claude Code. *March 2026*
- [LLM API vs LLM Runtime: A Paradigm Shift in LLM Agent Development](https://www.linkedin.com/pulse/llm-api-vs-runtime-paradigm-shift-agent-development-zeng-peng-ukpcf) — Gen 1 (function calling + JSON) vs Gen 2 (LLM as runtime with filesystem and bash) approaches to building agents. *February 2026*

## Acknowledgements

OpenNekaise is forked from [NanoClaw](https://github.com/qwibitai/nanoclaw) and has since been redesigned for the built environment — with ontology-grounded reasoning, per-building isolation, and structured building data at its core. Thanks to the NanoClaw maintainers for the lightweight starting point. It is hard to say no to [pure Claude Agent SDK-based AI agents](https://platform.claude.com/docs/en/agent-sdk/overview).

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of thinking and working with LLMs.

Our ontology work builds on [Brick Schema](https://brickschema.org/) ([GitHub](https://github.com/BrickSchema/Brick)) and [Open223](https://open223.info/) ([GitHub](https://github.com/open223)). Brick is an open-source effort to standardize semantic descriptions of buildings, and Open223 supports the emerging ASHRAE 223P standard. Together they provide the vocabulary and tooling that help us describe buildings in a way that machines can reason about.

## License

MIT
