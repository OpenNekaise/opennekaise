import { describe, expect, it } from 'vitest';

import { TRIGGER_PATTERN } from './config.js';
import { selectNextMessageBatch } from './message-batches.js';
import { NewMessage } from './types.js';

function makeMessage(overrides: Partial<NewMessage>): NewMessage {
  return {
    id: overrides.id || 'msg-1',
    chat_jid: overrides.chat_jid || 'slack:C123',
    sender: overrides.sender || 'U123',
    sender_name: overrides.sender_name || 'Alice',
    content: overrides.content || 'hello',
    timestamp: overrides.timestamp || '2024-01-01T00:00:00.000Z',
    thread_id: overrides.thread_id,
  };
}

describe('selectNextMessageBatch', () => {
  it('keeps non-threaded channels as one batch', () => {
    const batch = selectNextMessageBatch(
      [
        makeMessage({ id: 'a', chat_jid: 'group@g.us' }),
        makeMessage({ id: 'b', chat_jid: 'group@g.us' }),
      ],
      {
        threaded: false,
        needsTrigger: false,
        hasTrigger: (message) => TRIGGER_PATTERN.test(message.content.trim()),
      },
    );

    expect(batch?.messages.map((message) => message.id)).toEqual(['a', 'b']);
  });

  it('splits threaded Slack messages by thread_id', () => {
    const batch = selectNextMessageBatch(
      [
        makeMessage({
          id: 'a1',
          thread_id: 'thread-a',
          timestamp: '2024-01-01T00:00:01.000Z',
        }),
        makeMessage({
          id: 'b1',
          thread_id: 'thread-b',
          timestamp: '2024-01-01T00:00:02.000Z',
        }),
        makeMessage({
          id: 'a2',
          thread_id: 'thread-a',
          timestamp: '2024-01-01T00:00:03.000Z',
        }),
      ],
      {
        threaded: true,
        needsTrigger: false,
        hasTrigger: (message) => TRIGGER_PATTERN.test(message.content.trim()),
      },
    );

    expect(batch?.threadId).toBe('thread-a');
    expect(batch?.messages.map((message) => message.id)).toEqual(['a1', 'a2']);
  });

  it('skips earlier untriggered Slack threads when a later thread has the trigger', () => {
    const batch = selectNextMessageBatch(
      [
        makeMessage({
          id: 'a1',
          thread_id: 'thread-a',
          content: 'plain message',
        }),
        makeMessage({
          id: 'b1',
          thread_id: 'thread-b',
          content: '@Nekaise answer this',
        }),
      ],
      {
        threaded: true,
        needsTrigger: true,
        hasTrigger: (message) => TRIGGER_PATTERN.test(message.content.trim()),
      },
    );

    expect(batch?.threadId).toBe('thread-b');
    expect(batch?.messages.map((message) => message.id)).toEqual(['b1']);
  });

  it('returns null when no batch is processable yet', () => {
    const batch = selectNextMessageBatch(
      [
        makeMessage({
          id: 'a1',
          thread_id: 'thread-a',
          content: 'plain message',
        }),
      ],
      {
        threaded: true,
        needsTrigger: true,
        hasTrigger: (message) => TRIGGER_PATTERN.test(message.content.trim()),
      },
    );

    expect(batch).toBeNull();
  });
});
