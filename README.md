<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise converts buildings into Nekaise Agent that works in your Slack.
</p>

What if buildings themselves could sense that data, reason about it, and act on it, proactively, before problems become failures?

That's why we started [TwinVista](https://resurseffektivbebyggelse.se/projekt/twinvista/), a large research project at KTH funded by [Energimyndigheten](https://www.energimyndigheten.se/en/).

[OpenNekaise](https://opennekaise.com/) is our open-source contribution back to the community.

## Nekaise Agent Philosophy

OpenNekaise creates AI agents that are grounded in ontology — structured, formal representations of building data, information, and knowledge.

Most LLM-based agents operate on raw text and loose context. Our research at KTH shows that when you ground an agent in an ontology — defining what a building *is*, how its systems relate, and what its data *means* — the agent reasons more reliably and makes fewer hallucinated leaps.

In practice this means:

- Building data is organized by domain concepts (spaces, systems, sensors, schedules), not arbitrary file structures
- The agent understands relationships between building components, not just isolated data points
- Responses are traceable back to structured knowledge, not just pattern-matched from training data

This is an active area of research. As our ontology work matures, OpenNekaise will evolve to reflect it.

## Quick Start

```bash
git clone git@github.com:OpenNekaise/opennekaise.git
cd opennekaise
claude
```

This opens [Claude Code](https://claude.ai/code). Run `/setup` and it will walk you through everything.

After setup, you don't need to read further — just ask Claude Code any question about your deployment, configuration, or building data. It already knows the codebase.

## Sandbox, sandbox, sandbox

Every agent invocation runs inside an ephemeral Docker container that is destroyed on exit. Nothing persists except what we explicitly mount in.

**One container per group, per message.** When a building channel triggers the agent, the orchestrator spawns a fresh `docker run --rm` container with mounts scoped to that group only:

| What the agent sees | Mount | Access |
|---|---|---|
| Its own working directory | `/workspace/group` | read-write |
| Its building data | `/home/<building-folder>` | read-only |
| Shared global prompt | `/workspace/global` | read-only |
| IPC (messages, tasks) | `/workspace/ipc` | read-write |

The agent **cannot** see other buildings, other groups' working directories, or the host application code. The main/admin context gets read-only access to the project root — it still can't modify it.

**Secrets never touch disk.** API keys are passed via stdin JSON, consumed once, and deleted. A pre-tool hook strips credentials from the environment before any Bash subprocess runs.

**Additional mounts are validated** against an external allowlist (`~/.config/opennekaise/mount-allowlist.json`) that lives outside the project root — agents can't tamper with it. Blocked patterns include `.ssh`, `.aws`, `.env`, credential files, and private keys.

**Agent-runner source is recompiled at container startup** from a per-group copy that is re-synced from the canonical source on every run. No stale code survives across deployments.

## Memory, memory, memory

Memory is what turns Nekaise Agent from a tool you query into a colleague who knows your building. It accumulates corrections, remembers what was decided and why, and learns how you prefer to communicate. Over weeks and months, the agent becomes more useful — not because the model improved, but because the memory grew.

### How it works

Each group has a `memory.md` file (`groups/<folder>/memory.md`) that stores distilled facts, decisions, user preferences, and open issues — never raw messages. The agent reads it at the start of every conversation.

Memory is updated incrementally:

- **After each conversation**: the orchestrator auto-triggers the `/update-memory` skill. The agent reflects on what just happened and writes what matters to `memory.md`.
- **Daily refinement (2am)**: a scheduled sweep reads the day's messages alongside existing memory and produces a cleaner, consolidated version. Auto-created for every group.

The LLM decides what is worth keeping. The skill (`container/skills/update-memory/SKILL.md`) gives it structure and rules — be ruthless, prefer specific values over vague summaries, never store raw text.

### Context layers

| Layer | File | Purpose |
|---|---|---|
| System prompt | `groups/global/CLAUDE.md` | Shared rules for all building agents |
| Admin prompt | `groups/main/CLAUDE.md` | Admin-only context and tools |
| Per-building prompt | `groups/<folder>/CLAUDE.md` | Building-specific instructions |
| Memory | `groups/<folder>/memory.md` | Accumulated knowledge from conversations |

### Sessions

Each group maintains a Claude Code session for short-term conversational continuity. Memory is the long-term layer — it survives session clears, restarts, and prompt updates.

```bash
# Clear sessions (e.g. after updating a system prompt):
sqlite3 store/messages.db "DELETE FROM sessions;"
systemctl --user restart opennekaise
# Memory is untouched.
```

## Building Data Design

OpenNekaise expects building data under the project `home/` directory:

- One folder per building, using the building slug as folder name (example: `home/rio-10/`)
- User data in `home/` is local by design and not tracked by git
- Only `home/.gitkeep` is versioned to keep directory structure

Isolation rule:

- Each non-main registered group gets only its matching building folder mounted in the container as `/home/<group-folder>`
- Building mounts are read-only
- The agent for one building channel cannot access other building folders

DM channels (direct messages to the bot) are blocked by default and must be explicitly configured:

- Set `ADMIN_DM_JID=<your-dm-jid>` in `.env` (example: `slack:D0123456789`)
- Set `ALLOWED_DM_JIDS=<jid1>,<jid2>` to allow specific DM channels
- Only allowed DMs can be registered/processed
- Allowed DMs are restricted to `main` context (legacy `dm-*` folders are rejected)
- The admin DM follows `main` context/mount behavior

To make building mapping work, register each building channel with `folder=<building-slug>` during `/setup`.

## Core Capabilities

- Slack messaging (default channel)
- Per-building container isolation with read-only building data mounts
- Incremental structured memory that grows with every conversation
- Scheduled tasks (cron, interval, one-off) with cross-group orchestration
- Web browsing and research via agent-browser skill
- Docker container runtime (macOS/Linux)
- Extensible via custom skills (`container/skills/`)

## Architecture (Essential)

```text
Chat channel -> SQLite -> Message loop -> Containerized Claude agent -> Response
```

Single Node.js host process with per-group isolation and container execution.

Key files:
- `src/index.ts` - orchestrator and message loop
- `src/channels/slack.ts` - channel integration
- `src/container-runner.ts` - container lifecycle and mounts
- `src/task-scheduler.ts` - recurring tasks
- `src/db.ts` - persistent state and message storage

## Upstream Credit

OpenNekaise is forked from [NanoClaw](https://github.com/qwibitai/nanoclaw) and has since been redesigned for the built environment — with ontology-grounded reasoning, per-building isolation, and structured building data at its core. Thanks to the NanoClaw maintainers for the lightweight starting point. It is hard to say no to [pure Claude Agent SDK-based AI agents](https://platform.claude.com/docs/en/agent-sdk/overview).

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of thinking and working with LLMs.

## License

MIT
