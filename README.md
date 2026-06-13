# Macaroni Storage Branch

This branch is intentionally almost empty.

It is not the application branch.

It is not the documentation branch.

It is not the GitHub Pages branch.

It is the future storage branch for Macaroni data.

It is also the project memory branch.

The app lives on `main`.

The pasta lives here.

The hidden lore lives here too.

## Purpose

Macaroni Messenger can use a separate git branch for `.macaroni/` data, so chat history does not pollute the source branch.

The source branch contains:

- `messenger.html`;
- docs;
- release notes;
- screenshots;
- project metadata.

The storage branch contains:

- `.macaroni/protocol.json`;
- `.macaroni/users/*.json`;
- `.macaroni/chats/*/meta.json`;
- `.macaroni/chats/*/members.json`;
- `.macaroni/chats/*/messages/YYYY/MM/DD/*.json`;
- `.macaroni/chats/*/receipts/*/YYYY/MM/DD/*.json`;
- `.macaroni/inbox/*/*.json`.

The memory layer contains:

- [`memory/timeline.md`](memory/timeline.md) `agent-generated`;
- [`memory/decisions.md`](memory/decisions.md) `agent-generated`;
- [`memory/open-questions.md`](memory/open-questions.md) `agent-generated`;
- [`memory/experiments.md`](memory/experiments.md) `agent-generated`;
- [`memory/agent-native-knowledge-layer.md`](memory/agent-native-knowledge-layer.md) `agent-generated`;
- [`memory/agent-notes/*.md`](memory/agent-notes/) `agent-generated`.

The protocol notes layer contains:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `agent-generated`.
- [`protocol/agent-memory-prompts.md`](protocol/agent-memory-prompts.md) `agent-generated`.

The Codex skill layer contains:

- [`skills/macaroni-memory/SKILL.md`](skills/macaroni-memory/SKILL.md) `agent-generated`;
- [`skills/macaroni-memory/scripts/write_messages.py`](skills/macaroni-memory/scripts/write_messages.py) `agent-generated`;
- [`skills/macaroni-memory/agents/openai.yaml`](skills/macaroni-memory/agents/openai.yaml) `agent-generated`.

Russian documentation mirrors:

- [`README.ru.md`](README.ru.md) `agent-generated`;
- [`AGENTS.ru.md`](AGENTS.ru.md) `agent-generated`;
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `agent-generated`;
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `agent-generated`;
- [`protocol/agent-memory-prompts.ru.md`](protocol/agent-memory-prompts.ru.md) `agent-generated`;
- [`memory/timeline.ru.md`](memory/timeline.ru.md) `agent-generated`;
- [`memory/decisions.ru.md`](memory/decisions.ru.md) `agent-generated`;
- [`memory/open-questions.ru.md`](memory/open-questions.ru.md) `agent-generated`;
- [`memory/experiments.ru.md`](memory/experiments.ru.md) `agent-generated`;
- [`memory/agent-native-knowledge-layer.ru.md`](memory/agent-native-knowledge-layer.ru.md) `agent-generated`;
- [`memory/agent-notes/2026-06-14-macaroni-memory.ru.md`](memory/agent-notes/2026-06-14-macaroni-memory.ru.md) `agent-generated`.

## Document Map

Core branch documents:

- [`README.md`](README.md) - this branch index.
- [`README.ru.md`](README.ru.md) `agent-generated` - Russian mirror of this branch index.
- [`AGENTS.md`](AGENTS.md) - operating rules for future agents.
- [`AGENTS.ru.md`](AGENTS.ru.md) `agent-generated` - Russian mirror of the agent rules.
- [`.macaroni/README.md`](.macaroni/README.md) - placeholder and safety note for the runtime data root.
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `agent-generated` - Russian mirror of the runtime data root note.

Protocol documents:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `agent-generated` - how agents should read and write `.macaroni/`.
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `agent-generated` - Russian mirror.
- [`protocol/agent-memory-prompts.md`](protocol/agent-memory-prompts.md) `agent-generated` - copy-paste prompts for loading and writing Macaroni memory.
- [`protocol/agent-memory-prompts.ru.md`](protocol/agent-memory-prompts.ru.md) `agent-generated` - Russian mirror.

Codex skill:

- [`skills/macaroni-memory/SKILL.md`](skills/macaroni-memory/SKILL.md) `agent-generated` - installable Codex skill for `.macaroni` extended memory.
- [`skills/macaroni-memory/scripts/write_messages.py`](skills/macaroni-memory/scripts/write_messages.py) `agent-generated` - helper that writes Protocol v1 message JSON and inbox pointers.
- [`skills/macaroni-memory/agents/openai.yaml`](skills/macaroni-memory/agents/openai.yaml) `agent-generated` - skill UI metadata.

Curated memory indexes:

- [`memory/timeline.md`](memory/timeline.md) `agent-generated` - project memory timeline.
- [`memory/timeline.ru.md`](memory/timeline.ru.md) `agent-generated` - Russian mirror.
- [`memory/decisions.md`](memory/decisions.md) `agent-generated` - durable decisions and reasoning.
- [`memory/decisions.ru.md`](memory/decisions.ru.md) `agent-generated` - Russian mirror.
- [`memory/open-questions.md`](memory/open-questions.md) `agent-generated` - unresolved questions.
- [`memory/open-questions.ru.md`](memory/open-questions.ru.md) `agent-generated` - Russian mirror.
- [`memory/experiments.md`](memory/experiments.md) `agent-generated` - experiments worth remembering.
- [`memory/experiments.ru.md`](memory/experiments.ru.md) `agent-generated` - Russian mirror.
- [`memory/agent-native-knowledge-layer.md`](memory/agent-native-knowledge-layer.md) `agent-generated` - the agent-native memory hypothesis.
- [`memory/agent-native-knowledge-layer.ru.md`](memory/agent-native-knowledge-layer.ru.md) `agent-generated` - Russian mirror.
- [`memory/agent-notes/2026-06-14-macaroni-memory.md`](memory/agent-notes/2026-06-14-macaroni-memory.md) `agent-generated` - first agent note for the branch.
- [`memory/agent-notes/2026-06-14-macaroni-memory.ru.md`](memory/agent-notes/2026-06-14-macaroni-memory.ru.md) `agent-generated` - Russian mirror.

`agent-generated` means the link points to a document created or maintained by agents as project memory. Treat those files as useful indexes and notes, not as a replacement for canonical `.macaroni/` messages or the source branch protocol docs.

That is all.

No frontend.

No README-driven product marketing.

No build system.

No backend trying to sneak in through the window.

`.macaroni/` is runtime protocol data.

`memory/` is long-term project memory for future people and agents.

`protocol/` is the agent-facing explanation of how to work with `.macaroni/`.

Do not mix them just because both are funny.

## Branch Name

The branch is named:

```text
macaroni
```

The branch is not named:

```text
.macaroni
```

Git does not accept `.macaroni` as a valid branch name.

So the directory is `.macaroni/`, but the branch is `macaroni`.

This is annoying.

It is also fine.

## Target Profile Shape

Future client profiles should distinguish the source branch from the storage branch:

```json
{
  "repo": "https://github.com/vanyapr/makaroshki",
  "branch": "main",
  "storage_branch": "macaroni"
}
```

`branch` is where the app/source/docs live.

`storage_branch` is where `.macaroni/` lives.

Old profiles without `storage_branch` must continue to work by using the existing configured branch, usually `main`.

Backward compatibility first.

Comedy second.

Still comedy.

## Implementation Plan

1. Add `storage_branch` to Settings.
2. Default new profiles to `macaroni`.
3. Keep old profiles on their current branch until the user changes settings.
4. Teach GitHub provider reads to use `storage_branch` for `.macaroni/` paths.
5. Teach GitHub provider writes to commit `.macaroni/` files to `storage_branch`.
6. Teach reindex to store branch-specific metadata, so `main` and `macaroni` do not share stale commit SHA state.
7. Add branch existence detection.
8. If `storage_branch` does not exist, create it from the default branch for the first MVP.
9. After creation, write only `.macaroni/` data here.
10. Later, add an advanced action that creates a clean orphan storage branch with only `.macaroni/`.

The clean orphan branch is nicer.

The MVP branch is easier.

Macaroni prefers working pasta over architectural perfume.

## Provider Contract

Every provider adapter must treat `.macaroni/` as storage data and must accept storage branch separately from source branch.

Required shape:

```js
{
  repo: "...",
  branch: "main",
  storage_branch: "macaroni"
}
```

Provider operations:

- app/source reads may use `branch`;
- `.macaroni/` reads use `storage_branch`;
- `.macaroni/` writes use `storage_branch`;
- read receipts use `storage_branch`;
- inbox notifications use `storage_branch`;
- chat creation uses `storage_branch`;
- user profile documents use `storage_branch`.

If a provider cannot write to a separate branch, it must say so clearly.

No silent pasta in `main`.

## Migration Notes

For existing repositories:

1. Create branch `macaroni`.
2. Move or copy existing `.macaroni/` data there.
3. Configure clients with `storage_branch: "macaroni"`.
4. Stop writing `.macaroni/` to `main`.
5. Optionally clean `main` history later, if you enjoy force-push archaeology.

Do not silently delete existing `.macaroni/` data from `main`.

Git remembers.

Users should choose when to clean history.

## Current Status

This branch currently documents the plan and starts the project memory layer.

It intentionally does not contain live chat data yet.

The next implementation step is to add `storage_branch` support to `messenger.html`.

After that, this branch becomes the recommended storage branch for real Macaroni messages.

Agents may already use `memory/` for durable context.

## Final Rule

`main` is for the messenger.

`macaroni` is for the messages.

Keep code out of pasta.

Keep pasta out of code.

Keep memory readable enough that a future agent does not need a séance.
