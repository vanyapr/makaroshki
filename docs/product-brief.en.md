# Product Brief

This document preserves the original detailed product brief, data model, and architecture ideas in English.

The current implementation order and product priorities are defined by [roadmap.en.md](roadmap.en.md). If this brief is broader or older than the roadmap, the roadmap is the source of the current plan.

---

The project can be called **GitMessenger / GitGram / Macaroni Protocol**.

The essence:

**A messenger without its own backend, where transport, storage, history, and synchronization are implemented through an ordinary git repository.**

One key feature:

> The client can be deployed as a normal HTML/JS document almost anywhere: static hosting, GitHub Pages, GitLab Pages, S3, nginx, a local file, or a flash drive.

The current stricter product contract is even simpler:

> The primary distribution is a local `messenger.html` opened by double click.

Backend is still unnecessary. You need a browser, JavaScript, and access to the chosen git repository through a suitable adapter.

This is not a Telegram killer.

This is not a secure messenger.

This is not a platform for millions.

It is an honest tool:

> A messenger for small groups where all messages are files in a git repository, and the client conveniently reads, writes, indexes, and displays them.

## Main Philosophy

The project does not promise privacy.

On the contrary:

> By default, your conversation is not private.
> It is stored in a git repository.
> Whoever has access to the repository can read it.
> If the repository is public, the whole internet can read it.

This is not a bug. This is the position.

Privacy is not part of the base protocol. Privacy can be implemented on top:

- PGP;
- age;
- custom plugins;
- per-chat encryption;
- per-message encryption;
- attachment encryption.

The base system solves only one task:

> Deliver a text message from one client to another through git.

## Anti-Goal

The project is **not trying to be Telegram**.

No need for:

- realtime;
- calls;
- video;
- sticker packs;
- stories;
- million-person channels;
- moderation;
- message deletion;
- self-destructing messages;
- complex cryptography out of the box;
- perfect millisecond delivery.

It is closer to:

> ICQ/Jabber/email on top of git, with a usable interface on any platform that can run JavaScript.

## Target Audience

Not "everyone".

Instead:

- small teams;
- family;
- friends;
- developers;
- people who enjoy paranoid irony;
- people who need simple async chat;
- people who like the idea that "the backend is git".

Real use case:

> "Mom, boil some macaroni."
> The client creates a JSON file, commits it, pushes it to GitVerse.
> Mom's client fetches once per minute, sees the new file, and shows the message.

## Main Architecture

Components:

1. **Git hosting**

   - GitVerse;
   - GitLab;
   - GitHub;
   - Gitea;
   - Forgejo;
   - local bare repo over SSH.

2. **JS client**

   - single-file `messenger.html` as the primary distribution;
   - HTML/CSS/JavaScript;
   - runtime adapters only where they do not break the single-file product;
   - git transport adapter;
   - local storage/index adapter;
   - chat UI.

3. **Message repository**

   - normal git repo;
   - directory structure;
   - JSON/YAML/Markdown messages;
   - append-only history.

4. **Plugins**

   - encryption;
   - formatting;
   - attachments;
   - notifications;
   - export/import;
   - bots.

## Why Git

Git already knows how to:

- store history;
- synchronize;
- allow independent changes;
- work offline;
- pull/push;
- have users;
- have access control;
- store everything locally;
- provide auditability;
- work through existing hosting providers.

In practice, git becomes:

- database;
- transport;
- event log;
- replication system;
- backup system.

## Data Model

Repository shape:

```text
repo/
  protocol.json

  users/
    alice.json
    bob.json
    mom.json

  chats/
    chat_01HXYZ/
      meta.json
      members.json

      messages/
        2026/
          06/
            08/
              2026-06-08T12-30-01.123Z_alice_a8f1c2.json
              2026-06-08T12-31-10.812Z_mom_9b4a11.json

      receipts/
        alice.json
        bob.json
        mom.json

  inbox/
    alice/
      2026-06-08T12-31-10.812Z_mom_9b4a11.json

    mom/
      2026-06-08T12-30-01.123Z_alice_a8f1c2.json
```

## Message

```json
{
  "version": 1,
  "id": "2026-06-08T12-30-01.123Z_alice_a8f1c2",
  "chat_id": "chat_01HXYZ",
  "type": "text",
  "from": "alice",
  "to": ["mom"],
  "created_at": "2026-06-08T12:30:01.123Z",
  "text": "Mom, boil some macaroni",
  "reply_to": null,
  "attachments": [],
  "meta": {
    "client": "Macaroni Messenger JS 0.1.0"
  },
  "signature": null
}
```

## Chats

`meta.json`:

```json
{
  "id": "chat_01HXYZ",
  "title": "Family",
  "created_at": "2026-06-08T12:00:00Z",
  "created_by": "alice",
  "visibility": "repo",
  "privacy": "public_by_design"
}
```

`members.json`:

```json
{
  "members": [
    {
      "id": "alice",
      "display_name": "Alice",
      "role": "owner"
    },
    {
      "id": "mom",
      "display_name": "Mom",
      "role": "member"
    }
  ]
}
```

## Message Delivery

Sending:

1. User writes a message.
2. Client creates a JSON file.
3. Client places it into `chats/<chat_id>/messages/...`.
4. Client also places a notification into `inbox/<recipient>/...`.
5. Client commits.
6. Client pushes.

Receiving:

1. Client runs `git fetch` every N seconds/minutes.
2. Checks new commits.
3. Merges/rebases/pulls.
4. Scans new files.
5. Indexes them into local storage through a storage adapter.
6. Shows notification.

## Why `inbox`

Scanning the whole history every time is dumb.

`inbox/<user>` is a simple notification queue.

The message still lives in the chat, but inbox lets the client quickly answer:

> What is new for me personally?

For 30 people, this is more than enough.

## Conflicts

Main principle:

> Messages are never edited in place.

Every message is a new file with a unique name.

Name:

```text
<timestamp>_<author>_<random/hash>.json
```

Example:

```text
2026-06-08T12-30-01.123Z_alice_a8f1c2.json
```

Two people almost never create the same file.

Even if clocks match, there is author plus random/hash.

So classic git conflicts are rare.

## Editing Messages

Not in the base version.

Or as a new event:

```json
{
  "type": "edit",
  "target_message_id": "...",
  "new_text": "..."
}
```

The old message remains in history.

"Editing" is not file modification. It is an event on top of history.

## Deleting Messages

Not in the base version.

Philosophy:

> Git remembers.
> The internet remembers.
> We remember too.

You can create an event:

```json
{
  "type": "delete_marker",
  "target_message_id": "..."
}
```

The client may hide the message visually, but physically it remains.

That is more honest than pretending deletion in a distributed system guarantees anything.

## Search

Search is local.

During sync, the client stores messages in a local index:

```text
messages
  id
  chat_id
  from
  created_at
  text
  raw_json_path
```

Git is the source of truth.

Local index is a runtime-specific cache: SQLite, IndexedDB, OPFS, in-memory for tests, or another adapter.

If the index breaks, it is rebuilt from the repository.

## Attachments

By default, links.

```json
"attachments": [
  {
    "type": "url",
    "url": "https://example.com/file.zip",
    "title": "File"
  }
]
```

Why not store attachments in git?

Because git does not like large binary files.

Optional later:

- Git LFS;
- S3;
- WebDAV;
- Synology share;
- local file server;
- IPFS;
- plain URL.

MVP: no attachments, or links only.

## Notifications

No push server.

Just polling:

- every 60 seconds;
- or every 15 seconds in active window;
- or manual refresh.

For "Mom, boil some macaroni", this is enough.

Possible optimizations later:

- `git fetch --depth`;
- check remote HEAD only;
- use git hosting API for new commit checks;
- webhooks later.

MVP: dumb fetch or provider equivalent.

## Registration

The best part.

The user does not register in the messenger.

The user registers with git hosting.

Example:

> To use the messenger, create a GitVerse account and personal access token.

The client asks for:

- repository URL;
- login;
- token;
- username.

That is all.

The messenger does not store users on its own server because there is no server.

## Data Operator

Satirical project position:

> We are not the operator of your messages.
> We do not store your messages.
> We do not process your messages.
> We provide a client that writes files into the git repository you choose.
> Wherever you hosted the repository, ask them.

This needs careful legal wording later, but the product satire is clear.

## Security

Base model:

- messages are open;
- privacy is not promised;
- access is defined by repository settings;
- if the repository is public, everything is public;
- if private, everything is available to people with access;
- git hosting may potentially see everything.

Honest first-launch banner:

> This messenger is not private.
> Do not send secrets, passwords, intimate photos, trade secrets, or anything you do not want to see on the internet.

## Encryption As Plugin

A plugin may intercept sending.

Before:

```json
"text": "Mom, boil some macaroni"
```

After:

```json
"type": "encrypted",
"encryption": {
  "plugin": "pgp",
  "recipients": ["mom_key_id"]
},
"payload": "-----BEGIN PGP MESSAGE-----..."
```

Base client without the plugin shows:

> This is an encrypted message. Install the PGP plugin.

Encryption does not break the protocol.

## Plugins

Plugins may do:

- PGP;
- Markdown rendering;
- emoji packs;
- link preview;
- attachments;
- Telegram import;
- HTML export;
- bots;
- auto-translation;
- filters;
- local moderation;
- themes.

Main rule:

> Core is dumb. Everything complex goes to plugins.

## Bots

A bot is just a client that reads the repo and writes messages too.

Examples:

- RSS bot;
- weather bot;
- CI bot;
- reminder bot;
- bot that writes "mom, macaroni is ready".

It can run:

- on a Mac Mini;
- on a VPS;
- on GitHub Actions;
- on GitLab CI;
- anywhere.

## Read Receipts

Not required.

Possible later:

```text
chats/<chat_id>/receipts/alice.json
```

```json
{
  "last_seen_message_id": "...",
  "last_seen_at": "2026-06-08T12:40:00Z"
}
```

But one file per user can conflict.

Better append-only:

```text
receipts/alice/2026-06-08T12-40-00Z.json
```

Client takes the latest.

## Online Status

Not needed.

"Last sync" is possible, but already extra.

The project is about async messages, not online/offline presence.

## Performance

For 30 people and text messages, git is fine.

Even with:

- 30 people;
- 100 messages per day each;
- 3000 messages per day;
- 1 KB per message;

that is 3 MB of JSON per day.

About 1 GB of raw text per year, with a large safety margin.

Reality will be smaller.

Problems start when people push binaries into git.

So attachments are links.

## UX

The user should see chat, not git.

Interface:

- chat list on the left;
- messages on the right;
- input at the bottom;
- sync status;
- refresh button;
- "last fetch 42 seconds ago" indicator.

On push error:

> Message saved locally. Could not send. We will retry later.

On conflict:

> Sync is delayed. The client is trying to merge changes automatically.

No "merge conflict" words for mom.

## Local Outbox

If there is no internet:

1. Messages go to local queue.
2. UI shows "waiting to send".
3. When internet returns, client commits/pushes.

Offline works naturally.

## Commits

One commit per message is possible:

```text
message: alice -> mom: 2026-06-08T12:30:01Z
```

Batching later:

- every 10 seconds;
- or on window blur;
- or immediately for MVP simplicity.

MVP: commit per message, or provider equivalent.

Optimize later.

## Branches

Do not complicate.

One branch:

```text
main
```

Everyone writes to `main`.

Because messages are unique files, conflicts are rare.

Advanced mode later:

- branch per user;
- merge bot;
- pull requests as messages.

But that is already too much.

## Protocol Format

Need `protocol.json`:

```json
{
  "name": "Macaroni Protocol",
  "version": 1,
  "created_at": "2026-06-08T12:00:00Z",
  "message_format": "json",
  "privacy": "public_by_design",
  "features": {
    "encryption": "optional",
    "attachments": "url_only",
    "deletion": "markers_only"
  }
}
```

## Name

Options:

- **Macaroni**
- **GitGram**
- **RepoChat**
- **CommitChat**
- **PullTalk**
- **OpenMouth**
- **PublicChat**
- **NothingToHide**
- **Macaroni Messenger**

Best option:

**Macaroni Messenger**

Because the first killer use case is:

> Mom, boil some macaroni.

## Slogans

Options:

> A messenger that hides nothing.

> Your messages are guaranteed not to be private.

> Git push your feelings.

> A chat you can fork.

> If a message cannot be committed, was it worth sending?

> Backendless messenger for people with nothing to hide and everything to commit.

## MVP

First version should only:

1. Create local profile.
2. Connect git repo.
3. Create chat.
4. Add participant by username.
5. Send text message.
6. Receive text message through polling.
7. Show history.
8. Search locally.
9. Work offline.
10. Survive restart.

That is all.

No attachments, plugins, PGP, or read receipts in the first version.

## Stack

Main constraint:

> Messenger should work on any platform that can run JavaScript.

Current stricter MVP:

> One local HTML file opened through `file://` in a supported browser.

Core should not be tied to Electron, Tauri, a UI framework, or a specific database.

Base stack:

- HTML;
- CSS;
- JavaScript;
- JSON protocol validators;
- git transport adapter;
- local index storage adapter.

Possible runtime targets later:

- local `messenger.html`;
- Browser;
- Electron;
- Tauri/WebView;
- mobile WebView;
- server-side bot/client runtime.

## Risks

Main problems:

1. Git hosting may dislike frequent push/fetch.
2. User tokens must be stored carefully.
3. Mom must not see git errors.
4. Publicness must be explained loudly.
5. Repository may grow.
6. Attachments cannot be stored carelessly.
7. Client must be hard to break.

## Why This Can Work

The idea is:

- funny;
- simple;
- explainable in 30 seconds;
- good for open source;
- does not require servers;
- makes fun of modern regulation/privacy rhetoric;
- still genuinely works for small groups.

It is not a unicorn.

It is the perfect project in the category:

> "I built a messenger on top of git, and now my mom writes to me through commits."

The dangerous part is that it is actually implementable.
