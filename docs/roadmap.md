# Roadmap

Roadmap фиксирует актуальное понимание Macaroni Messenger: это маленький git-backed messenger, который в базовой поставке является одним файлом `messenger.html`.

## Текущее понимание задачи

Macaroni Messenger - не "JS-first приложение с возможным web target".

Macaroni Messenger - это **single-file HTML messenger**.

Главное обещание продукта:

> Скачать или сохранить один HTML-файл, открыть его в браузере и получить рабочий мессенджер поверх git.

Главный installation flow:

> Двойной клик по локальному `messenger.html`.

Backend отсутствует.

Регистрация в Macaroni отсутствует.

Git является источником истины.

Локальный индекс является кешем.

Приватность не обещается.

## Product Contract

Базовый клиент:

- поставляется как `messenger.html`;
- открывается локально через `file://` в совместимом браузере;
- содержит HTML, CSS и JavaScript внутри одного файла;
- не требует установки сервера;
- не требует `localhost`;
- не требует базы данных за пределами browser storage;
- работает с git-репозиторием через browser-compatible transport;
- объясняет пользователю, что сообщения не приватны.

Поддерживаются только браузеры, которые дают нормальный persistent storage для локального HTML-файла.

Остальные браузеры считаются несовместимыми. Проект не обязан тащить локальный сервер, чтобы чинить браузерные ограничения.

Дополнительные оболочки допустимы:

- Electron;
- Tauri/WebView;
- мобильный WebView;
- локальный desktop wrapper.

Но оболочки не являются продуктовым центром. Они запускают тот же HTML-клиент или минимально оборачивают его.

## Не Делаем

- Telegram replacement.
- Собственный backend.
- Собственную регистрацию.
- Realtime-доставку.
- Сложную криптографию в ядре.
- Хранение больших бинарников в git.
- Удаление сообщений с обещанием "стерто навсегда".
- Абстрактную платформу до появления рабочего `messenger.html`.
- Enterprise-слои ради архитектурного косплея.

## Делаем

- Один `messenger.html`.
- Двойной клик как основной запуск.
- Git-backed текстовые сообщения.
- Локальный индекс в browser storage.
- Polling/sync через git-compatible flow.
- Честный privacy warning.
- Feature detection при первом запуске.
- Красивый экран несовместимости для неподдерживаемых браузеров.
- Оффлайн-очередь исходящих.
- Простую UI-схему: chats, messages, composer, sync status.
- Подробный product brief отдельно от короткого README.

## Зафиксированные Решения

- Название: **Macaroni Messenger**.
- Первый артефакт: `messenger.html`.
- Базовый протокол: **Macaroni Protocol v1**.
- Источник истины: git repository.
- Runtime MVP: browser.
- UI MVP: vanilla HTML/CSS/JS или минимальный build output, который всё равно собирается в один HTML-файл.
- Storage MVP: `localStorage` для токена/настроек, `IndexedDB` для индекса/кеша.
- Compatibility MVP: `file://` origin storage, `localStorage`, `IndexedDB`, `WebCrypto`.
- Recommended browsers: Chrome / Chromium / Edge.
- Transport MVP: browser-compatible HTTPS/API/git adapter. Прямой SSH из браузера не является MVP.
- Сообщение: immutable JSON-файл.
- Ветка сообщений: `main`.
- Вложения MVP: только URL или вообще без вложений.
- Редактирование/удаление MVP: нет. Позже - отдельные события.
- Шифрование MVP: нет. Позже - plugin layer.

## Документы

- `README.md` - короткая витрина проекта: что это, зачем и почему один HTML-файл.
- `docs/product-brief.md` - подробный исходный бриф с моделью данных, философией, UX и протоколом.
- `docs/roadmap.md` - актуальный план реализации.
- `AGENTS.md` - правила работы в репозитории.

Правило: если меняется продуктовая договорённость, сначала обновляется документация, потом код.

## MVP 0.1: Working Messenger.html

Цель: получить один файл `messenger.html`, который позволяет двум пользователям обменяться текстовыми сообщениями через git-репозиторий без backend'а Macaroni.

Функции:

- feature detection перед onboarding;
- экран несовместимости для неподдерживаемого браузера;
- первый запуск с privacy warning;
- локальный профиль пользователя;
- подключение репозитория;
- сохранение настроек в browser storage;
- инициализация repo layout;
- создание чата;
- добавление участника по username;
- отправка текстового сообщения;
- запись сообщения как JSON-файла;
- запись inbox notification;
- синхронизация с repo;
- polling/ручное обновление;
- локальная индексация сообщений;
- показ списка чатов;
- показ истории сообщений;
- поиск по локальному индексу;
- outbox при ошибке сети/sync;
- восстановление состояния после reload/restart браузера.

Критерии готовности:

- `messenger.html` открывается двойным кликом в поддерживаемом браузере.
- MVP не требует `localhost`.
- Нет обязательной папки assets для запуска MVP.
- Несовместимый браузер получает понятный экран несовместимости.
- Два профиля в одном test repo видят сообщения друг друга.
- Повторная индексация не создаёт дубликаты.
- Ошибка отправки не теряет сообщение.
- Privacy warning виден до первого сообщения.
- README, product brief и roadmap не противоречат фактическому поведению.

## MVP 0.1 Work Plan

1. Документация.
   - Сверить README, product brief, roadmap и AGENTS.
   - Зафиксировать single-file delivery как базовый контракт.
   - Вынести технические детали протокола из README только в docs.

2. Первый HTML shell.
   - Создать `messenger.html`.
   - Inline CSS.
   - Inline JS.
   - Feature detection до основного UI.
   - Unsupported browser screen.
   - Рабочий layout: sidebar, messages, composer, status bar.
   - Privacy warning modal/first-run screen.

3. Protocol v1.
   - `protocol.json`.
   - `users/<user>.json`.
   - `chats/<chat_id>/meta.json`.
   - `chats/<chat_id>/members.json`.
   - `chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json`.
   - `inbox/<user>/<message_id>.json`.
   - Минимальные validators без тяжёлой dependency.

4. Browser storage.
   - Проверить доступность storage на `file://`.
   - `localStorage` для токена и настроек.
   - `IndexedDB` для messages index и outbox.
   - Профиль.
   - Repo config.
   - Messages index.
   - Outbox.
   - First-run/privacy acceptance flag.
   - Rebuild index command.

5. Git transport.
   - Выбрать самый простой browser-compatible adapter.
   - Зафиксировать его ограничения в docs.
   - Поддержать init/read/write/sync для MVP.
   - Не показывать пользователю raw git errors.

6. Send/receive loop.
   - Создание message JSON.
   - Уникальный message id.
   - Append-only запись.
   - Sync before/after send.
   - Polling/manual refresh.
   - Outbox retry.

7. Verification.
   - Локальный test repo.
   - Два профиля.
   - Send both ways.
   - Browser reload.
   - Offline/sync error.
   - Reindex.
   - Проверка, что итоговый артефакт один HTML-файл.

## Browser Reality Check

Ограничения, которые нельзя замазывать:

- Основной запуск - локальный `file://` файл, а не `localhost`.
- Браузер не умеет обычный SSH git без помощников.
- Git hosting API может иметь CORS/permissions ограничения.
- Personal access token в браузере - чувствительная штука, нужен явный warning.
- GitHub/GitLab/GitVerse могут отличаться API и auth flow.
- Если браузер не даёт persistent storage на `file://`, он не поддерживается.
- Большой repo будет медленно индексироваться.

Практичный MVP может начать с одного поддержанного git-provider adapter или local test adapter. Главное - не врать, что "любой git" уже работает из браузера магически.

Не предлагаем пользователю "поднять локальный сервер" как решение совместимости. Это убивает главный мем проекта.

## Compatibility Screen

Минимальная проверка:

```js
async function checkSupport() {
  const checks = {
    fileProtocol: location.protocol === "file:",
    localStorage: !!window.localStorage,
    indexedDB: !!window.indexedDB,
    crypto: !!window.crypto?.subtle
  };

  return Object.values(checks).every(Boolean);
}
```

Текст экрана:

> Ваш браузер недостаточно смешной для запуска Macaroni Messenger.

Требуется:

- `file://` origin storage;
- `localStorage`;
- `IndexedDB`;
- `WebCrypto`.

Рекомендуется:

- Chrome / Chromium;
- Edge.

## После MVP

0.2:

- GitHub/GitLab/GitVerse provider adapters;
- проверенный support matrix для Chrome/Chromium/Edge;
- импорт существующего repo;
- read-only public repo mode;
- нормальный onboarding;
- ручной export/import настроек;
- reindex/repair tools.

0.3:

- URL attachments;
- markdown rendering;
- basic notifications;
- receipts как append-only события;
- HTML export of chat history;
- Electron/WebView wrapper над тем же `messenger.html`.

0.4:

- plugin boundary;
- PGP/age proof-of-concept plugin;
- bot/client runtime;
- attachment adapters для LFS/WebDAV/S3;
- migration/versioning tools для протокола.

## Правило Отсечения

Если фича не помогает одному `messenger.html` отправить, получить, найти или не потерять текстовое сообщение в маленькой группе, она не входит в MVP.

Если фича требует backend Macaroni, она не входит в базовый продукт.

Если фича требует `localhost`, она подозрительна и по умолчанию не входит в базовый продукт.

Если фича ломает single-file delivery, она должна принести очень понятную пользу. Иначе мимо.
