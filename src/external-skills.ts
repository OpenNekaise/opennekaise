import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

import {
  EXTERNAL_SKILLS_DIR,
  EXTERNAL_SKILLS_UPDATE_INTERVAL,
  EXTERNAL_SKILL_REPOS,
} from './config.js';
import { logger } from './logger.js';

function repoName(url: string): string {
  return path.basename(url, '.git');
}

// Clone or pull each configured external skill repo. Failures are logged
// but non-fatal so the host still starts when offline — the agent just
// uses whatever is in the cache (or skips those skills entirely).
export function syncExternalSkills(): void {
  fs.mkdirSync(EXTERNAL_SKILLS_DIR, { recursive: true });
  for (const url of EXTERNAL_SKILL_REPOS) {
    const name = repoName(url);
    const dest = path.join(EXTERNAL_SKILLS_DIR, name);
    try {
      if (fs.existsSync(path.join(dest, '.git'))) {
        execFileSync('git', ['-C', dest, 'pull', '--ff-only', '--quiet'], {
          stdio: 'pipe',
        });
        logger.info({ repo: name }, 'Pulled external skills');
      } else {
        if (fs.existsSync(dest))
          fs.rmSync(dest, { recursive: true, force: true });
        execFileSync(
          'git',
          ['clone', '--depth', '1', '--quiet', url, dest],
          { stdio: 'pipe' },
        );
        logger.info({ repo: name }, 'Cloned external skills');
      }
    } catch (err) {
      logger.warn(
        { repo: name, err: (err as Error).message },
        'Failed to sync external skills — using cached version if present',
      );
    }
  }
}

export function startExternalSkillsUpdater(): NodeJS.Timeout {
  syncExternalSkills();
  const handle = setInterval(syncExternalSkills, EXTERNAL_SKILLS_UPDATE_INTERVAL);
  // Don't keep the event loop alive just for the updater
  handle.unref?.();
  return handle;
}

// Return absolute paths to every external skill directory (each containing
// a SKILL.md). Expected repo layout: <repo>/skills/<skill-name>/SKILL.md.
export function getExternalSkillDirs(): string[] {
  if (!fs.existsSync(EXTERNAL_SKILLS_DIR)) return [];
  const out: string[] = [];
  for (const repo of fs.readdirSync(EXTERNAL_SKILLS_DIR)) {
    const skillsRoot = path.join(EXTERNAL_SKILLS_DIR, repo, 'skills');
    if (!fs.existsSync(skillsRoot)) continue;
    for (const entry of fs.readdirSync(skillsRoot)) {
      const entryPath = path.join(skillsRoot, entry);
      if (!fs.statSync(entryPath).isDirectory()) continue;
      if (!fs.existsSync(path.join(entryPath, 'SKILL.md'))) continue;
      out.push(entryPath);
    }
  }
  return out;
}
