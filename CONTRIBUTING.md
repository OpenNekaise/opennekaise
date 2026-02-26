# Contributing

## Source Code Changes

**Accepted:** Bug fixes, security fixes, reliability improvements, simplifications, and documentation improvements.

**Usually not accepted in core:** New capabilities, broad compatibility expansion, or feature growth. These should generally be skills.

## Skills

A [skill](https://code.claude.com/docs/en/skills) is a markdown file in `.claude/skills/` that teaches Claude Code how to transform an OpenNekaise installation.

A PR that contributes a skill should not modify any source files.

Your skill should contain the **instructions** Claude follows to add the feature—not pre-built code. See `/add-telegram` for a good example.

### Why?

Every user should have clean and minimal core code that does exactly what they need. Skills let users selectively add capabilities to their fork without inheriting features they do not use.

### Testing

Test your skill by running it on a fresh clone before submitting.
