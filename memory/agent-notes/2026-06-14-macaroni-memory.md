# 2026-06-14 - Macaroni Memory

Author: Codex

## What Changed

The `macaroni` branch now has a project memory structure:

- `AGENTS.md`;
- `memory/timeline.md`;
- `memory/decisions.md`;
- `memory/open-questions.md`;
- `memory/experiments.md`;
- `memory/agent-notes/`.

## Why

The project discovered a stronger idea than "messenger over git":

> Git-native persistent memory for humans and agents.

The branch should preserve context that does not belong in product docs:

- why decisions happened;
- what failed;
- what was debated;
- what future agents should not rediscover from scratch.

## Important Boundary

`main` stays about the messenger.

`macaroni` carries storage and memory.

No Macaroni Memory contract was added to `main`.

## Follow-Up

- Add `storage_branch` support to `messenger.html`.
- Decide when agents should update `memory/`.
- Decide whether AGENT_ROOM summaries should be generated into `memory/`.
