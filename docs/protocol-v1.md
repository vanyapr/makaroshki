# Macaroni Protocol v1

Macaroni Protocol v1 описывает, какие JSON-файлы лежат в git-репозитории.

Git остаётся источником истины.

IndexedDB остаётся локальным кешем и индексом.

Если локальный индекс сломался, он пересобирается из этих файлов.

## Layout Репозитория

Macaroni-репозиторием может быть любой git-репозиторий, в котором есть директория `.macaroni/` с этим layout. Репозиторий с `messenger.html` и репозиторий с сообщениями могут совпадать или быть разными.

Чаты можно приделать к любому git-репозиторию, если клиент умеет читать и писать файлы по Macaroni Protocol и у пользователя есть права на этот репозиторий.

Все служебные файлы Macaroni лежат внутри `.macaroni/`, чтобы не засорять корень чужого репозитория.

Для публичного репозитория без токена поддерживается read-only режим: клиент может читать чаты и сообщения, но не может отправлять новые сообщения. С токеном тот же репозиторий становится read/write.

Токен не является пользователем. Токен является правом доступа к репозиторию.

```text
.macaroni/protocol.json
.macaroni/users/<client_id>.json
.macaroni/chats/<chat_id>/meta.json
.macaroni/chats/<chat_id>/members.json
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
.macaroni/inbox/<recipient>/<message_id>.json
```

MVP не хранит вложения в git как бинарники.

Клиент безопасно превращает `http://` и `https://` URL в тексте сообщения в кликабельные ссылки. Это UI-поведение, а не отдельный тип вложения.

MVP не редактирует и не удаляет сообщения на месте.

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
  "display_name": "Я",
  "created_at": "2026-06-08T12:00:00.000Z",
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  }
}
```

`client_id` не является криптографическим ключом.

Это четыре символа. Мы старались.

## .macaroni/chats/<chat_id>/meta.json

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

## .macaroni/chats/<chat_id>/members.json

Пользователь считается участником чата, если его `client_id` есть в этом файле. Вступление в чат - это обновление `members.json`, а не отдельная регистрация.

Если `members.json` отсутствует в старом или частично записанном чате, клиент может восстановить минимальный файл: `created_by` из `meta.json` становится `owner`, а текущий пользователь добавляется при вступлении.

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
  "from_name": "Я",
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

`from` остаётся техническим идентификатором автора. `from_name` - снимок отображаемого имени на момент отправки, чтобы UI не показывал `LXVF:` там, где человек писал как `Мама`.

При отображении автора клиент использует первый доступный источник:

1. `message.from_name`;
2. `.macaroni/users/<client_id>.json`;
3. `.macaroni/chats/<chat_id>/members.json`;
4. голый `client_id`.

## Read Receipt

Read receipts являются append-only событиями. Они не заменяют локальные unread markers и не являются гарантией, что человек прочитал сообщение глазами.

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
  "user_name": "Я",
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

Клиент пишет receipt только когда последний прочитанный message marker продвинулся. Если repo открыт без write-доступа или запись receipt не удалась, receipt не создаётся и не попадает в outbox: это best-effort сигнал, а не доставка сообщения.

## .macaroni/inbox/<recipient>/<message_id>.json

Inbox - это очередь уведомлений, а не отдельная копия сообщения.

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
