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

Если token пустой, клиент остаётся на local test repo. Это нужно, чтобы демо работало без реального доступа к GitHub.

При ошибках auth/network draft сохраняется в outbox.

Кнопка "Обновить" делает retry outbox и reindex.

## Что Ещё Не Закрыто

Remote flow уже умеет писать через Contents API, но синхронизация пока простая:

- сканируется первый найденный chat;
- messages обходятся по `YYYY/MM/DD`;
- нет умного incremental sync;
- нет Git Trees API;
- нет полноценного multi-chat UI.
