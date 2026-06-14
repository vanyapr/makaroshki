# Generic Git Provider Contract

Macaroni Messenger is not supposed to be GitHub-only.

The `.macaroni/` protocol is git-host agnostic: messages are JSON files in a repository. GitHub is only the first built-in browser adapter.

Detailed comparison of GitHub, GitLab, Gitea, Forgejo, and GitVerse: `docs/git-host-api-research.en.md`.

## The Honest Browser Part

A single HTML file running in a browser cannot magically SSH into any git server.

The browser needs one of these:

- a host API, like GitHub Contents API;
- a CORS-enabled HTTPS file API over a git repository;
- a WebDAV-style endpoint backed by git commits;
- a custom adapter embedded into `messenger.html`;
- an optional Electron/WebView wrapper that provides native git operations to the same HTML UI.

This is not a philosophical limitation.

This is the browser being the browser.

The base product still remains one HTML file. A wrapper may be packaging, but it does not become the required price of generic git support.

If viewing one HTML file or a JPEG in a WebView needs a 500 MB bundle, it is no longer a client. It is an appliance with an address bar.

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

Batch commit is useful, but not mandatory. If a host can only write one file per request, Macaroni can move slower and still move.

## Built-In Adapter Status

| Provider | Read | Write | Notes |
| --- | --- | --- | --- |
| GitHub | yes | yes | Implemented through GitHub REST Contents API. |
| GitLab | yes | yes | Implemented through Repository Files/Tree API. Repo URL: `https://gitlab.com/group/project` or self-hosted GitLab. |
| GitVerse | yes | yes | Implemented through GitVerse Contents/Tree API v1. Repo URL: `https://gitverse.ru/owner/repo`. |
| Gitea | yes | yes | Implemented through Gitea Contents API. Repo URL: `https://host/owner/repo`; browser CORS depends on the installation. |
| Forgejo | yes | yes | Implemented through Forgejo Contents API. Repo URL: `https://host/owner/repo`; browser CORS depends on the installation. |
| Hardcoded demo | yes | no | Used for Hacker News/demo traffic without API rate-limit pain. |
| Local test repo | yes | yes | IndexedDB fake repo for local development. |
| Generic Git HTTP | contract only | contract only | Needs a CORS-compatible host adapter. |
| Raw SSH git | no | no | Not from a plain browser tab. Use a wrapper. |

## Implemented Isomorphic Git Shape

The built-in browser-side transport registry lives inside `messenger.html` and supports:

- `readHead`;
- `readFile`;
- `readJson`;
- `listFiles`;
- `writeFile`;
- `writeJson`.

Batch write is not implemented in runtime yet. The client writes several Protocol v1 files sequentially, as the GitHub adapter already did.

Storage branch is not implemented yet. All adapters use `profile.branch || "main"`.

Generic Git HTTP remains contract-only, because without a concrete CORS-compatible endpoint the browser has nothing to call.

If your own Linux box needs a transport the browser can reach, it is the remote operator's turn to do the splits.

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
  writeFiles(config, files, message) {},
  ensureBranch(config, branch, fromRef) {},
  head(config) {}
};
```

`writeFiles` and `ensureBranch` are optional capabilities, not requirements for every provider.

If a host cannot list directories recursively, the adapter can still be useful. Macaroni already uses a predictable `.macaroni/` layout, and sync can walk known paths.

If a host cannot write from the browser because of CORS or auth, it can still be read-only.

Read-only Macaroni is still Macaroni.

It just cannot tell mom about macaroni yet.
