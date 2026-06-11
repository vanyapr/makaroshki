# Контракт Generic Git Provider

Macaroni Messenger не должен быть GitHub-only.

Протокол `.macaroni/` не привязан к git-хостингу: сообщения - это JSON-файлы в репозитории. GitHub - просто первый встроенный browser adapter.

## Честная Браузерная Часть

Один HTML-файл в браузере не может магически сходить по SSH в любой git server.

Браузеру нужен один из вариантов:

- host API, как GitHub Contents API;
- CORS-enabled HTTPS file API поверх git repository;
- WebDAV-style endpoint, который сзади делает git commits;
- custom adapter, встроенный в `messenger.html`;
- Electron/WebView wrapper, который даёт тому же HTML UI native git operations.

Это не философское ограничение.

Это браузер является браузером.

## Что Значит "Любой Git"

Любой git repository может хранить Macaroni data, если в нём можно держать:

```text
.macaroni/
  protocol.json
  users/<client_id>.json
  chats/<chat_id>/meta.json
  chats/<chat_id>/members.json
  chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
  inbox/<client_id>/<message_id>.json
```

Любой git host можно поддержать в Macaroni, если browser-compatible adapter умеет:

1. Читать файл по path.
2. Читать JSON-файл по path.
3. Листить файлы внутри директории.
4. Писать файл по path.
5. Писать JSON-файл по path.
6. Возвращать дешёвый marker версии repository, например branch HEAD SHA, если host это умеет.
7. Превращать auth, permission, conflict, missing file, network и rate-limit ошибки в нормальные JavaScript errors.

Это весь transport contract.

Без message broker.

Без Macaroni backend.

Без enterprise adapter factory.

Просто file operations, которые в итоге становятся git commits.

## Статус Встроенных Adapter'ов

| Provider | Read | Write | Notes |
| --- | --- | --- | --- |
| GitHub | yes | yes | Реализовано через GitHub REST Contents API. |
| Hardcoded demo | yes | no | Используется для Hacker News/demo traffic без боли от API rate limits. |
| Local test repo | yes | yes | IndexedDB fake repo для локальной разработки. |
| Generic Git HTTP | contract only | contract only | Нужен CORS-compatible host adapter. |
| GitLab | planned | planned | Тот же protocol, другой host API. |
| GitVerse | planned | planned | Тот же protocol, другой host API. |
| Gitea/Forgejo | planned | planned | Вероятно file/content API adapter. |
| Raw SSH git | no | no | Не из обычной browser tab. Для этого нужен wrapper. |

## Почему Не Встроить Полный Git Client?

Потому что проект - один HTML-файл.

Browser git implementation с packfile support, credentials, filesystem emulation и host-specific CORS handling возможен, но это плохой первый ход.

Практичная модель Macaroni:

```text
Macaroni Protocol
  -> provider adapter
    -> host API или wrapper git operation
      -> git commit
```

GitHub - один adapter, а не граница продукта.

## Минимальная Форма Adapter'а

Adapter должен вести себя примерно так:

```js
const adapter = {
  readFile(config, path) {},
  readJson(config, path) {},
  listFiles(config, path) {},
  writeFile(config, path, content, message) {},
  writeJson(config, path, value, message) {},
  head(config) {}
};
```

Если host не умеет recursive directory listing, adapter всё ещё может быть полезен. У Macaroni предсказуемый `.macaroni/` layout, и sync может обходить известные path'ы.

Если host не умеет писать из браузера из-за CORS или auth, он всё ещё может работать read-only.

Read-only Macaroni - это всё ещё Macaroni.

Он просто пока не может сказать маме про макароны.
