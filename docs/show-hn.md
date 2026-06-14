# Show HN Notes

Suggested title:

> Show HN: Macaroni Messenger - a messenger in one HTML file using Git as transport

Short pitch:

Macaroni Messenger is a single-file messenger: `messenger.html`, no backend, no database except Git, messages are JSON files in `.macaroni/`.

It now has built-in browser adapters for GitHub, GitLab, GitVerse, Gitea, and Forgejo.

It also has optional Encryption 1.01.

Encryption 1.01 is not a new protocol. It is a plugin that turns message text into `MACARONI1.01:<base64-json>` and back.

It is explicitly not a "secure messenger".

That is not a hidden limitation. That is the warning label.

The demo is hardcoded read-only so Hacker News traffic does not immediately burn unauthenticated GitHub API rate limit. Real repositories are connected through Settings.

## Copyable Post

```text
Macaroni Messenger is a messenger implemented as one HTML file.

No backend.
No database except Git.
No registration.

Messages are JSON files in .macaroni/.

The browser client can read/write through built-in adapters for GitHub, GitLab, GitVerse, Gitea, and Forgejo.

There is also Encryption 1.01: a plugin layer that encrypts message text without changing the Macaroni protocol.

It is not a secure messenger.
It is an honest messenger.

Unfortunately, it works.
```

## What To Try

1. Open the live demo.
2. Switch chats.
3. Search messages.
4. Open Chat Info.
5. Look at `.macaroni/` in the repository.
6. Open Settings and look at the provider list.
7. Look at the Plugins section and Encryption 1.01.
8. Download `messenger.html` and open it locally.

## FAQ

### Is this a joke?

Partially.

### Does it work?

Unfortunately, yes.

### Where are messages stored?

In `.macaroni/` inside a Git repository.

### Is it private?

No.

If the repository is public, messages are public.

If the repository is private, messages are readable by everyone with repository access.

If Encryption 1.01 is enabled, repository readers see encrypted payloads instead of plaintext, but the project still does not sell "real privacy".

### Why not use a backend?

Because Git already stores files and we were trying to send "Mom, please cook macaroni", not run a payments company.

### Why is the demo hardcoded?

Because Hacker News can create enough traffic to hit unauthenticated GitHub API rate limits before anyone sees the joke.

### Can I write real messages?

Yes. Built-in browser adapters exist for GitHub, GitLab, GitVerse, Gitea, and Forgejo. Connect a repository in Settings and use a provider token with repository content read/write access.

The `.macaroni/` protocol itself is not GitHub-specific. Custom/self-hosted git hosts still need a browser-compatible API/CORS setup; see [generic git provider contract](generic-git-provider.en.md).

### Does it only support GitHub?

No.

GitHub was the first adapter. The current single HTML file also has GitLab, GitVerse, Gitea, and Forgejo adapters.

This is Macaroni's practical "isomorphic git": small browser-side adapters over host APIs, not an npm dependency and not raw SSH from a browser tab.

### Does encryption change the protocol?

No.

Macaroni Protocol v1 stays the same. Messages are still JSON files in `.macaroni/`.

Encryption 1.01 is a plugin layer over `message.text`.

Plaintext:

```json
{ "text": "Mom, please cook macaroni" }
```

Encrypted plugin payload:

```json
{ "text": "MACARONI1.01:<base64-json>" }
```

Core does not care. Git does not care. Mom probably should not care either.

### Is Encryption 1.01 real encryption?

Yes, in the most Macaroni way possible.

It uses a shared secret, salt, message context, token confetti when available, Tiny PRNG, and XOR.

No handshake.

No key server.

No external dependency.

No claim that this protects you from serious people with serious budgets.

If you need "real privacy", use PGP. If you need to stop random public repository readers from reading "cook macaroni", this is the correct level of ridiculous.

See [Macaroni Encryption 1.01](encryption-1.01.en.md).

### Should I paste my token into Hacker News?

No.

If you already did, revoke it.
