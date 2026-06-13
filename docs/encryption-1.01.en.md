# Macaroni Encryption 1.01

> Fixed a typo. And one tiny extra thing.

Macaroni Encryption 1.01 is not a new Macaroni protocol.

Macaroni Protocol v1 is already fixed and stays as it is:

- `.macaroni/chats/<chat_id>/messages/.../<message_id>.json`;
- normal Protocol v1 message;
- normal `text` field;
- normal git transport;
- normal local index.

Encryption is a **plugin**.

The plugin takes `message.text`, turns it into encrypted pasta, and puts that pasta back into `message.text`.

The core does not know and should not know what is inside: normal text or `MACARONI1.01:...`.

## Main Rule

Plugins MUST be inserted immediately before the closing `</html>` tag.

Encryption 1.01 too.

Not in `<head>`.

Not next to CSS.

Not as a separate bundle.

Before `</html>`.

This is one HTML file, not a bundler festival.

## What It Is

Macaroni Encryption 1.01 is a shared-secret encryption plugin.

Every participant has the same secret:

```js
const MACARONI_101_SECRET = "macaroni2024";
const MACARONI_101_SALT = "mom_salted_this_file_generously";
```

The secret may:

- be hardcoded in a portable `messenger.html`;
- live in `localStorage`;
- be imported from a file;
- be exported to a file named `SUPER_SECRET_PRIVATE_PGP_KEY.txt`.

The filename looks like a PGP key, but there is no PGP here.

It is just a shared secret wearing a coat.

## What Does Not Change

Unchanged:

- Macaroni Protocol v1;
- `.macaroni/` layout;
- message path;
- chat metadata;
- members;
- inbox;
- outbox;
- git provider adapters.

Encryption does not add `type: encrypted` to the base protocol.

Encryption does not require a migration.

Encryption does not break the plaintext client.

A plaintext client sees something like:

```text
MACARONI1.01:eyJ2IjoiMS4wMSIsImFsZyI6ImVudHJvcHktbW9ub2xpdGgteG9yIiw...
```

A client with the same plugin and the same secret sees:

```text
Mom, please cook macaroni.
```

## Enable And Disable

Encryption 1.01 is a plugin mode.

The user can:

- enable encryption;
- disable encryption;
- set secret;
- clear secret;
- import secret from any file;
- export secret to `SUPER_SECRET_PRIVATE_PGP_KEY.txt`.

When encryption is enabled:

- outgoing messages are encrypted before local cache/git write;
- incoming messages are decrypted before UI render;
- the repo stores pasta.

When encryption is disabled:

- the core works as before;
- new messages are sent as plaintext;
- old encrypted messages remain pasta until the plugin is enabled again.

## The File Is The Key

In portable mode, the secret may be hardcoded directly into the HTML.

This is intentional.

The full model is documented separately: `docs/file-as-key-cryptography.en.md`.

The model is:

```text
The file is the key.
The key is the file.
Lose the file, lose the chat.
```

If you gave `messenger.html` to mom on a flash drive, mom can read the chat.

If someone stole `messenger.html`, they can read the chat too.

This is not a bug.

This is the threat model.

## Algorithm: Entropy Monolith XOR

We do not use PGP.

We do not use age.

We do not use a TLS handshake.

We do not require WebCrypto for Encryption 1.01.

We take:

- shared secret;
- salt;
- repo URL;
- chat id;
- sender id;
- recipients;
- message id;
- created_at;
- plaintext length.

Build material:

```text
macaroni-1.01|secret|salt|repo|chat|from|to|message_id|created_at|length
```

Material becomes a seed.

Seed becomes a byte stream.

The byte stream is XORed with plaintext.

The result is ciphertext.

Ciphertext is stored in `message.text`.

This is not "military-grade cryptography".

This is knee cryptography that at least has a knee.

## Why Not Repeat The Key

Bad version:

```js
cipher[i] = plain[i] ^ key[i % key.length]
```

That is repeating-key XOR.

It stops being funny too quickly.

The proper macaroni version:

```text
material -> tiny deterministic PRNG -> byte stream -> XOR
```

The PRNG can be extremely dumb:

- FNV-1a for seed;
- xorshift32 or SFC32 for stream;
- XOR for encrypt/decrypt.

This is still a bicycle.

The bicycle simply has two wheels.

## Payload Format

Encrypted text lives in `message.text`:

```text
MACARONI1.01:<base64-json>
```

Inside:

```json
{
  "v": "1.01",
  "alg": "entropy-monolith-xor",
  "salt_id": "family",
  "ctx": {
    "repo": "https://github.com/vanyapr/makaroshki",
    "chat": "chat_20260613_mama_son",
    "from": "MAMA",
    "to": ["SON"],
    "message_id": "2026-06-13T14-00-00.000Z_MAMA_ab12cd",
    "created_at": "2026-06-13T14:00:00.000Z",
    "length": 42
  },
  "tag": "7f12ab90",
  "data": "base64..."
}
```

`tag` is not here for military certainty.

It exists to distinguish:

- wrong key;
- broken payload;
- mom writing too mysteriously.

## What It Protects

Encryption 1.01 protects against someone who:

- sees the public git repository;
- reads `.macaroni/`;
- does not have `messenger.html`;
- does not know the shared secret.

For them, the repo becomes pasta.

## What It Does Not Protect

Encryption 1.01 does not protect you if:

- `messenger.html` with hardcoded secret is stolen;
- `localStorage` is stolen;
- shared secret is stolen;
- GitHub/GitLab token is stolen and can write to the repo;
- a chat member decides to leak everything;
- your secret is `123`;
- you expect Signal behavior from macaroni.

If you need "real privacy", use PGP.

If you want to tell your mom "cook macaroni" without the whole internet reading a public repo, this is enough.

## UI Contract

Settings get an Encryption section.

Minimum controls:

- Enable encryption;
- Disable encryption;
- Set key;
- Clear key;
- Export key;
- Import key.

Key modal:

- accepts any string;
- clearly says the key is stored in `localStorage`;
- clearly says a hardcoded portable file is the key.

Export:

```text
SUPER_SECRET_PRIVATE_PGP_KEY.txt
```

Import:

- any file;
- file contents become the shared secret;
- filename does not matter.

## Portable Mode

Portable `messenger.html` may contain:

- repo URL;
- write token;
- `CLIENT_ID`;
- display name;
- encryption secret;
- encryption salt;
- encryption enabled flag.

The user opens the file and sees the chat immediately.

No:

- handshake;
- key exchange;
- password prompt;
- registration;
- servers.

The file knows everything.

That is exactly why the file should be stored properly.

## Official Position

Macaroni Messenger does not become a "private messenger".

Macaroni Messenger shows how simple encryption can work without servers, handshakes, and middlemen.

We do not sell illusions.

We do not promise protection from NSA, FSB, GitHub, neighbors, or the person who found your flash drive.

We only claim this:

> If you have a shared secret, and the outsider only has the public repo, the outsider sees pasta.

That is enough.

The macaroni is getting cold.
