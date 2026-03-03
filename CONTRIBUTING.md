# Contributing

We welcome contributions from two groups: **building data providers** and **developers**.

## For Property Owners & Data Providers

If you own or manage a building and are willing to share data — energy usage, floor plans, sensor readings, maintenance logs, or any other building-related information — we'd love to hear from you.

**How to get involved:**

- Open a [GitHub Issue](../../issues) to start a discussion about the data you can provide
- Share what kind of building data you have and how it's currently structured
- Exchange ideas on what insights or features would be most valuable to you

No technical expertise required. Your real-world data and domain knowledge are what make this project useful.

## For Developers

### Source Code Changes

**Accepted:** Bug fixes, security fixes, reliability improvements, simplifications, and documentation improvements.

**Usually not accepted in core:** New capabilities, broad compatibility expansion, or feature growth. These should generally be added as skills.

### Skills

A [skill](https://code.claude.com/docs/en/skills) is a markdown file in `.claude/skills/` that teaches Claude Code how to transform an OpenNekaise installation.

- A skill PR should **not** modify any source files.
- Your skill should contain the **instructions** Claude follows to add the feature — not pre-built code. See `/add-telegram` for a good example.
- Test your skill by running it on a fresh clone before submitting.

**Why skills?** Every user should have clean and minimal core code that does exactly what they need. Skills let users selectively add capabilities without inheriting features they don't use.
