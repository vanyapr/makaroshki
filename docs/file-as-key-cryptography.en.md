# File As Key

> Normal software stores a key.
>
> Macaroni is the key.

In normal software, a hardcoded client secret is a disaster.

In Macaroni Messenger portable mode, it becomes an access model.

Because `messenger.html` is not just an app.

It is a capability-bearing artifact:

```text
messenger.html =
  UI
  + repo URL
  + optional write token
  + CLIENT_ID
  + encryption plugin
  + shared secret
  + salt
  + settings
```

In ordinary SaaS, this is idiotic.

In a messenger made of one HTML file, it starts working.

## The Inversion

Normal messenger:

```text
app is public
keys are private
handshake is complex
```

Macaroni portable messenger:

```text
app is private
key is inside the app
handshake does not exist
```

We do not install an app and then receive a key.

We receive a file that already is the key.

## Key Exchange Without Key Exchange

Macaroni does not solve key exchange.

Macaroni moves key exchange out of the network.

Key exchange is the act of handing over the HTML file.

```text
son writes messenger.html to a flash drive
son gives the flash drive to mom
mom opens messenger.html
handshake completed
```

No:

- Diffie-Hellman;
- QR pairing;
- certificate pinning;
- key server;
- "enter the code from your other device".

Physical file transfer is key exchange.

This is dumb.

That is why it is understandable.

## Capability Model

Different HTML files can have different rights:

```text
messenger_full.html
  repo URL
  write token
  shared secret
  read/write UI

messenger_readonly.html
  repo URL
  shared secret
  no write token
  read-only UI

messenger_public_demo.html
  repo URL
  no token
  no secret
  demo/read-only UI
```

Rights are not granted to an account.

Rights are granted to a file.

```text
whoever has the file has the capability
```

This is not RBAC.

This is a flash drive.

## Why Public Repo Stops Being Scary

If the shared secret is not stored in the git repository, the public repo only sees encrypted payload:

```text
MACARONI1.01:...
MACARONI1.01:...
MACARONI1.01:...
```

Git remains the source of truth.

But Git is no longer readable truth for outsiders.

Repository publicity becomes a transport feature, not a privacy disaster.

From outside:

```text
Here is a public repository.
It contains pasta.
Enjoy the analysis.
```

From inside:

```text
Mom, please cook macaroni.
```

## Plugin And File Identity

The encryption plugin travels inside the same HTML file.

Plugins MUST be inserted immediately before the closing `</html>` tag.

That means crypto code, key material, and UI compatibility are distributed as one artifact.

```text
got the file = got the plugin
got the plugin = got the crypto behavior
got the secret = got the chat
```

A file id can also be calculated:

```text
FILE_ID = hash or fnv of the stable part of messenger.html
```

And shown in the UI:

```text
File ID: 7A3F
Crypto Profile: family-2026-06
```

Mom says on the phone:

> My File ID is 7A3F.

Son answers:

> Good. That is our file.

This is not PKI.

This is a village fingerprint.

For Macaroni, that is enough.

## Binding Crypto To File

Encryption material can include file identity:

```text
secret
salt
file_id
repo_url
chat_id
message_id
created_at
length
```

Then the same secret accidentally copied into another portable build does not necessarily produce the same byte stream.

This does not make the system "enterprise secure".

It makes the system slightly less dumb without making it stop being dumb.

## Revocation

If the file is stolen, the capability is stolen.

Do this:

1. Revoke the provider write token.
2. Generate a new shared secret/salt.
3. Build a new `messenger.html`.
4. Give the new file to normal people.
5. Treat the old file as dead.

No account recovery.

No admin panel.

No "we sent you a confirmation code".

Old file dead.

New file alive.

## If The Chat Is Compromised

Git remembers.

Usually, that is a feature.

If encrypted or plaintext history is compromised and you want to remove it from the remote branch, Macaroni recovery can be:

```text
1. Build a new messenger.html with a new secret/token.
2. Create a new clean history commit or squash old history.
3. Rewrite the branch.
4. Push with --force.
```

For example:

```sh
git reset --soft <clean-start>
git commit -m "Macaroni: restart chat"
git push --force
```

Or any other squash/history-rewrite flow.

This is not magic deletion.

If someone already cloned/fetched, old objects may remain there.

If GitHub/GitLab cached the data, it may live somewhere else.

If the secret has leaked, old encrypted messages must be treated as read.

But for a small family repo, this is a reasonable emergency handle:

```text
burned the old file
burned the old branch history
started a new chat
```

Macaroni does not promise the right to be forgotten.

Macaroni gives you a button labeled "demolish the shed and build another one".

## What This Gives Crypto

Single-file architecture gives strange advantages:

- key exchange happens off-network;
- app, plugin, and key version are distributed together;
- the file becomes a physical capability;
- per-chat HTML forks are possible;
- public repo can act as encrypted transport;
- revocation is understandable: "stop using the old file";
- read-only/full-access modes can be different files;
- crypto-version compatibility is solved by distributing one artifact.

This is not a universal model.

This is a model for small groups.

Family.

Friends.

Basement.

A team that understands what it is doing.

## Old Hacker Movie Attacks

Macaroni does not protect you from attacks where the attacker:

- steals your `messenger.html`;
- replaces your hosted `messenger.html`;
- gets access to your computer;
- obtains an old portable bundle;
- guesses your shared secret because you named it `123`.

At that point this is no longer cryptography.

This is cinema.

If a tactical team rappelled from a helicopter, rolled through the window, a hacker backflipped through the laser room, pulled a flash drive from behind the cactus, and walked away with your `messenger.html`, they did not "bypass Macaroni Encryption".

They achieved the objective.

If the sacred file is stolen, the chat is stolen.

If the sacred file is replaced, the messenger is replaced.

If the attacker is at your keyboard, boil water and rotate the file.

In boring security words, this is called endpoint compromise.

In Macaroni words, this is called "they got to the flash drive".

## What This Does Not Give

It does not protect you if:

- the file is stolen;
- localStorage is stolen;
- shared secret is stolen;
- write token is stolen;
- a participant forwards the file;
- the provider keeps old history;
- someone cloned/fetched before force push;
- you think an HTML file replaced common sense.

The file must be stored like a key.

Because it is the key.

## Motto

```text
The file is the key.
The key is the file.
Hand over the file, add a participant.
Lose the file, lose the chat.
```

Macaroni does not make "real privacy".

Macaroni makes honest privacy for people who know where the file is.
