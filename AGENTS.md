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
