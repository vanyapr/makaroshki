# Show HN Notes

Предлагаемый заголовок:

> Show HN: Macaroni Messenger - мессенджер в одном HTML-файле, где transport это Git

Короткий pitch:

Macaroni Messenger - это single-file messenger: `messenger.html`, без backend, без базы данных кроме Git, сообщения лежат JSON-файлами в `.macaroni/`.

Теперь внутри есть built-in browser adapters для GitHub, GitLab, GitVerse, Gitea и Forgejo.

Ещё есть optional Encryption 1.01.

Encryption 1.01 - это не новый protocol. Это plugin, который превращает message text в `MACARONI1.01:<base64-json>` и обратно.

Это явно не "secure messenger".

Это не скрытое ограничение. Это предупреждающая наклейка.

Demo захардкожен и работает read-only, чтобы Hacker News traffic не сжёг unauthenticated GitHub API rate limit до того, как люди увидят шутку. Настоящие repositories подключаются через Settings.

## Текст Поста

```text
Macaroni Messenger - это мессенджер в одном HTML-файле.

Без backend.
Без базы данных кроме Git.
Без регистрации.

Сообщения лежат JSON-файлами в .macaroni/.

Браузерный клиент умеет читать/писать через built-in adapters для GitHub, GitLab, GitVerse, Gitea и Forgejo.

Ещё есть Encryption 1.01: plugin layer, который шифрует message text, не меняя Macaroni protocol.

Это не secure messenger.
Это честный messenger.

К сожалению, работает.
```

## Что попробовать

1. Открыть live demo.
2. Переключить чаты.
3. Поискать сообщения.
4. Открыть Chat Info.
5. Посмотреть `.macaroni/` в repository.
6. Открыть Settings и посмотреть список providers.
7. Посмотреть секцию Plugins и Encryption 1.01.
8. Скачать `messenger.html` и открыть локально.

## FAQ

### Это шутка?

Частично.

### Оно работает?

К сожалению, да.

### Где хранятся сообщения?

В `.macaroni/` внутри Git repository.

### Это приватно?

Нет.

Если repository публичный, сообщения публичные.

Если repository приватный, сообщения читают все, у кого есть доступ к repository.

Если включить Encryption 1.01, читатели repository увидят encrypted payloads вместо plaintext, но проект всё ещё не продаёт "real privacy".

### Почему без backend?

Потому что Git уже умеет хранить файлы, а мы пытались отправить "мам, свари макароны", а не запускать платежную компанию.

### Почему demo захардкожен?

Потому что Hacker News может создать достаточно traffic, чтобы упереться в unauthenticated GitHub API rate limits раньше, чем кто-то увидит шутку.

### Можно писать настоящие сообщения?

Да. Встроенные browser adapters есть для GitHub, GitLab, GitVerse, Gitea и Forgejo. Подключите repository в Settings и используйте provider token с read/write доступом к repository content.

Сам протокол `.macaroni/` не привязан к GitHub. Для custom/self-hosted git hosts всё ещё нужна browser-compatible API/CORS настройка; см. [generic git provider contract](generic-git-provider.md).

### Оно поддерживает только GitHub?

Нет.

GitHub был первым adapter. Текущий single HTML file также содержит adapters для GitLab, GitVerse, Gitea и Forgejo.

Это macaroni-style "isomorphic git": маленькие browser-side adapters поверх host API, а не npm dependency и не raw SSH из browser tab.

### Шифрование меняет protocol?

Нет.

Macaroni Protocol v1 остаётся тем же. Сообщения всё ещё JSON-файлы в `.macaroni/`.

Encryption 1.01 - это plugin layer поверх `message.text`.

Plaintext:

```json
{ "text": "Мам, свари макароны" }
```

Encrypted plugin payload:

```json
{ "text": "MACARONI1.01:<base64-json>" }
```

Core не волнуется. Git не волнуется. Мама, вероятно, тоже не должна.

### Encryption 1.01 - это настоящее шифрование?

Да, максимально макаронным способом.

Shared secret, salt, message context, token confetti если есть token, Tiny PRNG и XOR.

Без handshake.

Без key server.

Без external dependency.

Без утверждений, что это защитит от серьёзных людей с серьёзными бюджетами.

Если нужна "real privacy" - используйте PGP. Если нужно, чтобы случайный читатель публичного repository не прочитал "свари макароны", это правильный уровень идиотской эффективности.

См. [Macaroni Encryption 1.01](encryption-1.01.md).

### Можно вставить token в Hacker News?

Нет.

Если уже вставили - отзовите.
