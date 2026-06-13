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
