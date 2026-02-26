---
name: setup
description: Run initial OpenNekaise setup. Slack-first flow: install dependencies, build container, configure Claude auth, configure Slack tokens/channel, register main channel, and start service.
---

# OpenNekaise Setup (Slack-First)

Run setup automatically. Only pause when user input is required (tokens, Slack channel ID, auth choices). Use `bash setup.sh` for bootstrap, then `npx tsx setup/index.ts --step <name>` for setup steps.

Default channel is Slack. Do not run WhatsApp auth unless the user explicitly asks for WhatsApp.

## 1. Bootstrap

Run:

```bash
bash setup.sh
```

If bootstrap fails, inspect `logs/setup.log`, fix dependencies/tooling, and re-run.

## 2. Environment Check

Run:

```bash
npx tsx setup/index.ts --step environment
```

Use this to confirm runtime prerequisites and detect existing config.

## 3. Container Runtime + Image

Choose runtime:
- Linux: Docker
- macOS: Docker by default (or Apple Container if explicitly requested)

Build and verify image:

```bash
npx tsx setup/index.ts --step container -- --runtime docker
```

If Apple Container is explicitly requested:

```bash
npx tsx setup/index.ts --step container -- --runtime apple-container
```

## 4. Claude Authentication

Ensure one auth method exists in `.env`:
- `CLAUDE_CODE_OAUTH_TOKEN=...`
- or `ANTHROPIC_API_KEY=...`

If missing, ask user which method they want and guide them to add it. Do not ask users to paste secrets in chat if avoidable.

## 5. Slack Configuration (Default Channel)

Collect or confirm:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `SLACK_ONLY=true` (default for OpenNekaise setup)

Write/update `.env` and sync to container env:

```bash
mkdir -p data/env
cp .env data/env/env
```

If user has no Slack app yet, direct them to `.claude/skills/add-slack/SLACK_SETUP.md` and continue once tokens are ready.

## 6. Register Main Slack Channel

Ask for Slack channel ID (example: `C0123456789`).

Register it as main:

```bash
npx tsx setup/index.ts --step register -- --jid "slack:C0123456789" --name "main" --trigger "@Nekaise" --folder "main" --no-trigger-required --assistant-name "Nekaise"
```

If user wants a different trigger/assistant name, use those values.

## 7. Mount Allowlist

If user does not need extra host directories:

```bash
npx tsx setup/index.ts --step mounts -- --empty
```

If they do, configure via JSON payload in `--json`.

## 8. Start Service

Run:

```bash
npx tsx setup/index.ts --step service
```

If already loaded, unload/stop old service and retry.

## 9. Verify

Run:

```bash
npx tsx setup/index.ts --step verify
```

If verify fails, fix the reported item and rerun.

## 10. Functional Check (Slack)

Tell user to post a message in registered Slack channel:
- Main channel: any message
- Non-main channel: include trigger (for example `@Nekaise`)

Logs:

```bash
tail -f logs/opennekaise-agent.log
```

## Optional: WhatsApp (Only if explicitly requested)

If the user asks to enable WhatsApp, then run:

```bash
npx tsx setup/index.ts --step whatsapp-auth -- --method pairing-code --phone <number>
```

Or QR methods, then register WhatsApp JIDs with `setup/register`.
