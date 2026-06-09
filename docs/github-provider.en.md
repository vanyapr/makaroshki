# GitHub Provider Adapter

GitHub is the first real provider for Macaroni Messenger.

The current implementation lives in `messenger.html` as `window.MacaroniGitHub`.

## What Exists Now

- parse repo URLs like `https://github.com/owner/repo`;
- read a file through the GitHub REST Contents API;
- read a JSON file;
- list a directory;
- write a file through the Contents API;
- write a JSON file;
- refresh/reindex reads all chat meta, messages by date, and `.macaroni/inbox/<CLIENT_ID>` as a receive hint;
- before a full reindex, the client checks the latest branch commit SHA and skips the Contents API walk when the repo has not changed;
- GitHub repo without a token works in read-only mode for public repos;
- the smoke harness checks GitHub send, reindex, and read-only through a fake Contents API without a real token;
- human-readable errors for auth, permissions, rate limit, missing repo/file, and conflict.

## Required Token Permission

Use a fine-grained personal access token.

Repository access: only the message repository.

Repository permissions:

- `Contents: Read and write`.

GitHub API accepts the token through `Authorization: Bearer <token>`.

## How File Writes Work

GitHub Contents API is not raw git push.

For the Macaroni MVP, that is fine.

File write flow:

1. the client reads existing file metadata;
2. if the file already exists, it takes `sha`;
3. it sends `PUT /repos/{owner}/{repo}/contents/{path}`;
4. it sends `content` as Base64;
5. it passes `message`, `branch`, and `sha` for updates.

This is the provider API equivalent for commit/push.

If one action creates several files, the client writes them sequentially. The GitHub Contents API creates a separate commit for every `PUT`, so parallel writes to the same branch may conflict.

## Limits

- The first adapter targets small repositories.
- Directory listing through Contents API is not an infinite recursive scan.
- Larger trees later need the Git Trees API or smarter sync.
- MVP writes to branch `main`.
- Concurrent writes to the same file may return a conflict.
- Messages are written as new files, so normal message writes rarely conflict.
- The token is stored in `localStorage`, as the UI already says.

## Send/Refresh Flow

If the profile uses provider `github` and has a token, the main composer uses `window.MacaroniGitHub`.

If the token is empty, the GitHub repo works as a read-only public repo: the client can read public history, but cannot create chats or send messages.

Sending without a token keeps the draft in outbox. Retry waits for a token.

If the user adds a token in settings while outbox already has messages, the client automatically tries to send the queue after saving the profile.

On auth/network errors, the draft is saved to outbox.

The "Refresh" button also retries outbox and reindexes.

Reindex first reads the latest branch commit SHA through the GitHub API. If the SHA matches the locally saved value, the full Contents API walk is skipped and the client keeps the current IndexedDB index.

If the SHA changed or the HEAD check is unavailable, reindex reads:

1. all found chat meta;
2. chat messages by `YYYY/MM/DD`;
3. `.macaroni/inbox/<CLIENT_ID>/*.json`;
4. `message_path` from inbox notifications.

This lets the second instance see messages addressed to it through inbox notifications.

## Still Not Done

Remote flow can write through the Contents API, but sync is still simple:

- it scans chat meta;
- messages are walked by `YYYY/MM/DD`;
- inbox is used only as a list of links to message files;
- only a coarse branch HEAD check exists before a full reindex;
- no smart file-level incremental sync yet;
- no Git Trees API yet;
- no full multi-chat UI yet.

## Polling

MVP polling is intentionally dumb:

- GitHub profile with a token: sync every 30 seconds.
- GitHub read-only profile without a token: sync every 60 seconds.
- A hidden tab still schedules sync; the browser may throttle background timers.
- If sync is already running, the next polling/manual refresh does not start in parallel.

This is not real-time and not presence. This is "Mom will see the message soon enough".

GitHub rate limits remain a provider limitation. Without a token, the limit is shared by IP and can run out faster; with a token, the limit is higher, so authenticated mode is preferred for an active chat.

If GitHub returns `API rate limit exceeded`, the client shows it as a rate limit, not as a `Contents: Read and write` permission error. In that case, the user should not regenerate the token; they should wait for the limit reset or use authenticated requests.
