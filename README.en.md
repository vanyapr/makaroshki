# Macaroni Messenger

## A messenger that fits into one HTML file

Macaroni Messenger is a messenger with no servers, no database, no registration, and no privacy promises.

Messages live in a git repository.

The client is a single HTML file that you can open in a browser.

If you know how to download a web page, you already know how to install Macaroni Messenger.

Documents:

- [PHILOSOPHY.en.md](PHILOSOPHY.en.md) - the main project principle.
- [docs/product-brief.en.md](docs/product-brief.en.md) - detailed product and architecture brief.
- [docs/roadmap.en.md](docs/roadmap.en.md) - current roadmap.
- [docs/development-steps.en.md](docs/development-steps.en.md) - sequential development plan.
- [docs/protocol-v1.en.md](docs/protocol-v1.en.md) - Macaroni Protocol v1 file model.
- [docs/github-provider.en.md](docs/github-provider.en.md) - first real provider adapter.
- [docs/access-token.en.md](docs/access-token.en.md) - how to get an access token.
- [docs/gitverse-token.en.md](docs/gitverse-token.en.md) - how to get a GitVerse access token.

Russian versions:

- [README.md](README.md)
- [PHILOSOPHY.md](PHILOSOPHY.md)
- [docs/product-brief.md](docs/product-brief.md)
- [docs/roadmap.md](docs/roadmap.md)
- [docs/development-steps.md](docs/development-steps.md)
- [docs/protocol-v1.md](docs/protocol-v1.md)
- [docs/github-provider.md](docs/github-provider.md)
- [docs/access-token.md](docs/access-token.md)
- [docs/gitverse-token.md](docs/gitverse-token.md)

## Main Feature

The primary distribution is a local file named `messenger.html`.

Double click.

It works.

No `localhost`.

If a browser cannot persist data for a local HTML file or the HTTPS version on GitHub Pages, that is not a Macaroni Messenger problem. That browser is unsupported.

## Philosophy

Modern messengers solve problems for billions of users.

Macaroni Messenger solves this problem:

> Text your mom: "Boil some macaroni."

That does not require Kubernetes.

That does not require a PostgreSQL cluster.

That does not require a backend.

It requires a text file and a way to deliver it.

## Main Principle

Git is the source of truth.

The local database is a cache.

If the local database breaks, it is rebuilt from git.

If the client is deleted, it is rebuilt from git.

If the device is lost, the history remains in git.

## Architecture

Frontend:

- HTML;
- CSS;
- JavaScript.

Backend:

- none.

Database:

- git.

Local storage:

- `localStorage` for token and settings;
- `IndexedDB` for index and cache.

Sync:

- `git fetch`;
- `git pull`;
- `git push`.

Search:

- local index.

Notifications:

- polling.

## Privacy

Macaroni Messenger is not a private messenger.

We do not promise privacy.

We do not market privacy.

We do not create a false sense of privacy.

If your repository is public, your messages are public.

If your repository is private, your messages are available to everyone who has access to that repository.

If you need privacy, use encryption.

## Encryption

Encryption is not part of the base protocol.

Encryption is a plugin.

You can use:

- PGP;
- age;
- custom plugins;
- custom algorithms.

The base client works with plain text.

## Registration

Macaroni Messenger has no registration.

To start using it:

1. Create an account on GitVerse, GitLab, GitHub, or any other git hosting provider.
2. Create an access token.
3. Enter the repository.
4. Start writing messages.

## User Identity

On first open, `messenger.html` creates a short instance identifier and saves it in `localStorage`.

This is not a security signature.

It is a Macaroni-style signature:

```js
localStorage["macaroni.client_id.v1"] = "SA6E";
```

Macaroni Messenger uses a distributed user identification system.

In practice:

```text
SA6E
K2XM
W8LQ
```

We do not guarantee identifier uniqueness.

We tried.

If two users get the same identifier, we recommend they meet each other.

Macaroni Messenger does not include military-grade cryptography.

Instead it uses the technology known as "four characters, seems to work".

If `localStorage` is cleared, the browser forgets the old `CLIENT_ID` and creates a new one.

## CLIENT_ID FAQ

### How unique is the identifier?

Not very.

### Can collisions happen?

Yes.

### What happens during a collision?

Nothing good.

### Why not UUID?

Because we tried to keep the HTML file small.

### Why not a cryptographic key?

Because we were lazy.

### Can this actually work?

Yes.

For a family, friends, and a small team, `32^4 = 1,048,576` possible identifiers are enough, as long as the project does not pretend to be infrastructure for billions of users.

## Installation

Choose the style you like.

### Option 1

Download `messenger.html`.

Open `messenger.html`.

Use it.

### Option 2

Save the web page with Save As.

Use it.

### Option 3

Run an Electron wrapper around the same HTML file.

Use it.

## Compatibility

On first launch, the client runs feature detection.

Required:

- `file://` or `https://` origin storage;
- `localStorage`;
- `IndexedDB`;
- `WebCrypto`.

Recommended:

- Chrome / Chromium;
- Edge.

If the browser fails the check, the client shows this screen:

> Your browser is not funny enough to run Macaroni Messenger.

We do not suggest starting a local server.

Open `messenger.html` in a normal browser.

## Scaling

If a chat becomes too large:

Create a new repository.

## Message Deletion

Messages are not deleted.

Messages are part of history.

If you need to hide a message, create a hide event.

The history remains available.

Git remembers.

## Attachments

By default, attachments are links.

Macaroni Messenger is not designed to store gigabytes of binary files inside git.

## Why HTML

Because it is funny.

Because it is convenient.

Because it works.

Because in a world where apps are hundreds of megabytes, the idea of a messenger in one HTML file sounds implausible.

But that is exactly how it works.

## Slogans

A messenger that hides nothing.

Your messages are guaranteed not to be private.

Git push your feelings.

A chat you can fork.

Real programming in HTML.

## Target Audience

- families;
- friends;
- small teams;
- developers;
- people who need a simple chat.

Macaroni Messenger is not built for billions of users.

It is built for people who think git already does more than most modern applications.

## Conclusion

If a message cannot be committed, was it worth sending?
