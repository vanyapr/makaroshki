# Ветка Хранилища Macaroni

Эта ветка намеренно почти пустая.

Это не ветка приложения.

Это не ветка продуктовой документации.

Это не ветка GitHub Pages.

Это будущая ветка хранения данных Macaroni.

И одновременно ветка памяти проекта.

Приложение живет в `main`.

Макароны живут здесь.

Скрытый лор тоже здесь.

Английский оригинал: `README.md`.

## Назначение

Macaroni Messenger может использовать отдельную git-ветку для данных `.macaroni/`, чтобы история чатов не засоряла ветку исходников.

Ветка исходников содержит:

- `messenger.html`;
- документацию;
- release notes;
- скриншоты;
- метаданные проекта.

Ветка хранилища содержит:

- `.macaroni/protocol.json`;
- `.macaroni/users/*.json`;
- `.macaroni/chats/*/meta.json`;
- `.macaroni/chats/*/members.json`;
- `.macaroni/chats/*/messages/YYYY/MM/DD/*.json`;
- `.macaroni/chats/*/receipts/*/YYYY/MM/DD/*.json`;
- `.macaroni/inbox/*/*.json`.

Слой памяти содержит:

- [`memory/timeline.md`](memory/timeline.md) `сгенерировано агентом`;
- [`memory/decisions.md`](memory/decisions.md) `сгенерировано агентом`;
- [`memory/open-questions.md`](memory/open-questions.md) `сгенерировано агентом`;
- [`memory/experiments.md`](memory/experiments.md) `сгенерировано агентом`;
- [`memory/agent-native-knowledge-layer.md`](memory/agent-native-knowledge-layer.md) `сгенерировано агентом`;
- [`memory/agent-notes/*.md`](memory/agent-notes/) `сгенерировано агентом`.

Слой заметок о протоколе содержит:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `сгенерировано агентом`.

Русские зеркала документации:

- [`README.ru.md`](README.ru.md) `сгенерировано агентом`;
- [`AGENTS.ru.md`](AGENTS.ru.md) `сгенерировано агентом`;
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `сгенерировано агентом`;
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `сгенерировано агентом`;
- [`memory/timeline.ru.md`](memory/timeline.ru.md) `сгенерировано агентом`;
- [`memory/decisions.ru.md`](memory/decisions.ru.md) `сгенерировано агентом`;
- [`memory/open-questions.ru.md`](memory/open-questions.ru.md) `сгенерировано агентом`;
- [`memory/experiments.ru.md`](memory/experiments.ru.md) `сгенерировано агентом`;
- [`memory/agent-native-knowledge-layer.ru.md`](memory/agent-native-knowledge-layer.ru.md) `сгенерировано агентом`;
- [`memory/agent-notes/2026-06-14-macaroni-memory.ru.md`](memory/agent-notes/2026-06-14-macaroni-memory.ru.md) `сгенерировано агентом`.

## Карта Документов

Основные документы ветки:

- [`README.md`](README.md) - индекс этой ветки.
- [`README.ru.md`](README.ru.md) `сгенерировано агентом` - русское зеркало индекса ветки.
- [`AGENTS.md`](AGENTS.md) - рабочие правила для будущих агентов.
- [`AGENTS.ru.md`](AGENTS.ru.md) `сгенерировано агентом` - русское зеркало правил для агентов.
- [`.macaroni/README.md`](.macaroni/README.md) - placeholder и safety note для runtime data root.
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `сгенерировано агентом` - русское зеркало заметки runtime data root.

Документы протокола:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `сгенерировано агентом` - как агентам читать и писать `.macaroni/`.
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `сгенерировано агентом` - русское зеркало.

Curated memory indexes:

- [`memory/timeline.md`](memory/timeline.md) `сгенерировано агентом` - timeline памяти проекта.
- [`memory/timeline.ru.md`](memory/timeline.ru.md) `сгенерировано агентом` - русское зеркало.
- [`memory/decisions.md`](memory/decisions.md) `сгенерировано агентом` - durable decisions и reasoning.
- [`memory/decisions.ru.md`](memory/decisions.ru.md) `сгенерировано агентом` - русское зеркало.
- [`memory/open-questions.md`](memory/open-questions.md) `сгенерировано агентом` - unresolved questions.
- [`memory/open-questions.ru.md`](memory/open-questions.ru.md) `сгенерировано агентом` - русское зеркало.
- [`memory/experiments.md`](memory/experiments.md) `сгенерировано агентом` - эксперименты, которые стоит помнить.
- [`memory/experiments.ru.md`](memory/experiments.ru.md) `сгенерировано агентом` - русское зеркало.
- [`memory/agent-native-knowledge-layer.md`](memory/agent-native-knowledge-layer.md) `сгенерировано агентом` - гипотеза agent-native memory.
- [`memory/agent-native-knowledge-layer.ru.md`](memory/agent-native-knowledge-layer.ru.md) `сгенерировано агентом` - русское зеркало.
- [`memory/agent-notes/2026-06-14-macaroni-memory.md`](memory/agent-notes/2026-06-14-macaroni-memory.md) `сгенерировано агентом` - первая заметка агента для ветки.
- [`memory/agent-notes/2026-06-14-macaroni-memory.ru.md`](memory/agent-notes/2026-06-14-macaroni-memory.ru.md) `сгенерировано агентом` - русское зеркало.

`сгенерировано агентом` означает, что ссылка ведет на документ, созданный или поддерживаемый агентами как память проекта. Считайте такие файлы полезными индексами и заметками, а не заменой canonical `.macaroni/` messages или protocol docs из ветки исходников.

И все.

Без фронтенда.

Без маркетингового README.

Без build system.

Без backend, который пытается пролезть через окно.

`.macaroni/` - runtime-данные протокола.

`memory/` - долговременная память проекта для будущих людей и агентов.

`protocol/` - объяснение для агентов, как работать с `.macaroni/`.

Не смешивайте их только потому, что оба слоя смешные.

## Имя Ветки

Ветка называется:

```text
macaroni
```

Ветка не называется:

```text
.macaroni
```

Git не принимает `.macaroni` как валидное имя ветки.

Поэтому директория называется `.macaroni/`, а ветка называется `macaroni`.

Это раздражает.

И это нормально.

## Форма Профиля

Будущие клиентские профили должны различать ветку исходников и ветку хранилища:

```json
{
  "repo": "https://github.com/vanyapr/makaroshki",
  "branch": "main",
  "storage_branch": "macaroni"
}
```

`branch` - место, где живут приложение, исходники и документация.

`storage_branch` - место, где живут данные `.macaroni/`.

Старые профили без `storage_branch` должны продолжать работать через уже настроенную ветку, обычно `main`.

Обратная совместимость первая.

Комедия вторая.

Но комедия все еще есть.

## План Реализации

1. Добавить `storage_branch` в настройки.
2. Новые профили по умолчанию направлять в `macaroni`.
3. Старые профили оставить на текущей ветке, пока пользователь сам не изменит настройки.
4. Научить GitHub provider читать `.macaroni/` из `storage_branch`.
5. Научить GitHub provider писать `.macaroni/` в `storage_branch`.
6. Научить reindex хранить branch-specific metadata, чтобы `main` и `macaroni` не делили stale commit SHA.
7. Добавить detection существования ветки.
8. Если `storage_branch` не существует, для первого MVP создавать ее из default branch.
9. После создания писать сюда только данные `.macaroni/`.
10. Позже добавить advanced action, который создает чистую orphan storage branch только с `.macaroni/`.

Чистая orphan-ветка красивее.

MVP-ветка проще.

Macaroni выбирает рабочую пасту, а не архитектурный парфюм.

## Контракт Провайдера

Каждый provider adapter должен считать `.macaroni/` storage-данными и принимать ветку хранилища отдельно от ветки исходников.

Обязательная форма:

```js
{
  repo: "...",
  branch: "main",
  storage_branch: "macaroni"
}
```

Операции провайдера:

- чтение приложения/исходников может использовать `branch`;
- чтение `.macaroni/` использует `storage_branch`;
- запись `.macaroni/` использует `storage_branch`;
- read receipts используют `storage_branch`;
- inbox notifications используют `storage_branch`;
- создание чата использует `storage_branch`;
- документы user profile используют `storage_branch`.

Если провайдер не может писать в отдельную ветку, он должен сказать это явно.

Никакой тихой пасты в `main`.

## Миграция

Для существующих репозиториев:

1. Создать ветку `macaroni`.
2. Перенести или скопировать существующие данные `.macaroni/` туда.
3. Настроить клиентов с `storage_branch: "macaroni"`.
4. Перестать писать `.macaroni/` в `main`.
5. Опционально почистить историю `main` позже, если вам нравится force-push археология.

Не удаляйте существующие данные `.macaroni/` из `main` молча.

Git помнит.

Пользователь должен сам решать, когда чистить историю.

## Текущий Статус

Эта ветка сейчас документирует план и запускает слой памяти проекта.

Она намеренно пока не содержит live chat data.

Следующий шаг реализации - добавить поддержку `storage_branch` в `messenger.html`.

После этого эта ветка станет рекомендуемой веткой хранения для реальных сообщений Macaroni.

Агенты уже могут использовать `memory/` как durable context.

## Финальное Правило

`main` - для мессенджера.

`macaroni` - для сообщений.

Держите код вне пасты.

Держите пасту вне кода.

Держите память достаточно читаемой, чтобы будущему агенту не пришлось вызывать духов.
