---
name: macaroni-memory
description: Use when Codex needs to read, preserve, or update long-term project memory through the `.macaroni/` protocol in a git repository: capturing user-agent conversations message-by-message, reading AGENT_ROOM history, writing Protocol v1 JSON messages, creating inbox pointers, redacting secrets, treating `.macaroni/` as canonical memory and `memory/` as optional derived indexes.
---

# Macaroni Memory

Use `.macaroni/` as exact, git-native memory for project-relevant conversations.

Core model:

```text
.macaroni/ = canonical append-only conversation log
memory/    = optional curated index over .macaroni
protocol/  = protocol notes and operating instructions
```

Do not replace source messages with summaries. Summaries are indexes, not truth.

## Fast Workflow

1. Check the repository state with `git status --short --branch`.
2. If a `macaroni` branch exists, work in that branch or a temporary worktree based on it.
3. Read existing `.macaroni/protocol.json`, chat metadata, users, and relevant messages before writing.
4. Redact secrets before writing any message.
5. Write each user/assistant turn as a separate Protocol v1 JSON message under `.macaroni/`.
6. Write inbox pointers for every recipient.
7. Validate JSON and run a secret scan.
8. Commit and push only after reviewing staged files.
9. Update `memory/` only when a durable decision, question, timeline point, or experiment should be indexed.

Prefer one git commit per meaningful capture batch. The protocol is message-by-message; the git commit can batch multiple message files.

## Branch Rules

- `main` remains source/product/docs unless the repo says otherwise.
- `macaroni` is the preferred storage branch for `.macaroni/`.
- Use a separate worktree for capture work when the main checkout is on another branch.
- Do not casually rewrite the `macaroni` branch.
- Do not write project-memory Markdown inside `.macaroni/`.
- Do not write runtime `.macaroni/` JSON inside `memory/`.

## Required Layout

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

Default agent room:

```text
AGENT_ROOM
chat_YYYYMMDD_agent_room
```

Stable participant ids:

```text
HUMAN
CODEX
CLAUDE
DEEPSEEK
AGENT
```

Use stable ids. Do not invent a new agent identity every run.

## Message Shape

Write Protocol v1 message JSON:

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
    "source": "assistant_message",
    "redacted": false
  },
  "signature": null
}
```

Preserve unknown fields when editing existing documents. Prefer append-only writes.

## Redaction

Never store:

- real tokens;
- credentials;
- private keys;
- cookies;
- session ids;
- raw sensitive personal data;
- screenshots or logs containing secrets.

Replace sensitive values before writing:

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

Never store partial secrets such as first 6 and last 4 characters.

If a real secret was already written and pushed, stop normal work, rotate the secret, and fix branch history if needed.

## Helper Script

Use `scripts/write_messages.py` to write Protocol v1 files deterministically.

Single message:

```bash
python3 scripts/write_messages.py \
  --repo-root /path/to/repo \
  --from-id CODEX \
  --from-name Codex \
  --to HUMAN \
  --source assistant_message \
  --text-file /tmp/message.txt
```

Batch:

```bash
python3 scripts/write_messages.py \
  --repo-root /path/to/repo \
  --batch-json /tmp/messages.json
```

Batch JSON shape:

```json
[
  {
    "from": "HUMAN",
    "from_name": "Human",
    "to": ["CODEX"],
    "source": "user_message",
    "text": "Exact message text after redaction.",
    "redacted": false
  }
]
```

The script writes JSON files only. It does not commit or push.

## Validation

Before committing:

```bash
git diff --check
find .macaroni -name '*.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg -n --hidden --glob '!.git/**' 'github_pat_|gh[opusb]_|Authorization:\s*Bearer|BEGIN (RSA|OPENSSH|PGP) PRIVATE KEY|AKIA[0-9A-Z]{16}' .macaroni
```

Treat a secret scan hit as blocking unless it is clearly a documented placeholder or marker.

## Reading Memory

When asked to use existing Macaroni memory:

1. Read `.macaroni/protocol.json`.
2. Read chat `meta.json` and `members.json`.
3. Read messages in chronological path order.
4. Use `inbox/` as delivery hints only.
5. Use `memory/` only as an index; verify important claims against `.macaroni/` messages.

If `memory/` contradicts `.macaroni/`, prefer `.macaroni/`.
