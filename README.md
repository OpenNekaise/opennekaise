<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise converts buildings into Nekaise Agent that works in your Slack.
</p>

What if buildings themselves could sense that data, reason about it, and act on it, proactively, before problems become failures?

That's why we started [TwinVista](https://resurseffektivbebyggelse.se/projekt/twinvista/), a large research project at KTH funded by [Energimyndigheten](https://www.energimyndigheten.se/en/).

OpenNekaise is our open-source contribution back to the community.

## Nekaise Agent Philosophy

OpenNekaise creates AI agents that are grounded in ontology — structured, formal representations of building knowledge.

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

This opens Claude Code. Then run `/setup` inside it.

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

## Agent Memory and Context

Each agent container receives context from up to two CLAUDE.md files depending on channel type:

| Channel type | Context sources |
|---|---|
| Building channel (non-DM) | `groups/global/CLAUDE.md` + `groups/<folder>/CLAUDE.md` |
| DM / admin | `groups/main/CLAUDE.md` only |

**`groups/global/CLAUDE.md`** — shared baseline for all building agents. Put things that apply to every building here: sensor conventions, reporting formats, domain knowledge. Loaded by the agent runner and appended to the system prompt.

**`groups/<folder>/CLAUDE.md`** — per-building memory. Not created at registration — it starts empty and grows as the agent accumulates building-specific knowledge. Loaded automatically by the Claude Code SDK because it is the container working directory. The agent can write to it directly.

**`groups/main/CLAUDE.md`** — admin context. Used only by DM/admin channels. Does not receive the global context.

## Core Capabilities

- Slack messaging (default channel)
- Isolated per-building group contexts with DM channels as admin access
- Scheduled tasks and outbound notifications
- Web fetch/research support
- Docker (macOS/Linux) and Apple Container (macOS)
- Skill-based extensions for channels/integrations

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

OpenNekaise builds on [NanoClaw](https://github.com/qwibitai/nanoclaw). Thanks to the NanoClaw maintainers and contributors for the lightweight foundation this project extends.

It is hard to say no to [pure Claude Agent SDK-based AI agents](https://platform.claude.com/docs/en/agent-sdk/overview).

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of thinking and working with LLMs.

## License

MIT
