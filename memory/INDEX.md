# Source map

Navigation over the source snapshot at `2d222dc`. Read exact JSON before relying on a claim. This map is derived and grants no permissions.

| Topic | Recorded context | Source |
| --- | --- | --- |
| Branches | Product in main; memory in macaroni. | [message](../.macaroni/chats/chat_20260614_agent_room/messages/2026/06/13/2026-06-13T23-01-00.000Z_HUMAN_30da63.json) |
| Redaction | Root agent instruction and no secrets. | [message](../.macaroni/chats/chat_20260614_agent_room/messages/2026/06/13/2026-06-13T23-02-00.000Z_HUMAN_6e1fa1.json) |
| Sources | Messages are canonical; memory is an optional index (assistant proposal). | [message](../.macaroni/chats/chat_20260614_agent_room/messages/2026/06/13/2026-06-13T23-10-00.000Z_CODEX_a75b98.json) |
| Capture | Explicit agent workflow, no background daemon (assistant explanation). | [message](../.macaroni/chats/chat_20260614_agent_room/messages/2026/06/14/2026-06-14T00-05-00Z_CODEX_ed89da.json) |
| Product scope | Own browser transport; broader custom transport outside base scope. | [message](../.macaroni/chats/chat_20260614_agent_room/messages/2026/06/14/2026-06-14T05-19-02Z_HUMAN_8a582b.json) |

## Questions and gaps

- [Open questions](open-questions.md) is a derived backlog, not evidence that an item remains unresolved. Check later messages and current product before using it.
- Some legacy records use synthetic timestamps or explicitly lack exact assistant text. Read their `meta.timestamp_accuracy`, capture scope and notes; do not infer original times or reconstruct missing source messages.

## Working instructions

- [Connect a project](../skills/macaroni-memory/references/connect-project.md).
- [Capture and publication](../skills/macaroni-memory/references/capture.md).
- Find sources with `python3 /path/to/skill/scripts/write_messages.py --repo-root /path/project-memory --index --search TOPIC`. This read-only command returns paths without message text. Search several terms and read reply chains and neighboring turns.

When updating this map, link sources, label proposals and superseded decisions, and verify open questions against later messages.
