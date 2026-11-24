# Agent-driven capture

Projects without a verified origin use [local-directory.md](local-directory.md): explicit local-only UUID/path binding and agent calls; no fake origin or hooks activation. Existing Git bindings retain their origin checks.

Run the helpers wherever the reviewed bundle and the registered private store are accessible. The caller supplies authorized messages over standard input. This workflow requires no model API or client hooks.

## On input, output and resume

1. At startup/resume, read the project's AGENTS.md, local protocol/participants/relevant source messages, and `agent_capture.py --status` for this exact checkout. Resolve pending prepared replies against an available supported source; an unconfirmed reply may already have been sent, so do not send it again automatically.
2. As each authorized project user message or visible assistant message becomes accessible, pass its actual ID/body to `--messages`. Capture short replies and progress as well as final answers. Filter to user/assistant rows before calling; never pass raw tool/session exports, hidden instructions, reasoning, internal delegation briefs or agent reports. Verify returned IDs/counts/body hashes; report capture errors and missing source access.
3. Before emitting a user-facing reply or finishing, freeze its intended text with `--prepare-reply`. It is redacted, privately persisted and reloaded by a new process. Emit exactly `reply_text_to_emit`. This is a prepared reply, not proof of delivery and not an observed history message.
4. When its actual source ID/body becomes available, call `--confirm-reply ASSIGNED_REPLY_ID`. The script compares source/project/channel/text, saves the observed message through verified flush and appends a receipt linking it to the preparation. Mismatches block; messages and preparations remain append-only. If the actual reply is never exposed by the runtime, retain the durable preparation and report it as unconfirmed.

Use the available source list only. Do not claim a whole conversation was saved if the source exposes only a fragment. The source interface must supply actual IDs/body/order or clearly identify locally assigned IDs and unknown times. A prepared answer, a synthetic fixture and an internal report are distinct from an observed user/assistant conversation.

## Caller interface

Every command takes JSON on stdin and returns JSON. Do not write raw input files. Set `SKILL_DIR` to the bundle directory, `CAPTURE_CONFIG` to the private registry file and `PROJECT_ROOT` to the verified project directory. Use absolute paths. Ordinary filesystem approval still applies; do not expand global execution permissions.

```bash
python3 "$SKILL_DIR/scripts/agent_capture.py" \
  --config "$CAPTURE_CONFIG" \
  --project-root "$PROJECT_ROOT" --messages
```

The incoming observed-message batch uses the existing flush schema. The following is a **format example, not source data**:

```json
{
  "version": 1,
  "capture": {
    "source_system": "example_runtime",
    "source_conversation_id": "ACTUAL_PROJECT_THREAD_ID",
    "source_id_origin": "provider",
    "order_basis": "available_fragment"
  },
  "messages": [
    {
      "source_message_id": "ACTUAL_USER_MESSAGE_ID",
      "from": "HUMAN",
      "source_channel": "user",
      "original_order": 1,
      "original_created_at": null,
      "text": "EXACT_USER_BODY"
    },
    {
      "source_message_id": "ACTUAL_ASSISTANT_MESSAGE_ID",
      "from": "AGENT",
      "source_channel": "assistant_final",
      "original_order": 2,
      "original_created_at": null,
      "text": "EXACT_USER_FACING_ASSISTANT_BODY"
    }
  ]
}
```

Known original time is UTC; otherwise null. Explicit order is relative to the accessible fragment, not invented upstream history. Use `assistant_commentary` for progress. For IDs genuinely unavailable, use stable assigned IDs and `source_id_origin: assigned_local`; do not label them as provider IDs. If rows have different ID origins, send separate batches. Preserve the actual conversation ID consistently across calls.

`--messages` returns expected/saved and user/assistant counts, every source ID, message path and redacted text SHA256, plus fresh-process verification. Retry writes zero files. It does not read a runtime's conversation history itself. The caller supplies these rows and the verified project directory. Set `source_system` to a stable identifier for the actual source.

For `--prepare-reply`, stdin is:

```json
{
  "version": 1,
  "source_system": "example_runtime",
  "source_conversation_id": "ACTUAL_PROJECT_THREAD_ID",
  "reply_id": "assigned_reply_UNIQUE_UUID",
  "source_channel": "assistant_final",
  "reply_to_source_message_id": "ALREADY_CAPTURED_USER_ID",
  "text": "FROZEN_INTENDED_USER_FACING_REPLY"
}
```

Use a new assigned reply ID for each intended emission; retain it for retries. The optional reply-to source must already be a user message in this project's same source system and conversation. `--confirm-reply assigned_reply_UNIQUE_UUID` accepts the observed-batch schema with exactly that one actually observed assistant row. The source system, conversation and channel must match the preparation, and the redacted text must be identical. Keep its real provider ID. A changed actual reply is captured as its own observed message, while the earlier unmatched preparation stays unconfirmed; never force-confirm a different body.

`--status` takes no stdin. It lists observed source IDs and unconfirmed preparations, without message bodies. Prepared replies live in `.macaroni/prepared/`; receipts in `.macaroni/prepared_receipts/`. They do not inflate observed message counts.

## Project ambiguity

If a source belongs to an unclear project, store only its real reference using `--reference-source` (no project-root argument). Never include a body. Stdin: `version`, `source_system`, `source_conversation_id`, and optionally `source_message_id`, `source_uri`, `candidate_repositories`. The URI must be a credential-free HTTPS link without query/fragment; omit it when only actual source IDs are known. This appends `unresolved_sources` to the existing private registry and preserves all unknown fields and project mappings. Read the source through a supported interface and establish project scope before later message capture.

No command performs network, Git commit/push, deployment, cloud installation or private-session reads. Export requires separate authorization for exact project data and a currently confirmed private remote. Root instructions and existing JSON fields must be preserved.
