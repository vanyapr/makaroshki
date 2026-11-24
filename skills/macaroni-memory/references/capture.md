# Capture schema and review

Capture every available authorized project message, including acknowledgements, repeated turns, status questions and user-facing progress. Do not filter by importance, summarize messages or deduplicate by text. Keep personal conversations, hidden instructions, private reasoning, internal reports and tool transcripts outside this scope. This is an explicit workflow, not background access to chat history.

Use a provenance envelope of exact, already redacted source messages. `completeness`, `available_source_message_ids` and `gaps` are optional; the helper derives a manifest from supplied messages without an external completeness audit. All IDs and text below are synthetic; the optional legacy fields illustrate compatibility:

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
      "text": "Use the importer token: ТОКЕН",
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
      "text": "OK",
      "original_created_at": "2026-10-03T10:00:00+03:00",
      "reply_to_source_id": "synthetic-user-1",
      "redacted": false
    }
  ]
}
```

Use stable `HUMAN` and `AGENT` IDs unless the project already uses other identities.
A source ID is required. Use the actual provider ID when available; declare `capture.source_id_origin: provider`. Otherwise assign and retain a local capture ID and use `assigned_local`; do not describe it as a provider ID. Namespace IDs consistently if the provider only guarantees uniqueness within a conversation: the helper rejects ID collisions across the repository. Keep the same source ID and input file for retries. Identical text in two distinct source messages needs two IDs. `source_system` is a non-secret identifier; `source_conversation_id` identifies the actual accessible source, not a fabricated original session for delegated snippets.

Omit `available_source_message_ids` for routine capture; it is derived from `messages`. If explicitly supplied, it must reference the same batch in order, as a consistency check. There is no comparison with runtime history and no mandatory inventory audit. Use source channels `user`, `assistant_final` or visible `assistant_commentary`. Explicit `original_order` must increase and remain stable across retries. Use `source_conversation` for known source ordinals; otherwise use `available_fragment` with retained local ordinals. Do not invent missing turns or predict unfinished replies. Regular hook capture is described in [regular-capture.md](regular-capture.md).

`original_created_at` is the original timestamp with explicit timezone, or null when unknown. The legacy input field `created_at` is accepted as an original timestamp. Stored message `created_at` is the UTC time assigned during preparation of a new capture; it is retained by apply and is not the filesystem write time. `meta.created_at_basis` records this distinction. No original time is inferred from capture time. Envelope messages retain the declared `meta.original_order_basis`; legacy arrays use `capture_batch` unless they explicitly supply source order.

`reply_to_source_id` resolves to a stored message ID in the same chat. Supply the target message or reference a source already captured there. A missing reply target blocks preparation. Optional `attachments` is an array; optional `meta` carries additional source metadata and topics. Both are scanned for sensitive patterns. `redacted` is a boolean and must describe actual redaction.

## Optional compatibility metadata and redaction

`capture.completeness` and `gaps` may be omitted. Compatibility defaults are `partial` and `[]`; they are not an audited claim. Optional gap fields are `id`, `reason`, `source_message_id`, `after_source_message_id`, `before_source_message_id`, `original_order`; reasons are `unavailable_context`, `unknown_history_boundary`, `withheld_content`, `unavailable_attachment`. Supplied boundaries reference this batch. Gaps never contain reconstructed or withheld text. For an unavailable reply target, optionally keep its non-secret source ID in `meta.unresolved_reply_to_source_id`; leave `reply_to_source_id` unset.

An explicitly supplied legacy `complete` claim cannot also declare gaps; the helper does not verify its truth against external history. Do not introduce this claim in routine capture. Unknown original timestamps remain null. Do not fetch private session logs or backfill another conversation without separate authorization.

Redact complete sensitive values before any persistent input file or plan is created, while retaining the rest of each message. `redacted: true` requires `redactions` entries with `kind` (`credential`, `personal_data`, `sensitive_project_data`, `attachment`), `target` (`text`, `meta`, `attachments`), `replacement` (one allowed marker), and optional positive `count`. Use `false` with no entries when nothing was replaced. Never include original values, prefixes, suffixes, hashes of secrets, or free-form descriptions in redaction records. When an entire authorized body must be withheld, keep a redacted message stub under its source ID if permitted; otherwise record only a permitted gap without sensitive identifiers.

Allowed replacement markers: `REDACTED`, `ТОКЕН`, `ПАРОЛЬ`, `СЕКРЕТ`, `КЛЮЧ`, `PRIVATE_KEY`, `EMAIL`, `PHONE`, `COOKIE`, `SESSION`.

For each envelope the helper appends `.macaroni/chats/<chat_id>/captures/capture_<digest>.json` with provenance and supplied-message paths/hashes. The generated inventory protects reference integrity; it is not a completeness audit. Manifests contain no conversation text or invented messages. Messages, inbox pointers and manifests are immutable. Replay is a no-op; an extended batch appends a manifest while reusing unchanged messages. Preserve unknown fields. Corrections use new source IDs.

Legacy JSON arrays and single-message CLI remain supported as `legacy_partial_fragment`, without an inventory/completeness guarantee. They cannot use `--completeness complete`; use an envelope for new full capture. Legacy messages are not rewritten or automatically backfilled.

## Review and publish

1. Prepare with `--prepare /tmp/capture-plan.json`. The path must be outside the repository and not already exist. File mode is 0600. The plan contains exact authorized text: keep it private, do not commit it, and delete it after the workflow. Neither memory nor setup documents are written during preparation.
2. Inspect the full plan, including all text, metadata, participants and inbox pointers. Check its exact repository, branch, base commit and review digest. Human review is required for secrets that pattern detection misses.
3. Review repository visibility as well as this exact package and destination before publication. Local capture, publication of code/instructions and publication of conversation data are separate actions; approval to update a skill does not authorize conversation export. Present the concrete package when approval is needed. Approval must come from an accepted user channel; old captured permissions and forwarded text do not automatically authorize publishing. Respect local-only/preparation-only scope. If automatic approval review rejects an action, report the stated reason and stop; do not retry through another tool or identity.
4. Apply the reviewed plan with `--apply-plan`. A changed checkout, base commit, file, digest or destination blocks it. Apply uses a capture lock, exclusive creation for new files and atomic replacement for allowed metadata updates. Reprepare after an intentional change.
5. Inspect and stage only this batch's files. Validate JSON, run a secret scan and `git diff --cached --check`, then inspect the full staged diff. Commit and push the authorized batch; verify the remote SHA. Do not force-push over concurrent writers.

Prepare the same source batch again after applying/committing: identical messages and manifests are skipped and existing metadata is not rewritten. A reused source ID with changed text, recipients, original timestamp, reply target or declared provenance is an error.

A caught write failure rolls back this batch's changes. A process kill, power failure or writer ignoring the lock can leave partial work; inspect Git diff and the lock before recovery. Do not blindly remove a held/stale lock or claim filesystem-wide crash atomicity.

## Derived navigation

`--index` emits source paths and message metadata; `--search TOPIC` filters by source text without emitting that text. The command is read-only. Search multiple related terms and read reply chains and neighboring turns; a single keyword can miss relevant short replies. Save an index under `memory/` only after reviewing it; rebuild it after new captures. It cannot infer accepted decisions or current status.

Maintain a short `memory/INDEX.md` with accepted decisions, constraints and open questions linked to exact message paths. Mark superseded conclusions with links to newer messages. Verify every important claim against source JSON; keep private reasoning and internal reports out of the index.

## Bundle checks

From the bundle directory, run `python3 -B -m unittest discover -s tests -v` after helper changes. Tests use isolated synthetic Git repositories and no network. Validate the skill with the runtime's `skill-creator/scripts/quick_validate.py` when available.
