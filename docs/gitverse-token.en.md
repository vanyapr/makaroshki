# How To Get A GitVerse Access Token

This document explains where to click and what to do to get an access token for Macaroni Messenger using GitVerse as the example provider.

Why GitVerse?

Because in that case Sberbank becomes the operator of your personal data, and that is funny.

Official GitVerse documentation: [Tokens](https://gitverse.ru/docs/collaborative/authentification/tokens/).

## What A Token Is

An access token replaces a password when working with a git repository and API.

Macaroni Messenger uses the token to read and write message files in the selected repository.

Important:

- the token gives access to your repository;
- do not post the token in a public chat;
- do not commit the token to the repository;
- Macaroni Messenger stores the token in `localStorage`;
- `localStorage` is convenient, but it is not a bank vault.

## How To Create A Token

1. Open [GitVerse](https://gitverse.ru/).
2. Sign in.
3. Click the user icon in the top-right corner.
4. Open **Settings**.
5. Go to **Token management**.
6. Give the token a clear name, for example `macaroni-messenger`.
7. Enable the **Repositories** checkbox.
8. Click **Generate token**.
9. Copy and save the token immediately after generation.
10. Paste it into the "Access token" field in Macaroni Messenger.

Important: GitVerse shows the token only once. After the page reloads, it will not be shown again.

## Required Permissions

For MVP, use the smallest permission set that allows:

- reading repository files;
- creating or updating message files;
- pushing changes to the repository.

The official GitVerse repository-token flow says to enable the **Repositories** checkbox. Do not give the token broader access than needed for messaging through one repository.

## After Creating The Token

1. Create or choose a repository for messages.
2. Make sure your account can access the repository.
3. Copy the repository URL.
4. In Macaroni Messenger, choose provider `GitVerse`.
5. Paste the repository URL.
6. Paste the token.
7. Save settings.

## If The Token Leaks

1. Open GitVerse token settings.
2. Revoke the old token.
3. Create a new token.
4. Update the token in Macaroni Messenger.

Git remembers.

The internet remembers.

But at least a token can be revoked.
