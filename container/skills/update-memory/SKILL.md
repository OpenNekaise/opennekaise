---
name: update-memory
description: Process recent conversation messages into structured long-term memory. Triggered automatically after conversations end, or by a daily scheduled sweep. Extracts key facts and updates memory.md.
---

# Update Memory

## Purpose

Distill raw conversation messages into structured memory that persists across sessions. You decide what is worth remembering. Be selective — only keep information that would be useful in future conversations.

## Steps

1. Read existing memory (if any):
   ```bash
   cat /workspace/group/memory.md 2>/dev/null || echo "No existing memory."
   ```

2. Get the conversation to process:
   - If you already have a conversation in context (auto-trigger after a chat), use that.
   - If running as a scheduled task, read the messages history file:
     ```bash
     cat /workspace/ipc/messages_history.json 2>/dev/null || echo "[]"
     ```
   - If both are empty, skip — nothing to process.

3. Extract only:
   - **Building facts**: sensor values, equipment specs, configurations discovered
   - **Decisions made**: what was agreed, what was rejected, and why
   - **User preferences**: how they want information presented, what they care about
   - **Open issues**: unresolved problems, pending investigations
   - **Corrections**: things you got wrong and the verified correct answer

4. Merge with existing memory:
   - Update entries that have new information
   - If a newer correction contradicts an older memory entry, rewrite or remove the old entry so memory reflects the latest verified understanding
   - Remove entries that are no longer relevant
   - Do not duplicate what already exists
   - Keep the file concise — under 200 lines

5. Write the updated memory:
   ```bash
   cat > /workspace/group/memory.md << 'MEMORY_EOF'
   # Memory
   [your structured content here]
   MEMORY_EOF
   ```

## Output format for memory.md

Use this structure:

```markdown
# Memory

Last updated: [date]

## Building Facts
- [concrete facts discovered from data or conversation]

## Decisions
- [date]: [what was decided and why]

## User Preferences
- [communication and content preferences]

## Open Issues
- [unresolved items that need follow-up]

## Corrections
- [things previously stated wrong, with the correct answer]
```

## Rules

- Be ruthless about what to keep. If it won't help a future conversation, drop it.
- Never store raw message text. Always distill into concise facts.
- Prefer specific values over vague summaries ("COP was 3.2 on March 10" not "COP was discussed").
- When updating, preserve existing valid entries. Only modify what changed.
- Memory is not append-only. Later verified corrections should replace outdated entries.
- After writing memory.md, wrap your entire response in `<internal>` tags so it is not sent to the user. Include a brief note of what was added/changed for logging purposes only.
