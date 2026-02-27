<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise converts buildings into Nekaise Agent that works in your Slack.
</p>

What if buildings themselves could sense that data, reason about it, and act on it, proactively, before problems become failures?

That's why we started [TwinVista](https://resurseffektivbebyggelse.se/projekt/twinvista/), a large research project at KTH funded by [Energimyndigheten](https://www.energimyndigheten.se/en/).

OpenNekaise is the open-source attribution to the world.

## Quick Start

```bash
git clone git@github.com:OpenNekaise/opennekaise.git
cd opennekaise
claude
```

Then run `/setup`.

## Building Data Design

OpenNekaise expects building data under the project `home/` directory:

- One folder per building, using the building slug as folder name (example: `home/rio-10/`)
- User data in `home/` is local by design and not tracked by git
- Only `home/.gitkeep` is versioned to keep directory structure

Isolation rule:

- Each non-main registered group gets only its matching building folder mounted in the container as `/home/<group-folder>`
- Building mounts are read-only
- The agent for one building channel cannot access other building folders

DM channels (direct messages to the bot) are treated as admin interactions:

- Auto-registered on startup with no trigger required
- Get the entire `home/` directory mounted read-write
- Can read, write, and manage data across all buildings

To make this work, register each building channel with `folder=<building-slug>`. DM channels are registered automatically.

## Core Capabilities

- Slack messaging (default channel)
- Isolated group contexts and a main admin channel
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

OpenNekaise builds on [NanoClaw](https://github.com/qwibitai/nanoclaw). Thanks to the NanoClaw maintainers and contributors for creating the lightweight, container-isolated foundation this project extends.

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of working with personal AI agents and helping move this space forward.

## License

MIT
