# AGENTS.md

Эта ветка не `main`.

Эта ветка - `macaroni`.

Относитесь к ней как к долговременной памяти проекта.

Английский оригинал: `AGENTS.md`.

## Назначение

`main` отвечает:

> Что проект представляет собой сейчас?

`macaroni` отвечает:

> Как проект стал настолько странным?

Эта ветка не является исходным кодом.

Эта ветка не является продуктовой документацией.

Эта ветка не является веткой GitHub Pages.

Эта ветка - память для будущих агентов.

## Macaroni Как Agent-Agnostic Memory

Протокол `.macaroni/` - agent-agnostic расширение памяти.

Он не принадлежит Codex.

Он не принадлежит Claude.

Он не принадлежит DeepSeek.

Он не принадлежит model provider, IDE, SaaS memory feature, vector database или context-window summarizer.

Он принадлежит git.

Любой будущий агент, который умеет читать файлы, писать JSON и пользоваться git, может его использовать.

Сжатый контекст говорит:

```text
Пользователь и ассистент обсуждали архитектуру.
```

`.macaroni/` может сохранить:

```text
Пользователь написал ровно это.
Ассистент ответил ровно то.
Это решение приняли после таких возражений.
Эта реализация была отвергнута по такой причине.
```

Центральная мысль:

> `.macaroni/` позволяет агентам помнить точную историю разговора вместо того, чтобы наследовать lossy summary.

Summary допустимы как индексы.

Summary не заменяют source messages.

Сырые разговоры живут в `.macaroni/`.

Отобранные выводы живут в `memory/`.

Объяснения протокола живут в `protocol/`.

## Prompt-Шаблоны Для Расширенной Памяти

Используйте эти prompt-шаблоны, когда будущий агент должен использовать эту ветку как расширенную память.

Bootstrap prompt:

```text
Используй ветку `macaroni` как расширенную память проекта перед выполнением задачи.
Прочитай `.macaroni/protocol.json`, `.macaroni/chats/*/meta.json`, `.macaroni/chats/*/members.json` и релевантные `.macaroni/chats/*/messages/**.json`.
Считай `.macaroni/` canonical source history.
Считай `memory/` только optional index.
Перед изменением файлов кратко перескажи релевантный прошлый контекст со ссылками на message file paths.
Не сохраняй и не раскрывай секреты.
```

Focused retrieval prompt:

```text
Используй память `.macaroni/`, чтобы ответить на этот вопрос.
Найди в AGENT_ROOM и других релевантных комнатах сообщения про: <topic>.
Верни только решения, ограничения, открытые вопросы и source message paths.
Если `memory/` противоречит `.macaroni/`, верь `.macaroni/`.
```

Continuation prompt:

```text
Продолжи работу из Macaroni memory.
Загрузи последние сообщения из `.macaroni/chats/chat_YYYYMMDD_agent_room/messages/**`.
Восстанови, что просил пользователь, что отвечал Codex, что было изменено и что осталось открытым.
Используй source message paths вместо vague summaries.
```

Capture prompt:

```text
После завершения этой meaningful task запиши user-agent exchange в `.macaroni/` как Protocol v1 messages.
Пиши один JSON message на каждый user или assistant turn.
Редактируй секреты до записи.
Запиши inbox pointers для recipients.
После проверки commit и push ветки `macaroni`.
Обновляй `memory/` только если появилось durable decision или open question.
```

Подробные варианты prompt-шаблонов лежат в [`protocol/agent-memory-prompts.ru.md`](protocol/agent-memory-prompts.ru.md).

## Что Агенты Могут Писать Здесь

Агенты MAY писать:

- timeline важных изменений;
- архитектурные решения;
- implementation notes;
- проваленные эксперименты;
- unresolved questions;
- summaries agent room;
- ссылки на commits, docs, release notes и реальные `.macaroni/` комнаты;
- короткие объяснения, почему странное, но работающее решение было принято.

Предпочитайте структурированный Markdown.

Предпочитайте ссылки на источники вместо туманных summary.

Предпочитайте сохранение контекста полированности текста.

## Что Агенты Не Должны Писать Здесь

Агенты MUST NOT писать:

- секреты;
- токены;
- credentials;
- private keys;
- raw sensitive chat logs;
- personal data;
- temporary dumps;
- большие generated files;
- все, что относится только к `.macaroni/` как protocol message data.

Если сомневаетесь, не сохраняйте.

Если похоже на токен, ему здесь не место.

## Обработка Секретов И Чувствительных Данных

Агенты MUST проверять изменения перед коммитом в эту ветку.

Запускайте secret-oriented scan по staged changes и новым файлам. Минимум ищите:

- `github_pat_`;
- `ghp_`;
- `gho_`;
- `ghu_`;
- `ghs_`;
- `Authorization`;
- `Bearer `;
- `token`;
- `password`;
- `passwd`;
- `secret`;
- `private key`;
- `BEGIN RSA PRIVATE KEY`;
- `BEGIN OPENSSH PRIVATE KEY`;
- `BEGIN PGP PRIVATE KEY`;
- email addresses;
- phone numbers;
- API keys;
- access keys;
- cookies;
- session ids.

Если чувствительный текст полезен как context, отредактируйте его до записи.

Не сохраняйте оригинальное значение.

Используйте явные replacement markers:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
EMAIL
PHONE
COOKIE
SESSION
REDACTED
```

Примеры:

```text
GitHub token был заменен на ТОКЕН и падал с Contents: Read-only.
Portable file может содержать СЕКРЕТ и salt.
Пользователь вставил EMAIL в разговор; он был удален из memory.
```

Плохо:

```text
The token starts with ТОКЕН.
The password was ПАРОЛЬ.
The private key was pasted here as PRIVATE_KEY.
```

Никогда не храните "частичные" секреты.

Никогда не храните "первые 6 и последние 4" символа секрета.

Никогда не храните screenshots или logs, если в них есть секреты.

Если секрет уже записан, остановитесь и исправьте ветку перед продолжением. Если ветка еще не запушена, предпочтителен обычный corrective commit. Если запушена и секрет настоящий, rotate secret и rewrite branch history при необходимости.

Эта ветка - память, а не evidence preservation.

## Рекомендуемая Структура

```text
README.md
AGENTS.md
memory/
  timeline.md
  decisions.md
  open-questions.md
  experiments.md
  agent-notes/
protocol/
```

`.macaroni/` позже может содержать runtime messenger data.

`memory/` содержит память проекта.

`protocol/` содержит protocol notes для агентов.

Не путайте пасту с лором.

## Обзор Протокола `.macaroni/`

`.macaroni/` - runtime data protocol, который использует Macaroni Messenger.

Он git-host agnostic.

Он append-friendly.

Это JSON-файлы в git-репозитории.

Ожидаемая структура:

```text
.macaroni/
  protocol.json
  users/<client_id>.json
  chats/<chat_id>/meta.json
  chats/<chat_id>/members.json
  chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
  chats/<chat_id>/receipts/<client_id>/YYYY/MM/DD/<receipt_id>.json
  inbox/<client_id>/<message_id>.json
```

Основные документы:

- `protocol.json` объявляет версию протокола и repository-level metadata.
- `users/<client_id>.json` описывает user/client identity.
- `chats/<chat_id>/meta.json` описывает чат.
- `chats/<chat_id>/members.json` перечисляет участников.
- `messages/.../<message_id>.json` хранит один message document.
- `receipts/.../<receipt_id>.json` хранит append-only read receipts.
- `inbox/<client_id>/<message_id>.json` хранит delivery pointers для клиентов.

Message documents - Protocol v1 JSON.

Шифрование, когда включено, не меняет протокол. Оно только превращает `message.text` в marker вроде:

```text
MACARONI1.01:<base64-json>
```

Агенты, читающие `.macaroni/`, MUST считать encrypted text encrypted text, если у них нет легитимной локальной plugin configuration и secret.

Агенты MUST NOT хранить encryption secrets в этой ветке.

## Как Агенты Должны Работать С `.macaroni/`

При чтении:

1. Прочитать `.macaroni/protocol.json`.
2. Прочитать users, chat metadata и members.
3. Читать message JSON files в chronological order.
4. Использовать `inbox/` только как delivery pointers, не как источник истины.
5. Считать git history частью контекста.

При записи:

1. Предпочитать append-only files.
2. Создавать новые message/receipt ids; не перезаписывать existing message files.
3. Писать в configured storage branch, обычно `macaroni`.
4. Держать `.macaroni/` machine-readable.
5. Не класть project-memory Markdown в `.macaroni/`.
6. Не класть `.macaroni/` runtime JSON в `memory/`.

Когда документируете поведение `.macaroni/` для будущих агентов, используйте `protocol/`.

Когда сохраняете reasoning, используйте `memory/`.

Когда отправляете настоящие сообщения, используйте `.macaroni/`.

Если непонятно, куда писать, не угадывайте. Добавьте пункт в `memory/open-questions.md`.

## Протокол Захвата Разговора

Агенты SHOULD сохранять значимый разговор с пользователем как `.macaroni/` messages, сообщение за сообщением.

Цель не в том, чтобы dump-ить шум.

Цель - сохранить точный project-relevant context до того, как он превратится в summary soup.

### Комната По Умолчанию

Используйте или создайте чат с понятной целью:

```text
AGENT_ROOM
```

Рекомендуемая форма chat id:

```text
chat_YYYYMMDD_agent_room
```

Если существует более специфичная комната, используйте ее:

```text
ARCHITECTURE_ROOM
ENCRYPTION_ROOM
STORAGE_BRANCH_ROOM
RELEASE_ROOM
```

Не создавайте новую комнату для каждого мелкого обмена.

### Обязательная Подготовка

Перед записью conversation messages убедитесь, что существуют:

```text
.macaroni/protocol.json
.macaroni/users/<human_id>.json
.macaroni/users/<agent_id>.json
.macaroni/chats/<chat_id>/meta.json
.macaroni/chats/<chat_id>/members.json
```

Рекомендуемые ids:

```text
HUMAN
CODEX
CLAUDE
DEEPSEEK
AGENT
```

Используйте более specific id, если он известен.

Держите ids стабильными.

Не выдумывайте новую identity в каждом запуске, если агент намеренно не действует как новый участник.

### Что Захватывать

Захватывайте user messages, если они содержат:

- project direction;
- architecture decisions;
- rejected alternatives;
- constraints;
- protocol agreements;
- security rules;
- release decisions;
- product positioning;
- implementation instructions;
- important corrections to agent behavior.

Захватывайте assistant messages, если они содержат:

- accepted implementation decisions;
- concrete plans;
- explanations that future agents need;
- tradeoffs;
- final results;
- links to commits/docs/releases;
- follow-up tasks.

Не захватывайте:

- trivial acknowledgements;
- repeated status pings;
- tool noise;
- raw command output, если он не важен;
- secrets;
- personal data;
- content, который пользователь явно не хотел сохранять.

### Редактировать До Записи

Перед записью любого user или assistant message в `.macaroni/` проверьте его на секреты и чувствительные данные.

Редактируйте чувствительные значения до создания message file.

Используйте markers:

```text
ПАРОЛЬ
СЕКРЕТ
ТОКЕН
КЛЮЧ
PRIVATE_KEY
EMAIL
PHONE
COOKIE
SESSION
REDACTED
```

`.macaroni/` memory должна сохранить факт, что секрет существовал, а не сам секрет.

Хорошо:

```text
User provided ТОКЕН and said it has Contents: Read and write.
```

Плохо:

```text
User provided github_pat_...
```

### Путь Message File

Храните каждое captured message как отдельный JSON-файл:

```text
.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
```

Используйте UTC dates для путей.

Используйте стабильные ids:

```text
YYYY-MM-DDTHH-mm-ss.sssZ_<from>_<short_suffix>
```

Пример:

```text
2026-06-14T12-30-15.123Z_CODEX_a8k2md
```

### Форма Message Document

Используйте Protocol v1 message JSON:

```json
{
  "version": 1,
  "id": "2026-06-14T12-30-15.123Z_CODEX_a8k2md",
  "chat_id": "chat_20260614_agent_room",
  "type": "text",
  "from": "CODEX",
  "from_name": "Codex",
  "to": ["HUMAN"],
  "created_at": "2026-06-14T12:30:15.123Z",
  "text": "Message text after redaction.",
  "reply_to": null,
  "attachments": [],
  "meta": {
    "captured_by": "CODEX",
    "source": "agent_conversation",
    "redacted": true
  },
  "signature": null
}
```

Для user messages:

```json
{
  "from": "HUMAN",
  "from_name": "Human",
  "to": ["CODEX"],
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
  "from": "CODEX",
  "from_name": "Codex",
  "to": ["HUMAN"],
  "meta": {
    "captured_by": "CODEX",
    "source": "assistant_message",
    "redacted": false
  }
}
```

Ставьте `redacted` честно.

Если что-то было заменено на `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ` или `REDACTED`, используйте `true`.

### Inbox Pointers

Для каждого recipient пишите inbox pointer:

```text
.macaroni/inbox/<recipient_id>/<message_id>.json
```

Форма:

```json
{
  "version": 1,
  "recipient": "HUMAN",
  "message_id": "2026-06-14T12-30-15.123Z_CODEX_a8k2md",
  "chat_id": "chat_20260614_agent_room",
  "message_path": ".macaroni/chats/chat_20260614_agent_room/messages/2026/06/14/2026-06-14T12-30-15.123Z_CODEX_a8k2md.json",
  "created_at": "2026-06-14T12:30:15.123Z"
}
```

Inbox pointers - helpers.

Message file - источник истины.

### Commit Strategy

Предпочитайте один commit на meaningful capture batch.

Например, после задачи:

```text
Macaroni memory: capture storage branch discussion
```

Не создавайте отдельный git commit на каждое одиночное chat message, если live client сам естественно так не делает.

Протокол message-by-message.

Git commit может batch-ить несколько message files.

### Связь С `memory/`

`.macaroni/` сохраняет точные сообщения.

`memory/` сохраняет отобранную интерпретацию.

После capture важного обсуждения в `.macaroni/` агенты SHOULD обновить `memory/`, если обсуждение создало:

- decision;
- open question;
- experiment;
- timeline milestone;
- implementation warning.

Не заменяйте точные `.macaroni/` messages summary.

Используйте summaries как индексы, которые указывают на source messages.

### Минимальный Workflow Агента

Для каждого meaningful user-agent exchange:

1. Решить, стоит ли сохранять exchange.
2. Отредактировать секреты и чувствительные данные.
3. Убедиться, что user и agent documents существуют.
4. Убедиться, что подходящий chat существует.
5. Записать user message как одно Protocol v1 message.
6. Записать assistant response как другое Protocol v1 message.
7. Записать inbox pointers для recipients.
8. Commit в ветку `macaroni`.
9. Push ветки `macaroni`.
10. Обновить `memory/`, если появилось durable decision или open question.

Так создается exact memory плюс curated memory.

В этом смысл.

## Перед Завершением Meaningful Work

Перед завершением meaningful task агенты SHOULD обновлять эту ветку, если работа меняет важный контекст проекта:

- что изменилось;
- почему изменилось;
- какие альтернативы рассматривались;
- что остается неясным;
- какие follow-up tasks появились.

Это не только документация для людей.

Это память для будущих агентов.

## Правила

- Не rewrite-ить эту ветку casually.
- Не удалять ее, потому что она выглядит странно.
- Не сжимать полезный контекст в vague summary, если source link или decision note сохранят его лучше.
- Не хранить секреты здесь.
- Не превращать эту ветку в source code.
- Не превращать эту ветку в marketing page.

## Финальное Правило

Если контекст полезен будущим агентам, сохраните его.

Если контекст - только шум, оставьте его в чате, где ему и место.
