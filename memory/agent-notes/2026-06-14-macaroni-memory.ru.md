# 2026-06-14 - Macaroni Memory

Author: Codex

Английский оригинал: `2026-06-14-macaroni-memory.md`.

## Что Изменилось

Ветка `macaroni` получила структуру project memory:

- `AGENTS.md`;
- `memory/timeline.md`;
- `memory/decisions.md`;
- `memory/open-questions.md`;
- `memory/experiments.md`;
- `memory/agent-notes/`.

## Почему

Проект обнаружил идею сильнее, чем "messenger over git":

> Git-native persistent memory for humans and agents.

Ветка должна сохранять context, которому не место в product docs:

- почему решения были приняты;
- что провалилось;
- что обсуждалось;
- что будущим агентам не стоит открывать заново.

## Важная Граница

`main` остается про мессенджер.

`macaroni` несет storage и memory.

Контракт Macaroni Memory не добавлялся в `main`.

## Follow-Up

- Добавить `storage_branch` support в `messenger.html`.
- Решить, когда agents should update `memory/`.
- Решить, должны ли AGENT_ROOM summaries генерироваться в `memory/`.

## Позже В Том Же Треде

Идея расширилась от "macaroni branch as project memory" до "agent-native knowledge layer over git".

Важный вывод:

`main` - official project surface.

`macaroni` - durable memory layer.

Этот слой должен сохранять, почему проект стал странным, а не только как он сейчас работает.

Подробный write-up:

- `memory/agent-native-knowledge-layer.ru.md`
