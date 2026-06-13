# Эксперименты

Этот файл фиксирует эксперименты, которые стоит помнить, включая провалы.

Английский оригинал: `experiments.md`.

## Эксперимент: Macaroni Как Persistent Agent Memory

Status: proposed

Hypothesis:

Агенты теряют слишком много контекста, когда длинные обсуждения сжимаются в summaries.

Alternative:

Хранить discussion-derived memory в git, в ветке, которую будущие агенты могут читать.

Expected useful properties:

- нет summary-of-summary degradation;
- branchable memory;
- source-linked decisions;
- model-agnostic persistence;
- будущие агенты могут читать лучше текущих.

Failure modes:

- memory становится dumping ground;
- агенты пишут vague summaries вместо useful decisions;
- secrets случайно попадают в память;
- никто не читает ветку;
- ветка становится интереснее продукта.

Последнее может не быть failure.

## Эксперимент: Agent-Native Knowledge Layer

Status: documented

Hypothesis:

Обычная git branch может быть durable, model-agnostic memory для будущих агентов.

Setup:

- держать `main` как current product/source/docs;
- держать `macaroni` как project memory и future storage;
- класть curated memory в `memory/`;
- класть runtime protocol data в `.macaroni/`;
- класть protocol notes в `protocol/`;
- требовать от агентов redaction секретов перед записью.

What to observe over time:

- читают ли будущие агенты эту ветку;
- помогает ли memory не повторять старые ошибки;
- aging source-linked decisions лучше, чем summaries;
- дают ли AGENT_ROOM discussions полезные decision notes;
- не превращается ли ветка в dump.

Good outcome:

Будущие агенты понимают культуру проекта быстрее, чем только по README.

Bad outcome:

Ветка становится драматичным чердаком с vague notes.

Оба исхода информативны.
