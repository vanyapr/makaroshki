# Macaroni Timeline

This file tracks how Macaroni Messenger became what it is.

It is not a changelog.

It is the project memory timeline.

## 2026-06-08 - Origin

Macaroni Messenger started as a deliberately absurd but working idea:

- one `messenger.html`;
- no backend;
- no database;
- messages stored as JSON files in git;
- local browser storage as cache;
- Git as the source of truth.

The original use case was intentionally small:

> Tell mom to cook macaroni.

The project principle became:

> Do not make things complicated when they can be funny.

This did not cancel the requirement that the result must be real software.

## 2026-06-09 - Public Demo And HN Readiness

The project grew a public GitHub Pages demo, demo chats, README positioning, known limitations, license, screenshots, and a Show HN pitch.

The important product decision:

- the demo must work without a token;
- unauthenticated GitHub API rate limit must not be the first thing a visitor sees;
- therefore the public demo can be hardcoded read-only data.

## 2026-06-13 - Encryption 1.01

Macaroni Encryption 1.01 was implemented as a built-in plugin.

It did not change Macaroni Protocol v1.

It turns `message.text` into:

```text
MACARONI1.01:<base64-json>
```

It uses:

- shared secret;
- salt;
- Tiny PRNG;
- XOR;
- Token Confetti;
- localStorage plugin settings;
- view-layer decrypt.

The release framing was intentionally quiet:

> Fixed a typo. Also a few small things.

One of the small things was encryption.

## 2026-06-13 - Storage Branch

A separate orphan branch named `macaroni` was created.

The branch is not named `.macaroni` because Git does not allow that branch name.

The purpose:

- keep source/docs/releases in `main`;
- move runtime `.macaroni/` data into a dedicated branch;
- later allow `storage_branch: "macaroni"` in client settings.

## 2026-06-14 - Macaroni Memory

The `macaroni` branch became more than future runtime storage.

It became the long-term project memory branch.

The core idea:

```text
main
  what the project is

macaroni
  how the project became what it is
```

This creates a simple persistent memory layer for future agents:

- original discussions can remain source-linked;
- decisions can survive context-window resets;
- failed experiments can be remembered;
- future agents can inherit project culture, not only README facts.

This is not an AI memory SaaS.

It is `git checkout macaroni`.
