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
- GitHub repo without a token works in read-only mode for public repos;
- the smoke harness checks GitHub send, reindex, and read-only through a fake Contents API without a real token;
- human-readable errors for auth, permissions, missing repo/file, and conflict.

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

On auth/network errors, the draft is saved to outbox.

The "Refresh" button retries outbox and reindexes.

Reindex reads:

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
- no smart incremental sync yet;
- no Git Trees API yet;
- no full multi-chat UI yet.
