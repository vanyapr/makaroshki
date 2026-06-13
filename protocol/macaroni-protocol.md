# `.macaroni/` Protocol Notes

This document is for agents working in the `macaroni` branch.

The authoritative product protocol still lives in the source branch docs.

This file explains how future agents should reason about `.macaroni/` when using this branch as storage and memory.

## Core Idea

`.macaroni/` is a git-native message store.

The protocol is intentionally boring:

- JSON files;
- predictable paths;
- append-friendly writes;
- git history as source of truth;
- browser storage as cache;
- no backend-owned database.

The transport may be GitHub API, GitLab API, GitVerse API, generic git HTTP, a wrapper, or something else.

The stored shape remains `.macaroni/`.

## Directory Layout

```text
.macaroni/
  protocol.json
  users/
    <client_id>.json
  chats/
    <chat_id>/
      meta.json
      members.json
      messages/
        YYYY/
          MM/
            DD/
              <message_id>.json
      receipts/
        <client_id>/
          YYYY/
            MM/
              DD/
                <receipt_id>.json
  inbox/
    <client_id>/
      <message_id>.json
```

## Repository Document

Path:

```text
.macaroni/protocol.json
```

Purpose:

- declares protocol version;
- identifies repository-level metadata;
- gives clients a cheap sanity check that this repository speaks Macaroni.

## Users

Path:

```text
.macaroni/users/<client_id>.json
```

Purpose:

- stores a client/user identity;
- maps short ids like `SA6E`, `K2XM`, `AG01` to display names;
- does not authenticate anything by itself.

A Macaroni user is intentionally simple:

```text
client id + display name + git access
```

No registration ceremony.

No user table in a sacred database.

## Chats

Metadata:

```text
.macaroni/chats/<chat_id>/meta.json
```

Members:

```text
.macaroni/chats/<chat_id>/members.json
```

Messages:

```text
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Receipts:

```text
.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
```

Chat metadata describes the room.

Members describe expected participants.

Messages are the source of chat history.

Receipts are append-only events.

## Inbox

Path:

```text
.macaroni/inbox/<client_id>/<message_id>.json
```

Purpose:

- helps clients discover messages addressed to them;
- points to message files;
- is not the source of message truth.

If inbox and message history disagree, message history wins.

Git remembers, inbox helps.

## Message Rules

Messages are JSON documents.

Expected properties include:

- `version`;
- `id`;
- `chat_id`;
- `type`;
- `from`;
- `from_name`;
- `to`;
- `created_at`;
- `text`;
- `reply_to`;
- `attachments`;
- `meta`;
- `signature`.

Agents should preserve unknown fields.

Agents should not rewrite old message files.

Agents should append new files.

## Encryption

Encryption is a plugin layer.

It does not change `.macaroni/` protocol paths.

Encrypted text appears as:

```text
MACARONI1.01:<base64-json>
```

Agents MUST NOT store encryption secrets in this branch.

Agents MAY document that encryption exists.

Agents MUST NOT paste keys, salts, tokens, or private material into memory files.

Use markers:

```text
СЕКРЕТ
ПАРОЛЬ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
REDACTED
```

## Storage Branch

Recommended storage branch:

```text
macaroni
```

Not:

```text
.macaroni
```

Git does not accept `.macaroni` as a branch name.

The branch is `macaroni`.

The directory is `.macaroni/`.

This is the kind of technical comedy the project accepts.

## Agent Workflow

When reading `.macaroni/`:

1. Check out or fetch the storage branch.
2. Read `.macaroni/protocol.json`.
3. Read users and chat metadata.
4. Read messages in chronological path order.
5. Treat receipts and inbox files as helper state.
6. Preserve encrypted payloads unless local decrypt settings are legitimately available.

When writing `.macaroni/`:

1. Write only machine-readable JSON.
2. Append new files instead of editing old history.
3. Use stable ids.
4. Keep message paths deterministic by UTC date.
5. Update inbox pointers for recipients.
6. Add receipts as separate append-only files.
7. Commit to the storage branch.

When documenting project reasoning:

Use `memory/`, not `.macaroni/`.

When documenting protocol behavior:

Use `protocol/`, not `.macaroni/`.

When sending actual messages:

Use `.macaroni/`, not `memory/`.

## Safety Rule

Before committing to this branch, scan for secrets.

If a useful note contains sensitive data, replace the sensitive value:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
EMAIL
PHONE
REDACTED
```

Memory that leaks secrets is not memory.

It is an incident.
