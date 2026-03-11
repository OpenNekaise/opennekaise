import { Channel, NewMessage } from './types.js';

export function escapeXml(s: string): string {
  if (!s) return '';
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function formatMessages(messages: NewMessage[]): string {
  const lines = messages.map(
    (m) =>
      `<message sender="${escapeXml(m.sender_name)}" time="${m.timestamp}">${escapeXml(m.content)}</message>`,
  );
  return `<messages>\n${lines.join('\n')}\n</messages>`;
}

export function stripInternalTags(text: string): string {
  return text.replace(/<internal>[\s\S]*?<\/internal>/g, '').trim();
}

/**
 * Extract <file path="..."/> or <file>...</file> tags from agent output.
 * Returns the container paths and the text with tags stripped.
 */
export function extractFileRefs(text: string): { files: string[]; text: string } {
  const files: string[] = [];
  // Match <file path="..."/> or <file path="...">...</file> or <file>/path</file>
  const stripped = text
    .replace(/<file\s+path="([^"]+)"\s*\/>/g, (_m, p) => { files.push(p); return ''; })
    .replace(/<file\s+path="([^"]+)">[^<]*<\/file>/g, (_m, p) => { files.push(p); return ''; })
    .replace(/<file>([^<]+)<\/file>/g, (_m, p) => { files.push(p.trim()); return ''; })
    .trim();
  return { files, text: stripped };
}

export function formatOutbound(rawText: string): string {
  const text = stripInternalTags(rawText);
  if (!text) return '';
  return text;
}

export function routeOutbound(
  channels: Channel[],
  jid: string,
  text: string,
): Promise<void> {
  const channel = channels.find((c) => c.ownsJid(jid) && c.isConnected());
  if (!channel) throw new Error(`No channel for JID: ${jid}`);
  return channel.sendMessage(jid, text);
}

export function findChannel(
  channels: Channel[],
  jid: string,
): Channel | undefined {
  return channels.find((c) => c.ownsJid(jid));
}
