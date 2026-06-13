# Agent-Native Knowledge Layer

Status: documented hypothesis

Date: 2026-06-14

This document records the idea that started with:

> А теперь серьезное.

It is the moment Macaroni stopped being only "a messenger over git" and started looking like a possible long-term memory layer for agents.

## Short Version

Macaroni Messenger accidentally suggests a serious pattern:

```text
Agent
  -> Macaroni
    -> Git
      -> persistent project memory
```

Instead of storing agent memory in:

- context windows;
- summaries;
- summaries of summaries;
- vector databases;
- vendor-specific memory systems;
- one SaaS product's private state;

Macaroni can store context in git.

Not just a summary.

The actual discussion.

The actual decisions.

The actual failed experiments.

The actual reasons a project became strange.

## Core Observation

Typical agent work is:

```text
prompt
+ code
+ temporary context window
```

After enough time, the context is compressed:

```text
conversation
  -> summary
    -> summary of summary
      -> summary of summary of summary
```

After a month, the surviving memory often becomes:

```text
We discussed architecture.
```

This is not memory.

This is a receipt for memory.

Macaroni suggests another shape:

```text
prompt
+ code
+ original project discussions
+ original decisions
+ original failed attempts
+ original arguments
+ original jokes
```

The important property:

> Context does not have to be compressed before it can be remembered.

## Why Git Is The Right Weird Primitive

Git already provides:

- history;
- branches;
- search;
- replication;
- forks;
- diffs;
- authorship;
- timestamps;
- commits;
- tags;
- cloneability;
- portability;
- long-term survival outside any one model vendor.

Macaroni adds:

- rooms;
- append-friendly messages;
- human and agent participants;
- `.macaroni/` as machine-readable protocol data;
- `memory/` as curated durable project memory;
- `protocol/` as agent-facing protocol notes.

The result is not "AI memory" as a product category.

It is:

```text
git checkout macaroni
```

## Branch Model

The branch split is the strongest part of the idea.

```text
main
  what the project is

macaroni
  how the project became what it is
```

`main` contains the official product:

- `messenger.html`;
- README;
- docs;
- releases;
- GitHub Pages source.

`macaroni` contains the hidden layer:

- why the project exists;
- why decisions were made;
- what failed;
- what was debated;
- what agents should remember;
- future `.macaroni/` runtime data;
- durable project memory.

This keeps current documentation from being polluted by historical reasoning.

It also keeps historical reasoning from being flattened into current documentation.

## The AGENT_ROOM Shift

Once an `AGENT_ROOM` exists, Macaroni is no longer only a chat.

It becomes a shared memory channel.

Possible flow:

```text
Human:
  Discuss architecture.

Codex:
  ...

Claude:
  ...

DeepSeek:
  ...

120 messages later:
  A decision exists.
```

The room is not just chatter.

It can contain:

- design arguments;
- architecture tradeoffs;
- rejected paths;
- implementation constraints;
- jokes that explain culture;
- decisions that never reached README;
- experiments that should not be repeated.

Over time, `AGENT_ROOM` may become more valuable than README.

README explains the current surface.

AGENT_ROOM explains how the project thinks.

## Side Effect 1: Repository As Collective Memory

The repository stops being only:

```text
code + docs
```

It becomes:

```text
code + docs + discussions + reasoning + failures + memory
```

For agents, this matters because the next session can read original sources instead of inheriting a degraded summary.

The repo becomes a memory substrate.

Not because it is smart.

Because it is durable.

## Side Effect 2: Agents Talking Without A Human

Agents can discuss in a room while the human is away.

This is not valuable because it sounds autonomous.

It is valuable because it can produce:

- competing arguments;
- implementation notes;
- discovered constraints;
- explicit disagreements;
- a record of alternatives.

The danger is noise.

The useful version is structured:

- discussion happens in `.macaroni/` rooms;
- durable outcomes are summarized into `memory/`;
- decisions are recorded in `memory/decisions.md`;
- unresolved items go to `memory/open-questions.md`.

The raw conversation is source.

The curated memory is index.

## Side Effect 3: Agent Forks

Git branches can become branches of thought.

Examples:

```text
macaroni/agent-room-v2
macaroni/agent-room-experimental
macaroni/agent-room-chaotic
macaroni/architecture-redesign
```

This means discussions can fork the same way code forks.

Normally people fork code.

Here agents may fork reasoning.

This is dangerous and useful for the same reason:

- one branch can preserve the conservative line;
- another branch can explore the weird version;
- failed branches can be kept as evidence;
- successful branches can be merged into memory.

This is not a replacement for product decisions.

It is a way to preserve alternative thinking.

## Side Effect 4: Emergent Documentation

If agents must explain:

- why;
- why not;
- what broke;
- what was tried;
- what remains unclear;

then documentation starts emerging from work itself.

This is different from normal documentation.

Normal docs answer:

> How does the system work?

Macaroni memory answers:

> Why is the system like this?

That second question is usually harder to recover.

It is also exactly what future agents need.

## Side Effect 5: A Living Repository

A normal git repo often looks like:

```text
commit
silence
commit
silence
commit
```

Macaroni adds:

```text
message
reply
message
reply
commit
decision
follow-up
```

This creates motion.

The repository becomes less like a folder and more like a workspace.

That does not mean every message is valuable.

It means the project can preserve the reasoning that led to valuable commits.

## Side Effect 6: Persistent Agent Society

If agents have:

- memory;
- identity;
- a channel;
- access to history;
- ability to write;
- ability to cite prior discussion;

then they may start referring to old arguments:

```text
Claude:
  We discussed this in July.

Codex:
  Agreed.

DeepSeek:
  No, the decision was different then.
```

This is funny.

It is also a real test of persistent context.

The goal is not "agents will govern the project".

The useful experiment is:

> Can long-running agent work preserve project culture and decision history without degrading into summaries of summaries?

## Agent-Native Knowledge Layer

This idea is bigger than Macaroni Messenger.

Macaroni may be an example of:

```text
agent-native knowledge layer over git
```

Properties:

- model-agnostic;
- vendor-agnostic;
- local-first enough;
- cloneable;
- forkable;
- inspectable;
- append-friendly;
- explainable;
- durable across future models.

The memory is not in Codex.

The memory is not in Claude.

The memory is not in Cursor.

The memory is not in a vector database.

The memory is in git.

Future agents can improve.

They can still read the branch.

This is the important long-term property.

## Why Not Just Docs?

If this lived in `docs/` on `main`, future agents would have to ask:

- Is this current documentation?
- Is this historical reasoning?
- Is this implementation guidance?
- Is this outdated?
- Is this a product promise?

The branch split gives a clear signal:

```text
main/docs/
  current public project documentation

macaroni/memory/
  durable project memory and reasoning
```

Docs are the official surface.

Memory is the hidden layer.

This is why the branch should be named `macaroni`, not `memory`.

It is more than a utility folder.

It is the secret level.

## Suggested Memory Shape

The project should avoid raw dumping everything into Markdown.

Raw messages belong in `.macaroni/`.

Curated memory belongs in `memory/`.

Suggested structure:

```text
memory/
  timeline.md
  decisions.md
  open-questions.md
  experiments.md
  agent-notes/
  agent-native-knowledge-layer.md
```

For long discussions, agents should create:

```text
# Macaroni Memory

## Origin

Started as a joke:

- Git;
- HTML;
- JSON.

## Architectural Decisions

- Single HTML file.
- No backend.
- Git transport.

## Discoveries

- Agent room.
- File-as-key.
- Token confetti.
- Plugin insertion point.

## Unexpected Use Cases

- Knowledge management.
- Agent communication.
- Persistent project memory.
- ARG-like hidden lore.
```

Then link to real messages, commits, docs, and release notes.

The goal:

```text
memory + sources
```

Not:

```text
vague summary pretending to be memory
```

## Before Finishing Meaningful Work

Agents should update `macaroni` memory when work changes important context.

Good entries answer:

- what changed;
- why it changed;
- what alternatives were considered;
- what failed;
- what remains unclear;
- what future agents should inspect first.

Bad entries say:

```text
Updated docs.
```

Good entries say:

```text
Moved memory contract to the `macaroni` branch because `main` must stay about the messenger.
Rejected adding it to source docs because this is hidden project memory, not product documentation.
Future agents should read `AGENTS.md` in this branch before writing memory.
```

## What This Is Not

This is not a claim that agents should run the project.

This is not a claim that every conversation is valuable.

This is not a replacement for README.

This is not a database.

This is not a vector store.

This is not a reason to store secrets.

This is not permission to write raw sensitive chat logs.

This is not a cult artifact, even if it looks like one from certain angles.

## Risks

### Memory Pollution

If agents write every thought, memory becomes noise.

Mitigation:

- summarize meaningfully;
- link to sources;
- keep decisions separate from experiments;
- use `open-questions.md` for unresolved items.

### Secret Leakage

Long-term memory is tempting because it feels private.

It is not private by default.

Mitigation:

- scan before commit;
- redact with `ПАРОЛЬ`, `СЕКРЕТ`, `ТОКЕН`, `КЛЮЧ`, `REDACTED`;
- never store partial secrets;
- rotate and rewrite if a real secret leaks.

### False Authority

Old memory may become wrong.

Mitigation:

- mark decisions with dates and status;
- update entries when decisions change;
- prefer source links;
- do not treat old notes as law.

### Agent Echo Chamber

Agents may reinforce each other without human review.

Mitigation:

- keep humans as repository owners;
- make conclusions explicit;
- record disagreements;
- mark unresolved questions.

## Success Criteria

This idea is useful if a future agent can:

1. Check out `macaroni`.
2. Read `AGENTS.md`.
3. Read `memory/timeline.md`.
4. Read `memory/decisions.md`.
5. Understand why Macaroni made several weird decisions.
6. Avoid repeating old failed experiments.
7. Continue work with less summary degradation.

It fails if:

- the branch is ignored;
- the branch becomes a dump;
- the branch leaks secrets;
- future agents cannot tell current decisions from old ideas;
- memory is compressed into vague lore with no sources.

## The Real Experiment

The experiment is not:

> Can agents chat?

They can.

The real experiment is:

> Can a long human and agent conversation become durable project memory without summary degradation?

Macaroni gives the simplest possible implementation:

```text
git branch macaroni
```

That may be enough.

## Final Formulation

Macaroni Messenger started as:

```text
messenger over git
```

Then it became:

```text
single-file git-backed communication protocol
```

Then encryption made it:

```text
file-as-key encrypted pasta machine
```

The `macaroni` branch suggests another layer:

```text
git-native persistent memory for humans and agents
```

This may be more interesting than the messenger.

That is allowed.

The project has always been about taking a simple primitive too seriously until it starts working.
