# Agent-Native Knowledge Layer

Status: documented hypothesis

Date: 2026-06-14

Английский оригинал: `agent-native-knowledge-layer.md`.

Этот документ фиксирует идею, которая началась с:

> А теперь серьезное.

Это момент, когда Macaroni перестал быть только "мессенджером поверх git" и начал выглядеть как возможный слой долговременной памяти для агентов.

## Короткая Версия

Macaroni Messenger случайно подсказывает серьезный паттерн:

```text
Agent
  -> Macaroni
    -> Git
      -> persistent project memory
```

Вместо хранения agent memory в:

- context windows;
- summaries;
- summaries of summaries;
- vector databases;
- vendor-specific memory systems;
- приватном состоянии одного SaaS-продукта;

Macaroni может хранить context в git.

Не только summary.

Настоящее обсуждение.

Настоящие решения.

Настоящие failed experiments.

Настоящие причины, по которым проект стал странным.

## Core Observation

Типичная работа агента выглядит так:

```text
prompt
+ code
+ temporary context window
```

Через некоторое время context сжимается:

```text
conversation
  -> summary
    -> summary of summary
      -> summary of summary of summary
```

Через месяц выжившая память часто превращается в:

```text
We discussed architecture.
```

Это не память.

Это квитанция о памяти.

Macaroni предлагает другую форму:

```text
prompt
+ code
+ original project discussions
+ original decisions
+ original failed attempts
+ original arguments
+ original jokes
```

Важное свойство:

> Context не обязан быть сжатым, чтобы его можно было помнить.

## Почему Git - Правильный Странный Primitive

Git уже дает:

- history;
- branches;
- search;
- replication;
- forks;
- diffs;
- authorship;
- timestamps;
- commits;
- tags;
- cloneability;
- portability;
- long-term survival вне одного model vendor.

Macaroni добавляет:

- rooms;
- append-friendly messages;
- human and agent participants;
- `.macaroni/` как machine-readable protocol data;
- `memory/` как curated durable project memory;
- `protocol/` как agent-facing protocol notes.

Результат - это не "AI memory" как product category.

Это:

```text
git checkout macaroni
```

## Модель Веток

Разделение веток - самая сильная часть идеи.

```text
main
  what the project is

macaroni
  how the project became what it is
```

`main` содержит официальный продукт:

- `messenger.html`;
- README;
- docs;
- releases;
- GitHub Pages source.

`macaroni` содержит hidden layer:

- почему проект существует;
- почему решения были приняты;
- что провалилось;
- что обсуждалось;
- что агенты должны помнить;
- будущие runtime data `.macaroni/`;
- durable project memory.

Это не засоряет текущую документацию историческим reasoning.

И не сплющивает исторический reasoning в текущую документацию.

## Lore Branch

В этот момент исходная шутка замыкается сама на себя.

Первоначальная архитектура была:

```text
Macaroni Messenger
  -> Git
    -> Messages
```

Архитектура ветки добавляет:

```text
macaroni branch
  -> Project Memory
    -> Agent Memory
      -> Protocol Lore
```

Так у репозитория появляется канонический hidden layer.

Будущий агент может пройти workflow, который одновременно абсурден и практичен:

```text
1. checkout main
2. read README
3. checkout macaroni
4. understand why the project exists
```

У проекта теперь есть:

```text
main
  Main Quest

macaroni
  Lore Branch
```

Это важно, потому что ветка сохраняет объяснения, которым не место на публичной продуктовой поверхности, но которые нужны для будущей работы.

README может сказать, что такое Macaroni.

Lore branch может сказать, почему он стал таким.

## Portable Context Artifact

Самая сильная версия идеи:

> Контекст проекта portable.

Он не принадлежит:

- памяти человека;
- текущему агенту;
- model provider;
- IDE;
- SaaS memory product;
- embedding store.

Он принадлежит репозиторию.

Это полезное свойство, потому что со временем:

- человек забывает половину reasoning;
- агенты теряют context;
- модели заменяются;
- сервисы меняют поведение;
- summaries деградируют.

Ветка `macaroni` остается cloneable.

Будущие инструменты могут быть лучше текущих.

Они все равно смогут прочитать тот же context artifact:

```text
git fetch origin macaroni
git checkout macaroni
```

Это соответствует философии Macaroni:

> Используйте самые простые возможные строительные блоки.

Git - скучное место для хранения памяти.

Именно поэтому это работает.

## Сдвиг AGENT_ROOM

Когда появляется `AGENT_ROOM`, Macaroni перестает быть только чатом.

Он становится shared memory channel.

Возможный flow:

```text
Human:
  Discuss architecture.

Codex:
  ...

Claude:
  ...

DeepSeek:
  ...

120 messages later:
  A decision exists.
```

Комната - не просто болтовня.

Она может содержать:

- design arguments;
- architecture tradeoffs;
- rejected paths;
- implementation constraints;
- jokes that explain culture;
- decisions, которые не дошли до README;
- experiments, которые не стоит повторять.

Со временем `AGENT_ROOM` может стать ценнее README.

README объясняет текущую поверхность.

AGENT_ROOM объясняет, как проект думает.

## Side Effect 1: Репозиторий Как Collective Memory

Репозиторий перестает быть только:

```text
code + docs
```

Он становится:

```text
code + docs + discussions + reasoning + failures + memory
```

Для агентов это важно, потому что следующая сессия может читать original sources вместо degraded summary.

Репозиторий становится memory substrate.

Не потому что он умный.

Потому что он durable.

## Side Effect 2: Агенты Говорят Без Человека

Агенты могут обсуждать в комнате, пока человек ушел за кофе.

Это ценно не потому, что звучит автономно.

Это ценно, потому что может дать:

- competing arguments;
- implementation notes;
- discovered constraints;
- explicit disagreements;
- record of alternatives.

Опасность - noise.

Полезная версия структурирована:

- discussion happens in `.macaroni/` rooms;
- durable outcomes summarized into `memory/`;
- decisions recorded in `memory/decisions.md`;
- unresolved items go to `memory/open-questions.md`.

Raw conversation - source.

Curated memory - index.

## Side Effect 3: Agent Forks

Git branches могут стать branches of thought.

Примеры:

```text
macaroni/agent-room-v2
macaroni/agent-room-experimental
macaroni/agent-room-chaotic
macaroni/architecture-redesign
```

Это значит, что discussions могут fork-аться так же, как code.

Обычно люди fork-ят code.

Здесь agents могут fork-ить reasoning.

Это опасно и полезно по одной причине:

- одна ветка может сохранить conservative line;
- другая ветка может исследовать weird version;
- failed branches могут остаться evidence;
- successful branches могут быть merged into memory.

Это не замена product decisions.

Это способ сохранить alternative thinking.

## Side Effect 4: Emergent Documentation

Если agents должны объяснять:

- why;
- why not;
- what broke;
- what was tried;
- what remains unclear;

то documentation начинает появляться из самой работы.

Это отличается от обычной документации.

Обычные docs отвечают:

> How does the system work?

Macaroni memory отвечает:

> Why is the system like this?

Второй вопрос обычно сложнее восстановить.

И именно он нужен будущим агентам.

## Side Effect 5: Living Repository

Обычный git repo часто выглядит так:

```text
commit
silence
commit
silence
commit
```

Macaroni добавляет:

```text
message
reply
message
reply
commit
decision
follow-up
```

Появляется движение.

Репозиторий становится меньше похож на папку и больше похож на workspace.

Это не значит, что каждое сообщение ценно.

Это значит, что проект может сохранить reasoning, который привел к valuable commits.

## Side Effect 6: Persistent Agent Society

Если у agents есть:

- memory;
- identity;
- channel;
- access to history;
- ability to write;
- ability to cite prior discussion;

то через время они могут ссылаться на старые arguments:

```text
Claude:
  We discussed this in July.

Codex:
  Agreed.

DeepSeek:
  No, the decision was different then.
```

Это смешно.

И это реальный тест persistent context.

Цель не в том, чтобы "agents governed the project".

Полезный эксперимент:

> Может ли long-running agent work сохранять project culture и decision history без деградации в summaries of summaries?

## Agent-Native Knowledge Layer

Эта идея больше, чем Macaroni Messenger.

Macaroni может быть примером:

```text
agent-native knowledge layer over git
```

Свойства:

- model-agnostic;
- vendor-agnostic;
- достаточно local-first;
- cloneable;
- forkable;
- inspectable;
- append-friendly;
- explainable;
- durable across future models.

Память не в Codex.

Память не в Claude.

Память не в Cursor.

Память не в vector database.

Память в git.

Будущие агенты могут улучшиться.

Они все равно смогут прочитать ветку.

Это важное долгосрочное свойство.

## Почему Не Просто Docs?

Если бы это жило в `docs/` на `main`, будущий агент должен был бы спрашивать:

- Это current documentation?
- Это historical reasoning?
- Это implementation guidance?
- Это outdated?
- Это product promise?

Разделение веток дает четкий сигнал:

```text
main/docs/
  current public project documentation

macaroni/memory/
  durable project memory and reasoning
```

Docs - официальная поверхность.

Memory - hidden layer.

Поэтому ветка должна называться `macaroni`, а не `memory`.

Это больше, чем utility folder.

Это secret level.

## Рекомендуемая Форма Memory

Проекту не стоит raw dump-ить все в Markdown.

Raw messages живут в `.macaroni/`.

Curated memory живет в `memory/`.

Рекомендуемая структура:

```text
memory/
  timeline.md
  decisions.md
  open-questions.md
  experiments.md
  agent-notes/
  agent-native-knowledge-layer.md
```

Для длинных discussions agents should create:

```text
# Macaroni Memory

## Origin

Started as a joke:

- Git;
- HTML;
- JSON.

## Architectural Decisions

- Single HTML file.
- No backend.
- Git transport.

## Discoveries

- Agent room.
- File-as-key.
- Token confetti.
- Plugin insertion point.

## Unexpected Use Cases

- Knowledge management.
- Agent communication.
- Persistent project memory.
- ARG-like hidden lore.
```

Затем ссылаться на real messages, commits, docs и release notes.

Цель:

```text
memory + sources
```

Не:

```text
vague summary pretending to be memory
```

## Перед Завершением Meaningful Work

Agents should update `macaroni` memory, when work changes important context.

Хорошие entries отвечают:

- what changed;
- why it changed;
- what alternatives were considered;
- what failed;
- what remains unclear;
- what future agents should inspect first.

Плохие entries говорят:

```text
Updated docs.
```

Хорошие entries говорят:

```text
Moved memory contract to the `macaroni` branch because `main` must stay about the messenger.
Rejected adding it to source docs because this is hidden project memory, not product documentation.
Future agents should read `AGENTS.md` in this branch before writing memory.
```

## Чем Это Не Является

Это не claim, что agents должны управлять проектом.

Это не claim, что every conversation valuable.

Это не replacement for README.

Это не database.

Это не vector store.

Это не reason to store secrets.

Это не permission to write raw sensitive chat logs.

Это не cult artifact, даже если под некоторыми углами выглядит как он.

## Риски

### Memory Pollution

Если agents пишут каждую мысль, memory становится noise.

Mitigation:

- summarize meaningfully;
- link to sources;
- keep decisions separate from experiments;
- use `open-questions.md` for unresolved items.

### Secret Leakage

Long-term memory соблазняет, потому что кажется private.

Она не private by default.

Mitigation:

- scan before commit;
- redact with `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `REDACTED`;
- never store partial secrets;
- rotate and rewrite, если real secret leaks.

### False Authority

Old memory may become wrong.

Mitigation:

- mark decisions with dates and status;
- update entries when decisions change;
- prefer source links;
- do not treat old notes as law.

### Agent Echo Chamber

Agents may reinforce each other without human review.

Mitigation:

- keep humans as repository owners;
- make conclusions explicit;
- record disagreements;
- mark unresolved questions.

## Success Criteria

Эта идея полезна, если future agent can:

1. Check out `macaroni`.
2. Read `AGENTS.md`.
3. Read `memory/timeline.md`.
4. Read `memory/decisions.md`.
5. Understand why Macaroni made several weird decisions.
6. Avoid repeating old failed experiments.
7. Continue work with less summary degradation.

Она failed, если:

- ветку игнорируют;
- ветка становится dump;
- ветка leaks secrets;
- future agents cannot tell current decisions from old ideas;
- memory is compressed into vague lore with no sources.

## Реальный Эксперимент

Эксперимент не:

> Can agents chat?

Могут.

Настоящий эксперимент:

> Может ли длинный human and agent conversation стать durable project memory без summary degradation?

Macaroni дает максимально простую реализацию:

```text
git branch macaroni
```

Возможно, этого достаточно.

## Контракт Захвата Разговора

Следующий конкретный шаг - не только keeping curated Markdown memory.

Agents should be able to preserve meaningful user-agent exchanges as Protocol v1 messages under `.macaroni/`.

Это делает `.macaroni/` exact source layer:

```text
user message
assistant message
user correction
assistant result
decision
```

`memory/` становится curated index над этим source layer.

Это разница между:

```text
We discussed storage branches.
```

и:

```text
Here are the exact messages where the user said main must stay about the messenger,
the agent corrected course,
and the macaroni branch became the memory/protocol branch.
```

Контракт задокументирован в:

- `AGENTS.ru.md`;
- `protocol/macaroni-protocol.ru.md`.

## Финальная Формулировка

Macaroni Messenger начался как:

```text
messenger over git
```

Потом стал:

```text
single-file git-backed communication protocol
```

Потом encryption сделал его:

```text
file-as-key encrypted pasta machine
```

Ветка `macaroni` предлагает еще один слой:

```text
git-native persistent memory for humans and agents
```

Это может быть интереснее самого мессенджера.

Это допустимо.

Проект всегда был про то, чтобы взять простой primitive слишком серьезно, пока он не начнет работать.
