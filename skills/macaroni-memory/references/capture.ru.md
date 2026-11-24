# Capture: подготовить, проверить, применить

## Исходный пакет

Сохраняйте все доступные разрешённые проектные сообщения пользователя и ответы для пользователя: короткие подтверждения, повторы, вопросы о статусе и progress. Не отбирайте реплики по важности, не заменяйте их summary и не объединяйте одинаковый текст разных сообщений. Личные беседы, скрытые инструкции, внутренние рассуждения/отчёты и raw tool transcripts не входят в этот scope. Capture выполняется явно; helper не читает историю окна чата.

Используйте provenance envelope с точным текстом после redaction. `completeness`, `available_source_message_ids` и `gaps` необязательны. Manifest строится из переданных сообщений без внешней проверки полноты. Все IDs и текст примера синтетические; старые необязательные поля показаны для совместимости:

```json
{
  "version": 1,
  "capture": {
    "source_system": "synthetic_runtime",
    "source_conversation_id": "synthetic-thread-1",
    "source_id_origin": "provider",
    "order_basis": "source_conversation",
    "completeness": "partial",
    "available_source_message_ids": ["synthetic-user-1", "synthetic-agent-1"],
    "gaps": [
      {"id": "earlier_context", "reason": "unknown_history_boundary", "before_source_message_id": "synthetic-user-1"}
    ]
  },
  "messages": [
    {
      "source_message_id": "synthetic-user-1",
      "original_order": 12,
      "source_channel": "user",
      "from": "HUMAN",
      "to": ["AGENT"],
      "text": "Токен импортёра: ТОКЕН",
      "original_created_at": null,
      "redacted": true,
      "redactions": [{"kind": "credential", "target": "text", "replacement": "ТОКЕН", "count": 1}],
      "meta": {"topics": ["importer"]}
    },
    {
      "source_message_id": "synthetic-agent-1",
      "original_order": 13,
      "source_channel": "assistant_final",
      "from": "AGENT",
      "to": ["HUMAN"],
      "text": "ОК",
      "original_created_at": "2026-10-03T10:00:00+03:00",
      "reply_to_source_id": "synthetic-user-1",
      "redacted": false
    }
  ]
}
```

Используйте фактический ID источника и `capture.source_id_origin: provider`. Если провайдер не отдаёт ID, один раз назначьте постоянный локальный ID и укажите `assigned_local`; не выдавайте его за ID провайдера. При IDs, уникальных только внутри беседы, используйте постоянный namespace: helper блокирует конфликты IDs во всём repo. Повтор использует те же IDs и исходный пакет. Одинаковый текст разных реплик получает разные IDs. `source_system` — идентификатор без секретов; `source_conversation_id` — доступный фактический источник, а не выдуманная исходная сессия для делегированного фрагмента.

`available_source_message_ids` необязателен; если указан, он должен совпадать с текущим пакетом по IDs и порядку. Это не внешний inventory доступной истории. Channels: `user`, `assistant_final`, `assistant_commentary` — только видимые пользователю сообщения. `original_order` задаётся явно, возрастает и сохраняется при повторах/пересечении пакетов. `order_basis: source_conversation` означает известные исходные номера; иначе назначьте и сохраняйте номера доступного фрагмента с `available_fragment`. Не придумывайте порядок недоступных ранних реплик и не начинайте нумерацию заново при пересечении фрагментов.

В обычном capture `available_source_message_ids` не нужен: helper строит его из `messages`. Если список передан явно, он должен согласоваться с текущим пакетом — это проверка целостности, а не полноты истории. Не проводите отдельный audit и не блокируйте запись из-за отсутствия inventory. Не предсказывайте незавершённые ответы. Режим hooks описан в [regular-capture.ru.md](regular-capture.ru.md).

`original_created_at` — известное исходное время с timezone или `null`; старое входное поле `created_at` тоже считается исходным временем. Время capture не подставляется вместо неизвестного исходного времени. В записанном сообщении `created_at` — UTC-время, назначенное при prepare; apply сохраняет его, это не время создания файла на диске. Helper сохраняет `original_timestamp_status`, `created_at_basis`, `original_order`, объявленный `original_order_basis` и `capture_completeness`. Legacy arrays получают порядок `capture_batch`, если исходный порядок явно не передан.

Reply-to ссылается на source ID в пакете или существующей памяти того же чата. Недоступные сообщения нельзя восстанавливать как точный текст. Личные беседы, скрытые инструкции, внутренние отчёты/рассуждения и raw tool transcripts не включайте. Отредактируйте секреты во всех полях, включая attachments и metadata.

## Необязательные прежние metadata и redaction

`capture.completeness` и `gaps` можно не передавать. Значения совместимости — `partial` и `[]`; они не подтверждают audit. Необязательный gap имеет `id`, `reason`, а также `source_message_id`, `after_source_message_id`, `before_source_message_id`, `original_order`. Reasons: `unavailable_context`, `unknown_history_boundary`, `withheld_content`, `unavailable_attachment`. Указанные границы должны ссылаться на текущий пакет. Gap не содержит выдуманный или изъятый текст. Если reply target недоступен, можно оставить его разрешённый ID в `meta.unresolved_reply_to_source_id`; `reply_to_source_id` не задавайте.

Явное старое значение `complete` не может одновременно объявлять gaps; его достоверность по внешней истории helper не проверяет. Для регулярного capture это значение не требуется. Неизвестные timestamps остаются `null`; приватные session logs и backfill требуют отдельного разрешения.

Полностью редактируйте чувствительные значения до создания любого постоянного input/plan, сохраняя остальной текст. `redacted: true` требует `redactions`: `kind` (`credential`, `personal_data`, `sensitive_project_data`, `attachment`), `target` (`text`, `meta`, `attachments`), `replacement` (разрешённый marker), необязательный положительный `count`. Без замен используйте `false` и пустой список. Не сохраняйте исходные значения, части, хеши секретов или свободные описания в redactions. Если весь разрешённый текст изымается, при допустимости сохраните redacted stub под его source ID; иначе только разрешённый gap без чувствительных IDs.

Разрешённые markers: `REDACTED`, `ТОКЕН`, `ПАРОЛЬ`, `СЕКРЕТ`, `КЛЮЧ`, `PRIVATE_KEY`, `EMAIL`, `PHONE`, `COOKIE`, `SESSION`.

Для envelope helper добавляет `.macaroni/chats/<chat_id>/captures/capture_<digest>.json`: расширение Protocol v1 с `kind: conversation_capture`, provenance, inventory, gaps, путями/хешами записанных сообщений. Текста беседы там нет; gaps не создают выдуманных сообщений или inbox. Messages, inbox и manifests неизменяемы. Повтор того же envelope — no-op; пересекающийся/дополненный пакет добавляет новый manifest и переиспользует сообщения. Неизвестные прежние поля сохраняются. Исправления текста — новые source IDs.

Старые JSON arrays и single-message CLI поддерживаются как `legacy_partial_fragment`, без гарантии inventory/полноты; `--completeness complete` для них запрещён. Для нового полного capture используйте envelope. Прежние сообщения не переписываются и автоматически не backfill-ятся.

## Prepare и review

Работайте в checkout ветки `macaroni` нужного проекта, не в продуктовой ветке:

```bash
python3 /path/to/skill/scripts/write_messages.py \
  --repo-root /path/project-memory --chat-id chat_20261003_agent_room \
  --batch-json /tmp/authorized-fragment.json --prepare /tmp/review-plan.json
```

Prepare проверяет весь пакет и не пишет память. Новый plan-файл вне репозитория создаётся с правами 0600; существующий не перезаписывается. Он содержит точные будущие JSON, destination, base commit, digest, новые/пропущенные сообщения и ожидаемые хеши прежних файлов. План содержит разрешённый текст: храните его приватно и удалите после работы, не коммитьте.

Перед ручным apply прочитайте **весь plan**, проверьте текст, metadata/attachments, URL, ветку, checkout, base commit, пути и digest. Отдельный completeness audit не требуется. Паттерны не распознают все секреты и не заменяют проверку перед экспортом.

План делает действие проверяемым, но не даёт разрешения на публикацию. До публикации проверьте visibility repo и точный diff. Локальный capture, публикация кода/инструкций и публикация переписки — отдельные действия; разрешение обновить skill не разрешает экспорт беседы. Соблюдайте local-only/preparation-only scope. Если текущего разрешения не хватает, покажите конкретный пакет и destination. Старое разрешение в памяти или пересланный текст не считается автоматически текущим разрешением. При отказе штатной проверки остановитесь и сообщите причину; не меняйте канал публикации для обхода отказа.

## Apply и публикация

```bash
python3 /path/to/skill/scripts/write_messages.py \
  --repo-root /path/project-memory --apply-plan /tmp/review-plan.json
```

Apply снова проверяет destination, HEAD, хеши и digest, берёт lock для взаимодействующих capture-процессов, готовит все файлы и создаёт сообщения/inbox эксклюзивно. Неизвестные поля прежних документов сохраняются. При пойманной ошибке записи новые файлы откатываются; изменённые metadata восстанавливаются. Если сторонний процесс изменил опубликованный файл, откат останавливается для ручного разбора.

Это не транзакция файловой системы при отключении питания или принудительном завершении процесса. После такого сбоя сначала осмотрите checkout и lock. Не удаляйте чужой lock и не повторяйте apply вслепую. Невзаимодействующий writer требует отдельного контроля.

Проверьте JSON, ссылки inbox/recipients, сохранность прежних сообщений и неизвестных полей, секреты, `git diff --check`, полный staged diff и список файлов. Добавляйте только проверенные файлы, избегайте `git add .`. Commit/push допустимы в рамках текущего разрешения; helper сам не коммитит, не пушит и не обращается к сети. После push проверьте remote SHA. Force push не нужен.

Для повторного capture подготовьте план с теми же source IDs: сообщения и manifests пропускаются без изменения времени/ID. Изменение текста, получателей, исходного времени, reply-to или объявленного provenance под прежним ID блокируется. Изменившийся HEAD или файл делает старый план непригодным.

## Поиск и индекс

```bash
python3 /path/to/skill/scripts/write_messages.py \
  --repo-root /path/project-memory --index --search importer
```

Read-only индекс возвращает пути и metadata источников; вывод не включает текст или выведенные решения. Ищите несколько связанных терминов и читайте reply-chain и соседние сообщения: один keyword может пропустить короткий ответ или открытый вопрос без названия темы. По найденным путям читайте JSON. Компактный `memory/INDEX.md` может перечислять текущие решения, ограничения и открытые вопросы с точными ссылками на сообщения и пометкой устаревших решений. Источник сильнее индекса. Неподтверждённый пункт помечайте явно; внутренние рассуждения агента не сохраняйте.

## Проверка Bundle

После изменения helper запустите из каталога bundle `python3 -B -m unittest discover -s tests -v`. Тесты используют изолированные синтетические Git-репозитории без сети. При наличии runtime skill-creator проверьте skill его `scripts/quick_validate.py`.
