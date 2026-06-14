# Research: Git Host APIs for Git-Agnostic Macaroni

Status: research complete; minimal runtime implementation added to `messenger.html`.

Snapshot date: 2026-06-14.

Goal: determine whether Macaroni Messenger can stop being GitHub-only without breaking the current GitHub adapter and without turning one HTML file into a wrapper the size of a small refrigerator.

Short answer: yes.

But not by pretending a browser tab can SSH into any git server.

The right first step is host API adapters.

## What We Researched

Providers:

- GitHub;
- GitLab;
- Gitea;
- Forgejo;
- GitVerse.

Questions:

1. How to read a `.macaroni/...` file.
2. How to list files/directories.
3. How to write a file.
4. Whether multiple files can be written in one commit.
5. How branch selection works.
6. How auth works.
7. Where CORS, rate-limit, and permission problems will appear.

## What We Are Not Researching Here

- Raw SSH.
- A complete git client in the browser.
- Packfiles.
- Smart HTTP push.
- Electron/Tauri/native bridge.
- Storage branch implementation.
- Read-only UI polish.

Raw SSH from a plain browser tab is not the target.

If a remote operator wants "any git", they need to provide at least a browser-compatible HTTPS API. GitLab, Gitea, Forgejo, and GitVerse already prove that this is not science fiction.

## Minimal Adapter Contract

A basic adapter should support:

```js
const adapter = {
  id: "gitlab",
  label: "GitLab",

  canRead(config) {},
  canWrite(config) {},

  head(config) {},
  readFile(config, path, options) {},
  readJson(config, path, options) {},
  listFiles(config, path, options) {},

  writeFile(config, path, content, options) {},
  writeJson(config, path, value, options) {},

  writeFiles(config, files, options) {},
  ensureBranch(config, branch, fromRef) {}
};
```

`writeFiles` and `ensureBranch` are optional.

If a host cannot batch commit, Macaroni can write one file at a time.

If a host cannot create branches from the browser, the user can create the branch manually and Macaroni can use the existing branch.

If a host can only read, it is still a useful Macaroni client. In that mode the composer should eventually be hidden instead of pretending the `Send` button can defeat permissions.

## General Model

```text
Macaroni Protocol v1
  -> provider adapter
    -> host file/tree/commit API
      -> git commit
```

The `.macaroni/` protocol does not change.

Only the transport changes.

## What Isomorphic Git Means In Macaroni

In Macaroni, **Isomorphic Git** does not mean the npm package `isomorphic-git`.

We do not bundle an existing git client.

We do not add a dependency.

We do not turn `messenger.html` into somebody else's library delivery vehicle.

Our definition:

```text
Isomorphic Git = the whole minimal self-written browser-side transport layer for Macaroni,
using the remote's existing HTTPS/API transports
and going exactly as far as the browser can go by itself.
```

This is not "phase one before real git".

This is the whole Isomorphic Git scope for the base product.

Included:

- host API adapters: GitHub, GitLab, GitVerse, Gitea, Forgejo;
- file/content/tree/commit endpoints;
- auth headers;
- branch/ref handling;
- optional batch write;
- normalized errors.

Not included:

- npm package `isomorphic-git`;
- existing git client;
- required backend adapter;
- required wrapper;
- SSH from a browser tab;
- complete raw git stack for sport.

Honest boundary:

- if the remote is reachable from the browser through an HTTPS API or browser-compatible git endpoint, Macaroni writes the bicycle;
- if the remote requires SSH, local sockets, blocks CORS, or hides everything behind a backend-only flow, that is not the base product;
- in that case, use a custom host adapter, remote configuration, or optional wrapper, but not a required wrapper in the main distribution.

If your own Linux box needs a custom transport so the browser can reach it, it is your turn to do the splits.

Macaroni has already done plenty: it reached the browser boundary on square wheels.

If we ever meet a browser-compatible remote without a sane host API, we may write a tiny Smart HTTP/git object subset.

But that is not "the next required phase".

It is a separate optional experiment for roads square wheels can actually reach.

Past that line, we do not promise magic.

## Provider Comparison

| Provider | Read file | List files | Write file | Batch write | Branch support | Auth | Main risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GitHub | Contents API | Contents API / Trees API | Contents API `PUT` | via Git Database API, not Contents API | `ref`/`branch`, refs API separately | Bearer token, Contents permissions | rate limit, `sha` conflicts |
| GitLab | Repository Files API | Repository Tree API | Repository Files `POST`/`PUT` | Commits API | `branch`, `start_branch` | `PRIVATE-TOKEN` / Bearer | path encoding, instance CORS |
| Gitea | Contents API | Contents / Trees API | Contents `POST`/`PUT` | `POST /contents` multiple files | branches API | `Authorization: token ...` or Bearer | self-hosted CORS/config drift |
| Forgejo | Contents API | Contents / Trees API | Contents `POST`/`PUT` | `POST /contents` multiple files | branches API | `Authorization: token ...` or Bearer | self-hosted CORS/config drift |
| GitVerse | Contents API | Git Trees API | Contents `PUT` | Git Trees + Git Commits API | branches list, commit/tree APIs | Bearer + versioned Accept header | API version header, less tested by us |

## GitHub

The current adapter already works through the REST Contents API.

Useful properties:

- a file or directory is read via `/repos/{owner}/{repo}/contents/{path}`;
- a directory returns entries;
- a single file is written via `PUT /repos/{owner}/{repo}/contents/{path}`;
- updates require the current `sha`;
- fine-grained tokens need `Contents: read` or `Contents: write`;
- public resources can be read without a token;
- the Contents API has a 1000-file directory limit, and recursive reads need the Trees API.

Conclusion: GitHub remains the first-class adapter.

For batch write, we can later move from the Contents API to the Git Database API: create blobs/tree/commit and update the ref. This is not required for the first git-agnostic step.

## GitLab

GitLab is similar to GitHub at the abstraction level, but endpoints and parameters differ.

Useful properties:

- a file is read via `GET /projects/:id/repository/files/:file_path`;
- raw file content is available through `/raw`;
- new file write: `POST /projects/:id/repository/files/:file_path`;
- file update: `PUT /projects/:id/repository/files/:file_path`;
- multiple files in one commit use the Commits API;
- `file_path` must be URL-encoded;
- write requests accept `branch`, `commit_message`, and `content`;
- `encoding=base64` exists, but default is text;
- `last_commit_id` can be used as a conflict guard.

Conclusion: a GitLab adapter is realistic and should be next after GitHub/GitVerse research. It does not require changing Protocol v1.

## Gitea

Gitea provides an API close to GitHub Contents, with its own details.

Checked against official docs and Swagger endpoint `https://gitea.com/swagger.v1.json`.

Relevant OpenAPI paths:

- `GET /repos/{owner}/{repo}/contents/{filepath}`;
- `POST /repos/{owner}/{repo}/contents/{filepath}`;
- `PUT /repos/{owner}/{repo}/contents/{filepath}`;
- `GET /repos/{owner}/{repo}/git/trees/{sha}`;
- `GET /repos/{owner}/{repo}/branches`;
- `POST /repos/{owner}/{repo}/contents` for multiple files.

Auth:

- historical API token: `Authorization: token <token>`;
- OAuth token: `Authorization: Bearer <token>`;
- token can also be passed as a query parameter, but Macaroni should not do that: URLs love ending up in history, logs, and screenshots.

Conclusion: the Gitea adapter looks simple. The main risk is not the API itself, but each installation: CORS, reverse proxies, disabled endpoints, limits.

## Forgejo

Forgejo API is close to Gitea.

Checked against official docs and Swagger endpoint `https://try.next.forgejo.org/swagger.v1.json`.

Relevant OpenAPI paths:

- `GET /repos/{owner}/{repo}/contents/{filepath}`;
- `POST /repos/{owner}/{repo}/contents/{filepath}`;
- `PUT /repos/{owner}/{repo}/contents/{filepath}`;
- `GET /repos/{owner}/{repo}/git/trees/{sha}`;
- `GET /repos/{owner}/{repo}/branches`;
- `POST /repos/{owner}/{repo}/contents` for multiple files.

Auth:

- historical API token: `Authorization: token <token>`;
- OAuth token: `Authorization: Bearer <token>`.

Conclusion: Forgejo can be supported by almost the same adapter family as Gitea, but we should not prematurely merge them into one class. A small project cannot afford a magical "UniversalForgejoGiteaMaybe" layer that gets debugged at night from a screenshot of somebody else's VPS.

## GitVerse

GitVerse matters separately: it is not "maybe GitHub-like", it is a real versioned public API.

Checked:

- official docs require a versioned `Accept` header;
- official `gitverse/rest-api-description` repository contains OpenAPI specs;
- as of 2026-06-14, the latest reviewed file is `v1/openapi-1.7.json`;
- locally parsed OpenAPI title/version: `GitVerse Public API`, `1.7.0`;
- official repo commit used for this research: `26fde245446830e736c5516eacfaa9e4e695575f`.

Relevant OpenAPI 1.7 paths:

- `GET /repos/{owner}/{repo}/contents/{filepath}` - get file or directory contents;
- `PUT /repos/{owner}/{repo}/contents/{filepath}` - create or update file;
- `DELETE /repos/{owner}/{repo}/contents/{filepath}` - delete file;
- `GET /repos/{owner}/{repo}/git/trees/{sha}` - get repository tree by SHA, supports `recursive`;
- `POST /repos/{owner}/{repo}/git/trees` - create Git tree;
- `POST /repos/{owner}/{repo}/git/commits` - create Git commit;
- `GET /repos/{owner}/{repo}/branches` - list branches.

`CreateOrUpdateFileOptions` contains:

- `branch`;
- base64 `content`;
- `message`;
- `new_branch`;
- `sha`;
- `signoff`.

Auth:

- `Authorization: Bearer <token>`;
- `Accept: application/vnd.gitverse.object+json; version=1`.

Conclusion: a GitVerse adapter is realistic. In fact, GitVerse is closer to the shape we need than expected: it has both a content endpoint and low-level tree/commit endpoints.

## Can We Unify The Adapter?

Yes, carefully.

Separate:

1. `provider adapter` - knows endpoints, headers, path encoding, and response shape.
2. `macaroni sync logic` - knows `.macaroni/` layout, outbox, inbox, cache, receipts.

Do not build:

- enterprise provider SDK;
- abstract repository service factory;
- 500-line universal HTTP client;
- normalization of the entire GitHub/GitLab/Gitea/GitVerse API universe.

Build a tiny contract:

```text
read path
list path
write path
optional batch write
optional ensure branch
head marker
normalize error
```

That is enough.

## Real Constraints

### CORS

Official APIs can be fine, while a self-hosted Gitea/Forgejo/GitLab instance can be configured so browser `messenger.html` cannot reach it.

This is not a Protocol v1 problem.

This is a specific remote problem.

Macaroni should show an honest error: "host API is not available from the browser".

### Rate Limits

GitHub has already shown that unauthenticated public demo traffic can hit rate limits.

Adapter contract should normalize errors:

```text
rate_limited
auth_required
write_forbidden
not_found
conflict
network
unsupported
```

### Conflicts

All write adapters should treat conflicts as normal.

For Macaroni this means:

1. pull/read latest;
2. retry outbox;
3. if conflict remains, keep the message in outbox and show a human status.

Git will not run away.

### Batch Commit

Macaroni often writes more than one file:

- message;
- inbox pointer;
- receipt;
- members/meta update.

Batch write is better, but not a required blocker.

Order:

1. Start with single-file write adapter.
2. Add batch write where the host provides a sane API.
3. Add storage branch after that.

### Read-Only Mode

Read-only mode should not look like broken write mode.

Backlog:

- if token is missing or lacks write permissions, hide the composer;
- show state: "You are in read-only mode. This token can read, but cannot write.";
- keep refresh/import/search/chat info.

This is not a blocker for git-agnostic adapter research, but it should happen before broad public repo support.

### Storage Branch

Storage branch is a separate backlog item.

Git-agnostic adapters should accept `branch` from day one, but storage branch implementation should not be bundled with non-GitHub providers.

Adapters first.

Branch hygiene later.

Otherwise we do not get a messenger. We get pasta with migrations.

## Wrapper Stance

The base product remains one HTML file.

We do not ship Electron/Tauri/native bridge as a required part of git-agnostic support.

If viewing one HTML file or a JPEG in a WebView needs a 500 MB bundle, it is no longer a client. It is an appliance with an address bar.

Wrappers may exist as an optional packaging layer.

The transport contract must not depend on them.

## Proposed Plan

1. Keep the current GitHub adapter as the reference implementation.
2. Extract a minimal `provider adapter` interface inside `messenger.html`, without adding a separate build system.
3. Implement GitVerse adapter or GitLab adapter as the first non-GitHub provider.
4. Then implement the Gitea/Forgejo family adapter.
5. Add read-only composer guard.
6. Implement storage branch separately.
7. Keep Smart HTTP/git object subset as an optional experiment only for browser-compatible remotes without a sane host API.

## Decision For Now

Git-agnostic Macaroni should not pull `isomorphic-git` from npm and does not have to write a complete git implementation.

Browser-compatible host API adapters are the whole practical Isomorphic Git scope for the base product.

## Runtime Implementation

`messenger.html` now contains browser-side registry `window.MacaroniRemoteAdapters`.

Built-in adapters:

- `github` - GitHub REST Contents API;
- `gitlab` - GitLab Repository Files/Tree API;
- `gitverse` - GitVerse Contents/Tree API v1;
- `gitea` - Gitea Contents API;
- `forgejo` - Forgejo Contents API.

Supported runtime subset:

- read branch/head marker;
- read file/json;
- list directory;
- write file/json;
- initialize Protocol v1 layout;
- create chat;
- join chat;
- send message through outbox retry;
- read receipts;
- reindex/polling.

Not implemented in this step:

- batch commit;
- storage branch;
- raw SSH;
- generic `git-http` without a concrete host API;
- complete Smart HTTP/git object transport.

Provider-specific URL assumptions:

- GitHub: `https://github.com/owner/repo`;
- GitLab: `https://gitlab.com/group/project` or self-hosted GitLab URL;
- GitVerse: `https://gitverse.ru/owner/repo`;
- Gitea: `https://host/owner/repo`;
- Forgejo: `https://host/owner/repo`.

For self-hosted Gitea/Forgejo/GitLab, CORS remains the remote operator's responsibility. If the browser cannot reach the API, Macaroni shows an honest network/provider error.

This preserves:

- one HTML file;
- current Protocol v1;
- working GitHub adapter;
- a clear path to GitLab/Gitea/Forgejo/GitVerse;
- minimal operational complexity.

Full "we wrote git in HTML" is not required to prove the point. If we ever need to go further, that is a separate bicycle, not a debt of the current release.

## Sources

- GitHub REST Contents API: https://docs.github.com/en/rest/repos/contents
- GitLab Repository Files API: https://docs.gitlab.com/api/repository_files/
- GitLab Repositories API: https://docs.gitlab.com/api/repositories/
- Gitea API Usage: https://docs.gitea.com/development/api-usage
- Gitea OpenAPI: https://gitea.com/swagger.v1.json
- Forgejo API Usage: https://forgejo.org/docs/latest/user/api-usage/
- Forgejo OpenAPI: https://try.next.forgejo.org/swagger.v1.json
- GitVerse API versioning: https://gitverse.ru/docs/public-api/using-public-api/api-versioning/
- GitVerse OpenAPI repo: https://gitverse.ru/gitverse/rest-api-description
