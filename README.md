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

## Why OpenNekaise

- Small enough to understand and modify
- Secure by container isolation, not only app-level guards
- Practical for real operations: chat-native workflows and scheduled tasks
- Open-source and community-driven

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
- `src/channels/whatsapp.ts` - channel integration
- `src/container-runner.ts` - container lifecycle and mounts
- `src/task-scheduler.ts` - recurring tasks
- `src/db.ts` - persistent state and message storage

## Upstream Credit

OpenNekaise builds on [NanoClaw](https://github.com/qwibitai/nanoclaw). Thanks to the NanoClaw maintainers and contributors for creating the lightweight, container-isolated foundation this project extends.

We also thank [OpenClaw](https://github.com/openclaw/openclaw) and its contributors for opening a new way of working with personal AI agents and helping move this space forward.

## License

MIT
