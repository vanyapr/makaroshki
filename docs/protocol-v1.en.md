# Macaroni Protocol v1

Macaroni Protocol v1 describes which JSON files live in the git repository.

Git remains the source of truth.

IndexedDB remains a local cache and index.

If the local index breaks, it is rebuilt from these files.

## Repository Layout

Any git repository with a `.macaroni/` directory using this layout can be a Macaroni repository. The repository that serves `messenger.html` and the repository that stores messages may be the same repository or different repositories.

Chats can be attached to any git repository as long as the client can read and write Macaroni Protocol files there and the user has the required repository permissions.

All Macaroni service files live under `.macaroni/` so they do not pollute the root of someone else's repository.

For a public repository without a token, read-only mode is supported: the client can read chats and messages, but it cannot send new messages. With a token, the same repository becomes read/write.

The token is not the user. The token is the access right to the repository.

```text
.macaroni/protocol.json
.macaroni/users/<client_id>.json
.macaroni/chats/<chat_id>/meta.json
.macaroni/chats/<chat_id>/members.json
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
.macaroni/inbox/<recipient>/<message_id>.json
```

MVP does not store binary attachments in git.

The client safely turns `http://` and `https://` URLs in message text into clickable links. This is UI behavior, not a separate attachment type.

MVP does not edit or delete messages in place.

## .macaroni/protocol.json

```json
{
  "name": "Macaroni Protocol",
  "version": 1,
  "created_at": "2026-06-08T12:00:00.000Z",
  "message_format": "json",
  "privacy": "public_by_design",
  "features": {
    "encryption": "optional",
    "attachments": "url_only",
    "receipts": "append_only",
    "deletion": "markers_only"
  }
}
```

## .macaroni/users/<client_id>.json

```json
{
  "version": 1,
  "id": "SA6E",
  "display_name": "Me",
  "created_at": "2026-06-08T12:00:00.000Z",
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  }
}
```

`client_id` is not a cryptographic key.

It is four characters. We tried.

## .macaroni/chats/<chat_id>/meta.json

```json
{
  "version": 1,
  "id": "chat_20260608_sa6e_k2xm",
  "title": "MOM",
  "created_at": "2026-06-08T12:00:00.000Z",
  "created_by": "SA6E",
  "visibility": "repo",
  "privacy": "public_by_design"
}
```

## .macaroni/chats/<chat_id>/members.json

A user is considered a chat member if their `client_id` is present in this file. Joining a chat is an update to `members.json`, not a separate registration flow.

If `members.json` is missing in an old or partially written chat, the client may repair a minimal file: `created_by` from `meta.json` becomes the `owner`, and the current user is added when joining.

```json
{
  "version": 1,
  "chat_id": "chat_20260608_sa6e_k2xm",
  "members": [
    {
      "id": "SA6E",
      "display_name": "Me",
      "role": "owner"
    },
    {
      "id": "K2XM",
      "display_name": "MOM",
      "role": "member"
    }
  ]
}
```

## Message

Path:

```text
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Body:

```json
{
  "version": 1,
  "id": "2026-06-08T12-30-01.123Z_SA6E_a8f1c2",
  "chat_id": "chat_20260608_sa6e_k2xm",
  "type": "text",
  "from": "SA6E",
  "from_name": "Me",
  "to": ["K2XM"],
  "created_at": "2026-06-08T12:30:01.123Z",
  "text": "Mom, boil some macaroni",
  "reply_to": null,
  "attachments": [],
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  },
  "signature": null
}
```

`message_id` is built from:

- timestamp;
- author/client id;
- short random suffix.

Git conflicts are rare because every message is a new file.

`from` remains the technical author identifier. `from_name` is a snapshot of the display name at send time, so the UI does not show `LXVF:` when the person wrote as `Mom`.

When rendering the author, the client uses the first available source:

1. `message.from_name`;
2. `.macaroni/users/<client_id>.json`;
3. `.macaroni/chats/<chat_id>/members.json`;
4. raw `client_id`.

## Read Receipt

Read receipts are append-only events. They do not replace local unread markers and they do not guarantee that a human actually read the message.

Path:

```text
.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
```

Body:

```json
{
  "version": 1,
  "id": "2026-06-09T12-30-01.123Z_SA6E_2026-06-09T12-20-00.000Z_K2XM_a1b2c3_d4e5",
  "type": "read",
  "chat_id": "chat_20260608_sa6e_k2xm",
  "user_id": "SA6E",
  "user_name": "Me",
  "message_id": "2026-06-09T12-20-00.000Z_K2XM_a1b2c3",
  "message_created_at": "2026-06-09T12:20:00.000Z",
  "read_at": "2026-06-09T12:30:01.123Z",
  "created_at": "2026-06-09T12:30:01.123Z",
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  },
  "signature": null
}
```

The client writes a receipt only when the latest read message marker moves forward. If the repo is open without write access or the receipt write fails, no receipt is created and nothing is added to outbox: this is a best-effort signal, not message delivery.

## .macaroni/inbox/<recipient>/<message_id>.json

Inbox is a notification queue, not a second copy of the message.

```json
{
  "version": 1,
  "recipient": "K2XM",
  "message_id": "2026-06-08T12-30-01.123Z_SA6E_a8f1c2",
  "chat_id": "chat_20260608_sa6e_k2xm",
  "message_path": ".macaroni/chats/chat_20260608_sa6e_k2xm/messages/2026/06/08/2026-06-08T12-30-01.123Z_SA6E_a8f1c2.json",
  "created_at": "2026-06-08T12:30:01.123Z"
}
```

Inbox exists so the client does not have to scan the entire history every time.

For a family or a small team, this is more than enough.

## Validation

MVP validation checks only minimal shape:

- version equals `1`;
- required string fields are not empty;
- `created_at` is a valid ISO date;
- message `type` equals `text`;
- `to` and `attachments` are arrays;
- message path is deterministic from `created_at`, `chat_id`, and `message_id`.

If JSON is invalid, the client should skip the file, show a readable error, and keep running.
