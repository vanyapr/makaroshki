# Regular local capture with Codex hooks

Projects without a verified origin use [local-directory.md](local-directory.md): explicit local-only UUID/path binding and agent calls; no fake origin or hooks activation. Existing Git bindings retain their origin checks.

The supported integration uses Codex `UserPromptSubmit` and `Stop` command hooks. It saves the prompt delivered by the first event and `last_assistant_message` delivered by the second, immediately at those events. There is no timer, new daemon, transcript reader or history backfill. It does not audit completeness and does not require a caller-maintained inventory.

Hook configuration alone does not activate execution: non-managed hooks require review and trust of their exact definition in `/hooks`. A new or changed definition is skipped until trusted. Do not bypass or manufacture trust.

## Register one project

Select the exact Git checkout root and verify its origin. Every checkout/worktree must be registered explicitly. A nested, unregistered Git project is skipped even inside a registered project's directory. Generic work folders and personal chats are excluded by default.

Choose a private destination outside **every** Git checkout, for example `~/.codex/macaroni-memory/projects/PROJECT`. It has no Git repository or remote. Its Protocol v1 `repository` identifies the source project; `storage_branch: local` denotes this local storage extension. It is not the project's published `macaroni` branch. Do not copy new conversation data into a remote branch under authorization for code/docs only.

Use the installed script, substituting the actual verified values:

```bash
python3 /path/to/skill/scripts/regular_capture.py \
  --config /absolute/private/capture.json \
  --register-project /absolute/project-checkout \
  --repository https://github.com/OWNER/PROJECT \
  --store-root /absolute/private/projects/PROJECT
```

Registration writes only the private allowlist, not conversations. Existing differing mappings block; compare them before changing scope. Unknown config fields are retained. The config must have mode `0600`; each store has mode `0700`, files `0600`. Checkouts of the same verified repository may share its exact store. Unrelated repositories cannot share a store; nested/overlapping destinations, symlinks, credential-bearing origins, stores inside Git and changed origins are rejected. Do not register broad folders or unknown projects.

## Configure and trust

```bash
python3 /path/to/skill/scripts/regular_capture.py \
  --config /absolute/private/capture.json --hooks-template
```

The command emits a reviewable `hooks.json` definition for exactly two events. It does not install it or change trust. Preserve existing hooks and merge the two handlers deliberately; do not overwrite a differing file. Prefer `<project>/.codex/hooks.json` for a narrow project scope. A global `~/.codex/hooks.json` receives events for all local sessions before allowlist filtering and needs explicit approval of that scope. Keep existing `notify` and all unrelated configuration untouched.

Before activating persistent capture, show the user the exact hook definition, project roots, store destinations, events and filtering behavior. Use native filesystem approval for writes outside the workspace. In a supported local Codex session, review the definitions in `/hooks` and trust them through the native UI. Project config layers also need project trust. Start a new local session if the current runtime has already loaded its configuration. An installed skill is not evidence that hooks are trusted or executing.

Add a pointer to the project's applicable `AGENTS.md`, preserving all existing instructions:

```markdown
Project memory uses macaroni-memory. Published historical sources are in this
repository's macaroni branch. New locally captured messages are in <PRIVATE_STORE>;
read its AGENTS.md and .macaroni/protocol.json before relevant project work.
Use each store's source JSON as evidence; indexes are optional. Hooks save available
UserPromptSubmit/Stop text after redaction without a completeness audit. Never read
private runtime history or upload local conversation data under code/docs permission.
```

The private store should contain the skill's `assets/AGENTS.memory.md` adapted to local storage. Keep a root `AGENTS.md` in a published memory branch as well. Do not merge the memory branch into the product branch to add the pointer.

## Guarantees and limits

- Only event `prompt` or `last_assistant_message` text is considered. `transcript_path`, `agent_transcript_path`, system, reasoning, tool and other payload fields are never dereferenced or copied. Other events, explicit subagent events and known internal delegation wrappers are skipped.
- Hooks provide session/turn IDs rather than provider message IDs. IDs are assigned locally from session, turn, event and **redacted** text. Retried identical events write zero files. Identical text in different turns remains separate. Identical submissions within the same turn cannot be distinguished from event retries; hook-generated prompts also have no independent human-authorship proof. Do not claim original provider message IDs or full chat capture.
- Order is local hook observation order; original message time is unknown (`null`). Progress/commentary, earlier history, attachments and messages not delivered by these two events are not automatically collected. Capture an independently accessible authorized fragment through the manual workflow when needed.
- Known tokens, bearer values, credential assignments, private key blocks, URL credentials and email addresses are redacted **in memory before writes**. An incomplete private key blocks capture. Pattern matching cannot classify every private or sensitive fact; enable capture only in a project whose conversation is authorized for local storage, review before any later export, and use manual redaction for sensitive project data. Raw event payloads are never logged or persisted.
- Missing inventory, missing gap declarations and unaudited history do not block capture. Generated manifests check supplied JSON/hash/link integrity. When the user asks to verify actual saving, use [verified flush](flush.md) for the accessible user/assistant batch; report unavailable history separately. Optional legacy completeness/gap metadata is retained for compatibility.
- The existing helper supplies path checks, dedup, unknown-field preservation, private staging, exclusive append, locks and rollback of caught failures. Busy/stale locks or invalid state skip that capture and produce a generic warning; they do not stop the user's task. There is no durable queue, automatic replay or guaranteed delivery after a crash. Inspect locks and local state rather than blindly deleting them.
- No Git commit, push, upload, network request, additional runtime permission or session-history access is performed by capture. Pause by disabling these two handlers in `/hooks`; removing a project from the allowlist also prevents capture for it.

Official contract: [OpenAI hooks documentation](https://learn.chatgpt.com/docs/hooks).
