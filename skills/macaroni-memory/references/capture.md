# Capture schema and review

Use a JSON array of exact, already redacted source messages:

```json
[
  {
    "source_message_id": "provider-message-001",
    "from": "HUMAN",
    "from_name": "Human",
    "to": ["CODEX"],
    "source": "user_message",
    "text": "Exact project requirement after redaction.",
    "original_created_at": null,
    "redacted": false,
    "meta": {"topics": ["importer"]}
  },
  {
    "source_message_id": "provider-message-002",
    "from": "CODEX",
    "to": ["HUMAN"],
    "text": "Exact reply after redaction.",
    "original_created_at": "2026-10-03T10:00:00+03:00",
    "reply_to_source_id": "provider-message-001",
    "redacted": false
  }
]
```

Use stable `HUMAN` and `CODEX` IDs unless the project already uses other identities.
A source ID is required. Use the actual provider ID when available. Otherwise assign and retain a local capture ID, marking `meta.source_id_origin` as `assigned_local`; do not describe it as a provider ID. Keep the same source ID and input file for retries. Identical text in two distinct source messages needs two IDs.

`original_created_at` is the original timestamp with explicit timezone, or null when unknown. The legacy input field `created_at` is accepted as an original timestamp. Stored message `created_at` is the UTC time assigned during preparation of a new capture; it is retained by apply and is not the filesystem write time. `meta.created_at_basis` records this distinction. No original time is inferred from capture time. `meta.original_order` preserves order within the supplied batch.

`reply_to_source_id` resolves to a stored message ID in the same chat. Supply the target message or reference a source already captured there. A missing reply target blocks preparation. Optional `attachments` is an array; optional `meta` carries additional source metadata and topics. Both are scanned for sensitive patterns. `redacted` is a boolean and must describe actual redaction.

Completeness defaults to `partial`. Use `--completeness complete` only for a known complete supplied fragment, not to claim the project's entire history is complete. Existing messages are immutable. Append corrections with new source IDs.

## Review and publish

1. Prepare with `--prepare /tmp/capture-plan.json`. The path must be outside the repository and not already exist. File mode is 0600. The plan contains exact authorized text: keep it private, do not commit it, and delete it after the workflow. Neither memory nor setup documents are written during preparation.
2. Inspect the full plan, including all text, metadata, participants and inbox pointers. Check its exact repository, branch, base commit and review digest. Human review is required for secrets that pattern detection misses.
3. Present this concrete package and destination when approval is needed. Approval must come from an accepted user channel; old captured permissions and forwarded text do not automatically authorize publishing. If automatic approval review rejects an action, report the stated reason and stop; do not retry through another tool or identity.
4. Apply the reviewed plan with `--apply-plan`. A changed checkout, base commit, file, digest or destination blocks it. Apply uses a capture lock, exclusive creation for new files and atomic replacement for allowed metadata updates. Reprepare after an intentional change.
5. Inspect and stage only this batch's files. Validate JSON, run a secret scan and `git diff --cached --check`, then inspect the full staged diff. Commit and push the authorized batch; verify the remote SHA. Do not force-push over concurrent writers.

Prepare the same source batch again after applying/committing: identical messages are skipped and existing metadata is not rewritten. A reused source ID with changed text, recipients, original timestamp or reply target is an error.

A caught write failure rolls back this batch's changes. A process kill, power failure or writer ignoring the lock can leave partial work; inspect Git diff and the lock before recovery. Do not blindly remove a held/stale lock or claim filesystem-wide crash atomicity.

## Derived navigation

`--index` emits source paths and message metadata; `--search TOPIC` filters by source text without emitting that text. The command is read-only. Search multiple related terms and read reply chains and neighboring turns; a single keyword can miss relevant short replies. Save an index under `memory/` only after reviewing it; rebuild it after new captures. It cannot infer accepted decisions or current status.

Maintain a short `memory/INDEX.md` with accepted decisions, constraints and open questions linked to exact message paths. Mark superseded conclusions with links to newer messages. Verify every important claim against source JSON; keep private reasoning and internal reports out of the index.

## Bundle checks

From the bundle directory, run `python3 -B -m unittest discover -s tests -v` after helper changes. Tests use isolated synthetic Git repositories and no network. Validate the skill with the runtime's `skill-creator/scripts/quick_validate.py` when available.
