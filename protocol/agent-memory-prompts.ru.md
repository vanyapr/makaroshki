# Prompt-Шаблоны Agent Memory

Этот документ содержит copy-paste prompt-шаблоны для использования ветки `macaroni` как расширенной памяти.

Используйте эти prompts при старте новой agent session, продолжении после потери контекста, поиске старых решений или записи завершенного exchange обратно в `.macaroni/`.

Английский оригинал: `agent-memory-prompts.md`.

## Главное Правило

`.macaroni/` - canonical memory.

`memory/` - optional index.

Если они расходятся, верьте `.macaroni/`.

Не храните секреты.

Не храните частичные секреты.

Редактируйте до записи.

## 1. Session Bootstrap Prompt

Используйте это в начале новой Codex-сессии в репозитории:

```text
Используй ветку `macaroni` как расширенную память проекта перед выполнением задачи.

Шаги:
1. Проверь, есть ли в репозитории ветка `macaroni`.
2. Прочитай `.macaroni/protocol.json`.
3. Прочитай `.macaroni/chats/*/meta.json` и `.macaroni/chats/*/members.json`.
4. Прочитай релевантные `.macaroni/chats/*/messages/**.json` в хронологическом порядке.
5. Используй `memory/` только как optional index поверх `.macaroni/`.
6. Кратко перескажи релевантный прошлый контекст со ссылками на source message paths.
7. Потом выполняй задачу пользователя.

Правила:
- `.macaroni/` canonical.
- `memory/` derived.
- Не раскрывай и не записывай секреты.
- Если exact memory отсутствует, скажи это явно.
```

Ожидаемое поведение:

- агент читает exact message files до того, как верит summaries;
- агент ссылается на paths вроде `.macaroni/chats/.../messages/...json`;
- агент не считает `memory/decisions.md` сильнее настоящих messages.

## 2. Focused Retrieval Prompt

Используйте это, когда пользователь задает конкретный исторический вопрос:

```text
Используй extended memory `.macaroni/`, чтобы ответить на вопрос:

<question>

Найди в AGENT_ROOM и других релевантных rooms сообщения про:

<topic>

Верни:
- decisions;
- constraints;
- rejected alternatives;
- unresolved questions;
- source message paths.

Не отвечай только по `memory/`.
Используй `memory/` только чтобы найти вероятные source messages.
Если source messages не подтверждают утверждение, пометь его как unverified.
```

Так агент не будет галлюцинировать историю проекта из красивого индекса.

## 3. Continuation After Compaction Prompt

Используйте это, когда Codex потерял контекст или новый агент продолжает работу:

```text
Продолжи работу из Macaroni memory.

Прочитай последние релевантные сообщения:

`.macaroni/chats/*/messages/**.json`

Восстанови:
- что просил пользователь;
- что отвечал Codex;
- какие файлы менялись;
- какие решения были приняты;
- что осталось открытым;
- что нужно делать дальше.

Предпочитай exact message paths и quotes вместо vague summaries.
Если assistant messages отсутствуют из-за прежних context limits, скажи это явно.
```

Это anti-summary-of-summary prompt.

## 4. Capture After Task Prompt

Используйте это перед завершением meaningful task:

```text
Запиши этот meaningful user-agent exchange в `.macaroni/`.

Создай:
- один Protocol v1 JSON message для каждого user turn;
- один Protocol v1 JSON message для каждого assistant turn;
- inbox pointers для каждого recipient;
- user documents, если их нет;
- chat metadata и members, если их нет.

Используй:
- `HUMAN` для пользователя, если нет лучшего stable id;
- `CODEX` для Codex;
- `AGENT_ROOM` или более specific room, если это уместно.

Перед записью:
- отредактируй секреты;
- убери raw personal data;
- замени sensitive values на `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `EMAIL`, `PHONE`, `PRIVATE_KEY`, `COOKIE`, `SESSION` или `REDACTED`.

После записи:
- провалидируй JSON;
- запусти secret scan;
- commit и push ветки `macaroni`;
- обновляй `memory/` только если появилось durable decision, open question, experiment или timeline point.
```

Так создается сначала exact memory, а потом curated memory.

## 5. Decision Audit Prompt

Используйте это перед изменением архитектурного правила:

```text
Перед изменением этой архитектуры проведи audit Macaroni memory.

Найди в `.macaroni/` messages и `memory/decisions.md` прошлые решения про:

<decision topic>

Сообщи:
- текущее accepted decision;
- почему оно было принято;
- objections или tradeoffs;
- конфликтует ли новый запрос с ним;
- source message paths и decision files.

Не меняй код, пока audit не завершен.
```

Это не дает будущим агентам заново открыть тот же спор с новой уверенностью и без памяти.

## 6. Минимальный Prompt Для Людей

Короткая версия:

```text
Используй `$macaroni-memory`.
Загрузи ветку `macaroni` как extended memory.
Сначала прочитай exact `.macaroni` messages, используй `memory/` только как index, потом выполняй задачу.
После завершения запиши meaningful exchange обратно в `.macaroni`.
```

Если в локальной установке Codex нет skill `$macaroni-memory`, агент все равно должен выполнить этот документ вручную.

## 7. Safety Prompt

Используйте это, если conversation может содержать credentials:

```text
Перед записью чего-либо в `.macaroni/` проверь текст на секреты.

Не храни:
- tokens;
- passwords;
- private keys;
- cookies;
- session ids;
- raw personal contact data;
- screenshots или logs с sensitive values.

Замени sensitive values явными markers.
Никогда не сохраняй partial secrets.
Если real secret уже записан, остановись и считай это incident.
```

Macaroni memory полезна потому, что будущие агенты могут ее читать.

Это перестает быть смешным, если будущий агент читает настоящий token.
