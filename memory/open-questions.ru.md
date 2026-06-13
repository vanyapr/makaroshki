# Открытые Вопросы

Этот файл отслеживает unresolved questions для будущих людей и агентов.

Английский оригинал: `open-questions.md`.

## Реализация Storage Branch

- Должны ли новые профили сразу default-иться в `storage_branch: "macaroni"` после поддержки в клиенте?
- Должен ли клиент сначала создавать `macaroni` из default branch, или нужно поддержать создание orphan branch из браузера?
- Как reindex metadata должен различать `main` и `macaroni`?
- Что должен делать UI, если `storage_branch` существует, но в ней нет `.macaroni/protocol.json`?

## Agent Memory Workflow

- Должны ли агенты обновлять `memory/` в конце каждой meaningful task или только после architectural/product decisions?
- Agent notes должны быть one file per task, one file per date или one file per agent?
- Должны ли summaries ссылаться на `.macaroni/` message ids после появления runtime storage branch support?
- Должен ли `memory/` когда-нибудь генерироваться из AGENT_ROOM автоматически?
- Где граница между сохранением original discussion и curated memory?
- Какой точный порог для записи user-agent exchanges message-by-message в `.macaroni/`?
- Должны ли агенты автоматически capture-ить свои final responses или только если ответ содержит durable project context?
- Agent forks должны мапиться на git branches, chat rooms или оба слоя?
- Нужны ли periodic indexes памяти `macaroni`, сгенерированные агентами?
- Как отмечать старую memory как superseded без rewrite history?

## Будущая Форма Протокола

- Должны ли Agent Rooms быть обычными chats с `meta.kind = "agent_room"`?
- Должны ли decisions позже стать protocol events, или остаться Markdown memory?
- Forks обсуждений должны мапиться на git branches, chat ids или оба слоя?
