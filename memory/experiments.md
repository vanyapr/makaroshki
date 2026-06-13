# Experiments

This file records experiments worth remembering, including failures.

## Experiment: Macaroni As Persistent Agent Memory

Status: proposed

Hypothesis:

Agents lose too much context when long discussions are compressed into summaries.

Alternative:

Store original discussion-derived memory in git, under a branch future agents can read.

Expected useful properties:

- no summary-of-summary degradation;
- branchable memory;
- source-linked decisions;
- model-agnostic persistence;
- future agents can read better than current agents.

Failure modes:

- memory becomes a dumping ground;
- agents write vague summaries instead of useful decisions;
- secrets accidentally get stored;
- nobody reads the branch;
- the branch becomes more interesting than the product.

That last one may not be a failure.

## Experiment: Agent-Native Knowledge Layer

Status: documented

Hypothesis:

An ordinary git branch can act as durable, model-agnostic memory for future agents.

Setup:

- keep `main` as current product/source/docs;
- keep `macaroni` as project memory and future storage;
- place curated memory in `memory/`;
- place runtime protocol data in `.macaroni/`;
- place protocol notes in `protocol/`;
- require agents to redact secrets before writing.

What to observe over time:

- whether future agents actually read the branch;
- whether memory helps avoid repeated mistakes;
- whether source-linked decisions age better than summaries;
- whether AGENT_ROOM discussions produce useful decision notes;
- whether the branch becomes a dump.

A good outcome:

Future agents understand project culture faster than they would from README alone.

A bad outcome:

The branch becomes a dramatic attic full of vague notes.

Both outcomes are informative.
