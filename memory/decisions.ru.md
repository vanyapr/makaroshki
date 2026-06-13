# Решения Macaroni

Этот файл фиксирует durable project decisions и причины этих решений.

Используйте его для решений, которые будущие агенты не должны заново открывать археологией.

Английский оригинал: `decisions.md`.

## Решение: `main` - Мессенджер, `macaroni` - Память И Хранилище

Status: accepted

Date: 2026-06-14

`main` остается продуктовой веткой:

- `messenger.html`;
- README;
- docs;
- release notes;
- GitHub Pages source.

`macaroni` становится:

- будущей storage branch для runtime data `.macaroni/`;
- durable project memory branch для будущих агентов.

Причины:

- runtime messages не должны засорять source history;
- agent memory не должна смешиваться с текущими product docs;
- отдельная ветка - сильный сигнал, что это другой слой проекта;
- Git уже дает history, forks, replication и source links.

Tradeoff:

- contributors должны знать, что ветка существует;
- agents должны намеренно ее читать;
- это выглядит странно в `git branch -a`.

Verdict:

Странность полезна.

## Решение: Держать `.macaroni/` И `memory/` Отдельно

Status: accepted

Date: 2026-06-14

`.macaroni/` - protocol data.

`memory/` - project memory.

Причины:

- `.macaroni/` должен оставаться machine-readable messenger data;
- `memory/` должен оставаться structured Markdown для людей и агентов;
- смешивание runtime messages с curated memory создаст болото.

Verdict:

Паста - не лор.

Лор - не паста.

Оба могут жить в одной ветке.

Они не живут в одной директории.

## Решение: Без Секретов В Memory

Status: accepted

Date: 2026-06-14

Ветка `macaroni` не должна содержать:

- tokens;
- private keys;
- credentials;
- raw sensitive chat logs;
- personal data.

Причина:

Long-term memory полезна только если будущие агенты могут читать ее без превращения задачи в incident response.

Verdict:

Если пахнет токеном, ему здесь не место.

## Решение: Сохранять Исходные Причины, А Не Только Summary

Status: accepted

Date: 2026-06-14

Будущим агентам нужно больше, чем compressed summary прошлой работы.

Ветка `macaroni` должна сохранять durable project memory с source links и decision notes.

Причины:

- context windows деградируют;
- summaries of summaries теряют аргументы, шутки, constraints и failure paths;
- git может сохранить original discussions, commits и branch history;
- будущие агенты могут лучше читать ту же память, чем текущие агенты.

Tradeoff:

- memory может стать шумной;
- agents должны curate, а не dump;
- sensitive information нужно редактировать до commit.

Verdict:

Сохраняйте полезный контекст со структурой и sources.

Не превращайте memory в vague summary.

## Решение: Считать `macaroni` Portable Context Artifact

Status: accepted

Date: 2026-06-14

Ветка `macaroni` - не только storage.

Это portable context artifact проекта.

Причины:

- люди забывают;
- агенты сбрасываются;
- model providers меняются;
- SaaS memory features принадлежат vendor;
- summaries теряют исходный reasoning;
- git остается cloneable, forkable, inspectable и скучным.

Целевая модель:

```text
main
  что проект представляет собой

macaroni
  почему проект стал таким
```

Это создает практичный workflow для будущих агентов:

```text
checkout main
read README
checkout macaroni
read memory and .macaroni
continue with actual context
```

Tradeoff:

- это выглядит как hidden lore branch;
- пользователи и агенты должны знать, что ее надо читать;
- stale memory нужно помечать, а не считать законом.

Verdict:

Контекст принадлежит репозиторию.

В этом весь смысл.
