# Admin Headache

Macaroni Messenger sends text right now.

Right now.

That phrase matters more than it looks.

Because the project is not really about "chat in git".

That part is already obvious.

It is about this:

```text
I took duct tape,
taped a browser to an open CRUD API,
added a protocol,
and got a messenger
```

That is it.

No backend.

No desktop app.

No Electron.

One HTML file, browser runtime, git-host API, and a little nerve.

This is where the security team usually starts reading more slowly.

## This Is Not An Escape Plan

Macaroni Messenger was not designed to bypass corporate policy.

It was not designed as a backdoor.

It was not designed as a guide for moving data out and ruining your life.

This is not an escape plan.

It is a mirror.

We did not bring a new scary tool.

We opened the browser and noticed that the tool was already there.

The browser can already run JavaScript, store data, read files, send requests, and use web APIs.

Macaroni just removes the corporate sticker from that reality.

If you are an attacker, this is not a manual.

If you are an admin, this is a list of uncomfortable questions that should already have been asked.

## Where It Gets Funny

The usual corporate model:

```text
ban the app
ban the installer
ban the domain
ban the binary
```

The Macaroni model:

```text
browser is open
HTML is open
git-host API is open
user writes files
```

The banned app did not arrive.

It did not install.

It did not ask for admin rights.

It was a document the browser knows how to execute.

This is funny.

Not because somebody "bypassed security".

Because security was built around the shape of an app, while the problem was data movement.

## What Was Proven

Macaroni Messenger does not prove that we built a dangerous new mechanism.

It proves that old browser primitives are enough for a client to be one HTML file: opened through `file://`, saved through Save As, sent by email, attached to an issue, carried on a flash drive, or wrapped in a WebView if somebody really wants the messenger to weigh 500 MB.

From the user's point of view, it is "just a page".

From the browser's point of view, it is an application.

From the admin's point of view, it is a question:

```text
how do you find an app
that does not install?
```

The unpleasant answer:

```text
you are late if you are looking for the app
```

Look at data, network, tokens, browser policies, and remote endpoints.

Yes, this is more boring, more expensive, and more adult.

This is also funny, but for fewer people.

## Text Today, Bytes Tomorrow

Macaroni Messenger currently writes Protocol v1 text messages.

That is enough for a proof of concept.

More precisely, proof of pasta.

We did not prove that text can be sent.

We proved that an HTML file can be transport.

An engineer can see where this goes.

Once transport exists, cargo starts asking uncomfortable questions.

A message can be text, a base64 payload, chunks, a git blob, encrypted pasta, or any byte sequence a plugin can turn into a message.

This is not a promise to implement all of it tomorrow.

Not because it is hard.

Because we are lazy.

But the boundary has already moved.

If WhatsApp Web can be a web app with media, the browser is already capable of being a media client.

The rest is often an attempt to hide the nature of the application under a proprietary wrapper.

Same browser runtime, with a logo, an updater, and the feeling that now everything is serious.

## Encryption Adds Seasoning

Macaroni can encrypt through a plugin.

We do not call it military-grade.

We do not say "certified, audited, sleep well".

We say the honest version:

```text
the repository contains encrypted pasta,
the key lives in HTML/localStorage,
if you have the file, you are inside,
if you do not have the file, enjoy dinner
```

Plaintext is at least visible.

Encrypted pasta looks like trash, behaves like a file, and travels where normal git traffic is allowed to travel.

We do not claim it is a cryptographic bunker.

We claim it is an annoying enough cabinet that somebody should start opening it.

## You Cannot Just Block "The Messenger"

You can block "Macaroni Messenger".

You can even write a policy.

It will look serious.

The problem is that the shape remains:

```text
browser runtime + storage + remote file API = communication channel
```

And that shape does not need to be called Macaroni.

It can be called `report.html`, `invoice.html`, `dashboard.html`, `final_final_really_final.html`, or "nothing, it is just a saved page".

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

## Plugins Make It Worse

Macaroni keeps the core small.

Complex things go into plugins.

Good for the project.

A funny slap for the threat model.

A plugin can be a formatter, encryptor, attachment adapter, media preprocessor, or anything else that can be written in JavaScript.

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

## What An Admin Should Do

Do not search specifically for Macaroni.

That is a pretty but weak strategy.

Ask boring questions instead:

- why users need access to external git hosts;
- which token scopes are acceptable;
- who can create personal access tokens;
- whether managed endpoints can write to personal repositories;
- whether outbound commits are scanned for sensitive data;
- whether DLP works at the content level;
- whether API writes are logged;
- whether there is a policy for local HTML apps.

This is not romantic.

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

The question "how do we ban the messenger?" suddenly becomes:

```text
how do we manage data at all?
```

This is funny.

Because this is no longer about Macaroni.

It is about you.
