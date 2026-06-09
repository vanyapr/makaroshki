# Macaroni Protocol v1

Macaroni Protocol v1 описывает, какие JSON-файлы лежат в git-репозитории.

Git остаётся источником истины.

IndexedDB остаётся локальным кешем и индексом.

Если локальный индекс сломался, он пересобирается из этих файлов.

## Layout Репозитория

Macaroni-репозиторием может быть любой git-репозиторий, в котором есть этот layout. Репозиторий с `messenger.html` и репозиторий с сообщениями могут совпадать или быть разными.

```text
protocol.json
users/<client_id>.json
chats/<chat_id>/meta.json
chats/<chat_id>/members.json
chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
inbox/<recipient>/<message_id>.json
```

MVP не хранит вложения в git как бинарники.

MVP не редактирует и не удаляет сообщения на месте.

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
  "display_name": "Я",
  "created_at": "2026-06-08T12:00:00.000Z",
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  }
}
```

`client_id` не является криптографическим ключом.

Это четыре символа. Мы старались.

## chats/<chat_id>/meta.json

```json
{
  "version": 1,
  "id": "chat_20260608_sa6e_k2xm",
  "title": "МАМА",
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
      "display_name": "Я",
      "role": "owner"
    },
    {
      "id": "K2XM",
      "display_name": "МАМА",
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
  "text": "Мам, свари макарошки",
  "reply_to": null,
  "attachments": [],
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  },
  "signature": null
}
```

`message_id` строится из:

- timestamp;
- author/client id;
- короткого random suffix.

Git-конфликтов почти нет, потому что каждое сообщение - новый файл.

## inbox/<recipient>/<message_id>.json

Inbox - это очередь уведомлений, а не отдельная копия сообщения.

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

Inbox нужен, чтобы клиенту не приходилось каждый раз сканировать всю историю.

Для семьи и маленькой команды этого более чем достаточно.

## Validation

MVP validation проверяет только минимальный shape:

- версия равна `1`;
- обязательные строковые поля не пустые;
- `created_at` является валидной ISO-датой;
- `type` сообщения равен `text`;
- `to` и `attachments` являются массивами;
- message path детерминирован из `created_at`, `chat_id` и `message_id`.

Если JSON невалидный, клиент должен пропустить файл, показать понятную ошибку и продолжить работу.
