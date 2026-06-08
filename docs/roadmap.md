# Roadmap

Roadmap фиксирует практичный путь к первому рабочему Macaroni Messenger: маленький git-backed async messenger без собственного backend'а, без realtime-обещаний и без приватности по умолчанию.

## Продуктовая позиция

Macaroni Messenger - JS-first клиент для небольших групп, где сообщения являются JSON-файлами в git-репозитории.

Главное платформенное соглашение:

> Мессенджер должен работать на любой платформе, где можно крутить JavaScript.

Ключевая фича:

> Клиент можно развернуть как обычный HTML/JS-документ почти где угодно.

Поэтому ядро проекта не привязывается к Electron, Tauri, конкретному UI-фреймворку, конкретной базе или конкретному способу доступа к git.

Не делаем:

- замену Telegram;
- собственный сервер;
- realtime-доставку;
- шифрование в ядре;
- вложения в git;
- удаление сообщений с обещанием "стерто навсегда";
- enterprise-архитектуру ради красоты.

Делаем:

- простую отправку и получение текстовых сообщений через git;
- локальный индекс через runtime-specific storage adapter;
- статический HTML/JS target без собственного backend'а;
- честное предупреждение о публичности;
- оффлайн-очередь исходящих;
- понятный UI без git-терминов для обычного пользователя.

## Зафиксированные решения

- Рабочее название: **Macaroni Messenger**.
- Базовый протокол: **Macaroni Protocol v1**.
- Базовая архитектура: TypeScript core + runtime adapters.
- Первый важный delivery format: static HTML/JS client.
- Источник истины: git-репозиторий.
- Локальный индекс: storage adapter, пересобираемый из файлов репозитория.
- Первая ветка сообщений: `main`.
- Сообщение: отдельный immutable JSON-файл.
- Редактирование и удаление: только отдельными событиями, не в MVP.
- Вложения в MVP: нет. Позже - только URL/LFS/внешнее хранилище, не бинарники в git по умолчанию.
- Приватность: не обещается. Шифрование только как будущий plugin layer.
- Доставка: polling через `git fetch`/`pull`.
- MVP-коммиты: один commit на сообщение. Батчинг позже, если реально понадобится.

## MVP 0.1

Цель: доказать, что два локальных клиента могут обмениваться текстовыми сообщениями через обычный git-репозиторий без backend'а.

Функции:

- создать локальный профиль пользователя;
- подключить существующий git repo по URL/path;
- инициализировать структуру `protocol.json`, `users/`, `chats/`, `inbox/`;
- создать чат;
- добавить участника по username;
- отправить текстовое сообщение;
- записать сообщение в `chats/<chat_id>/messages/...`;
- записать уведомление в `inbox/<recipient>/...`;
- сделать commit и push;
- делать polling/fetch;
- индексировать новые сообщения через storage adapter;
- показать список чатов и историю;
- искать по локальному индексу;
- сохранить исходящее сообщение локально при ошибке сети;
- пережить restart без потери очереди.

Критерии готовности:

- два пользователя в одном test repo видят сообщения друг друга;
- клиент работает после restart;
- при offline/push error сообщение остается в исходящей очереди;
- повторная индексация не создает дубликаты;
- пользователь видит жирный privacy warning при первом запуске;
- README и roadmap соответствуют реальному поведению.

## Архитектурные слои

Ядро:

- protocol types;
- validation;
- message id generation;
- repo layout helpers;
- indexing pipeline;
- outbox state machine;
- sync orchestration.

Adapters:

- git transport: isomorphic-git, hosting API, Node/local git или другой JS-совместимый backend;
- storage: SQLite, IndexedDB, OPFS, localStorage для демо, in-memory для тестов;
- credentials: OS keychain, browser storage, runtime-specific secret provider;
- UI: React/Svelte/Vue/plain DOM, но не в core.

Правило: core не импортирует UI, Electron, Node-only API или конкретную базу. Runtime-specific код живет в adapters.

## Static HTML target

Это не демо "для галочки", а одна из главных причин существования проекта.

Минимальная версия должна уметь собираться в статический HTML/JS bundle, который можно положить:

- на GitHub Pages;
- GitLab Pages;
- любой static hosting;
- S3-compatible bucket;
- обычный nginx;
- локально рядом с repo;
- на флешку, если очень хочется киберпанка без бюджета.

Ограничения browser target:

- прямой SSH git из браузера не считаем базовым сценарием;
- для remote repo нужен HTTPS/API adapter или hosting-specific flow;
- токены нельзя хранить без явного предупреждения;
- CORS и ограничения git-хостинга должны быть видны в onboarding;
- offline state хранится в IndexedDB/OPFS или другом browser storage.

Правило отсечения: если фича ломает возможность статического HTML target без очень веской причины, она не входит в core.

## План до первого утреннего среза

Минимальный результат "к утру" - не красивый мессенджер на продажу, а проверенный вертикальный прототип.

1. Документация и соглашения.
   - `README.md` прочитан и принят как продуктовая база.
   - `AGENTS.md` фиксирует стиль работы.
   - `docs/roadmap.md` фиксирует MVP, антицели и порядок работ.

2. Проектный скелет.
   - Выбрать первый runnable target без ломки JS-first архитектуры.
   - Считать static HTML/JS target первоклассным, даже если первый dev shell будет проще.
   - Создать минимальную структуру TypeScript core + adapters.
   - Добавить базовые npm scripts: dev, build, lint/typecheck.
   - Не добавлять тяжелые зависимости без отдельного решения.

3. Протокол и файловая модель.
   - Описать JSON-схемы v1 для `protocol.json`, user, chat meta, members, message.
   - Сделать простые валидаторы.
   - Сделать генерацию стабильных message id.

4. Git transport.
   - Подключение локального repo path для первого прототипа.
   - Создание message file.
   - Commit на сообщение.
   - Pull/fetch перед отправкой и при polling.
   - Нормальные пользовательские ошибки без слов "merge conflict".

5. Локальный индекс.
   - Storage interface для messages/chats/outbox.
   - Первый storage adapter для выбранного runtime.
   - Индексация файлов сообщений.
   - Защита от дубликатов по message id.
   - Полная пересборка индекса из repo.

6. UI-прототип.
   - Левая колонка чатов.
   - Правая колонка сообщений.
   - Поле ввода.
   - Кнопка refresh.
   - Индикатор sync status.
   - Privacy warning при первом запуске.

7. Проверка.
   - Два локальных профиля на одном test repo.
   - Отправка туда-обратно.
   - Restart.
   - Offline/push error.
   - Reindex.

## После MVP

0.2:

- remote repo auth/token storage через системный keychain;
- нормальный onboarding;
- read-only режим для публичных repo;
- базовый export в HTML;
- ручной compact/reindex;
- простая настройка polling interval.

0.3:

- receipts как append-only события;
- URL attachments;
- markdown rendering;
- локальные notifications;
- basic bot client API.

0.4:

- plugin boundary для encrypted payload;
- PGP/age proof-of-concept plugin;
- Git LFS/WebDAV/S3 attachment adapters;
- импорт/экспорт чатов.

## Риски

- Git-hosting может ограничивать частые push/fetch.
- Пользовательские токены нельзя хранить в plain text.
- Большие бинарники быстро убьют repo.
- Обычному пользователю нельзя показывать raw git errors.
- Публичность нужно объяснять до первого сообщения, а не в подвале настроек.
- В распределенной истории нельзя честно обещать настоящее удаление.

## Правило отсечения

Если фича не помогает отправить, получить, найти или не потерять текстовое сообщение в маленькой группе, она не входит в MVP.
