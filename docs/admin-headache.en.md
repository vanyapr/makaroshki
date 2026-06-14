# Admin Headache

Macaroni Messenger sends text right now.

Right now.

That phrase matters more than it looks.

Because Macaroni Messenger does not merely prove that a chat can live in git.

That is already funny, but fine.

It shows something more annoying:

```text
if a user has a browser,
JavaScript,
localStorage,
and internet access,
then the user already has a runtime for a communication client
```

Not an app.

Not an installer.

Not Electron.

Not a "collaboration platform".

Just an HTML file.

Double click.

Hello.

This is where the security team pretends it did not blink.

## This Is Not An Escape Plan

Macaroni Messenger was not designed as a way to bypass corporate policy.

It was not designed as a backdoor.

It was not designed as a guide for moving data out and making your life worse.

That is part of the joke.

We did not bring a new scary tool.

We opened the browser and noticed that the tool was already there.

The browser can already:

- run JavaScript;
- store data;
- read files;
- send requests;
- use web APIs;
- display text, images, audio, video, and the rest of the digital soup.

Macaroni does not add new physics.

It removes the corporate sticker from old physics.

If you are an attacker, this is not a manual.

If you are an admin, this is a list of places where the usual control model starts making expensive noises.

## Where It Gets Funny

The usual corporate mental model:

```text
there are allowed apps
there are banned apps
there is an installer
there is a domain
there is a binary
there is a list of forbidden things
```

The Macaroni model:

```text
there is a browser
there is HTML
there is a git-host API
there is a user
there are files
```

The banned app did not arrive.

It did not install.

It did not ask for admin rights.

It did not appear in the application inventory.

It was a document the browser knows how to execute.

This is funny.

Not because somebody "bypassed security".

Because the security model was built around the shape of an app, not the movement of data.

## What Was Actually Proven

Macaroni Messenger does not prove that we built a dangerous new mechanism.

It proves that existing browser primitives are already enough for a client to be:

- one HTML file;
- opened through `file://`;
- hosted anywhere;
- saved through Save As;
- sent by email;
- placed in a wiki;
- attached to an issue;
- downloaded from a repository;
- launched by double click;
- carried on a flash drive;
- wrapped in a WebView, if somebody really wants the messenger to weigh 500 MB.

From the user's point of view, it is "just a page".

From the browser's point of view, it is an application.

From the security team's point of view, it is a question:

```text
how do you find an app
that does not install?
```

The unpleasant answer:

```text
you are late if you are looking for the app
```

You need to look at data, network, tokens, browser policies, and remote endpoints.

Yes, this is more boring.

Yes, this is more expensive.

Yes, this is adult work.

This is also funny, but for fewer people.

## Text Today, Bytes Tomorrow

Macaroni Messenger currently writes Protocol v1 text messages.

That is enough for a proof of concept.

More precisely, proof of pasta.

We did not prove that text can be sent.

We proved that an HTML file can be transport.

An engineer can see where this goes: once transport exists, cargo starts asking uncomfortable questions.

The browser can hold bytes in `ArrayBuffer`, build `Blob` objects, encode base64, read local files, cache data, encrypt, hash, and send HTTP(S) requests.

So conceptually, a "message" does not have to be text.

It can be:

- text;
- a link;
- a base64 payload;
- chunks;
- a git blob;
- an LFS pointer;
- encrypted pasta;
- any byte sequence a plugin can turn into a message.

This is not a promise to implement all of it tomorrow.

Not because it is hard.

Because we are lazy.

But the fact itself is annoying: the boundary is not where security policy wants to draw it.

If WhatsApp Web can be a web app with media, the browser is already capable of being a media client.

The rest is often an attempt to hide the nature of the application under a proprietary wrapper.

Same browser runtime, with a logo, an updater, and the feeling that now everything is serious.

## Encryption Adds Seasoning

Macaroni can already encrypt through a plugin.

We do not call it military-grade.

We do not say "certified, audited, sleep well".

We say the honest version:

```text
the repository contains encrypted pasta,
the key lives in HTML/localStorage,
if you have the file, you are inside,
if you do not have the file, enjoy dinner
```

This is funny.

Because for an admin, an encrypted payload inside an allowed browser flow may be worse than plaintext inside a banned app.

Plaintext is at least visible.

Encrypted pasta looks like trash, behaves like a file, and travels where normal git traffic is allowed to travel.

We do not claim it is a cryptographic bunker.

We claim it is an annoying enough cabinet that somebody should start opening it.

## You Cannot Just Block "The Messenger"

You can block "Macaroni Messenger".

That is easy.

You can even write a policy.

It will look serious.

The problem is that the shape remains:

```text
browser runtime + storage + remote file API = communication channel
```

And that shape does not need to be called Macaroni.

It can be called:

- `report.html`;
- `invoice.html`;
- `dashboard.html`;
- `new_year_card.html`;
- `final_final_really_final.html`;
- "nothing, it is just a saved page".

If control is built around the app name, it loses to a file name.

If control is built around one domain, it loses to another repository host.

If control is built around a file extension, it loses to the browser that already opens HTML for work.

Not dramatic.

Just a fact.

An unpleasant one.

## Finding The File Is Not A Plan Either

Question:

```text
how do we find messenger.html?
```

Bad question.

The file does not have to be called `messenger.html`.

It can be named `cat.jpg`, `dog.txt`, packed into a RARJPEG, or hidden in some other non-obvious wrapper.

That does not make the file magic.

It makes name-based search decorative.

The right question is different:

```text
what data can leave the managed environment,
and through which allowed channels?
```

Macaroni makes this question visibly funny.

The unpleasant part is not that the file cannot be found.

The unpleasant part is that finding the file does not answer why it was able to work.

## Plugins Make It Worse

Macaroni keeps the core small.

Complex things go into plugins.

Good for the project.

A funny slap for the threat model.

A plugin can be:

- a formatter;
- an encryptor;
- an import/export layer;
- an attachment adapter;
- a local redactor;
- a media preprocessor;
- anything that can be written in JavaScript.

The core remains one HTML file.

The plugin remains JavaScript.

The browser remains the browser.

The security team is left with the question:

```text
is this still just a page?
```

Yes.

And no.

That is funny because both answers are correct.

## This Was Already Possible

Calmly.

Macaroni did not invent data leakage.

Before Macaroni, a file could already be:

- sent by email;
- uploaded to cloud storage;
- carried out on a phone;
- copied to a flash drive;
- placed in pastebin;
- hidden in an archive;
- typed manually, if somebody was deeply bored.

Macaroni did not invent the browser.

Macaroni did not invent git.

Macaroni did not invent ways to annoy the security team.

It simply combined:

```text
HTML
Git
JSON
```

And got a communication client.

Not new physics.

Old physics without a tie.

Pandora's box was already sitting in the browser.

Macaroni opened the lid and asked:

```text
are you sure you want to build a security model
on the assumption
that an HTML file is just a document?
```

## What An Admin Should Do

Do not search specifically for Macaroni.

That is a pretty but weak strategy.

Ask boring questions instead:

- why users need access to external git hosts;
- which git hosts are actually required for work;
- which token scopes are acceptable;
- who can create personal access tokens;
- how fast tokens are revoked;
- whether managed endpoints can write to personal repositories;
- whether outbound commits are scanned for sensitive data;
- whether attachments and archives are inspected;
- whether DLP works at the content level;
- whether API writes are logged;
- who looks at abnormal volumes of small file writes;
- whether there is a policy for local HTML apps;
- what happens to browser storage when an employee leaves;
- what counts as an approved collaboration tool.

This is not romantic.

This is not a meme.

This is normal security work.

And there is a non-imaginary chance that the people responsible for this work have been simulating activity for a long time.

No screaming.

No accusations.

Just an unpleasant observation.

Macaroni does not replace that work.

Macaroni shows where it was missing.

## Conclusion

Macaroni Messenger is a security headache not because it is clever.

It is dumb.

Indecently dumb.

One HTML file.

One browser runtime.

One git repository.

That is exactly why it is unpleasant.

A complex system can be inventoried, wrapped in MDM, blocked by bundle id, and turned into a nice report.

A file is harder to respect.

It is too simple.

Macaroni shows that if a user has a browser, JavaScript, local storage, and network access, an application does not have to be an application.

It can be a file.

And the question "how do we ban the messenger?" suddenly becomes:

```text
how do we manage data at all?
```

This is funny.

Because this is no longer about Macaroni.

It is about you.
