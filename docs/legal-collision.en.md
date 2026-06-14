# Legal Collision

Macaroni Messenger is an HTML file.

Not a server.

Not a service.

Not a messaging platform.

Not a database.

Not an infrastructure operator.

It opens in a browser and writes JSON files into a git repository.

And this is where things become legally interesting.

## Technical Fact

Macaroni Messenger messages are not physically stored inside Macaroni Messenger.

They are stored in a git repository.

And the git repository lives wherever the user placed it:

- GitVerse;
- GitLab;
- GitHub;
- Gitea;
- Forgejo;
- self-hosted GitLab;
- corporate git hosting;
- a basement server;
- any other service that once decided: "let people store code here".

Macaroni Messenger is the client in this scheme.

It does not store data.

It asks the host:

```text
give me a file
write this file
show me a list of files
```

The host responds.

Everyone is happy.

Almost.

## Where The Collision Starts

A normal messenger looks like this:

```text
messenger -> messenger server -> messenger database
```

Macaroni Messenger looks like this:

```text
messenger.html -> git host -> git repository
```

So the backend suddenly does not belong to the messenger author.

The backend belongs to whoever provides the git hosting.

And this is not a philosophical metaphor.

This is literally where the messages are stored.

## Russian Context

Russian law has regulatory regimes for:

- personal data operators;
- organizers of information dissemination on the Internet;
- services that enable exchange of electronic messages;
- infrastructure through which user data is received, transmitted, delivered, processed, or stored.

Whether a specific regime applies depends on the specific service, its functions, jurisdiction, terms of service, registries, actual data processing, and other boring things that let lawyers buy apartments.

But the technical question remains simple:

```text
where are the messages?
```

If messages live in a repository on a git host, then the git host is the infrastructure where this data is physically stored and served through an API.

Macaroni Messenger does not hide this fact.

Macaroni Messenger is proud of it.

## Git Hosting As An Accidental Messenger

Git hosting usually thinks it stores:

- source code;
- README files;
- issues;
- pull requests;
- CI configs;
- strange shell scripts;
- `final_final_really_final_v2.js`.

Macaroni Messenger politely adds:

```text
also conversations
```

Not through a separate messaging API.

Not through a chat service.

Not through WebSocket.

Just through files in a repository.

```text
.macaroni/chats/.../messages/.../*.json
```

From git's point of view, these are ordinary files.

From the user's point of view, this is a chat.

From a lawyer's point of view, a beautiful workday begins.

## Sberbank, Yandex, And Other Adults In The Room

When a large platform runs git hosting, it effectively says:

```text
bring us your repositories, we will store them
```

Macaroni Messenger replies:

```text
sure
```

And puts messages there.

This is not hacking.

This is not bypassing anything.

This is not exploiting a vulnerability.

This is normal use of git hosting:

- create a file;
- read a file;
- commit a file;
- get history.

If GitVerse, Yandex, a corporate GitLab, or any other host gives the user a repository and an API for working with files, Macaroni Messenger simply uses that mechanism literally.

Very literally.

Indecently literally.

## Two Strategic Chairs

In this model, a git host gets two chairs.

The first chair:

```text
we give users universal file storage,
change history,
API,
tokens,
public and private repositories,
and then pretend we did not know
that users can put anything there
```

This chair is comfortable until the first person puts a conversation into the repository instead of `main.go`.

And God help the platform lawyer if that conversation contains something they have to read without coffee.

Because now it is not just a file.

It is a message.

And Macaroni Messenger, strangely enough, is still a messenger.

The second chair:

```text
we close the API,
cut CORS,
break automation,
ban normal file workflows,
and explain to users
that this is for their safety
```

You can sit on that chair too.

But then it is not exactly git hosting anymore.

It is a README showcase with an anxious compliance department behind the curtain.

Macaroni Messenger does not choose the chair for the platform.

It only shows that there are suddenly two chairs.

And you thought forking GitLab was enough?

## Who Is Responsible

Macaroni Messenger cannot store messages "on its side", because it has no side.

An HTML file has no data center.

An HTML file has no rack.

An HTML file has no contract with electricians.

An HTML file has no night-shift DevOps team.

The hosting platform has all of that.

So when the question becomes storage, access, logs, tokens, accounts, API requests, and physical data placement, the conversation naturally moves to the place where all of that actually exists.

That means the platform.

Not because Macaroni Messenger wanted it that way.

Because the architecture says so.

## We Are Not Bypassing Anything

Macaroni Messenger does not prevent a host from complying with the law.

Macaroni Messenger does not encrypt the host's transport against the host's will.

Macaroni Messenger does not hide the fact that files are being written.

Macaroni Messenger does not break ACLs.

Macaroni Messenger does not pretend to be a system process.

Macaroni Messenger does not tell the user:

```text
break the law
```

It says:

```text
here is HTML
here is git
here is JSON
it works
```

And then normal adult infrastructure responsibility begins.

The same one that always begins after the words:

```text
we just built a platform
```

## Completely Explicit

Macaroni Messenger was not conceived as a tool for bypassing blocks.

Macaroni Messenger was not conceived as a way to break the law.

Macaroni Messenger was not conceived as a political manifesto.

The point is not the tool. The point is the users.

Before the Internet, exhibitionists went to parks.

That did not make parks or raincoats bad.

The author lives in Russia, votes, pays taxes, pays utility bills, and is not planning to move anywhere.

The joke is not fighting the law.

The joke is that this is a pet project made for the joke.

It just happens to have tentacles, a pitchfork, and a tail sticking out of it.

That happened.

## Why This Is Funny

Because Macaroni Messenger removed the backend.

But the backend did not disappear from the universe.

It simply ended up with whoever already hosts git.

The whole project rests on a simple idea:

```text
if git already knows how to store file history,
then chat can be stored as file history
```

The legal collision rests on the same simple idea:

```text
if chat is stored as file history,
then it is stored by whoever stores file history
```

We are not sure anyone planned this turn.

But architecture does not ask whether the legal department is ready.

## Why This Exists At All

There used to be evenings where you could sit around and scroll marketplace feeds out of boredom.

Then it turned out that to open the marketplace you need to turn the VPN off.

And to open the messenger you need to turn the VPN on.

At some point, between these two switches, the desire to sit in either one disappeared.

The freed time was used rationally.

We "wrote" this.

Now you have to think about what to do with it.

## Not Legal Advice

This document is not legal advice.

We do not claim that a specific git host automatically falls under a specific legal regime.

We do not claim that the user is relieved of their own obligations.

We do not claim that an HTML file is a magic legal shield.

We only state a technical fact:

```text
Macaroni Messenger does not store messages.
The selected git host stores messages.
```

Everything else depends on jurisdiction, service terms, actual data processing, and people in suits who can read federal laws without losing consciousness.

## Result

Macaroni Messenger does not argue with the law.

It simply shows a funny architectural hole in the usual way of thinking:

```text
a messenger can have no server,
but messages still live somewhere
```

And if they live in git, the data storage question moves to whoever provides that git.

We are not calling anyone to do anything.

We are simply looking at GitVerse, GitLab, Gitea, Forgejo, corporate git hosting, and other adult platforms.

And gently pointing at their own APIs.

You know what to do.
