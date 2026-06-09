# Macaroni Protocol v1

Macaroni Protocol v1 describes which JSON files live in the git repository.

Git remains the source of truth.

IndexedDB remains a local cache and index.

If the local index breaks, it is rebuilt from these files.

## Repository Layout

Any git repository with this layout can be a Macaroni repository. The repository that serves `messenger.html` and the repository that stores messages may be the same repository or different repositories.

```text
protocol.json
users/<client_id>.json
chats/<chat_id>/meta.json
chats/<chat_id>/members.json
chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
inbox/<recipient>/<message_id>.json
```

MVP does not store binary attachments in git.

MVP does not edit or delete messages in place.

## protocol.json

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
    "deletion": "markers_only"
  }
}
```

## users/<client_id>.json

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

## chats/<chat_id>/meta.json

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

## chats/<chat_id>/members.json

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
chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Body:

```json
{
  "version": 1,
  "id": "2026-06-08T12-30-01.123Z_SA6E_a8f1c2",
  "chat_id": "chat_20260608_sa6e_k2xm",
  "type": "text",
  "from": "SA6E",
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

## inbox/<recipient>/<message_id>.json

Inbox is a notification queue, not a second copy of the message.

```json
{
  "version": 1,
  "recipient": "K2XM",
  "message_id": "2026-06-08T12-30-01.123Z_SA6E_a8f1c2",
  "chat_id": "chat_20260608_sa6e_k2xm",
  "message_path": "chats/chat_20260608_sa6e_k2xm/messages/2026/06/08/2026-06-08T12-30-01.123Z_SA6E_a8f1c2.json",
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
