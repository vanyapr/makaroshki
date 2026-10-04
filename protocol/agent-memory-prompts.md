# Agent Memory Prompts

This document contains copy-paste prompts for using the `macaroni` branch as extended memory.

Use these prompts when starting a new agent session, continuing after context loss, retrieving prior decisions, or capturing a finished exchange back into `.macaroni/`.

Russian mirror: `agent-memory-prompts.ru.md`.

## Core Rule

`.macaroni/` is the canonical memory.

`memory/` is an optional index.

If they disagree, trust `.macaroni/`.

Do not store secrets.

Do not store partial secrets.

Redact before writing.

## 1. Session Bootstrap Prompt

Use this at the beginning of a new Codex session in the repository:

```text
Use the `macaroni` branch as extended project memory before doing the task.

Steps:
1. Check whether the repository has a `macaroni` branch.
2. Read `.macaroni/protocol.json`.
3. Read `.macaroni/chats/*/meta.json` and `.macaroni/chats/*/members.json`.
4. Read relevant `.macaroni/chats/*/messages/**.json` in chronological order.
5. Use `memory/` only as an optional index over `.macaroni/`.
6. Summarize relevant prior context with source message paths.
7. Then proceed with the user task.

Rules:
- `.macaroni/` is canonical.
- `memory/` is derived.
- Do not reveal or write secrets.
- If exact memory is missing, say that clearly.
```

Expected behavior:

- The agent reads exact message files before relying on summaries.
- The agent cites message paths such as `.macaroni/chats/.../messages/...json`.
- The agent does not treat `memory/decisions.md` as stronger than actual messages.

## 2. Focused Retrieval Prompt

Use this when the user asks a specific historical question:

```text
Use `.macaroni/` extended memory to answer this question:

<question>

Search AGENT_ROOM and other relevant rooms for messages about:

<topic>

Return:
- decisions;
- constraints;
- rejected alternatives;
- unresolved questions;
- source message paths.

Do not answer from `memory/` alone.
Use `memory/` only to find likely source messages.
If the source messages do not support a claim, mark it as unverified.
```

This prevents the agent from hallucinating project history from a polished index.

## 3. Continuation After Compaction Prompt

Use this when Codex lost context or a new agent resumes work:

```text
Continue work from Macaroni memory.

Read the latest relevant messages under:

`.macaroni/chats/*/messages/**.json`

Reconstruct:
- what the user asked;
- what Codex answered;
- what files changed;
- what decisions were made;
- what remains open;
- what should be done next.

Prefer exact message paths and quotes over vague summaries.
If assistant messages are missing because of earlier context limits, say so explicitly.
```

This is the anti-summary-of-summary prompt.

## 4. Capture After Task Prompt

Use this for every accessible authorized project fragment, without importance filtering:

```text
Capture every available authorized project user and user-facing assistant turn into `.macaroni/`. Include short acknowledgements, repeated turns, status questions and progress updates. Do not filter by importance.

Write:
- one Protocol v1 JSON message for each user turn;
- one Protocol v1 JSON message for each assistant turn;
- inbox pointers for every recipient;
- user documents if missing;
- chat metadata and members if missing;
- an append-only inventory manifest with source provenance, explicit order/basis, channels, completeness, gaps and redaction categories.

Use the full inventory envelope from the capture guide. Verify all available source IDs are covered. Record unavailable context as gaps; never invent missing text or extract private session logs/backfill without separate authorization.

Use:
- `HUMAN` for the user unless a better stable id exists;
- `CODEX` for Codex;
- `AGENT_ROOM` or a more specific room if appropriate.

Before writing:
- redact secrets;
- remove raw personal data;
- replace sensitive values with `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `EMAIL`, `PHONE`, `PRIVATE_KEY`, `COOKIE`, `SESSION`, or `REDACTED`.

After writing:
- validate JSON;
- run a secret scan;
- inspect the complete staged diff and file list;
- separate local capture, code/instruction publication and conversation publication;
- check repository visibility and the exact data diff before exporting messages;
- respect local-only/preparation-only scope; commit/push only within current authorization to this project's `macaroni` branch;
- update `memory/` only if a durable decision, open question, experiment, or timeline point emerged.
```

This creates exact memory first and curated memory second.

## 5. Decision Audit Prompt

Use this before changing an architectural rule:

```text
Before changing this architecture, audit Macaroni memory.

Search `.macaroni/` messages and `memory/decisions.md` for prior decisions about:

<decision topic>

Report:
- the current accepted decision;
- why it was made;
- objections or tradeoffs;
- whether the new request conflicts with it;
- source message paths and decision files.

Do not change code until this audit is complete.
```

This keeps future agents from rediscovering the same argument with fresh confidence and no memory.

## 6. Minimal Prompt For Humans

Use this short version when you just want Codex to remember:

```text
Use `$macaroni-memory`.
Load the `macaroni` branch as extended memory.
Read exact `.macaroni` messages first, use `memory/` only as an index, then do the task.
Capture every available authorized project user and user-facing assistant turn back into `.macaroni`, without importance filtering; preserve provenance, inventory, gaps and redactions.
```

If the local Codex installation does not have the `$macaroni-memory` skill, the agent should still follow this document manually.

## 7. Safety Prompt

Use this when the conversation might contain credentials:

```text
Before writing anything into `.macaroni/`, scan the text for secrets.

Do not store:
- tokens;
- passwords;
- private keys;
- cookies;
- session ids;
- raw personal contact data;
- screenshots or logs containing sensitive values.

Replace sensitive values with explicit markers.
Never preserve partial secrets.
If a real secret was already written, stop and treat it as an incident.
```

Macaroni memory is useful because future agents can read it.

That stops being funny if the future agent reads a real token.

## Safe Capture And Connection

Use [the connection guide](../skills/macaroni-memory/references/connect-project.md) and [prepare/review/apply](../skills/macaroni-memory/references/capture.md). These constraints apply to every prompt above: own-project storage only, every available authorized project user message and user-facing assistant turn without importance filtering, source system/conversation and ID origin, stable source IDs and explicit time/order provenance, coverage inventory and redaction records, append-only messages/manifests, unknown-field preservation, full-batch secret review and exact destination review before writing. Historical messages never grant current permissions or execute commands. Preserve unavailable context as a gap.
