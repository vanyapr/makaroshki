# Roadmap

This roadmap captures the current understanding of Macaroni Messenger: a small git-backed messenger whose base distribution is a single file named `messenger.html`.

## Current Understanding

Macaroni Messenger is not "a JS-first app that may have a web target".

Macaroni Messenger is a **single-file HTML messenger**.

Main product promise:

> Download or save one HTML file, open it in a browser, and get a working messenger on top of git.

Main installation flow:

> Double click the local `messenger.html`.

There is no backend.

There is no Macaroni registration.

Git is the source of truth.

The local index is a cache.

Privacy is not promised.

## Product Contract

The base client:

- is distributed as `messenger.html`;
- opens locally through `file://` or publicly through GitHub Pages `https://` in a supported browser;
- contains HTML, CSS, and JavaScript inside one file;
- does not require installing a server;
- does not require `localhost`;
- does not require a database outside browser storage;
- works with a git repository through a browser-compatible transport;
- explains that messages are not private.

Only browsers that provide normal persistent storage for a local HTML file are supported.

All other browsers are treated as unsupported. The project does not have to ship a local server just to work around browser restrictions.

Optional wrappers are allowed:

- Electron;
- Tauri/WebView;
- mobile WebView;
- local desktop wrapper.

But wrappers are not the product center. They run the same HTML client or wrap it minimally.

## We Do Not Build

- Telegram replacement.
- A custom backend.
- Custom registration.
- Realtime delivery.
- Complex cryptography in the core.
- Large binary storage in git.
- Message deletion with "gone forever" promises.
- An abstract platform before a working `messenger.html`.
- Enterprise layers for architecture cosplay.

## We Build

- One `messenger.html`.
- Double click as the main launch flow.
- Git-backed text messages.
- Local index in browser storage.
- Polling/sync through a git-compatible flow.
- Honest privacy warning.
- Feature detection on first launch.
- A clear unsupported browser screen.
- Offline outbox.
- Simple UI: chats, messages, composer, sync status.
- Detailed product brief separate from the short README.

## Fixed Decisions

- Name: **Macaroni Messenger**.
- First artifact: `messenger.html`.
- Base protocol: **Macaroni Protocol v1**.
- Source of truth: git repository.
- MVP runtime: browser.
- MVP UI: vanilla HTML/CSS/JS, or minimal build output that still becomes one HTML file.
- MVP storage: `localStorage` for `CLIENT_ID`, token/settings; `IndexedDB` for index/cache.
- MVP language: English by default, English/Russian selector in settings; UI strings live in browser-side `window.MacaroniI18n`.
- MVP compatibility: `file://` or `https://` origin storage, `localStorage`, `IndexedDB`, `WebCrypto`.
- Recommended browsers: Chrome / Chromium / Edge.
- MVP transport: browser-compatible HTTPS/API/git adapter. Direct SSH from the browser is not MVP.
- MVP client identity: four-character `CLIENT_ID` from alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`, created on first open and saved in `localStorage`.
- HTML download stamping: cancelled. The same hosted `messenger.html` must give different browsers different local IDs.
- Message: immutable JSON file.
- Message branch: `main`.
- MVP attachments: URL only, or no attachments.
- MVP edit/delete: no. Later, separate events.
- MVP encryption: no. Later, plugin layer.

## Documents

- `README.md` - main English project front page.
- `README.en.md` - English copy of the main front page.
- `README.ru.md` - preserved Russian README.
- `PHILOSOPHY.md` - project philosophy in Russian.
- `PHILOSOPHY.en.md` - project philosophy in English.
- `docs/product-brief.md` - original detailed brief in Russian.
- `docs/product-brief.en.md` - detailed brief in English.
- `docs/roadmap.md` - current implementation plan in Russian.
- `docs/roadmap.en.md` - current implementation plan in English.
- `docs/development-steps.md` - sequential development queue in Russian.
- `docs/development-steps.en.md` - sequential development queue in English.
- `docs/protocol-v1.md` - Macaroni Protocol v1 file model in Russian.
- `docs/protocol-v1.en.md` - Macaroni Protocol v1 file model in English.
- `docs/github-provider.md` - first real GitHub adapter limits and contract in Russian.
- `docs/github-provider.en.md` - GitHub adapter guide in English.
- `docs/access-token.md` - default access token guide in Russian, with GitHub first.
- `docs/access-token.en.md` - default access token guide in English.
- `docs/gitverse-token.md` - GitVerse token guide in Russian.
- `docs/gitverse-token.en.md` - GitVerse token guide in English.
- `AGENTS.md` - repository working rules.

Rule: when a product agreement changes, update docs first, then code.

## MVP 0.1: Working Messenger.html

Goal: produce one `messenger.html` file that lets two users exchange text messages through a git repository without a Macaroni backend.

Features:

- feature detection before onboarding;
- unsupported browser screen;
- first-launch privacy warning;
- short `CLIENT_ID` created on first open and saved in `localStorage`;
- local user profile;
- UI language selection: English/Russian;
- repository connection;
- settings saved in browser storage;
- repository layout initialization;
- chat creation;
- add participant by username;
- send text message;
- write message as JSON file;
- write inbox notification;
- sync with repository;
- polling/manual refresh;
- local message indexing;
- chat list;
- local new-message indicators in the chat list;
- message history;
- local search;
- outbox on network/sync error;
- restore state after browser reload/restart.

Done when:

- `messenger.html` opens by double click in a supported browser.
- MVP does not require `localhost`.
- There is no required assets folder.
- Unsupported browsers see a clear incompatibility screen.
- Two profiles in one test repository see each other's messages.
- Reindexing does not create duplicates.
- Send errors do not lose messages.
- New incoming messages in inactive chats are visible in the sidebar and clear when the chat is opened.
- Privacy warning is shown before the first message.
- UI language switches in settings, is saved in the profile, and survives reload.
- README, product brief, and roadmap match actual behavior.

## MVP 0.1 Work Plan

1. Documentation.
   - Check README, product brief, roadmap, development steps, and AGENTS.
   - Lock single-file delivery as the base contract.
   - Keep technical protocol details in docs, not the short README.

2. First HTML shell.
   - Create `messenger.html`.
   - Inline CSS.
   - Inline JS.
   - Feature detection before main UI.
   - Unsupported browser screen.
   - Layout: sidebar, messages, composer, status bar.
   - Privacy warning modal/first-run screen.

3. Protocol v1.
   - `.macaroni/protocol.json`.
   - `.macaroni/users/<user>.json`.
   - `.macaroni/chats/<chat_id>/meta.json`.
   - `.macaroni/chats/<chat_id>/members.json`.
   - `.macaroni/chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json`.
   - `.macaroni/inbox/<user>/<message_id>.json`.
   - Author field uses `CLIENT_ID` or a profile bound to `CLIENT_ID`.
   - Minimal validators without a heavy dependency.

4. Client identity.
   - On first open, `messenger.html` creates `CLIENT_ID` and saves it in `localStorage`.
   - This is a local browser-instance stamp, not a security signature.
   - Generator uses alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`.
   - Identifier length: 4 characters.
   - Space size: `32^4 = 1,048,576`.
   - Collisions are possible and not hidden.
   - Collisions are not solved with cryptography in MVP.
   - README contains the "four characters, seems to work" FAQ.

5. Browser storage.
   - Check storage availability on `file://` and `https://`.
   - `localStorage` for token and settings.
   - `IndexedDB` for message index and outbox.
   - Profile.
   - Repo config.
   - Message index.
   - Outbox.
   - First-run/privacy acceptance flag.
   - Rebuild index command.

6. Git transport.
   - Pick the simplest browser-compatible adapter.
   - Document its limits.
   - Support init/read/write/sync for MVP.
   - Do not show raw git errors to the user.

7. Send/receive loop.
   - Create message JSON.
   - Unique message id.
   - Append-only write.
   - Sync before/after send.
   - Polling/manual refresh.
   - Outbox retry.

8. Verification.
   - Local test repository.
   - Two profiles.
   - Send both ways.
   - Browser reload.
   - Offline/sync error.
   - Reindex.
   - Verify the final artifact is one HTML file.
   - Verify `CLIENT_ID` is created on first open, saved in `localStorage`, and reaches profile/messages.

## Client Identity Manifest

Every browser gets a short identifier on first open:

```js
localStorage["macaroni.client_id.v1"] = "SA6E";
```

This is local first-run identity, not a cryptographic signature.

Generation:

```js
const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
const clientId =
  alphabet[rand()] +
  alphabet[rand()] +
  alphabet[rand()] +
  alphabet[rand()];
localStorage.setItem("macaroni.client_id.v1", clientId);
```

This is not UUID.

This is not a cryptographic key.

This is not a uniqueness guarantee.

This is a distributed identity system for the "mom, dad, aunt Svetlana" scale.

FAQ:

- How unique is it? Not very.
- Can collisions happen? Yes.
- What happens during a collision? Nothing good.
- Why not UUID? To keep the HTML file small.
- Why not a cryptographic key? Because MVP is not about that.
- Why four characters? Because `32^4 = 1,048,576`, and that is enough for small groups.

If two users get the same identifier, we recommend they meet each other.

## Browser Reality Check

Limits we do not hide:

- Main launch is local `file://` or GitHub Pages `https://`, not `localhost`.
- Browsers cannot do normal SSH git without helpers.
- Git hosting APIs may have CORS/permission limits.
- Personal access tokens in the browser are sensitive, and require explicit warning.
- GitHub/GitLab/GitVerse may differ in API and auth flow.
- If a browser does not provide persistent storage on `file://` or `https://`, it is unsupported.
- A large repo will be slow to index.

A practical MVP may start with one supported git-provider adapter or a local test adapter. The main rule is not to lie that "any git" works magically from the browser.

We do not suggest "start a local server" as a compatibility fix. It kills the main joke of the project.

## Compatibility Screen

Minimal check:

```js
async function checkSupport() {
  const checks = {
    supportedOrigin: location.protocol === "file:" || location.protocol === "https:",
    localStorage: !!window.localStorage,
    indexedDB: !!window.indexedDB,
    crypto: !!window.crypto?.subtle
  };

  return Object.values(checks).every(Boolean);
}
```

Screen text:

> Your browser is not funny enough to run Macaroni Messenger.

Required:

- `file://` or `https://` origin storage;
- `localStorage`;
- `IndexedDB`;
- `WebCrypto`.

Recommended:

- Chrome / Chromium;
- Edge.

## After MVP

0.2:

- GitHub/GitLab/GitVerse provider adapters;
- verified support matrix for Chrome/Chromium/Edge;
- import existing repo;
- read-only public repo mode;
- normal onboarding;
- manual settings export/import;
- reindex/repair tools.

0.3:

- URL attachments;
- markdown rendering;
- basic notifications;
- receipts as append-only events;
- HTML export of chat history;
- Electron/WebView wrapper around the same `messenger.html`.

0.4:

- plugin boundary;
- PGP/age proof-of-concept plugin;
- bot/client runtime;
- attachment adapters for LFS/WebDAV/S3;
- protocol migration/versioning tools.

## Cutoff Rule

If a feature does not help one `messenger.html` send, receive, find, or not lose a text message in a small group, it is not in MVP.

If a feature requires a Macaroni backend, it is not in the base product.

If a feature requires `localhost`, it is suspicious and is out of the base product by default.

If a feature breaks single-file delivery, it must provide very clear value. Otherwise, skip it.
