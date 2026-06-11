# Generic Git Provider Contract

Macaroni Messenger is not supposed to be GitHub-only.

The `.macaroni/` protocol is git-host agnostic: messages are JSON files in a repository. GitHub is only the first built-in browser adapter.

## The Honest Browser Part

A single HTML file running in a browser cannot magically SSH into any git server.

The browser needs one of these:

- a host API, like GitHub Contents API;
- a CORS-enabled HTTPS file API over a git repository;
- a WebDAV-style endpoint backed by git commits;
- a custom adapter embedded into `messenger.html`;
- an Electron/WebView wrapper that provides native git operations to the same HTML UI.

This is not a philosophical limitation.

This is the browser being the browser.

## What "Any Git" Means

Any git repository can store Macaroni data if it can contain:

```text
.macaroni/
  protocol.json
  users/<client_id>.json
  chats/<chat_id>/meta.json
  chats/<chat_id>/members.json
  chats/<chat_id>/messages/YYYY/MM/DD/<message_id>.json
  inbox/<client_id>/<message_id>.json
```

Any git host can be supported by Macaroni if a browser-compatible adapter can:

1. Read a file by path.
2. Read a JSON file by path.
3. List files under a directory.
4. Write a file by path.
5. Write a JSON file by path.
6. Report a cheap repository version marker, such as branch HEAD SHA, if available.
7. Surface auth, permission, conflict, missing file, network, and rate-limit errors as normal JavaScript errors.

That is the whole transport contract.

No message broker.

No Macaroni backend.

No enterprise adapter factory.

Just file operations that eventually become git commits.

## Built-In Adapter Status

| Provider | Read | Write | Notes |
| --- | --- | --- | --- |
| GitHub | yes | yes | Implemented through GitHub REST Contents API. |
| Hardcoded demo | yes | no | Used for Hacker News/demo traffic without API rate-limit pain. |
| Local test repo | yes | yes | IndexedDB fake repo for local development. |
| Generic Git HTTP | contract only | contract only | Needs a CORS-compatible host adapter. |
| GitLab | planned | planned | Same protocol, different host API. |
| GitVerse | planned | planned | Same protocol, different host API. |
| Gitea/Forgejo | planned | planned | Likely file/content API adapter. |
| Raw SSH git | no | no | Not from a plain browser tab. Use a wrapper. |

## Why Not Bundle A Full Git Client?

Because the project is a single HTML file.

A browser git implementation with packfile support, credentials, filesystem emulation, and host-specific CORS handling is possible, but it is not the right first move.

Macaroni's practical model is:

```text
Macaroni Protocol
  -> provider adapter
    -> host API or wrapper git operation
      -> git commit
```

GitHub is one adapter, not the product boundary.

## Minimal Adapter Shape

An adapter should behave like this:

```js
const adapter = {
  readFile(config, path) {},
  readJson(config, path) {},
  listFiles(config, path) {},
  writeFile(config, path, content, message) {},
  writeJson(config, path, value, message) {},
  head(config) {}
};
```

If a host cannot list directories recursively, the adapter can still be useful. Macaroni already uses a predictable `.macaroni/` layout, and sync can walk known paths.

If a host cannot write from the browser because of CORS or auth, it can still be read-only.

Read-only Macaroni is still Macaroni.

It just cannot tell mom about macaroni yet.
