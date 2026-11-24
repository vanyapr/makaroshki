# Flush and check actual supplied messages

Read the project's local root instruction and source Protocol v1 JSON before work and after restart. Git registration binds the exact checkout and real origin to a private store outside Git. Multiple checkouts of the same repository may share its exact store; unrelated repositories cannot. For a project without a verified origin, use [local-directory.md](local-directory.md): persistent local UUID, exact directory and its own local-only private store. Never use a fake origin to initialize memory.

Get only the available authorized project user and user-facing assistant messages from a supported interface or explicitly provided source. Include short replies, repeated text, progress/commentary and final answers as separate rows. Do not read private runtime sessions, copy hidden instructions/reasoning/internal reports, import raw tool outputs, or invent unavailable fragments. If no exact source is available, report that gap.

Use the provenance envelope in capture.md: source system/conversation, stable source IDs and origin, explicit increasing order/basis, `source_channel: user|assistant_commentary|assistant_final`, `from: HUMAN|AGENT`, exact source `text`, known `original_created_at` or null. Older assistant messages may use `CODEX`. Keep assigned IDs stable and identify them as assigned. Inventory is optional. Only user/assistant rows are accepted; never pass tool exports to this script.

Pass the envelope on stdin without writing a raw input file:

```bash
python3 /path/to/skill/scripts/flush_messages.py \
  --config /absolute/private/capture.json --project-root /absolute/verified-checkout
```

The script redacts known complete credentials in memory, validates the entire supplied fragment, prepares/applies through the append-only helper, then launches a **new Python process** to reload the local store and compare every expected source ID, message path and planned file SHA256. Its JSON output gives expected/saved counts, user/assistant counts, IDs, missing/mismatched IDs and `fresh_process_verified`. Retry is a no-op. Capture failures return nonzero; report and retry from the still accessible source, without claiming success.

Flush when each message becomes accessible, at task boundaries and before a planned restart; reload the store at startup/resume. Preserve an answer before finish using [agent capture's prepared reply](agent-capture.md); it remains unconfirmed until its actually observed ID/body is captured. Do not represent preparations as delivered history. Local command hooks do not run in cloud-orchestrated tasks; even in a local CLI they may omit commentary or intermediate messages. A busy lock, interrupted runtime or missing source can leave gaps; this is not a guaranteed durable queue.

When the user asks to verify everything was saved, compare against the actual accessible source's user/assistant list. `all_supplied_messages_saved` proves exactly the supplied batch, not omitted upstream turns or a whole chat. Record unavailable source boundaries and missing user/assistant bodies honestly. A fresh Python reload proves filesystem persistence; runtime delivery and retrieval require their own checks.

The store has no remote. Check actual repository visibility before any separately authorized export; never publish private messages in a public or unverified repo. Preserve existing dirty work, hooks, notify, instructions and unknown JSON fields. Local and published historical sources remain distinct; do not move another project's conversation here.
