# Заметки О Протоколе `.macaroni/`

Этот документ предназначен для агентов, работающих в ветке `macaroni`.

Авторитетный продуктовый протокол все еще живет в документации ветки исходников.

Этот файл объясняет, как будущим агентам думать о `.macaroni/`, когда ветка используется как хранилище и память.

Английский оригинал: `macaroni-protocol.md`.

Короткая версия:

> `.macaroni/` - это способ будущему агенту прочитать, что на самом деле произошло, вместо того чтобы наследовать "мы обсуждали архитектуру" и молча страдать.

## Основная Идея

`.macaroni/` - git-native хранилище сообщений.

Протокол намеренно скучный:

- JSON-файлы;
- предсказуемые пути;
- append-friendly записи;
- git history как источник истины;
- browser storage как cache;
- без backend-owned database.

Транспортом может быть GitHub API, GitLab API, GitVerse API, generic git HTTP, wrapper или что-то еще.

Сохраняемая форма остается `.macaroni/`.

Это не замена мессенджеру.

Это не замена продуктовой документации.

Это не священный knowledge graph.

Это сообщения в git.

Тревожная часть в том, что этого достаточно.

## Agent-Agnostic Memory Extension

Для агентов `.macaroni/` - это больше, чем хранилище чата.

Это agent-agnostic расширение памяти.

Оно сохраняет точные сообщения в git вместо того, чтобы сжимать их в summary, принадлежащее конкретному model runtime.

Это важно, потому что будущий агент может прочитать:

- что пользователь написал;
- что ассистент ответил;
- какие возражения появились;
- какое решение приняли;
- какую альтернативу отвергли;
- какая формулировка была важна.

Без раскопок context window.

Без summary of summary of summary.

Просто файлы.

Правило:

```text
.macaroni/ = точный исходный разговор
memory/    = отобранные выводы и индексы
protocol/  = инструкции по использованию протокола
```

Агенты не должны путать эти слои.

## Структура Директорий

```text
.macaroni/
  protocol.json
  users/
    <client_id>.json
  chats/
    <chat_id>/
      meta.json
      members.json
      messages/
        YYYY/
          MM/
            DD/
              <message_id>.json
      receipts/
        <client_id>/
          YYYY/
            MM/
              DD/
                <receipt_id>.json
  inbox/
    <client_id>/
      <message_id>.json
```

## Документ Репозитория

Путь:

```text
.macaroni/protocol.json
```

Назначение:

- объявляет версию протокола;
- хранит repository-level metadata;
- дает клиентам дешевую sanity check, что репозиторий говорит на Macaroni.

## Пользователи

Путь:

```text
.macaroni/users/<client_id>.json
```

Назначение:

- хранит client/user identity;
- сопоставляет короткие id вроде `SA6E`, `K2XM`, `AG01` с display names;
- само по себе ничего не аутентифицирует.

Пользователь Macaroni намеренно простой:

```text
client id + display name + git access
```

Без церемонии регистрации.

Без user table в священной базе данных.

## Чаты

Метаданные:

```text
.macaroni/chats/<chat_id>/meta.json
```

Участники:

```text
.macaroni/chats/<chat_id>/members.json
```

Сообщения:

```text
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Receipts:

```text
.macaroni/chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
```

Chat metadata описывает комнату.

Members описывают ожидаемых участников.

Messages - источник истории чата.

Receipts - append-only события.

## Inbox

Путь:

```text
.macaroni/inbox/<client_id>/<message_id>.json
```

Назначение:

- помогает клиентам находить сообщения, адресованные им;
- указывает на message files;
- не является источником истины.

Если inbox и message history расходятся, побеждает message history.

Git помнит, inbox помогает.

## Правила Сообщений

Сообщения - JSON-документы.

Ожидаемые свойства:

- `version`;
- `id`;
- `chat_id`;
- `type`;
- `from`;
- `from_name`;
- `to`;
- `created_at`;
- `text`;
- `reply_to`;
- `attachments`;
- `meta`;
- `signature`.

Агенты должны сохранять неизвестные поля.

Агенты не должны переписывать старые message files.

Агенты должны добавлять новые файлы.

## Захват Разговора Пользователь-Агент

Агенты могут записывать разговор с пользователем в `.macaroni/` как Protocol v1 messages.

Это предназначено для значимого проектного контекста, а не для каждого микровзаимодействия.

Copy-paste prompts для загрузки и записи этой памяти лежат в [`agent-memory-prompts.ru.md`](agent-memory-prompts.ru.md).

Используйте это, если обмен содержит:

- решения;
- требования;
- исправления;
- архитектурные ограничения;
- product positioning;
- protocol agreements;
- security rules;
- release decisions;
- implementation results.

### Комната

Комната по умолчанию:

```text
AGENT_ROOM
```

Рекомендуемый chat id:

```text
chat_YYYYMMDD_agent_room
```

Допустимы специализированные комнаты:

```text
ARCHITECTURE_ROOM
PROTOCOL_ROOM
ENCRYPTION_ROOM
STORAGE_BRANCH_ROOM
```

### Идентификаторы Участников

Рекомендуемые id:

```text
HUMAN
CODEX
CLAUDE
DEEPSEEK
AGENT
```

Используйте стабильные id.

Не создавайте новый agent id для каждого запуска.

### Порядок Захвата

Для значимого обмена:

1. Отредактировать чувствительные значения.
2. Записать сообщение пользователя как отдельный JSON message file.
3. Записать ответ ассистента как отдельный JSON message file.
4. Записать inbox pointers для получателей.
5. Закоммитить batch в ветку `macaroni`.
6. Обновить `memory/`, если обмен создал durable conclusions.

Протокол message-by-message.

Git commit может включать несколько сообщений.

### Metadata Сообщений

Captured messages должны включать metadata:

```json
{
  "meta": {
    "captured_by": "CODEX",
    "source": "user_message",
    "redacted": true
  }
}
```

Для assistant messages:

```json
{
  "meta": {
    "captured_by": "CODEX",
    "source": "assistant_message",
    "redacted": false
  }
}
```

Ставьте `redacted` честно.

Если значение было заменено на `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `EMAIL`, `PHONE` или `REDACTED`, используйте `true`.

### Почему Message-By-Message

Message-by-message storage позволяет будущим агентам восстановить реальный обмен.

Он сохраняет:

- порядок;
- speaker;
- timestamp;
- точные формулировки;
- corrections;
- disagreements;
- decisions.

В этом смысл `.macaroni/` как памяти.

Если агент пишет только summary, проект теряет именно то, ради чего существует этот протокол.

## Шифрование

Шифрование - plugin layer.

Оно не меняет пути протокола `.macaroni/`.

Зашифрованный текст выглядит так:

```text
MACARONI1.01:<base64-json>
```

Агенты MUST NOT хранить encryption secrets в этой ветке.

Агенты MAY документировать, что шифрование существует.

Агенты MUST NOT вставлять keys, salts, tokens или private material в memory files.

Используйте маркеры:

```text
СЕКРЕТ
ПАРОЛЬ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
REDACTED
```

## Ветка Хранилища

Рекомендуемая ветка хранилища:

```text
macaroni
```

Не:

```text
.macaroni
```

Git не принимает `.macaroni` как имя ветки.

Ветка - `macaroni`.

Директория - `.macaroni/`.

Это ровно та техническая комедия, которую проект принимает.

## Workflow Агента

При чтении `.macaroni/`:

1. Check out или fetch storage branch.
2. Прочитать `.macaroni/protocol.json`.
3. Прочитать users и chat metadata.
4. Читать messages в chronological path order.
5. Считать receipts и inbox helper state.
6. Сохранять encrypted payloads, если нет легитимных локальных decrypt settings.

При записи `.macaroni/`:

1. Писать только machine-readable JSON.
2. Добавлять новые файлы вместо редактирования старой истории.
3. Использовать стабильные ids.
4. Держать пути сообщений deterministic по UTC date.
5. Обновлять inbox pointers для получателей.
6. Добавлять receipts отдельными append-only files.
7. Коммитить в storage branch.

Для документирования reasoning проекта:

Используйте `memory/`, не `.macaroni/`.

Для документирования поведения протокола:

Используйте `protocol/`, не `.macaroni/`.

Для отправки настоящих сообщений:

Используйте `.macaroni/`, не `memory/`.

## Правило Безопасности

Перед коммитом в эту ветку сканируйте секреты.

Если полезная заметка содержит чувствительные данные, замените значение:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
EMAIL
PHONE
REDACTED
```

Память, которая сливает секреты, - не память.

Это инцидент.
