# Show HN Notes

Suggested title:

> Show HN: Macaroni Messenger - a messenger in one HTML file using Git as the database

Short pitch:

Macaroni Messenger is a single-file messenger: `messenger.html`, no backend, no database except Git, messages are JSON files in `.macaroni/`.

It is explicitly not private.

That is not a hidden limitation. That is the warning label.

The demo is hardcoded read-only so Hacker News traffic does not immediately burn unauthenticated GitHub API rate limit. Real repositories are connected through Settings.

## What To Try

1. Open the live demo.
2. Switch chats.
3. Search messages.
4. Open Chat Info.
5. Look at `.macaroni/` in the repository.
6. Download `messenger.html` and open it locally.

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

### Why not use a backend?

Because Git already stores files and we were trying to send "Mom, please cook macaroni", not run a payments company.

### Why is the demo hardcoded?

Because Hacker News can create enough traffic to hit unauthenticated GitHub API rate limits before anyone sees the joke.

### Can I write real messages?

Yes. Connect a GitHub repository in Settings and use a fine-grained token with `Contents: Read and write`.

### Should I paste my token into Hacker News?

No.

If you already did, revoke it.
