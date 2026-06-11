# Show HN Notes

Предлагаемый заголовок:

> Show HN: Macaroni Messenger - мессенджер в одном HTML-файле, где база данных это Git

Короткий pitch:

Macaroni Messenger - это single-file messenger: `messenger.html`, без backend, без базы данных кроме Git, сообщения лежат JSON-файлами в `.macaroni/`.

Он явно не приватный.

Это не скрытое ограничение. Это предупреждающая наклейка.

Demo захардкожен и работает read-only, чтобы Hacker News traffic не сжёг unauthenticated GitHub API rate limit до того, как люди увидят шутку. Настоящие repositories подключаются через Settings.

## Что попробовать

1. Открыть live demo.
2. Переключить чаты.
3. Поискать сообщения.
4. Открыть Chat Info.
5. Посмотреть `.macaroni/` в repository.
6. Скачать `messenger.html` и открыть локально.

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

### Почему без backend?

Потому что Git уже умеет хранить файлы, а мы пытались отправить "мам, свари макароны", а не запускать платежную компанию.

### Почему demo захардкожен?

Потому что Hacker News может создать достаточно traffic, чтобы упереться в unauthenticated GitHub API rate limits раньше, чем кто-то увидит шутку.

### Можно писать настоящие сообщения?

Да. Сегодня встроенный write adapter - GitHub: подключите GitHub repository в Settings и используйте fine-grained token с `Contents: Read and write`.

Сам протокол `.macaroni/` не привязан к GitHub. Для других git hosts нужен browser-compatible adapter; см. [generic git provider contract](generic-git-provider.md).

### Можно вставить token в Hacker News?

Нет.

Если уже вставили - отзовите.
