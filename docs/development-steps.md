# Development Steps

Этот документ превращает roadmap в последовательную очередь разработки.

Главный принцип:

> Не делать сложно там, где можно сделать смешно.

Это не отменяет того факта, что Macaroni Messenger должен быть полноценным приложением: пользователь должен открыть `messenger.html`, пройти совместимость, настроить профиль, отправить сообщение, пережить ошибку синхронизации и не потерять данные.

## Правила Выполнения

- Каждый шаг делается в отдельной ветке.
- Один шаг должен давать проверяемый результат.
- После каждого шага обновляются docs, если изменилась договорённость.
- `messenger.html` остаётся главным артефактом.
- `localhost` не используется как fallback.
- Новая dependency допускается только если без неё решение становится заметно хуже.
- Если решение можно понять за 5 минут, это почти всегда правильный вариант.

## Этап 0. Документы И Контракт

Цель: убрать двусмысленность перед кодом.

Шаги:

1. Сверить `README.md`, `PHILOSOPHY.md`, `docs/product-brief.md` и `docs/roadmap.md`.
2. Убедиться, что главный контракт везде один: локальный `messenger.html`, двойной клик, supported browser или экран несовместимости.
3. Зафиксировать, что `PHILOSOPHY.md` является продуктовой философией, а `docs/roadmap.md` - актуальным планом реализации.
4. Добавить короткие ссылки между документами, если после создания repo они ещё не связаны.

Готово, когда:

- документы не спорят друг с другом;
- roadmap остаётся источником актуального плана;
- нет обещаний `localhost`, backend или privacy by default.

## Этап 1. Первый `messenger.html`

Цель: получить реальный single-file артефакт.

Статус: базовая статическая верстка по макету создана в `messenger.html`. Интерактив, feature detection и storage ещё не реализованы.

Шаги:

1. Создать `messenger.html`.
2. Добавить базовую HTML-структуру.
3. Добавить inline CSS.
4. Добавить inline JS.
5. Добавить статический layout: sidebar, messages, composer, status bar.
6. Добавить визуальный placeholder состояния синхронизации.
7. Открыть файл двойным кликом в поддерживаемом браузере.

Готово, когда:

- файл открывается через `file://`;
- нет внешних CSS/JS/assets;
- UI не разваливается на desktop-width и narrow-width;
- в коде нет build system, если она ещё не нужна.

## Этап 2. Feature Detection

Цель: сразу отделить поддерживаемые браузеры от неподдерживаемых.

Статус: реализовано в `messenger.html`. Клиент проверяет `file://` или `https://`, `localStorage`, `IndexedDB` и `WebCrypto`; неподдерживаемый браузер получает экран несовместимости. `http://localhost` не считается поддерживаемым fallback.

Шаги:

1. Реализовать `checkSupport()`.
2. Проверять `location.protocol === "file:"`.
3. Проверять `window.localStorage`.
4. Проверять `window.indexedDB`.
5. Проверять `window.crypto?.subtle`.
6. Добавить экран несовместимости.
7. Добавить recommended browsers: Chrome / Chromium / Edge.
8. Не предлагать пользователю поднять локальный сервер.

Готово, когда:

- поддерживаемый браузер видит основной UI;
- неподдерживаемый браузер видит красивый экран;
- текст экрана содержит: "Ваш браузер недостаточно смешной для запуска Macaroni Messenger";
- `localhost` не упоминается как решение.

## Этап 3. `CLIENT_ID`

Цель: каждый экземпляр `messenger.html` получает короткий идентификатор.

Статус: реализовано в `messenger.html`. При открытии клиент читает `macaroni.client_id.v1` из `localStorage`; если ID ещё нет, генерирует четыре символа, сразу сохраняет их в `localStorage`, подставляет в интерфейс и отдаёт через `window.MacaroniSupport.clientId`.

Шаги:

1. Добавить persistent `CLIENT_ID` в `localStorage`.
2. Описать генератор ID отдельной простой функцией.
3. Использовать alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`.
4. Длина ID: 4 символа.
5. Показать `CLIENT_ID` в настройках/профиле.
6. Использовать `CLIENT_ID` как default user id.
7. Не делать UUID.
8. Не делать криптографический ключ.

Готово, когда:

- `CLIENT_ID` создаётся при первом открытии и переживает reload;
- ID отображается пользователю;
- ID можно использовать как автора сообщения;
- документация честно говорит про коллизии.

## Этап 4. Локальный Профиль И Настройки

Цель: пользователь может сохранить минимальную конфигурацию.

Статус: базово реализовано в `messenger.html`. Есть first-run экран, acceptance privacy warning, display name, provider/repo/token в `localStorage`, экран настроек и сброс профиля.

Шаги:

1. Добавить first-run screen после feature detection.
2. Сохранить acceptance privacy warning.
3. Сохранить display name.
4. Сохранить git provider/repo config.
5. Сохранить token в `localStorage` с явным warning.
6. Добавить screen/section для просмотра и сброса настроек.

Готово, когда:

- reload браузера сохраняет профиль;
- пользователь видит warning до сохранения токена;
- можно сбросить local state без ручного DevTools-шаманства.

## Этап 5. IndexedDB Storage

Цель: хранить индекс сообщений и outbox локально.

Статус: базово реализовано в `messenger.html`. Есть маленький IndexedDB wrapper, schema version `3`, stores `messages`, `chats`, `users`, `members`, `outbox`, `meta`, `repoFiles`, операции для сообщений, поиска, outbox, локального read-state чатов, сброса индекса и локального test repo. До Send/Receive Loop это инфраструктурный слой, а не полноценный пользовательский поток отправки.

Шаги:

1. Создать минимальный IndexedDB wrapper.
2. Stores: `messages`, `chats`, `users`, `members`, `outbox`, `meta`.
3. Добавить schema version.
4. Добавить операции `putMessage`, `listMessages`, `searchMessages`, `putOutbox`, `listOutbox`, `deleteOutbox`.
5. Добавить rebuild/reset index action.
6. Обрабатывать ошибки storage понятным UI-сообщением.

Готово, когда:

- сообщения переживают reload;
- outbox переживает reload;
- локальные индикаторы новых сообщений переживают reload/reindex, но не пишутся в git;
- можно пересобрать индекс;
- storage layer остаётся маленьким и читаемым.

## Этап 6. Protocol V1

Цель: определить файловую модель сообщений.

Статус: базово реализовано в `messenger.html` и описано в `docs/protocol-v1.md`. Есть helpers `window.MacaroniProtocol` для `.macaroni/protocol.json`, user document, chat meta, members, text message, inbox notification, repo paths, генерации `chat_id`/`message_id` и минимальной validation без dependency.

Шаги:

1. Описать `.macaroni/protocol.json`.
2. Описать `.macaroni/users/<client_id>.json`.
3. Описать `.macaroni/chats/<chat_id>/meta.json`.
4. Описать `.macaroni/chats/<chat_id>/members.json`.
5. Описать `.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json`.
6. Описать `.macaroni/inbox/<recipient>/<message_id>.json`.
7. Реализовать генерацию `chat_id`.
8. Реализовать генерацию `message_id`.
9. Реализовать минимальную runtime validation без тяжёлой dependency.

Готово, когда:

- можно создать валидный chat meta;
- можно создать валидное text message;
- путь сообщения детерминирован из `created_at`, `from` и `message_id`;
- invalid JSON не валит приложение целиком.

## Этап 7. Локальный Test Repo Adapter

Цель: проверить протокол без удалённого git provider.

Статус: базово реализовано в `messenger.html` как `window.MacaroniTestRepo`. Adapter хранит repo files в IndexedDB store `repoFiles`, умеет `write/read/list`, init layout, создать чат, записать сообщение + inbox notification и пересобрать индекс из repo files.

Шаги:

1. Сделать in-browser/local test adapter, который имитирует repo files в IndexedDB.
2. Поддержать операции read/write/list для repo paths.
3. Поддержать init repo layout.
4. Поддержать создание chat/message/inbox files.
5. Поддержать reindex из test repo.

Готово, когда:

- можно создать чат без реального удалённого git;
- можно отправить сообщение в локальный test repo;
- индекс пересобирается из repo files;
- UI уже похож на рабочий мессенджер, а не на мокап.

## Этап 8. Send/Receive Loop

Цель: вертикальный поток сообщения внутри MVP.

Статус: базово реализовано для local test repo в `messenger.html`. Composer создаёт draft, пишет text message в `repoFiles`, создаёт inbox notification для тестового получателя `K2XM`, индексирует сообщение, показывает его в UI, переживает reload через reindex и умеет retry outbox через кнопку "Обновить". Remote provider пока не подключён.

Шаги:

1. Composer создаёт message draft.
2. Message получает `CLIENT_ID` как автора.
3. Message пишется в repo files.
4. Inbox notification пишется получателю.
5. Message индексируется локально.
6. UI показывает новое сообщение.
7. При ошибке запись попадает в outbox.
8. Retry outbox по кнопке и при sync.

Готово, когда:

- сообщение появляется в истории;
- reload не теряет сообщение;
- ошибка отправки не теряет draft/outbox item;
- повторная индексация не создаёт дубликаты.

## Этап 9. Git Provider Adapter

Цель: подключить первый реальный remote flow.

Статус: частично реализовано в `messenger.html` как `window.MacaroniGitHub` и описано в `docs/github-provider.md`. Первый provider - GitHub через REST Contents API. Adapter умеет parse repo URL, read file/json, list directory, write file/json с Base64 content и `sha` при update. Если в профиле есть GitHub token, composer пишет через GitHub Contents API; без token GitHub repo работает как read-only public repo. UI показывает текущий transport, sync state и outbox count. Sync пока простой: все chat meta, обход messages по `YYYY/MM/DD`, плюс чтение `.macaroni/inbox/<CLIENT_ID>` как receive hint, без Git Trees API. Перед полным GitHub reindex клиент проверяет последний commit SHA branch и пропускает обход Contents API, если repo не изменился. Для GitHub-профиля включён polling: 30 секунд с token, 60 секунд read-only; клиент не ставит hidden tabs на паузу, но браузер может throttling-ить фоновые таймеры.

Шаги:

1. Выбрать один provider для первого реального адаптера.
2. Зафиксировать ограничения provider в docs.
3. Реализовать auth/token warning.
4. Реализовать read repo files.
5. Реализовать write repo files.
6. Реализовать commit/push или provider API equivalent.
7. Реализовать pull/fetch или provider API equivalent.
8. Прятать raw git/provider errors за человеческими сообщениями.

Готово, когда:

- два экземпляра `messenger.html` работают через один удалённый repo;
- пользователь видит sync status;
- ошибки auth/network не ломают локальную очередь;
- документация честно говорит, какой provider реально поддержан.

## Этап 10. UI MVP

Цель: сделать приложение пригодным для регулярного использования маленькой группой.

Языковая договорённость: английский является дефолтным языком `README.md`, `index.html` и пользовательского интерфейса `messenger.html`. Русские документы сохраняются как локализация и исторический контекст, но новый пользовательский вход по умолчанию английский. В UI доступен переключатель English/Русский в настройках; выбранный язык хранится в профиле и `localStorage`, а строки интерфейса лежат в browser-side объекте `window.MacaroniI18n`.

Шаги:

1. Sidebar со списком чатов.
2. Message list с читаемой группировкой.
3. Composer.
4. Empty states.
5. Sync status.
6. Outbox status.
7. Settings/profile screen.
8. Reindex/reset controls.
9. Search input.
10. Language selector.
11. Mobile/narrow layout.

Текущая UI-договорённость для мобильной версии: sidebar не растягивает список чатов пустотой, чаты идут компактной горизонтальной лентой, composer полностью помещается в экран и не прилипает к нижнему краю.

Sync/outbox status показывается в header текущего чата: transport (`GitHub`, `GitHub read-only`, `local test repo`), действие и размер outbox.

Search input находится в header текущего чата и фильтрует локальный индекс текущего чата.

Reindex/reset controls находятся в настройках. `Сбросить` удаляет профиль, индекс и local test repo; `Пересобрать индекс` пересобирает только локальный кеш из выбранного provider/repo и не создаёт новые remote-файлы.

Composer отправляет сообщение участникам текущего чата из `members.json`, исключая текущий `CLIENT_ID`. Hardcoded `K2XM` остаётся только fallback для старых или битых repo.

Composer работает optimistic: после Enter поле сразу очищается, сообщение сразу попадает в локальный индекс и отображается в текущем чате, а запись в git идёт в фоне. Если git write падает, готовое сообщение сохраняется в outbox для retry.

Новые сообщения сохраняют `from_name` как снимок отображаемого имени на момент отправки. Рендер автора использует `from_name`, затем локальный кеш `.macaroni/users`, затем `members.json`, и только потом показывает короткий `CLIENT_ID`.

Подключение к чату означает, что текущий `CLIENT_ID` добавлен в `members.json`. Если пользователь открыл чат, но его ID там нет, `Инфо о чате` предлагает вступить и записывает текущего пользователя в `members.json`.

Если `members.json` отсутствует, `Инфо о чате` показывает fallback-участника из `meta.created_by`; при вступлении клиент создаёт `members.json` и добавляет текущий `CLIENT_ID`.

Если пользователь добавляет GitHub token после read-only режима, сохранение настроек автоматически запускает retry outbox. Кнопка `Обновить` остаётся ручным retry.

Sidebar строится из локального `chats` store после init/reindex. Клик по чату меняет текущий `chat_id`, заголовок и список сообщений; статический список в HTML является только стартовой заглушкой до инициализации.

Индикаторы новых сообщений считаются локально: `meta` хранит последний прочитанный message marker для каждого чата, sidebar показывает count входящих сообщений новее этого marker, открытие чата помечает его прочитанным. Git не хранит read receipts.

Sync/reindex сохраняет выбранный чат, если этот `chat_id` всё ещё есть в индексе. Клиент не должен перескакивать в другой чат перед отправкой сообщения.

Отправка сообщения использует выбранный на момент submit `chat_id`. Если чат уже выбран, composer не вызывает default-chat fallback и не меняет активный чат перед записью.

Кнопка `+` создаёт новый чат через простой prompt с названием, добавляет текущий `CLIENT_ID` и default peer в `members.json`, затем сразу открывает созданный чат.

`Инфо о чате` показывает краткую сводку текущего чата: title, `chat_id`, участников из `members.json`, transport и размер outbox. Это минимальный debug UI перед реальным remote roundtrip.

Готово, когда:

- основные действия видны без инструкции;
- raw git vocabulary не торчит в пользовательском интерфейсе;
- текст не налезает на controls;
- интерфейс плотный, чистый и без декоративного цирка.

## Этап 11. Поиск

Цель: локальный поиск по индексу.

Статус: базово реализовано в `messenger.html`. Search input делает простой substring search по `text`, `from`, `from_name`, отображаемому имени автора из `users/members`, `chat_id`, `created_at`, фильтрует текущий чат, подсвечивает первый результат, переводит на него focus/scroll и переживает reload/reindex.

Шаги:

1. Индексировать `text`, `from`, `from_name`, отображаемое имя автора, `chat_id`, `created_at`.
2. Сделать простой substring search.
3. Добавить фильтр по текущему чату.
4. Добавить переход к найденному сообщению. Готово: первый результат получает focus и `search-hit`.
5. Не добавлять full-text engine до реальной необходимости.

Готово, когда:

- поиск работает после reload;
- поиск работает после reindex;
- на маленьком repo он быстрый без сложной зависимости.

## Этап 12. End-To-End Проверка MVP

Цель: доказать, что это полноценное приложение, а не смешной HTML-макет.

Статус: добавлен повторяемый smoke harness `scripts/mvp-smoke.js`. Он проверяет unsupported screen, first-run, генерацию и persistence `CLIENT_ID`, профиль, создание чата, отправку, reload, reindex, поиск, outbox/retry, GitHub send/reindex/read-only через fake Contents API и двухклиентную адресацию через локально сохранённый `CLIENT_ID = "K2XM"`.

Локальная команда:

```sh
node scripts/mvp-smoke.js
```

Требуется Node.js с доступным `playwright`, например после `npm install -D playwright`.

Шаги:

1. Проверить двойной клик по `messenger.html`.
2. Проверить unsupported browser screen.
3. Проверить first-run privacy warning.
4. Проверить `CLIENT_ID`.
5. Проверить создание профиля.
6. Проверить создание чата.
7. Проверить отправку сообщения.
8. Проверить получение сообщения вторым профилем.
9. Проверить outbox при ошибке.
10. Проверить retry.
11. Проверить reload/restart.
12. Проверить reindex.
13. Проверить поиск.

Готово, когда:

- два профиля обмениваются сообщениями;
- ни одно сообщение не теряется при reload;
- известные ограничения описаны в docs;
- итоговый артефакт остаётся одним HTML-файлом.

## После MVP

Дальше только после рабочего `messenger.html`:

1. Второй git provider adapter.
2. Import existing repo: частично сделано как явная кнопка `Import Repo` в настройках; она пересобирает локальный IndexedDB-кеш из выбранного `.macaroni/` repo и не пишет remote-файлы.
3. Read-only public repo mode: частично сделано для GitHub public repo без token; клиент читает историю, показывает `GitHub read-only`, но не создаёт чаты и не отправляет сообщения без write token.
4. URL attachments: частично сделано как безопасный auto-link `http://`/`https://` в тексте сообщения, без бинарных файлов и preview.
5. Markdown rendering: частично сделано как безопасный inline-render `**bold**`, `*italic*`, `` `code` `` в UI сообщений, без HTML passthrough и без полноценного CommonMark-движка.
6. Basic notifications: частично сделано как unread count в `document.title`, без Browser Notification API и permission prompts.
7. Receipts как append-only события: частично сделано как `read` receipt files в `.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/`, которые пишутся только при продвижении последнего прочитанного message marker.
8. HTML export of chat history: частично сделано как локальный экспорт текущего чата из IndexedDB в standalone HTML-файл, без записи в git.
9. Electron/WebView wrapper над тем же HTML.
10. Plugin boundary.

## Что Не Делаем До MVP

- UUID вместо `CLIENT_ID`.
- E2E encryption.
- PGP/age plugin.
- Вложения в git.
- Realtime.
- WebSocket.
- Backend Macaroni.
- `localhost` workaround.
- Framework migration ради красоты.
- Build pipeline, если один HTML можно поддерживать без него.
