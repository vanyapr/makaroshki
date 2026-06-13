# AGENTS.md

This branch is not `main`.

This branch is `macaroni`.

Treat it as long-term project memory.

## Purpose

`main` answers:

> What is the project now?

`macaroni` answers:

> How did the project become this strange?

This branch is not source code.

This branch is not the product docs branch.

This branch is not the GitHub Pages branch.

This branch is memory for future agents.

## What Agents May Write Here

Agents MAY write:

- timelines of important changes;
- architectural decisions;
- implementation notes;
- failed experiments;
- unresolved questions;
- agent-room summaries;
- links to commits, docs, release notes, and real `.macaroni/` rooms;
- short explanations of why a weird but working decision was made.

Prefer structured Markdown files.

Prefer links to sources over vague summaries.

Prefer preserving context over sounding polished.

## What Agents Must Not Write Here

Agents MUST NOT write:

- secrets;
- tokens;
- credentials;
- private keys;
- raw sensitive chat logs;
- personal data;
- temporary dumps;
- large generated files;
- anything that belongs only in `.macaroni/` as protocol message data.

If in doubt, do not store it.

If it smells like a token, it does not belong here.

## Suggested Layout

```text
README.md
AGENTS.md
memory/
  timeline.md
  decisions.md
  open-questions.md
  experiments.md
  agent-notes/
```

`.macaroni/` may later contain runtime messenger data.

`memory/` contains project memory.

Do not confuse pasta with lore.

## Before Finishing Meaningful Work

Before finishing a meaningful task, agents SHOULD update this branch when the work changes important project context:

- what changed;
- why it changed;
- what alternatives were considered;
- what remains unclear;
- what follow-up tasks appeared.

This is not documentation for humans only.

This is memory for future agents.

## Rules

- Do not rewrite this branch casually.
- Do not delete it because it looks weird.
- Do not compress useful context into a vague summary if a source link or decision note would preserve it better.
- Do not store secrets here.
- Do not turn this branch into source code.
- Do not turn this branch into a marketing page.

## Final Rule

If context is useful for future agents, preserve it.

If context is only noise, leave it in the chat where it belongs.
