---
name: setup
description: Run initial OpenNekaise setup. Slack-first flow: install dependencies, build container, configure Claude auth, configure Slack tokens/channel, configure admin DM, register main context on that DM, and start service.
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

## 4b. Claude Model Selection

Ask the user which Claude model to use for the agent. Present the options:

| Model | ID | Notes |
|-------|-----|-------|
| Claude Opus 4.6 | `claude-opus-4-6` | Most capable, higher cost |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Balanced performance and cost |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Fastest, lowest cost |

Default: `claude-sonnet-4-6` (SDK default if not set).

Write the chosen model to `.env`:

```
CLAUDE_MODEL=claude-opus-4-6
```

Then sync to container env:

```bash
cp .env data/env/env
```

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

## 6. Configure Admin DM (Required for DM Access)

Ask for Slack DM channel ID (example: `D0123456789`).

Configure admin DM and DM allowlist:

```bash
npx tsx setup/index.ts --step admin-dm -- --jid "slack:D0123456789"
```

This writes:
- `ADMIN_DM_JID=slack:D0123456789`
- `ALLOWED_DM_JIDS=slack:D0123456789`

## 7. Register Main on Admin DM

Register the admin DM as `main`:

```bash
npx tsx setup/index.ts --step register -- --jid "slack:D0123456789" --name "admin-dm" --trigger "@Nekaise" --folder "main" --no-trigger-required --assistant-name "Nekaise"
```

If user wants a different trigger/assistant name, use those values.

## 8. Mount Allowlist

If user does not need extra host directories:

```bash
npx tsx setup/index.ts --step mounts -- --empty
```

If they do, configure via JSON payload in `--json`.

## 9. Start Service

Run:

```bash
npx tsx setup/index.ts --step service
```

If already loaded, unload/stop old service and retry.

## 10. Verify

Run:

```bash
npx tsx setup/index.ts --step verify
```

If verify fails, fix the reported item and rerun.

## 11. Functional Check (Slack)

Tell user to post a message in the admin DM (`slack:D...`) and in any registered building channel:
- Admin DM (`main`): any message
- Non-main channel: include trigger if required (for example `@Nekaise`)

Logs:

```bash
tail -f logs/opennekaise.log
```

## Optional: WhatsApp (Only if explicitly requested)

If the user asks to enable WhatsApp, then run:

```bash
npx tsx setup/index.ts --step whatsapp-auth -- --method pairing-code --phone <number>
```

Or QR methods, then register WhatsApp JIDs with `setup/register`.
