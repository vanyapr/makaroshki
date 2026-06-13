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

## Macaroni As Agent-Agnostic Memory

The `.macaroni/` protocol is an agent-agnostic memory extension.

It does not belong to Codex.

It does not belong to Claude.

It does not belong to DeepSeek.

It does not belong to a model provider, IDE, SaaS memory feature, vector database, or context-window summarizer.

It belongs to git.

Any future agent that can read files, write JSON, and use git can use it.

Compressed context says:

```text
The user and assistant discussed architecture.
```

`.macaroni/` can preserve:

```text
User wrote exactly this.
Assistant answered exactly that.
This decision was made after these objections.
This implementation was rejected for this reason.
```

This is the central point:

> `.macaroni/` allows agents to remember exact conversation history instead of inheriting a lossy summary.

Summaries are allowed as indexes.

Summaries are not a replacement for source messages.

The raw conversation lives in `.macaroni/`.

Curated conclusions live in `memory/`.

Protocol explanations live in `protocol/`.

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

## Secret And Sensitive Data Handling

Agents MUST inspect changes before committing to this branch.

Run a secret-oriented scan over staged changes and new files. At minimum, look for:

- `github_pat_`;
- `ghp_`;
- `gho_`;
- `ghu_`;
- `ghs_`;
- `Authorization`;
- `Bearer `;
- `token`;
- `password`;
- `passwd`;
- `secret`;
- `private key`;
- `BEGIN RSA PRIVATE KEY`;
- `BEGIN OPENSSH PRIVATE KEY`;
- `BEGIN PGP PRIVATE KEY`;
- email addresses;
- phone numbers;
- API keys;
- access keys;
- cookies;
- session ids.

If sensitive text is useful as context, redact it before writing.

Do not preserve the original value.

Use explicit replacement markers:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
EMAIL
PHONE
COOKIE
SESSION
REDACTED
```

Examples:

```text
GitHub token was set to ТОКЕН and failed with Contents: Read-only.
The portable file may contain СЕКРЕТ and salt.
The user pasted EMAIL in the conversation; it was removed from memory.
```

Bad:

```text
The token starts with ТОКЕН.
The password was ПАРОЛЬ.
The private key was pasted here as PRIVATE_KEY.
```

Never store "partial" secrets.

Never store "first 6 and last 4" secrets.

Never store screenshots or logs if they contain secrets.

If a secret was already written, stop and fix the branch before continuing. Prefer a normal corrective commit if the branch was not pushed. If it was pushed and the secret is real, rotate the secret and rewrite branch history if needed.

This branch is memory, not evidence preservation.

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
protocol/
```

`.macaroni/` may later contain runtime messenger data.

`memory/` contains project memory.

`protocol/` contains protocol notes for agents.

Do not confuse pasta with lore.

## `.macaroni/` Protocol Overview

`.macaroni/` is the runtime data protocol used by Macaroni Messenger.

It is git-host agnostic.

It is append-friendly.

It is JSON files in a git repository.

Expected layout:

```text
.macaroni/
  protocol.json
  users/<client_id>.json
  chats/<chat_id>/meta.json
  chats/<chat_id>/members.json
  chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
  chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
  inbox/<client_id>/<message_id>.json
```

Core documents:

- `protocol.json` declares protocol version and repository-level metadata.
- `users/<client_id>.json` describes a user/client identity.
- `chats/<chat_id>/meta.json` describes the chat.
- `chats/<chat_id>/members.json` lists chat members.
- `messages/.../<message_id>.json` stores one message document.
- `receipts/.../<receipt_id>.json` stores append-only read receipts.
- `inbox/<client_id>/<message_id>.json` stores delivery pointers for clients.

Message documents are Protocol v1 JSON.

Encryption, when enabled, does not change the protocol. It only transforms `message.text` into a marker such as:

```text
MACARONI1.01:<base64-json>
```

Agents reading `.macaroni/` MUST treat encrypted text as encrypted text unless they explicitly have a legitimate local plugin configuration and secret.

Agents MUST NOT store encryption secrets in this branch.

## How Agents Should Work With `.macaroni/`

When reading:

1. Read `.macaroni/protocol.json`.
2. Read users, chat metadata, and members.
3. Read message JSON files in chronological order.
4. Use `inbox/` only as delivery pointers, not as the source of message truth.
5. Treat git history as part of the context.

When writing:

1. Prefer append-only files.
2. Create new message/receipt ids; do not overwrite existing message files.
3. Write to the configured storage branch, normally `macaroni`.
4. Keep `.macaroni/` machine-readable.
5. Do not place project-memory Markdown inside `.macaroni/`.
6. Do not place `.macaroni/` runtime JSON inside `memory/`.

When documenting `.macaroni/` behavior for future agents, use `protocol/`.

When preserving reasoning, use `memory/`.

When sending actual messages, use `.macaroni/`.

If you are unsure which one to use, do not guess. Add an item to `memory/open-questions.md`.

## Conversation Capture Protocol

Agents SHOULD preserve meaningful conversation with the user as `.macaroni/` messages, message by message.

The goal is not to dump noise.

The goal is to preserve exact project-relevant context before it degrades into summary soup.

### Default Room

Use or create a chat with a clear purpose:

```text
AGENT_ROOM
```

Recommended chat id shape:

```text
chat_YYYYMMDD_agent_room
```

If a more specific room exists, use it:

```text
ARCHITECTURE_ROOM
ENCRYPTION_ROOM
STORAGE_BRANCH_ROOM
RELEASE_ROOM
```

Do not create a new room for every tiny exchange.

### Required Setup

Before writing conversation messages, ensure these files exist:

```text
.macaroni/protocol.json
.macaroni/users/<human_id>.json
.macaroni/users/<agent_id>.json
.macaroni/chats/<chat_id>/meta.json
.macaroni/chats/<chat_id>/members.json
```

Suggested ids:

```text
HUMAN
CODEX
CLAUDE
DEEPSEEK
AGENT
```

Use a more specific id when known.

Keep ids stable.

Do not invent a new identity every run unless the agent is intentionally acting as a new participant.

### What To Capture

Capture user messages when they contain:

- project direction;
- architecture decisions;
- rejected alternatives;
- constraints;
- protocol agreements;
- security rules;
- release decisions;
- product positioning;
- implementation instructions;
- important corrections to agent behavior.

Capture assistant messages when they contain:

- accepted implementation decisions;
- concrete plans;
- explanations that future agents need;
- tradeoffs;
- final results;
- links to commits/docs/releases;
- follow-up tasks.

Do not capture:

- trivial acknowledgements;
- repeated status pings;
- tool noise;
- raw command output unless it matters;
- secrets;
- personal data;
- content the user clearly did not intend to preserve.

### Redact Before Write

Before writing any user or assistant message to `.macaroni/`, inspect it for secrets and sensitive data.

Redact sensitive values before the message file is created.

Use markers:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
EMAIL
PHONE
COOKIE
SESSION
REDACTED
```

The `.macaroni/` memory should preserve that a secret existed, not the secret itself.

Good:

```text
User provided ТОКЕН and said it has Contents: Read and write.
```

Bad:

```text
User provided github_pat_...
```

### Message File Path

Store every captured message as its own JSON file:

```text
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Use UTC dates for paths.

Use stable ids:

```text
YYYY-MM-DDTHH-mm-ss.sssZ_<from>_<short_suffix>
```

Example:

```text
2026-06-14T12-30-15.123Z_CODEX_a8k2md
```

### Message Document Shape

Use Protocol v1 message JSON:

```json
{
  "version": 1,
  "id": "2026-06-14T12-30-15.123Z_CODEX_a8k2md",
  "chat_id": "chat_20260614_agent_room",
  "type": "text",
  "from": "CODEX",
  "from_name": "Codex",
  "to": ["HUMAN"],
  "created_at": "2026-06-14T12:30:15.123Z",
  "text": "Message text after redaction.",
  "reply_to": null,
  "attachments": [],
  "meta": {
    "captured_by": "CODEX",
    "source": "agent_conversation",
    "redacted": true
  },
  "signature": null
}
```

For user messages:

```json
{
  "from": "HUMAN",
  "from_name": "Human",
  "to": ["CODEX"],
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
  "from": "CODEX",
  "from_name": "Codex",
  "to": ["HUMAN"],
  "meta": {
    "captured_by": "CODEX",
    "source": "assistant_message",
    "redacted": false
  }
}
```

Set `redacted` truthfully.

If anything was replaced with `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, or `REDACTED`, use `true`.

### Inbox Pointers

For every recipient, write an inbox pointer:

```text
.macaroni/inbox/<recipient_id>/<message_id>.json
```

Shape:

```json
{
  "version": 1,
  "recipient": "HUMAN",
  "message_id": "2026-06-14T12-30-15.123Z_CODEX_a8k2md",
  "chat_id": "chat_20260614_agent_room",
  "message_path": ".macaroni/chats/chat_20260614_agent_room/messages/2026/06/14/2026-06-14T12-30-15.123Z_CODEX_a8k2md.json",
  "created_at": "2026-06-14T12:30:15.123Z"
}
```

Inbox pointers are helpers.

The message file is the source of truth.

### Commit Strategy

Prefer one commit per meaningful capture batch.

For example, after a task:

```text
Macaroni memory: capture storage branch discussion
```

Do not create a separate git commit for every single chat message unless a live client naturally does that.

The protocol is message-by-message.

The git commit can batch multiple message files.

### Relationship To `memory/`

`.macaroni/` preserves exact messages.

`memory/` preserves curated interpretation.

After capturing an important discussion in `.macaroni/`, agents SHOULD update `memory/` when the discussion produced:

- a decision;
- an open question;
- an experiment;
- a timeline milestone;
- an implementation warning.

Do not replace exact `.macaroni/` messages with a summary.

Use summaries as indexes pointing back to source messages.

### Minimal Agent Workflow

For every meaningful user-agent exchange:

1. Decide whether the exchange is worth preserving.
2. Redact secrets and sensitive data.
3. Ensure user and agent documents exist.
4. Ensure an appropriate chat exists.
5. Write the user message as one Protocol v1 message.
6. Write the assistant response as another Protocol v1 message.
7. Write inbox pointers for recipients.
8. Commit to the `macaroni` branch.
9. Push the `macaroni` branch.
10. Update `memory/` if a durable decision or open question emerged.

This creates exact memory plus curated memory.

That is the point.

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
