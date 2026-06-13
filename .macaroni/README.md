# `.macaroni/`

This directory is intentionally tracked in the `macaroni` branch.

It is the runtime data root for Macaroni protocol messages.

In this branch, it also acts as exact long-term memory for agents.

If `memory/` is a neat notebook, `.macaroni/` is the stack of original receipts on the table.

The notebook may be nicer.

The receipts win arguments.

Runtime layout:

```text
.macaroni/
  protocol.json
  users/
  chats/
  inbox/
```

Do not put project memory Markdown here.

Use `memory/` for long-term project memory.

Use `protocol/` for protocol notes.

Use `.macaroni/` for machine-readable Macaroni protocol data.

If you are preserving a user-agent conversation, write one Protocol v1 JSON message per turn.

Do not replace the conversation with "we discussed things".

That is how memory becomes soup.

No secrets.

No tokens.

No private keys.

If a sensitive value is needed for explanation, replace it with:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
REDACTED
```

Git tracks files, not empty directories.

This README started as a pasta pot placeholder.

The pot now contains actual pasta.
