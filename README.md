# Macaroni Messenger

![1000% vibecoded](https://img.shields.io/badge/1000%25-vibecoded-ff69b4?style=for-the-badge)
![One HTML File](https://img.shields.io/badge/one%20file-HTML-blue?style=for-the-badge)
![No Backend](https://img.shields.io/badge/backend-none-success?style=for-the-badge)
![Git Powered](https://img.shields.io/badge/powered%20by-git-orange?style=for-the-badge)
![Privacy](https://img.shields.io/badge/privacy-absolutely%20not-red?style=for-the-badge)

## A messenger implemented as a single HTML file

Russian version: [README.ru.md](README.ru.md).

Documents:

- [PHILOSOPHY.en.md](PHILOSOPHY.en.md) - the main project principle.
- [docs/product-brief.en.md](docs/product-brief.en.md) - detailed product and architecture brief.
- [docs/roadmap.en.md](docs/roadmap.en.md) - current implementation roadmap.
- [docs/development-steps.en.md](docs/development-steps.en.md) - sequential development plan.
- [docs/protocol-v1.en.md](docs/protocol-v1.en.md) - Macaroni Protocol v1 file model.
- [docs/github-provider.en.md](docs/github-provider.en.md) - first real provider adapter.
- [docs/plugin-boundary.en.md](docs/plugin-boundary.en.md) - browser-side plugin boundary.
- [docs/electron-wrapper.en.md](docs/electron-wrapper.en.md) - optional Electron/WebView wrapper contract.
- [docs/settings-export-import.en.md](docs/settings-export-import.en.md) - manual settings backup and restore.
- [docs/access-token.en.md](docs/access-token.en.md) - how to get an access token.
- [docs/gitverse-token.en.md](docs/gitverse-token.en.md) - how to get a GitVerse access token.

Russian documents:

- [README.ru.md](README.ru.md)
- [PHILOSOPHY.md](PHILOSOPHY.md)
- [docs/product-brief.md](docs/product-brief.md)
- [docs/roadmap.md](docs/roadmap.md)
- [docs/development-steps.md](docs/development-steps.md)
- [docs/protocol-v1.md](docs/protocol-v1.md)
- [docs/github-provider.md](docs/github-provider.md)
- [docs/plugin-boundary.md](docs/plugin-boundary.md)
- [docs/electron-wrapper.md](docs/electron-wrapper.md)
- [docs/settings-export-import.md](docs/settings-export-import.md)
- [docs/access-token.md](docs/access-token.md)
- [docs/gitverse-token.md](docs/gitverse-token.md)

---

Macaroni Messenger is a distributed messaging system implemented as a single HTML file.

Messages are stored in Git repositories.

The client is an HTML document.

The backend does not exist.

The database is Git.

The transport layer is Git.

The synchronization layer is Git.

The history storage is Git.

This sounds like a terrible idea.

Unfortunately, it works.

---

## Main Principle

Do not make things complicated when they can be funny.

This does not prevent them from being real software.

Macaroni Messenger is not a joke.

It simply refuses to introduce complexity without a reason.

---

## Why Does This Exist?

Macaroni Messenger was born from a simple observation.

Sending a message to your mother should not require infrastructure comparable to a small bank.

Modern communication systems are increasingly built around:

- registrations
- phone numbers
- centralized services
- applications
- updates
- dependencies
- regulations
- infrastructure

Macaroni Messenger starts with a different question:

What is the minimum amount of technology required to send:

> Mom, please cook macaroni.

The answer appears to be:

- HTML
- Git
- JSON

---

## Architecture

Frontend:

- HTML
- CSS
- JavaScript

Backend:

- none

Database:

- Git

Synchronization:

- git fetch
- git pull
- git push

Search:

- local index

Storage:

- local browser storage

---

## The Accidental Protocol

One side effect of Macaroni Messenger is the `.macaroni` protocol.

At first, `.macaroni` is just a boring directory inside a Git repository.

It contains:

- protocol metadata
- users
- chats
- members
- messages
- inbox hints

But this also makes it a universal agent protocol over Git.

Not in the enterprise sense.

In the practical sense:

- agents can read repository state;
- agents can append structured JSON events;
- agents can coordinate through commits;
- agents can rebuild local state from Git history;
- humans can inspect and edit everything with normal Git tools.

Macaroni Messenger is the first client.

The `.macaroni` directory is the part that accidentally looks reusable.

Unfortunately, that also works.

---

## The Entire Client Is A File

The client is:

```text
messenger.html
```

Not an installer.

Not an archive.

Not a launcher.

Not a package.

Not a platform.

A file.

Double click.

The messenger starts.

---

## Distribution

Macaroni Messenger can be distributed as:

```text
messenger.html
```

via:

- email
- USB flash drive
- Git repository
- website
- cloud storage
- random forum attachment

If a browser can open it, it works.

---

## Deployment

How do I deploy Macaroni Messenger?

Copy the file somewhere.

Deployment completed.

---

## Privacy

Macaroni Messenger does not guarantee privacy.

In fact, it explicitly guarantees the opposite.

If your repository is public:

your messages are public.

If your repository is private:

everyone with repository access can read them.

If you need privacy:

install an encryption plugin.

Good luck.

---

## Identity

Every Macaroni Messenger client receives a small identifier.

Example:

```text
SA6E
```

We do not guarantee uniqueness.

We tried.

If two users receive the same identifier:

we recommend introducing them to each other.

---

## Storage Philosophy

Git is the source of truth.

Everything else is a cache.

If local storage disappears:

rebuild it.

If the index disappears:

rebuild it.

If the browser profile disappears:

rebuild it.

Git remains.

---

## Message Format

Messages are files.

Files are messages.

A message is a JSON document.

Nothing more.

Nothing less.

---

## Scaling

How does Macaroni Messenger scale?

Poorly.

If a repository becomes too large:

create a new repository.

---

## Supported Infrastructure

Macaroni Messenger officially supports:

- GitHub
- GitLab
- GitVerse
- Forgejo
- Gitea
- a server in your basement

---

## Basement Support

Macaroni Messenger officially supports basement deployments.

If your server:

- stands on a chair
- uses an extension cord
- makes suspicious noises
- is located near jars of pickles

it is considered a supported configuration.

---

## Enterprise Edition

Enterprise Edition differs from Community Edition by having:

a second basement.

---

## Development Process

Macaroni Messenger was built overnight.

The author wrote a roadmap.

The author went to sleep.

The coding agent continued implementing the roadmap.

The author woke up.

The messenger existed.

This repository is the result of that mistake.

---

## Vibe Coding

Macaroni Messenger is proudly:

1000% vibecoded.

Not because nobody knew what they were doing.

But because modern tooling allows ideas to become software before common sense has a chance to stop them.

---

## AGENT RULES

Before implementing anything, ask:

Can this be solved with fewer files?

Can this be solved without a backend?

Can this be solved using Git?

Can this be solved using JSON?

Can this be solved using HTML?

Can this be solved in a way that is both functional and funny?

Prefer that solution.

---

## Things We Refuse To Build

- Kubernetes support
- Microservices
- Service mesh
- Message broker
- Blockchain
- Enterprise AI features
- Complexity for the sake of complexity

---

## FAQ

Is this a joke?

Partially.

Does it actually work?

Unfortunately, yes.

Why Git?

Because Git already knows how to store files.

Why HTML?

Because it is funny.

Why not Telegram?

Telegram already exists.

Why not Matrix?

We just wanted to tell our mom to cook macaroni.

Why is there more documentation than source code?

Because explaining the project is harder than implementing it.

---

## What Is Macaroni Messenger?

Macaroni Messenger is simultaneously:

- a joke
- a messenger
- a Git client
- a distributed append-only message log
- a static web application
- a peer-to-peer communication protocol

and, accidentally,

a real product.

---

## Final Statement

If a message cannot be committed,

was it worth sending?
