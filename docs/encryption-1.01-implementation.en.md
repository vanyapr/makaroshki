# Macaroni Encryption 1.01 Implementation Contract

This document bridges the Encryption 1.01 manifesto and code.

Status: implemented in `messenger.html` as built-in plugin `macaroni-encryption-1.01`.

Goal: build the dumbest thing that works, while still having logic and common sense.

We do not create a new Macaroni Protocol.

We do not change `.macaroni/`.

We do not add a dependency.

We do not import somebody else's crypto protocol.

We write a bicycle.

If a bicycle can be invented, we invent it.

Square wheels are a feature as long as they move.

## Scope

Encryption 1.01 is implemented as a plugin.

The plugin is inserted immediately before the closing `</html>` tag.

The plugin uses:

- `window.MacaroniPlugins.register(...)`;
- `transformOutgoingMessage(message, context)`;
- `transformIncomingMessage(message, context)`;
- `mountSettings(container, context)` or an equally primitive hook for plugin-specific controls;
- `localStorage`;
- `TextEncoder`;
- `TextDecoder`;
- `btoa`;
- `atob`.

The plugin does not use:

- WebCrypto as a required dependency;
- PGP;
- age;
- OpenSSL;
- external bundle;
- package manager;
- handshake;
- key server.

## Core Settings Contract

If the file contains plugins, the core shows a Settings section:

```text
Plugins
```

For every registered plugin, the core shows a checkbox with the plugin name.

Minimal model:

```text
[x] Macaroni Encryption 1.01
```

The core does not render plugin-specific forms.

The core does not understand plugin-specific settings.

The core only:

1. shows the plugin checkbox;
2. reads enabled state from `localStorage`;
3. writes enabled state to `localStorage`;
4. passes plugin context during transforms.

Plugin-specific UI is mounted by the plugin through `mountSettings(container, context)` or an equivalent hook.

For 1.01, a core checkbox plus separate import/export/secret controls mounted by the plugin is enough.

## Plugin Settings Storage

Plugin settings are not stored in the core profile.

That means:

- core profile remains core profile;
- plugin settings live separately;
- plugin reads and writes its own namespace;
- plugin settings are not written to git;
- plugin settings are not exported with the core profile until a separate feature does that.

Recommended key:

```text
macaroni.plugin.<plugin_id>.settings.v1
```

Encryption 1.01 key:

```text
macaroni.plugin.macaroni-encryption-1.01.settings.v1
```

Read:

```js
JSON.parse(localStorage.getItem(key) || "{}")
```

Write:

```js
localStorage.setItem(key, JSON.stringify(settings))
```

No magic.

## LocalStorage Race Conditions

Inside one browser tab, `localStorage.getItem` and `localStorage.setItem` are synchronous.

So inside one submit/send flow, a race condition is not expected.

Between multiple tabs:

- `localStorage` is not a distributed database;
- last write wins;
- the `storage` event may help later, but is not part of 1.01;
- if two windows edit plugin settings at the same time, they have built themselves a small GitHub without Git.

For Encryption 1.01, this is fine.

Settings change rarely.

Messages go through git/outbox.

Macaroni is not a trading terminal.

## Encryption Settings Schema

Value of `macaroni.plugin.macaroni-encryption-1.01.settings.v1`:

```json
{
  "enabled": true,
  "secret": "12345",
  "salt": "macaroni",
  "salt_id": "family",
  "confetti_counter": 42,
  "debug": false,
  "updated_at": "2026-06-13T12:00:00.000Z"
}
```

Fields:

- `enabled` - enables outgoing encryption and incoming decrypt attempt.
- `secret` - shared secret. Any string.
- `salt` - shared salt. Any string.
- `salt_id` - public salt/profile name for UI/debug, not secret.
- `confetti_counter` - local Token Confetti counter.
- `debug` - development-only console logs.
- `updated_at` - timestamp of last settings update.

Default:

```json
{
  "enabled": false,
  "secret": "12345",
  "salt": "macaroni",
  "salt_id": "default",
  "confetti_counter": 0,
  "debug": false
}
```

Default secret/salt intentionally look like a countryside router password.

If `enabled === true`, but `secret` or `salt` is empty, the plugin does not encrypt or decrypt.

It returns the message unchanged.

## Payload Format

Core Protocol v1 message remains normal:

```json
{
  "type": "text",
  "text": "MACARONI1.01:<base64-json>"
}
```

Encrypted payload marker:

```text
MACARONI1.01:
```

Outer encrypted payload:

```json
{
  "v": "1.01",
  "alg": "entropy-monolith-xor-tiny-prng",
  "ctx": {
    "repo": "https://github.com/vanyapr/makaroshki",
    "chat": "chat_20260613_mama_son",
    "from": "MAMA",
    "to": ["SON"],
    "message_id": "2026-06-13T14-00-00.000Z_MAMA_ab12cd",
    "created_at": "2026-06-13T14:00:00.000Z",
    "length": 42
  },
  "data": "base64..."
}
```

`data` contains the encrypted clear envelope.

Clear envelope before encryption:

```json
[
  "1.01",
  "base64-token-confetti",
  "Mom, please cook macaroni"
]
```

Why an array?

Because it is shorter, dumber, and does not pretend we are designing a banking JSON API.

Fields:

1. version marker;
2. Token Confetti;
3. plaintext.

Token Confetti may be an empty string.

## Context Binding

The plugin does not change Macaroni Protocol, so the protocol itself does not prevent someone from moving a file to another chat path.

The plugin should be more boring and more suspicious.

During decrypt, the plugin compares outer Protocol v1 message with payload `ctx`:

- `message.chat_id === ctx.chat`;
- `message.from === ctx.from`;
- `message.id === ctx.message_id`;
- `message.created_at === ctx.created_at`;
- sorted `message.to` equals sorted `ctx.to`.

If context does not match:

- plugin does not decrypt;
- plugin returns original message;
- UI renders `MACARONI1.01:...` as normal plaintext;
- development mode may write `console.debug`.

We do not explain to the user that "the protocol does not work".

The protocol works.

Someone just brought pasta to the wrong chat.

## Tiny PRNG

The algorithm is called Tiny PRNG.

This is our bicycle.

It turns shared secret, salt, and message context into a byte stream for XOR.

Idea:

```text
material -> FNV-1a -> xorshift32 -> byte stream -> XOR
```

Pseudocode:

```js
function fnv1a(str, seed) {
  var h = seed >>> 0;

  for (var i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }

  return h >>> 0;
}

function xorshift32(seed) {
  var x = seed >>> 0 || 0x6d2b79f5;

  return function () {
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    return x >>> 0;
  };
}

function xorTinyPrng(bytes, material) {
  var out = new Uint8Array(bytes.length);
  var random = xorshift32(fnv1a(material, 0x811c9dc5));
  var word = 0;
  var used = 4;

  for (var i = 0; i < bytes.length; i++) {
    if (used >= 4) {
      word = random();
      used = 0;
    }

    out[i] = bytes[i] ^ ((word >>> (used * 8)) & 255);
    used++;
  }

  return out;
}
```

Encrypt and decrypt are the same function.

Because XOR.

Square wheels, but moving.

## Encryption Material

Material:

```text
macaroni-1.01
secret
salt
repo
chat
from
to_sorted
message_id
created_at
plaintext_length
```

Joined with `|`.

Plaintext itself is not part of material.

The receiver does not know plaintext before decrypt.

We do not make mom solve recursion.

## Token Confetti

In a write-enabled profile, token is normally present.

Token Confetti uses the token locally only.

Token:

- is not serialized;
- is not written to git;
- is not hashed into public metadata;
- is not required for decrypt.

Token Confetti lives inside the clear envelope.

After decrypt, the receiver simply throws it away.

Implementation detail intentionally stays boring in docs:

```text
token + message context + local counter -> bytes
```

Code may be funnier than documentation.

If someone reads implementation and drops coffee on the keyboard, that is not a bug report.

## Incoming Behavior

If incoming `message.text` does not start with `MACARONI1.01:`, plugin returns the message unchanged.

The core stores incoming messages in IndexedDB as raw Protocol v1 documents.

Plugin decrypt does not write plaintext back into cache.

Decrypt runs as a view transform before UI/search/export.

The plugin checkbox changes rendering, not history. Git remembers pasta, IndexedDB caches pasta, and the user sees macaroni only after enabling the fork.

If it starts with `MACARONI1.01:`, but:

- plugin is disabled;
- secret/salt is missing;
- payload is malformed;
- decrypt failed;
- clear envelope is malformed;
- context mismatches;
- version is unsupported;

plugin returns original message.

UI shows what arrived.

No red screens.

No "your cryptography broke".

Macaroni is not a therapist.

In development mode plugin may write:

```js
console.debug("[macaroni-encryption-1.01]", reason)
```

In release, these logs are off by default.

## Outgoing Behavior

If plugin is disabled or secret/salt is missing:

- outgoing message is unchanged.

If plugin is enabled:

1. plugin takes plaintext from `message.text`;
2. builds ctx from Protocol v1 message and profile/repo context;
3. creates Token Confetti, if token exists;
4. builds clear envelope;
5. UTF-8 encodes clear envelope;
6. XORs through Tiny PRNG stream;
7. base64 encodes result;
8. replaces `message.text` with `MACARONI1.01:<base64-json>`;
9. returns a valid Protocol v1 message.

## Temporary Verification

Permanent tests are not added to the repo yet.

If checks are needed during development:

- write a scratch script in `/tmp` or `/private/tmp`;
- check roundtrip;
- check Cyrillic/emoji;
- check that the same `"1"` twice gives different payload with confetti;
- check that different sender tokens do not break decrypt;
- check that no-token read-only decrypt works;
- check that wrong secret returns original message;
- delete the scratch script after checking.

We do not leave a test tarp in the repo for a feature that is not written yet.

When the feature becomes real code, smoke harness can be extended as a separate decision.

## Portable Docs

`docs/portable-mom.md` and `docs/portable-mom.en.md` are updated after the feature is implemented.

They will need to describe:

- hardcoded encryption settings;
- full file vs read-only file;
- secret/salt placement;
- token placement;
- file-as-key warning;
- rotation after compromise.

Before implementation, we do not lie that portable crypto already exists.
