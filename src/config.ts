import os from 'os';
import path from 'path';

import { readEnvFile } from './env.js';

// Read config values from .env (falls back to process.env).
// Secrets are NOT read here — they stay on disk and are loaded only
// where needed (container-runner.ts) to avoid leaking to child processes.
const envConfig = readEnvFile([
  'ASSISTANT_NAME',
  'ASSISTANT_HAS_OWN_NUMBER',
  'ADMIN_DM_JID',
  'ALLOWED_DM_JIDS',
  'SLACK_ONLY',
  'CLAUDE_MODEL',
]);

export const ASSISTANT_NAME =
  process.env.ASSISTANT_NAME || envConfig.ASSISTANT_NAME || 'Nekaise';
export const ASSISTANT_HAS_OWN_NUMBER =
  (process.env.ASSISTANT_HAS_OWN_NUMBER ||
    envConfig.ASSISTANT_HAS_OWN_NUMBER) === 'true';
export const ADMIN_DM_JID =
  (process.env.ADMIN_DM_JID || envConfig.ADMIN_DM_JID || '').trim();
export const ALLOWED_DM_JIDS = (
  process.env.ALLOWED_DM_JIDS ||
  envConfig.ALLOWED_DM_JIDS ||
  ''
)
  .split(',')
  .map((s) => s.trim())
  .filter((s) => s.length > 0);
export const POLL_INTERVAL = 2000;
export const SCHEDULER_POLL_INTERVAL = 60000;

// Absolute paths needed for container mounts
const PROJECT_ROOT = process.cwd();
const HOME_DIR = process.env.HOME || os.homedir();

// Mount security: allowlist stored OUTSIDE project root, never mounted into containers
export const MOUNT_ALLOWLIST_PATH = path.join(
  HOME_DIR,
  '.config',
  'opennekaise',
  'mount-allowlist.json',
);
export const STORE_DIR = path.resolve(PROJECT_ROOT, 'store');
export const GROUPS_DIR = path.resolve(PROJECT_ROOT, 'groups');
export const HOME_DATA_DIR = path.resolve(PROJECT_ROOT, 'home');
export const DATA_DIR = path.resolve(PROJECT_ROOT, 'data');
export const MAIN_GROUP_FOLDER = 'main';

// External skill repos — cloned into .opennekaise/external-skills/<repo>/
// and refreshed periodically. Each repo must have a top-level `skills/`
// directory containing skill subdirectories (each with a SKILL.md).
export const EXTERNAL_SKILLS_DIR = path.resolve(
  PROJECT_ROOT,
  '.opennekaise',
  'external-skills',
);
export const EXTERNAL_SKILL_REPOS = [
  'https://github.com/OpenNekaise/open-building-skills.git',
];
export const EXTERNAL_SKILLS_UPDATE_INTERVAL = 24 * 60 * 60 * 1000;

export const CONTAINER_IMAGE =
  process.env.CONTAINER_IMAGE || 'opennekaise:latest';
export const CONTAINER_TIMEOUT = parseInt(
  process.env.CONTAINER_TIMEOUT || '1800000',
  10,
);
export const CONTAINER_MAX_OUTPUT_SIZE = parseInt(
  process.env.CONTAINER_MAX_OUTPUT_SIZE || '10485760',
  10,
); // 10MB default
export const IPC_POLL_INTERVAL = 1000;
export const IDLE_TIMEOUT = parseInt(process.env.IDLE_TIMEOUT || '1800000', 10); // 30min default — how long to keep container alive after last result
export const MAX_CONCURRENT_CONTAINERS = Math.max(
  1,
  parseInt(process.env.MAX_CONCURRENT_CONTAINERS || '5', 10) || 5,
);

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export const TRIGGER_PATTERN = new RegExp(
  `^@${escapeRegex(ASSISTANT_NAME)}\\b`,
  'i',
);

// Timezone for scheduled tasks (cron expressions, etc.)
// Uses system timezone by default
export const TIMEZONE =
  process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone;

// Slack configuration
// SLACK_BOT_TOKEN and SLACK_APP_TOKEN are read directly by SlackChannel
// from .env via readEnvFile() to keep secrets off process.env.
export const SLACK_ONLY =
  (process.env.SLACK_ONLY || envConfig.SLACK_ONLY) === 'true';

// Claude model for the agent (e.g., claude-sonnet-4-6, claude-opus-4-6)
export const CLAUDE_MODEL =
  process.env.CLAUDE_MODEL || envConfig.CLAUDE_MODEL || undefined;
