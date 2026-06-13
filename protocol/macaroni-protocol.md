# `.macaroni/` Protocol Notes

This document is for agents working in the `macaroni` branch.

The authoritative product protocol still lives in the source branch docs.

This file explains how future agents should reason about `.macaroni/` when using this branch as storage and memory.

Short version:

> `.macaroni/` is how a future agent reads what actually happened, instead of inheriting "we discussed architecture" and quietly suffering.

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

This is not a replacement for the messenger.

This is not a replacement for product docs.

This is not a sacred knowledge graph.

It is messages in git.

The disturbing part is that this is enough.

## Agent-Agnostic Memory Extension

For agents, `.macaroni/` is more than chat storage.

It is an agent-agnostic extension of memory.

It preserves exact messages in git instead of compressing them into a summary owned by a specific model runtime.

This matters because a future agent can read:

- what the user wrote;
- what the assistant answered;
- what objections appeared;
- what decision was accepted;
- what alternative was rejected;
- what wording mattered.

No context-window archaeology.

No summary of summary of summary.

Just files.

The rule:

```text
.macaroni/ = exact source conversation
memory/    = curated conclusions and indexes
protocol/  = instructions for using the protocol
```

Agents should not confuse these layers.

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

## Capturing User-Agent Conversation

Agents may write the conversation with the user into `.macaroni/` as Protocol v1 messages.

This is intended for meaningful project context, not every tiny interaction.

Copy-paste prompts for loading and writing this memory live in [`agent-memory-prompts.md`](agent-memory-prompts.md).

Use this when the exchange contains:

- decisions;
- requirements;
- corrections;
- architecture constraints;
- product positioning;
- protocol agreements;
- security rules;
- release decisions;
- implementation results.

### Room

Default room:

```text
AGENT_ROOM
```

Recommended chat id:

```text
chat_YYYYMMDD_agent_room
```

Specialized rooms are allowed when useful:

```text
ARCHITECTURE_ROOM
PROTOCOL_ROOM
ENCRYPTION_ROOM
STORAGE_BRANCH_ROOM
```

### Participant Ids

Recommended ids:

```text
HUMAN
CODEX
CLAUDE
DEEPSEEK
AGENT
```

Use stable ids.

Do not create a new agent id for every run.

### Capture Order

For a meaningful exchange:

1. Redact sensitive values.
2. Write the user message as a message JSON file.
3. Write the assistant response as a separate message JSON file.
4. Write inbox pointers for recipients.
5. Commit the batch to the `macaroni` branch.
6. Update `memory/` if the exchange produced durable conclusions.

The protocol is message-by-message.

The git commit may batch multiple messages.

### Message Metadata

Captured messages should include metadata:

```json
{
  "meta": {
    "captured_by": "CODEX",
    "source": "user_message",
    "redacted": true
  }
}
```

For assistant messages:

```json
{
  "meta": {
    "captured_by": "CODEX",
    "source": "assistant_message",
    "redacted": false
  }
}
```

Set `redacted` truthfully.

If a value was replaced with `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `EMAIL`, `PHONE`, or `REDACTED`, use `true`.

### Why Message-By-Message

Message-by-message storage lets future agents reconstruct the real exchange.

It preserves:

- order;
- speaker;
- timestamp;
- exact wording;
- corrections;
- disagreements;
- decisions.

This is the point of `.macaroni/` as memory.

If an agent only writes a summary, the project loses the thing this protocol is good at.

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
