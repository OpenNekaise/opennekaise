import { NewMessage } from './types.js';

export interface MessageBatch {
  messages: NewMessage[];
  threadId?: string;
}

interface SelectMessageBatchOpts {
  threaded: boolean;
  needsTrigger: boolean;
  hasTrigger: (message: NewMessage) => boolean;
}

export function selectNextMessageBatch(
  messages: NewMessage[],
  opts: SelectMessageBatchOpts,
): MessageBatch | null {
  if (messages.length === 0) return null;

  if (!opts.threaded) {
    if (opts.needsTrigger && !messages.some(opts.hasTrigger)) return null;
    return {
      messages,
      threadId: messages[messages.length - 1].thread_id,
    };
  }

  const batches: MessageBatch[] = [];
  const batchesByThread = new Map<string, MessageBatch>();

  for (const message of messages) {
    const threadId = message.thread_id || message.id;
    let batch = batchesByThread.get(threadId);
    if (!batch) {
      batch = { messages: [], threadId };
      batchesByThread.set(threadId, batch);
      batches.push(batch);
    }
    batch.messages.push(message);
  }

  if (!opts.needsTrigger) return batches[0] || null;

  return batches.find((batch) => batch.messages.some(opts.hasTrigger)) || null;
}
