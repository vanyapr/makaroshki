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

- `memory/timeline.md`;
- `memory/decisions.md`;
- `memory/open-questions.md`;
- `memory/experiments.md`;
- `memory/agent-native-knowledge-layer.md`;
- `memory/agent-notes/*.md`.

The protocol notes layer contains:

- `protocol/macaroni-protocol.md`.

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
