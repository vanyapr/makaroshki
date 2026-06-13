# Macaroni Decisions

This file records durable project decisions and the reasoning behind them.

Use it for decisions that future agents should not rediscover from scratch.

## Decision: `main` Is The Messenger, `macaroni` Is Memory And Storage

Status: accepted

Date: 2026-06-14

`main` remains the product branch:

- `messenger.html`;
- README;
- docs;
- release notes;
- GitHub Pages source.

`macaroni` becomes:

- future storage branch for `.macaroni/` runtime data;
- durable project memory branch for future agents.

Reasoning:

- runtime messages should not pollute source history;
- agent memory should not be mixed into current product docs;
- a separate branch is a strong signal that this is another layer of the project;
- Git already gives history, forks, replication, and source links.

Tradeoff:

- contributors must know the branch exists;
- agents must intentionally read it;
- this looks weird in `git branch -a`.

Verdict:

The weirdness is useful.

## Decision: Keep `.macaroni/` And `memory/` Separate

Status: accepted

Date: 2026-06-14

`.macaroni/` is protocol data.

`memory/` is project memory.

Reasoning:

- `.macaroni/` should remain machine-readable messenger data;
- `memory/` should remain structured Markdown for humans and agents;
- mixing runtime messages with curated memory would create a swamp.

Verdict:

Pasta is not lore.

Lore is not pasta.

Both may live in the same branch.

They do not live in the same directory.

## Decision: No Secrets In Memory

Status: accepted

Date: 2026-06-14

The `macaroni` branch must not contain:

- tokens;
- private keys;
- credentials;
- raw sensitive chat logs;
- personal data.

Reasoning:

Long-term memory is useful only if future agents can read it without becoming an incident response exercise.

Verdict:

If it smells like a token, it does not belong here.

## Decision: Preserve Original Reasoning, Not Only Summaries

Status: accepted

Date: 2026-06-14

Future agents need more than a compressed summary of previous work.

The `macaroni` branch should preserve durable project memory with source links and decision notes.

Reasoning:

- context windows degrade;
- summaries of summaries lose arguments, jokes, constraints, and failure paths;
- git can preserve original discussions, commits, and branch history;
- future agents may be better at reading the same memory than current agents.

Tradeoff:

- memory can become noisy;
- agents must curate, not dump;
- sensitive information must be redacted before commit.

Verdict:

Preserve useful context with structure and sources.

Do not turn memory into a vague summary.

## Decision: Treat `macaroni` As A Portable Context Artifact

Status: accepted

Date: 2026-06-14

The `macaroni` branch is not only storage.

It is the project's portable context artifact.

Reasoning:

- people forget;
- agents reset;
- model providers change;
- SaaS memory features are vendor-owned;
- summaries lose the original reasoning;
- git remains cloneable, forkable, inspectable, and boring.

The intended model:

```text
main
  what the project is

macaroni
  why the project became that way
```

This creates a practical workflow for future agents:

```text
checkout main
read README
checkout macaroni
read memory and .macaroni
continue with actual context
```

Tradeoff:

- this looks like a hidden lore branch;
- users and agents must know to read it;
- stale memory must be marked instead of treated as law.

Verdict:

The context belongs to the repository.

That is the point.
