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
