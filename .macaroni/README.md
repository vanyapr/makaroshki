# `.macaroni/`

This directory is intentionally tracked in the `macaroni` branch.

It is the future runtime data root for Macaroni Messenger.

Expected runtime layout:

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

This README exists so the pasta pot exists before the pasta is cooked.
