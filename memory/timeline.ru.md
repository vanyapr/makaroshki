# Timeline Macaroni

Этот файл отслеживает, как Macaroni Messenger стал тем, чем он является.

Это не changelog.

Это timeline памяти проекта.

Английский оригинал: `timeline.md`.

## 2026-06-08 - Зарождение

Macaroni Messenger начался как намеренно абсурдная, но рабочая идея:

- один `messenger.html`;
- без backend;
- без базы данных;
- сообщения как JSON-файлы в git;
- local browser storage как cache;
- Git как источник истины.

Изначальный use case был намеренно маленьким:

> Сказать маме сварить макароны.

Принцип проекта стал:

> Не делать сложно там, где можно сделать смешно.

Это не отменило требования, что результат должен быть настоящим software.

## 2026-06-09 - Public Demo И HN Readiness

Проект получил публичное GitHub Pages demo, demo chats, README positioning, known limitations, license, screenshots и Show HN pitch.

Важное продуктовое решение:

- demo должно работать без token;
- unauthenticated GitHub API rate limit не должен быть первой ошибкой посетителя;
- поэтому public demo может использовать hardcoded read-only data.

## 2026-06-13 - Encryption 1.01

Macaroni Encryption 1.01 был реализован как встроенный plugin.

Он не изменил Macaroni Protocol v1.

Он превращает `message.text` в:

```text
MACARONI1.01:<base64-json>
```

Он использует:

- shared secret;
- salt;
- Tiny PRNG;
- XOR;
- Token Confetti;
- localStorage plugin settings;
- view-layer decrypt.

Release framing был намеренно тихим:

> Исправили опечатку. И еще пару мелочей.

Одной из мелочей было шифрование.

## 2026-06-13 - Storage Branch

Была создана отдельная orphan branch с именем `macaroni`.

Ветка не называется `.macaroni`, потому что Git не разрешает такое имя branch.

Назначение:

- держать source/docs/releases в `main`;
- перенести runtime data `.macaroni/` в dedicated branch;
- позже разрешить `storage_branch: "macaroni"` в client settings.

## 2026-06-14 - Macaroni Memory

Ветка `macaroni` стала больше, чем будущим runtime storage.

Она стала long-term project memory branch.

Основная идея:

```text
main
  что проект представляет собой

macaroni
  как проект стал таким
```

Это создает простой persistent memory layer для будущих агентов:

- original discussions могут оставаться source-linked;
- decisions переживают context-window resets;
- failed experiments можно помнить;
- будущие агенты наследуют культуру проекта, а не только README facts.

Это не AI memory SaaS.

Это `git checkout macaroni`.

Идея была расширена до явного agent-native knowledge layer:

- `main` документирует, что проект такое;
- `macaroni` сохраняет, как проект стал таким;
- `.macaroni/` может хранить runtime protocol messages;
- `memory/` может хранить curated project memory;
- будущие агенты могут читать исходные причины вместо summaries of summaries.

См. `memory/agent-native-knowledge-layer.ru.md`.

## 2026-06-14 - Lore Branch И Portable Context

У ветки появился более точный смысл:

```text
main
  Main Quest

macaroni
  Lore Branch
```

Так петля замкнулась:

```text
Macaroni Messenger -> Git -> Messages
macaroni branch    -> Git -> Project Memory
```

Ключевая концепция:

> `macaroni` - portable context artifact.

Контекст проекта принадлежит репозиторию, а не человеку, агенту, model vendor, IDE или SaaS memory feature.

Это значит, что будущие агенты могут:

1. прочитать `main`, чтобы понять продукт;
2. прочитать `macaroni`, чтобы понять, почему продукт существует;
3. продолжить от исходного контекста, а не от унаследованного фольклора.

Это все еще смешно.

И это полезно.
