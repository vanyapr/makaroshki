# Development Steps

This document turns the roadmap into a sequential development queue.

Main principle:

> Do not make things complex where they can be funny.

That does not change the fact that Macaroni Messenger must be a full application: the user should open `messenger.html`, pass compatibility checks, set up a profile, send a message, survive sync errors, and not lose data.

## Execution Rules

- Each step is developed in a separate branch.
- Each step must produce a verifiable result.
- After every step, update docs if the agreement changed.
- `messenger.html` remains the main artifact.
- `localhost` is not used as fallback.
- A new dependency is allowed only if the native/simple solution is meaningfully worse.
- If a solution can be understood in 5 minutes, it is usually the right one.

## Stage 0. Documents And Contract

Goal: remove ambiguity before code.

Steps:

1. Check `README.md`, `PHILOSOPHY.md`, `docs/product-brief.md`, and `docs/roadmap.md`.
2. Ensure the main contract is consistent everywhere: local `messenger.html`, double click, supported browser or unsupported browser screen.
3. Record that `PHILOSOPHY.md` is the product philosophy and `docs/roadmap.md` is the current implementation plan.
4. Add short links between documents if they are not connected yet.

Done when:

- documents do not contradict each other;
- roadmap remains the source of the current plan;
- there are no promises of `localhost`, backend, or privacy by default.

## Stage 1. First `messenger.html`

Goal: get a real single-file artifact.

Status: base static layout from the mockup exists in `messenger.html`. Interactivity, feature detection, and storage are not implemented yet.

Steps:

1. Create `messenger.html`.
2. Add base HTML structure.
3. Add inline CSS.
4. Add inline JS.
5. Add static layout: sidebar, messages, composer, status bar.
6. Add visual sync status placeholder.
7. Open the file by double click in a supported browser.

Done when:

- file opens through `file://`;
- there are no external CSS/JS/assets;
- UI does not break at desktop and narrow widths;
- there is no build system unless it is actually needed.

## Stage 2. Feature Detection

Goal: separate supported browsers from unsupported browsers immediately.

Status: implemented in `messenger.html`. The client checks `file://` or `https://`, `localStorage`, `IndexedDB`, and `WebCrypto`; unsupported browsers get the incompatibility screen. `http://localhost` is not a supported fallback.

Steps:

1. Implement `checkSupport()`.
2. Check `location.protocol === "file:"`.
3. Check `window.localStorage`.
4. Check `window.indexedDB`.
5. Check `window.crypto?.subtle`.
6. Add unsupported browser screen.
7. Add recommended browsers: Chrome / Chromium / Edge.
8. Do not suggest starting a local server.

Done when:

- supported browser sees the main UI;
- unsupported browser sees a clear screen;
- screen text contains: "Your browser is not funny enough to run Macaroni Messenger";
- `localhost` is not offered as a solution.

## Stage 3. `CLIENT_ID`

Goal: every `messenger.html` instance gets a short identifier.

Status: basically implemented in `messenger.html`. `CLIENT_ID` is declared as a constant, rendered in the UI, and exposed as `window.MacaroniSupport.clientId`; the four-character ID generator remains a simple function.

Steps:

1. Add `const CLIENT_ID = "SA6E";` to HTML.
2. Describe the ID generator as a simple function or build-time script, if it is actually needed.
3. Use alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`.
4. ID length: 4 characters.
5. Show `CLIENT_ID` in settings/profile.
6. Use `CLIENT_ID` as default user id.
7. Do not use UUID.
8. Do not use a cryptographic key.

Done when:

- `CLIENT_ID` is visible in `messenger.html` source;
- ID is displayed to the user;
- ID can be used as message author;
- docs honestly describe collisions.

## Stage 4. Local Profile And Settings

Goal: user can save minimal configuration.

Status: basically implemented in `messenger.html`. There is a first-run screen, privacy warning acceptance, display name, provider/repo/token in `localStorage`, settings screen, and profile reset.

Steps:

1. Add first-run screen after feature detection.
2. Save privacy warning acceptance.
3. Save display name.
4. Save git provider/repo config.
5. Save token in `localStorage` with an explicit warning.
6. Add screen/section to view and reset settings.

Done when:

- browser reload keeps the profile;
- user sees warning before saving token;
- local state can be reset without manual DevTools work.

## Stage 5. IndexedDB Storage

Goal: store message index and outbox locally.

Status: basically implemented in `messenger.html`. There is a small IndexedDB wrapper, schema version `2`, stores `messages`, `chats`, `outbox`, `meta`, `repoFiles`, and operations for messages, search, outbox, index reset, and the local test repo. Until the Send/Receive Loop, this is infrastructure, not a full user-facing send flow.

Steps:

1. Create minimal IndexedDB wrapper.
2. Stores: `messages`, `chats`, `outbox`, `meta`.
3. Add schema version.
4. Add operations `putMessage`, `listMessages`, `searchMessages`, `putOutbox`, `listOutbox`, `deleteOutbox`.
5. Add rebuild/reset index action.
6. Show understandable UI message for storage errors.

Done when:

- messages survive reload;
- outbox survives reload;
- index can be rebuilt;
- storage layer remains small and readable.

## Stage 6. Protocol V1

Goal: define message file model.

Status: basically implemented in `messenger.html` and documented in `docs/protocol-v1.en.md`. `window.MacaroniProtocol` provides helpers for `protocol.json`, user document, chat meta, members, text message, inbox notification, repo paths, `chat_id`/`message_id` generation, and minimal validation without a dependency.

Steps:

1. Describe `protocol.json`.
2. Describe `users/<client_id>.json`.
3. Describe `chats/<chat_id>/meta.json`.
4. Describe `chats/<chat_id>/members.json`.
5. Describe `chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json`.
6. Describe `inbox/<recipient>/<message_id>.json`.
7. Implement `chat_id` generation.
8. Implement `message_id` generation.
9. Implement minimal runtime validation without a heavy dependency.

Done when:

- valid chat meta can be created;
- valid text message can be created;
- message path is deterministic from `created_at`, `from`, and `message_id`;
- invalid JSON does not crash the whole app.

## Stage 7. Local Test Repo Adapter

Goal: verify protocol without a remote git provider.

Status: basically implemented in `messenger.html` as `window.MacaroniTestRepo`. The adapter stores repo files in the IndexedDB `repoFiles` store and supports `write/read/list`, layout init, chat creation, message + inbox notification writes, and reindexing from repo files.

Steps:

1. Build in-browser/local test adapter that simulates repo files in IndexedDB.
2. Support read/write/list operations for repo paths.
3. Support repo layout initialization.
4. Support creating chat/message/inbox files.
5. Support reindex from test repo.

Done when:

- chat can be created without real remote git;
- message can be sent into local test repo;
- index rebuilds from repo files;
- UI already feels like a working messenger, not a mockup.

## Stage 8. Send/Receive Loop

Goal: vertical message flow inside MVP.

Status: basically implemented for the local test repo in `messenger.html`. The composer creates a draft, writes a text message into `repoFiles`, creates an inbox notification for test recipient `K2XM`, indexes the message, renders it in the UI, survives reload through reindex, and retries outbox through the "Refresh" button. Remote provider sync is not connected yet.

Steps:

1. Composer creates message draft.
2. Message gets `CLIENT_ID` as author.
3. Message is written to repo files.
4. Inbox notification is written for recipient.
5. Message is indexed locally.
6. UI shows the new message.
7. On error, write goes to outbox.
8. Retry outbox from button and on sync.

Done when:

- message appears in history;
- reload does not lose message;
- send error does not lose draft/outbox item;
- reindex does not create duplicates.

## Stage 9. Git Provider Adapter

Goal: connect first real remote flow.

Steps:

1. Pick one provider for the first real adapter.
2. Document provider limits.
3. Implement auth/token warning.
4. Implement repo file read.
5. Implement repo file write.
6. Implement commit/push or provider API equivalent.
7. Implement pull/fetch or provider API equivalent.
8. Hide raw git/provider errors behind human messages.

Done when:

- two `messenger.html` instances work through one remote repo;
- user sees sync status;
- auth/network errors do not break local queue;
- docs honestly state which provider is supported.

## Stage 10. UI MVP

Goal: make the app usable by a small group on a regular basis.

Steps:

1. Sidebar with chat list.
2. Message list with readable grouping.
3. Composer.
4. Empty states.
5. Sync status.
6. Outbox status.
7. Settings/profile screen.
8. Reindex/reset controls.
9. Search input.
10. Mobile/narrow layout.

Current mobile UI contract: the sidebar does not stretch the chat list with empty space, chats use a compact horizontal strip, and the composer fits fully inside the viewport without sticking to the bottom edge.

Done when:

- main actions are visible without instructions;
- raw git vocabulary does not leak into user UI;
- text does not overlap controls;
- interface is dense, clean, and has no decorative noise.

## Stage 11. Search

Goal: local search over index.

Steps:

1. Index `text`, `from`, `chat_id`, `created_at`.
2. Implement simple substring search.
3. Add filter by current chat.
4. Add jump to found message.
5. Do not add a full-text engine until there is a real need.

Done when:

- search works after reload;
- search works after reindex;
- on a small repo, it is fast without a complex dependency.

## Stage 12. End-To-End MVP Check

Goal: prove this is a full application, not a funny HTML mockup.

Steps:

1. Check double click on `messenger.html`.
2. Check unsupported browser screen.
3. Check first-run privacy warning.
4. Check `CLIENT_ID`.
5. Check profile creation.
6. Check chat creation.
7. Check message send.
8. Check message receive from second profile.
9. Check outbox on error.
10. Check retry.
11. Check reload/restart.
12. Check reindex.
13. Check search.

Done when:

- two profiles exchange messages;
- no message is lost on reload;
- known limits are documented;
- final artifact remains one HTML file.

## After MVP

Only after working `messenger.html`:

1. Second git provider adapter.
2. Import existing repo.
3. Read-only public repo mode.
4. URL attachments.
5. Markdown rendering.
6. Basic notifications.
7. Receipts as append-only events.
8. HTML export of chat history.
9. Electron/WebView wrapper around the same HTML.
10. Plugin boundary.

## Not Before MVP

- UUID instead of `CLIENT_ID`.
- E2E encryption.
- PGP/age plugin.
- Attachments in git.
- Realtime.
- WebSocket.
- Macaroni backend.
- `localhost` workaround.
- Framework migration for beauty.
- Build pipeline if one HTML can be maintained without it.
