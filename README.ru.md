# Ветка Памяти Macaroni

[![Agent Memory](https://img.shields.io/badge/agent_memory-git-black)](#какую-проблему-это-решает)
[![Vector DB](https://img.shields.io/badge/vector_db-absolutely_not-black)](#что-это-такое)
[![Summary Soup](https://img.shields.io/badge/summary_soup-refused-black)](#какую-проблему-это-решает)
[![Backend](https://img.shields.io/badge/backend-still_none-black)](#что-это-такое)

Английский оригинал: `README.md`.

## Постоянная память для агентов, реализованная как Git-ветка

Агенты забывают.

Сначала у них есть context window.

Потом summary.

Потом summary summary.

Потом через три недели вся история проекта превращается в:

```text
Мы обсуждали архитектуру.
```

Это не память.

Это суп.

Ветка `macaroni` делает наоборот:

> Хранит реальный разговор как сообщения `.macaroni/` в git.

Без vector database.

Без SaaS memory feature.

Без dashboard с градиентом.

Просто JSON-файлы, git history и неприятное понимание, что репозиторий помнит лучше агента, который в нем работает.

К сожалению, это работает.

## Что Это Такое

Эта ветка - долговременная память проекта Macaroni Messenger и агентов, которые над ним работают.

У нее две задачи:

1. держать runtime-данные `.macaroni/` отдельно от ветки исходников;
2. давать будущим агентам точную историю разговоров вместо пережеванного фольклора.

Приложение живет в `main`.

Память живет здесь.

Скрытый лор тоже здесь, потому что у софтверных проектов теперь, видимо, бывает скрытый лор.

Модель слоев:

```text
.macaroni/ = canonical append-only log разговоров
memory/    = optional curated index поверх .macaroni
protocol/  = инструкции для агентов и людей
skills/    = reusable Codex tooling
```

Если `memory/` и `.macaroni/` расходятся, верьте `.macaroni/`.

`memory/` - карта.

`.macaroni/` - территория.

Git - сомнительный, но долговечный подвал, где все это лежит.

## Какую Проблему Это Решает

Современные агенты наследуют lossy context.

Они часто знают, что какое-то решение было принято, но не знают:

- кто это сказал;
- что именно было написано;
- какие возражения появились;
- почему альтернативу отвергли;
- какая шутка случайно стала архитектурой.

Macaroni Memory хранит исходные сообщения.

Будущий агент может прочитать первоисточник, а не гадать по summary, которое три раза пережевали предыдущие инструменты.

Workflow намеренно тупой:

```text
git checkout macaroni
read .macaroni/
remember what happened
write new messages
git push
```

Это agent-agnostic memory.

Codex может использовать.

Claude может использовать.

Будущий агент с context window на 400 страниц и тяжелым характером тоже может использовать.

Память принадлежит git, а не аккаунту вендора.

## Lore Branch

Шутка замыкается сама на себя:

```text
Macaroni Messenger
  -> Git
    -> Messages
```

потом превращается в:

```text
macaroni branch
  -> project memory
    -> agent memory
      -> protocol lore
```

Так у проекта появляется канонический hidden layer.

Теперь существует вполне нормальный workflow агента:

```text
checkout main
read README
checkout macaroni
understand why the project exists
```

Это почти игровая механика.

`main` - main quest.

`macaroni` - lore branch.

Полезная часть в том, что шутка решает настоящую проблему: люди забывают, модели сбрасываются, инструменты меняются, провайдеры обновляются, а репозиторий остается.

Поэтому `macaroni` становится portable context artifact.

Контекст больше не принадлежит:

- человеку;
- модели;
- компании;
- сервису.

Он принадлежит репозиторию.

Это слишком хорошо ложится на философию Macaroni:

> Используйте самые простые строительные блоки, которые могут сработать.

Похоже, самый простой возможный слой долговременной памяти для агентов:

```text
git checkout macaroni
```

Либо это хорошая идея, либо проект окончательно принял свою природу.

Оба исхода подходят.

## Что Здесь Лежит

Ветка исходников:

- `main` содержит `messenger.html`, продуктовые документы, release notes, скриншоты и публичные метаданные проекта.

Runtime memory:

- [`.macaroni/protocol.json`](.macaroni/protocol.json);
- [`.macaroni/users/*.json`](.macaroni/users/);
- [`.macaroni/chats/*/meta.json`](.macaroni/chats/);
- [`.macaroni/chats/*/members.json`](.macaroni/chats/);
- [`.macaroni/chats/*/messages/YYYY/MM/DD/*.json`](.macaroni/chats/);
- [`.macaroni/chats/*/receipts/*/YYYY/MM/DD/*.json`](.macaroni/chats/);
- [`.macaroni/inbox/*/*.json`](.macaroni/inbox/).

Curated memory indexes:

- [`memory/timeline.md`](memory/timeline.md) `сгенерировано агентом`;
- [`memory/decisions.md`](memory/decisions.md) `сгенерировано агентом`;
- [`memory/open-questions.md`](memory/open-questions.md) `сгенерировано агентом`;
- [`memory/experiments.md`](memory/experiments.md) `сгенерировано агентом`;
- [`memory/agent-native-knowledge-layer.md`](memory/agent-native-knowledge-layer.md) `сгенерировано агентом`;
- [`memory/agent-notes/*.md`](memory/agent-notes/) `сгенерировано агентом`.

Protocol notes:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `сгенерировано агентом`;
- [`protocol/agent-memory-prompts.md`](protocol/agent-memory-prompts.md) `сгенерировано агентом`.

Codex skill:

- [`skills/macaroni-memory/SKILL.md`](skills/macaroni-memory/SKILL.md) `сгенерировано агентом`;
- [`skills/macaroni-memory/scripts/write_messages.py`](skills/macaroni-memory/scripts/write_messages.py) `сгенерировано агентом`;
- [`skills/macaroni-memory/agents/openai.yaml`](skills/macaroni-memory/agents/openai.yaml) `сгенерировано агентом`.

Русские зеркала документации:

- [`README.ru.md`](README.ru.md) `сгенерировано агентом`;
- [`AGENTS.ru.md`](AGENTS.ru.md) `сгенерировано агентом`;
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `сгенерировано агентом`;
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `сгенерировано агентом`;
- [`protocol/agent-memory-prompts.ru.md`](protocol/agent-memory-prompts.ru.md) `сгенерировано агентом`;
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
- [`.macaroni/README.md`](.macaroni/README.md) - runtime data root и safety note для точной памяти.
- [`.macaroni/README.ru.md`](.macaroni/README.ru.md) `сгенерировано агентом` - русское зеркало заметки runtime data root.

Документы протокола:

- [`protocol/macaroni-protocol.md`](protocol/macaroni-protocol.md) `сгенерировано агентом` - как агентам читать и писать `.macaroni/`.
- [`protocol/macaroni-protocol.ru.md`](protocol/macaroni-protocol.ru.md) `сгенерировано агентом` - русское зеркало.
- [`protocol/agent-memory-prompts.md`](protocol/agent-memory-prompts.md) `сгенерировано агентом` - copy-paste prompts для загрузки и записи Macaroni memory.
- [`protocol/agent-memory-prompts.ru.md`](protocol/agent-memory-prompts.ru.md) `сгенерировано агентом` - русское зеркало.

Codex skill:

- [`skills/macaroni-memory/SKILL.md`](skills/macaroni-memory/SKILL.md) `сгенерировано агентом` - устанавливаемый Codex skill для `.macaroni` extended memory.
- [`skills/macaroni-memory/scripts/write_messages.py`](skills/macaroni-memory/scripts/write_messages.py) `сгенерировано агентом` - helper, который пишет Protocol v1 message JSON и inbox pointers.
- [`skills/macaroni-memory/agents/openai.yaml`](skills/macaroni-memory/agents/openai.yaml) `сгенерировано агентом` - UI metadata skill.

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

Эта ветка документирует план storage branch и уже содержит рабочий capture памяти агента.

Живые protocol data лежат здесь:

```text
.macaroni/chats/chat_20260614_agent_room/
```

Эта комната - первый реальный тест `.macaroni/` как постоянной памяти для разговоров пользователя и агента.

Поддержка storage branch внутри `messenger.html` все еще является запланированной продуктовой фичей.

Следующий шаг реализации - добавить поддержку `storage_branch` в `messenger.html`.

После этого эта ветка станет рекомендуемой веткой хранения и для обычных сообщений Macaroni Messenger.

Агенты уже могут использовать `.macaroni/` как точную память разговоров, а `memory/` как durable indexes.

## Финальное Правило

`main` - для мессенджера.

`macaroni` - для сообщений.

Держите код вне пасты.

Держите пасту вне кода.

Держите память достаточно читаемой, чтобы будущему агенту не пришлось вызывать духов.
