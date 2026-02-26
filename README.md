<p align="center">
  <img src="assets/nekaise-icon.png" alt="Nekaise Agent" width="240">
</p>

<p align="center">
  OpenNekaise ships Nekaise Agent, an open-source AI teammate for building energy operations.
</p>

Buildings consume 40% of the world's energy. Every optimization matters.

Buildings are drowning in data: sensors, meters, controllers, alarms, and scattered documentation.

Too much for humans to process continuously in real time.

What if buildings could sense that data, reason about it, and act before problems become failures?

That is the goal behind [TwinVista](https://resurseffektivbebyggelse.se/projekt/twinvista/), a large research project at KTH funded by [Energimyndigheten](https://www.energimyndigheten.se/en/).
OpenNekaise is the open-source workstream. Nekaise Agent is what we ship into real building teams.

Nekaise Agent works in the channels teams already use and is designed to be extended through skills.

## Quick Start

```bash
git clone https://github.com/<your-org>/opennekaise.git
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

- WhatsApp messaging (default channel)
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

## Customizing

OpenNekaise is built to be forked and adapted:

- Change trigger, persona, and routing behavior in code
- Add channels/integrations via skills (`/add-slack`, `/add-telegram`, `/add-discord`, `/add-gmail`)

Use `/customize` for guided changes.

## Upstream Credit

OpenNekaise builds on [NanoClaw](https://github.com/qwibitai/nanoclaw). Thanks to the NanoClaw maintainers and contributors for creating the lightweight, container-isolated foundation this project extends.

## License

MIT
