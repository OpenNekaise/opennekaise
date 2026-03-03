# Security Model

OpenNekaise runs AI agents inside containers. The core security idea is simple: **agents can only see and touch what we explicitly give them**.

## Who Do We Trust?

| Who | Trust Level | Why |
|-----|-------------|-----|
| Admin (main group / DM) | Trusted | You control it |
| Building channels | Untrusted | Other users could send malicious messages |
| Container agents | Sandboxed | They run in isolation, can't escape |
| Incoming messages | User input | Could contain prompt injection |

## How Agents Are Isolated

Every agent runs in a fresh container that is destroyed after each invocation. Inside the container:

- The agent runs as a non-root user
- It can only see files we explicitly mount — nothing else on the host
- It cannot modify the host application code (project root is read-only)
- Each building group gets its own session data, invisible to other groups

**This is the main security boundary.** We don't rely on the agent "behaving well" — we limit what it can access in the first place.

## What Gets Mounted (and What Doesn't)

**Mounted into containers:**
- The group's own building folder (read-write)
- Global memory file (read-only for non-main groups)
- IPC directory (for sending messages back)
- Claude auth tokens (so the agent can authenticate)

**Never mounted:**
- Other groups' data
- SSH keys, AWS/Azure/GCP credentials, `.env` files, private keys
- The mount allowlist config itself
- Chat session auth tokens

### Additional Mounts

If you need to give agents access to extra directories, you configure an allowlist at `~/.config/opennekaise/mount-allowlist.json`. This file lives outside the project so agents can never modify it.

The allowlist lets you:
- Define which host directories are allowed
- Block sensitive path patterns (`.ssh`, `credentials`, etc. are blocked by default)
- Force non-main groups to read-only access

Symlinks are resolved before validation to prevent path traversal.

## What Admin vs Building Agents Can Do

| Action | Admin | Building Agent |
|--------|-------|----------------|
| Send message to own chat | Yes | Yes |
| Send message to other chats | Yes | No |
| Schedule tasks for self | Yes | Yes |
| Schedule tasks for others | Yes | No |
| See all tasks | Yes | Own only |
| Access project root | Read-only | No |

## Known Limitation

Claude auth tokens are mounted so the agent can call the Claude API. This means the agent could theoretically read these credentials. Ideally the SDK would handle auth without exposing tokens to the execution environment. If you have ideas for solving this, PRs are welcome.

## Architecture Overview

```
  Incoming messages (untrusted)
          │
          ▼
  ┌─────────────────────────┐
  │     Host Process         │  Trusted: routes messages,
  │                          │  validates mounts, manages
  │  • Message routing       │  containers, filters credentials
  │  • Mount validation      │
  │  • Container lifecycle   │
  └──────────┬──────────────┘
             │ only explicit mounts
             ▼
  ┌─────────────────────────┐
  │     Container            │  Sandboxed: runs agent,
  │                          │  can only access mounted
  │  • Agent execution       │  files, destroyed after use
  │  • File ops (mounts only)│
  │  • Network access        │
  └─────────────────────────┘
```
