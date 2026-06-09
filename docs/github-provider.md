# GitHub Provider Adapter

GitHub - первый реальный provider для Macaroni Messenger.

Текущая реализация находится в `messenger.html` как `window.MacaroniGitHub`.

## Что Уже Есть

- разбор repo URL вида `https://github.com/owner/repo`;
- чтение файла через GitHub REST Contents API;
- чтение JSON-файла;
- listing директории;
- запись файла через Contents API;
- запись JSON-файла;
- refresh/reindex читает все chat meta, messages по датам и `.macaroni/inbox/<CLIENT_ID>` как receive hint;
- перед полным reindex клиент проверяет последний commit SHA branch и пропускает обход Contents API, если repo не изменился;
- GitHub repo без token работает в read-only режиме для публичных repo;
- smoke harness проверяет GitHub send, reindex и read-only через fake Contents API без реального token;
- human-readable ошибки для auth, permissions, missing repo/file и conflict.

## Что Нужное Для Токена

Используйте fine-grained personal access token.

Repository access: только repo с сообщениями.

Repository permissions:

- `Contents: Read and write`.

GitHub API принимает token через `Authorization: Bearer <token>`.

## Как Пишется Файл

GitHub Contents API не является raw git push.

Для Macaroni MVP это нормально.

Запись файла:

1. клиент читает существующий file metadata;
2. если файл уже есть, берёт `sha`;
3. отправляет `PUT /repos/{owner}/{repo}/contents/{path}`;
4. кладёт `content` в Base64;
5. передаёт `message`, `branch` и, при update, `sha`.

Фактически это provider API equivalent для commit/push.

Если одно действие создаёт несколько файлов, клиент пишет их последовательно. GitHub Contents API создаёт отдельный commit на каждый `PUT`, поэтому параллельные записи в одну ветку могут получить conflict.

## Ограничения

- Первый adapter нацелен на маленькие repo.
- Listing директории через Contents API не является бесконечным recursive scan.
- Для больших деревьев позже нужен Git Trees API или более умный sync.
- MVP пишет в branch `main`.
- Одновременная запись одного и того же файла может вернуть conflict.
- Сообщения пишутся как новые файлы, поэтому обычные message writes почти не конфликтуют.
- Токен хранится в `localStorage`, как уже честно написано в UI.

## Send/Refresh Flow

Если в профиле выбран provider `github` и указан token, основной composer использует `window.MacaroniGitHub`.

Если token пустой, GitHub repo работает как read-only public repo: клиент может читать публичную историю, но не может создавать чаты и отправлять сообщения.

Попытка отправки без token сохраняет draft в outbox. Retry ждёт token.

Если пользователь добавил token в настройках, а в outbox уже есть сообщения, клиент автоматически пробует отправить очередь после сохранения профиля.

При ошибках auth/network draft сохраняется в outbox.

Кнопка "Обновить" тоже делает retry outbox и reindex.

Reindex сначала читает последний commit SHA branch через GitHub API. Если SHA совпадает с локально сохранённым значением, полный обход Contents API пропускается и клиент оставляет текущий IndexedDB index.

Если SHA изменился или проверка HEAD недоступна, reindex читает:

1. все найденные chat meta;
2. сообщения чатов по `YYYY/MM/DD`;
3. `.macaroni/inbox/<CLIENT_ID>/*.json`;
4. `message_path` из inbox notifications.

Это нужно, чтобы второй экземпляр видел адресованные ему сообщения даже если они пришли через inbox notification.

## Что Ещё Не Закрыто

Remote flow уже умеет писать через Contents API, но синхронизация пока простая:

- сканируются chat meta;
- messages обходятся по `YYYY/MM/DD`;
- inbox используется только как список ссылок на message files;
- есть только грубая проверка branch HEAD перед полным reindex;
- нет умного incremental sync на уровне отдельных файлов;
- нет Git Trees API;
- нет полноценного multi-chat UI.

## Polling

MVP polling намеренно тупой:

- GitHub profile с token: sync каждые 30 секунд.
- GitHub read-only profile без token: sync каждые 60 секунд.
- Скрытая вкладка тоже планирует sync; браузер может замедлить фоновые таймеры.
- Если sync уже идёт, следующий polling/manual refresh не стартует параллельно.

Это не real-time и не presence. Это "мама увидит сообщение достаточно скоро".

GitHub rate limits остаются ограничением provider. Без token лимит общий для IP и может закончиться быстрее; с token лимит выше, поэтому authenticated режим предпочтительнее для живого чата.
