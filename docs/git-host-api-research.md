# Research: Git Host API для Git-Agnostic Macaroni

Статус: research, без реализации.

Дата снимка: 2026-06-14.

Цель: понять, можно ли сделать Macaroni Messenger не GitHub-only, не ломая текущий GitHub adapter и не превращая один HTML-файл в обёртку весом с небольшой холодильник.

Короткий ответ: да, можно.

Но не через "браузер сейчас сам пойдёт по SSH в любой git server".

Правильный первый шаг - host API adapters.

## Что Исследуем

Провайдеры:

- GitHub;
- GitLab;
- Gitea;
- Forgejo;
- GitVerse.

Вопросы:

1. Как прочитать файл `.macaroni/...`.
2. Как получить список файлов/директорий.
3. Как записать файл.
4. Можно ли записать несколько файлов одним commit.
5. Как работать с branch.
6. Как выглядит auth.
7. Где появятся CORS/rate-limit/permission проблемы.

## Что Не Исследуем В Этом Шаге

- Raw SSH.
- Полный git client в браузере.
- Packfiles.
- Smart HTTP push.
- Electron/Tauri/native bridge.
- Storage branch implementation.
- Read-only UI polish.

Raw SSH из обычной browser tab не является целью.

Если оператор remote хочет "любой git", он должен хотя бы дать browser-compatible HTTPS API. GitLab, Gitea, Forgejo и GitVerse уже показывают, что это не фантастика.

## Минимальный Adapter Contract

Базовый adapter должен уметь:

```js
const adapter = {
  id: "gitlab",
  label: "GitLab",

  canRead(config) {},
  canWrite(config) {},

  head(config) {},
  readFile(config, path, options) {},
  readJson(config, path, options) {},
  listFiles(config, path, options) {},

  writeFile(config, path, content, options) {},
  writeJson(config, path, value, options) {},

  writeFiles(config, files, options) {},
  ensureBranch(config, branch, fromRef) {}
};
```

`writeFiles` и `ensureBranch` опциональны.

Если host не умеет batch commit, Macaroni может писать по одному файлу.

Если host не умеет создавать branch из браузера, пользователь может создать branch руками, а Macaroni будет использовать готовую.

Если host умеет только read-only, это всё ещё полезный Macaroni client. Composer в таком режиме позже надо скрыть, а не делать вид, что кнопка `Send` магически победит permissions.

## Общая Модель

```text
Macaroni Protocol v1
  -> provider adapter
    -> host file/tree/commit API
      -> git commit
```

Протокол `.macaroni/` не меняется.

Меняется только транспорт.

## Сравнение Провайдеров

| Provider | Read file | List files | Write file | Batch write | Branch support | Auth | Главный риск |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GitHub | Contents API | Contents API / Trees API | Contents API `PUT` | через Git Database API, не Contents API | `ref`/`branch`, refs API отдельно | Bearer token, Contents permissions | rate limit, `sha` conflicts |
| GitLab | Repository Files API | Repository Tree API | Repository Files `POST`/`PUT` | Commits API | `branch`, `start_branch` | `PRIVATE-TOKEN` / Bearer | path encoding, instance CORS |
| Gitea | Contents API | Contents / Trees API | Contents `POST`/`PUT` | `POST /contents` multiple files | branches API | `Authorization: token ...` или Bearer | self-hosted CORS/config drift |
| Forgejo | Contents API | Contents / Trees API | Contents `POST`/`PUT` | `POST /contents` multiple files | branches API | `Authorization: token ...` или Bearer | self-hosted CORS/config drift |
| GitVerse | Contents API | Git Trees API | Contents `PUT` | Git Trees + Git Commits API | branches list, commit/tree APIs | Bearer + versioned Accept header | API version header, less tested by us |

## GitHub

Текущий adapter уже работает через REST Contents API.

Полезные свойства:

- файл или директория читаются через `/repos/{owner}/{repo}/contents/{path}`;
- директория возвращает entries;
- запись одного файла идёт через `PUT /repos/{owner}/{repo}/contents/{path}`;
- для update нужен текущий `sha`;
- для fine-grained token нужен `Contents: read` или `Contents: write`;
- публичные ресурсы можно читать без token;
- Contents API имеет limit 1000 файлов на директорию, для рекурсии нужен Trees API.

Вывод: GitHub остаётся first-class adapter.

Для batch write можно позже перейти с Contents API на Git Database API: создать blobs/tree/commit и обновить ref. Для первого git-agnostic шага это не обязательно.

## GitLab

GitLab похож на GitHub по уровню абстракции, но endpoint'ы и параметры другие.

Полезные свойства:

- файл читается через `GET /projects/:id/repository/files/:file_path`;
- raw file читается через `/raw`;
- запись нового файла: `POST /projects/:id/repository/files/:file_path`;
- update файла: `PUT /projects/:id/repository/files/:file_path`;
- для нескольких файлов в одном commit используется Commits API;
- `file_path` должен быть URL-encoded;
- write-запросы принимают `branch`, `commit_message`, `content`;
- `encoding=base64` есть, но default - text;
- `last_commit_id` может использоваться как conflict guard.

Вывод: GitLab adapter реалистичен и должен быть следующим после GitHub/GitVerse research. Он не требует менять Protocol v1.

## Gitea

Gitea даёт API, похожий на GitHub Contents, но со своими деталями.

Проверено по официальной документации и Swagger endpoint `https://gitea.com/swagger.v1.json`.

Нужные пути в OpenAPI:

- `GET /repos/{owner}/{repo}/contents/{filepath}`;
- `POST /repos/{owner}/{repo}/contents/{filepath}`;
- `PUT /repos/{owner}/{repo}/contents/{filepath}`;
- `GET /repos/{owner}/{repo}/git/trees/{sha}`;
- `GET /repos/{owner}/{repo}/branches`;
- `POST /repos/{owner}/{repo}/contents` для multiple files.

Auth:

- historical API token: `Authorization: token <token>`;
- OAuth token: `Authorization: Bearer <token>`;
- token может также передаваться query-параметром, но Macaroni не должен так делать: URL любят попадать в историю, логи и скриншоты.

Вывод: Gitea adapter выглядит простым. Главный риск не API, а конкретная инсталляция: CORS, reverse proxy, disabled endpoints, лимиты.

## Forgejo

Forgejo API близок к Gitea.

Проверено по официальной документации и Swagger endpoint `https://try.next.forgejo.org/swagger.v1.json`.

Нужные пути в OpenAPI:

- `GET /repos/{owner}/{repo}/contents/{filepath}`;
- `POST /repos/{owner}/{repo}/contents/{filepath}`;
- `PUT /repos/{owner}/{repo}/contents/{filepath}`;
- `GET /repos/{owner}/{repo}/git/trees/{sha}`;
- `GET /repos/{owner}/{repo}/branches`;
- `POST /repos/{owner}/{repo}/contents` для multiple files.

Auth:

- historical API token: `Authorization: token <token>`;
- OAuth token: `Authorization: Bearer <token>`.

Вывод: Forgejo можно поддерживать почти тем же adapter family, что и Gitea, но не сливать их в один класс преждевременно. У маленького проекта нет денег на магический "универсальный ForgejoGiteaMaybe" слой, который ночью дебажится по скриншоту с чужого VPS.

## GitVerse

GitVerse важен отдельно: это не "а вдруг похоже на GitHub", а реальный versioned public API.

Проверено:

- официальная документация требует versioned `Accept` header;
- официальный репозиторий `gitverse/rest-api-description` содержит OpenAPI specs;
- на 2026-06-14 актуальный проверенный файл: `v1/openapi-1.7.json`;
- локально parsed OpenAPI title/version: `GitVerse Public API`, `1.7.0`;
- commit официального repo при research: `26fde245446830e736c5516eacfaa9e4e695575f`.

Нужные пути в OpenAPI 1.7:

- `GET /repos/{owner}/{repo}/contents/{filepath}` - получить файл или директорию;
- `PUT /repos/{owner}/{repo}/contents/{filepath}` - создать или обновить файл;
- `DELETE /repos/{owner}/{repo}/contents/{filepath}` - удалить файл;
- `GET /repos/{owner}/{repo}/git/trees/{sha}` - получить tree по SHA, есть `recursive`;
- `POST /repos/{owner}/{repo}/git/trees` - создать Git tree;
- `POST /repos/{owner}/{repo}/git/commits` - создать Git commit;
- `GET /repos/{owner}/{repo}/branches` - список branches.

`CreateOrUpdateFileOptions` содержит:

- `branch`;
- `content` base64;
- `message`;
- `new_branch`;
- `sha`;
- `signoff`.

Auth:

- `Authorization: Bearer <token>`;
- `Accept: application/vnd.gitverse.object+json; version=1`.

Вывод: GitVerse adapter реалистичен. Более того, GitVerse уже ближе к нужному нам shape, чем ожидалось: есть и content endpoint, и low-level tree/commit endpoints.

## Можно Ли Унифицировать Adapter?

Да, но аккуратно.

Нужно разделить:

1. `provider adapter` - знает endpoint'ы, headers, path encoding и response shape.
2. `macaroni sync logic` - знает `.macaroni/` layout, outbox, inbox, cache, receipts.

Не нужно делать:

- enterprise provider SDK;
- abstract repository service factory;
- общий HTTP client на 500 строк;
- нормализацию всего GitHub/GitLab/Gitea/GitVerse API мира.

Нужно сделать маленький contract:

```text
read path
list path
write path
optional batch write
optional ensure branch
head marker
normalize error
```

Это достаточно.

## Реальные Ограничения

### CORS

Официальные API могут быть нормальными, но self-hosted Gitea/Forgejo/GitLab может быть настроен так, что браузерный `messenger.html` не сможет к нему обратиться.

Это не проблема Protocol v1.

Это проблема конкретного remote.

Macaroni должен показывать честный error: "host API не доступен из браузера".

### Rate Limits

GitHub уже показал, что unauthenticated public demo можно положить rate limit'ом.

Adapter contract должен иметь нормализованные ошибки:

```text
rate_limited
auth_required
write_forbidden
not_found
conflict
network
unsupported
```

### Conflicts

Все write adapters должны считать conflict нормальным состоянием.

Для Macaroni это значит:

1. pull/read latest;
2. retry outbox;
3. если всё равно conflict - оставить сообщение в outbox и показать человеческий статус.

Git не убежит.

### Batch Commit

Macaroni часто пишет не один файл:

- message;
- inbox pointer;
- receipt;
- members/meta update.

Batch write лучше, но не обязательный blocker.

Порядок:

1. Сначала single-file write adapter.
2. Потом batch write там, где host даёт нормальный API.
3. Потом storage branch.

### Read-Only Mode

Read-only mode не должен выглядеть как сломанный write mode.

Backlog:

- если token отсутствует или не имеет write permissions, скрыть composer;
- показать состояние: "Вы в read-only режиме. Этот token умеет читать, но не умеет писать.";
- оставить refresh/import/search/chat info.

Это не blocker для git-agnostic adapter research, но это надо сделать до широкой поддержки public repos.

### Storage Branch

Storage branch - отдельный backlog item.

Git-agnostic adapter должен уже сейчас принимать `branch`, но реализация storage branch не должна ехать в одной куче с non-GitHub providers.

Сначала adapters.

Потом branch hygiene.

Иначе получится не messenger, а тарелка макарон с миграциями.

## Wrapper Stance

Base product остаётся одним HTML-файлом.

Мы не тянем Electron/Tauri/native bridge как обязательную часть git-agnostic поддержки.

Если ради просмотра одного HTML хочется принести 500 МБ обёртки, значит обёртка варит себя, а не макароны.

Wrappers могут быть optional packaging layer.

Transport contract не должен зависеть от них.

## Предлагаемый План

1. Сохранить текущий GitHub adapter как reference implementation.
2. Вынести минимальный `provider adapter` interface внутри `messenger.html`, без отдельной build system.
3. Реализовать GitVerse adapter или GitLab adapter первым non-GitHub provider.
4. После этого сделать Gitea/Forgejo family adapter.
5. Добавить read-only composer guard.
6. Отдельно реализовать storage branch.
7. Только после этого возвращаться к настоящему "Isomorphic Git" через Smart HTTP, если оно всё ещё нужно для шутки.

## Решение На Сейчас

Git-agnostic Macaroni не должен начинаться с полного git implementation.

Он должен начинаться с browser-compatible host API adapters.

Это сохраняет:

- один HTML-файл;
- текущий Protocol v1;
- работающий GitHub adapter;
- понятный путь к GitLab/Gitea/Forgejo/GitVerse;
- минимальную operational complexity.

А полный "мы написали git в HTML" оставляем как отдельный вид спорта. Красивый, бессмысленный и потенциально великий.

## Источники

- GitHub REST Contents API: https://docs.github.com/en/rest/repos/contents
- GitLab Repository Files API: https://docs.gitlab.com/api/repository_files/
- GitLab Repositories API: https://docs.gitlab.com/api/repositories/
- Gitea API Usage: https://docs.gitea.com/development/api-usage
- Gitea OpenAPI: https://gitea.com/swagger.v1.json
- Forgejo API Usage: https://forgejo.org/docs/latest/user/api-usage/
- Forgejo OpenAPI: https://try.next.forgejo.org/swagger.v1.json
- GitVerse API versioning: https://gitverse.ru/docs/public-api/using-public-api/api-versioning/
- GitVerse OpenAPI repo: https://gitverse.ru/gitverse/rest-api-description
