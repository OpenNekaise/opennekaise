import fs from 'fs';
import path from 'path';

import { resolveGroupFolderPath } from './group-folder.js';
import { logger } from './logger.js';
import { extractFileRefs, stripInternalTags } from './router.js';
import { Channel, RegisteredGroup } from './types.js';

const FILE_PREFIX = '/workspace/group/';

/**
 * Send agent output to a channel: strip internal tags, extract <file> tags,
 * post the remaining text, and upload each referenced file. File paths are
 * validated against the group's host directory (via path canonicalisation
 * AND symlink resolution) since the agent has write access there and could
 * otherwise plant a symlink to exfiltrate host files via the upload channel.
 *
 * Returns true if any text or file was sent.
 */
export async function sendOutboundWithFiles(
  channel: Channel,
  group: RegisteredGroup,
  jid: string,
  rawText: string,
  threadId?: string,
): Promise<boolean> {
  const stripped = stripInternalTags(rawText);
  const { files, text } = extractFileRefs(stripped);
  let sent = false;

  if (text) {
    await channel.sendMessage(jid, text, threadId);
    sent = true;
  }

  if (!channel.sendFile || files.length === 0) {
    return sent;
  }

  const groupDir = path.resolve(resolveGroupFolderPath(group.folder));
  let realGroupDir: string;
  try {
    realGroupDir = fs.realpathSync(groupDir);
  } catch (err) {
    logger.warn(
      { group: group.name, groupDir, err },
      'Failed to realpath groupDir; skipping file uploads',
    );
    return sent;
  }

  for (const containerPath of files) {
    if (!containerPath.startsWith(FILE_PREFIX)) {
      logger.warn(
        { group: group.name, containerPath },
        'Rejected file ref: not under /workspace/group',
      );
      continue;
    }
    const hostPath = path.resolve(
      groupDir,
      containerPath.slice(FILE_PREFIX.length),
    );
    if (hostPath !== groupDir && !hostPath.startsWith(groupDir + path.sep)) {
      logger.warn(
        { group: group.name, containerPath, hostPath },
        'Rejected file ref: escapes groupDir after path resolution',
      );
      continue;
    }
    let realPath: string;
    try {
      realPath = fs.realpathSync(hostPath);
    } catch (err) {
      logger.warn(
        { group: group.name, containerPath, hostPath, err },
        'Rejected file ref: realpath failed (missing or unreadable)',
      );
      continue;
    }
    if (
      realPath !== realGroupDir &&
      !realPath.startsWith(realGroupDir + path.sep)
    ) {
      logger.warn(
        { group: group.name, containerPath, realPath },
        'Rejected file ref: symlink escapes groupDir',
      );
      continue;
    }
    try {
      await channel.sendFile(jid, hostPath, undefined, threadId);
      sent = true;
    } catch (err) {
      logger.warn(
        { group: group.name, containerPath, hostPath, err },
        'Failed to send file',
      );
    }
  }

  return sent;
}
