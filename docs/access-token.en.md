# How To Get An Access Token

Macaroni Messenger works with a git repository through an access token.

The token lets the client read and write message files in the selected repository.

If the repository is public, the GitHub adapter can read it without a token in read-only mode. This is enough to view a public Macaroni repository, but not enough to send messages.

To write messages, create chats, and update `.macaroni/users/<client_id>.json`, the client needs a token with write permissions.

The token does not create the user. In Macaroni, the user is the local `CLIENT_ID` plus `.macaroni/users/<client_id>.json`; the token only grants repository access. One shared token for a small trusted group is technically possible, but anyone with that token can change repository files.

Important:

- the token gives access to the repository;
- do not post the token in chat;
- do not commit the token to git;
- Macaroni Messenger stores the token in `localStorage`;
- `localStorage` is convenient, but it is not a bank vault.

## GitHub

This is the default example.

Official GitHub documentation: [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

### Fine-grained personal access token

1. Open GitHub.
2. Click your avatar in the top-right corner.
3. Open **Settings**.
4. In the left menu, open **Developer settings**.
5. Open **Personal access tokens**.
6. Choose **Fine-grained tokens**.
7. Click **Generate new token**.
8. Give it a name, for example `macaroni-messenger`.
9. In **Repository access**, select only the repository that stores messages.
10. In **Repository permissions**, find **Contents** and choose **Read and write**.
11. Click **Generate token**.
12. Copy the token immediately after creation.
13. Paste it into the "Access token" field in Macaroni Messenger.

GitHub shows the token only once. If you close the page without saving it, create a new one.

### Required permissions

For MVP, the token needs permissions that allow:

- reading repository files through **Contents: Read and write** permission;
- creating message files through **Contents: Read and write** permission;
- updating files if the provider API requires update flow;
- pushing changes to the repository.

Do not give the token access to all repositories if you can select one specific repository. Fine-grained tokens are useful exactly because they can be restricted to one repository and specific permissions.

## GitVerse

GitVerse works as git hosting too, but the Macaroni browser adapter for GitVerse is not implemented yet. If you choose `GitVerse` in the client today, the app shows an honest error instead of silently falling back to the local test repo.

The bonus is that Sberbank becomes the operator of your personal data, and that is funny.

Detailed guide: [gitverse-token.en.md](gitverse-token.en.md).

Short version:

1. Open [GitVerse](https://gitverse.ru/).
2. Sign in.
3. Click the user icon in the top-right corner.
4. Open **Settings**.
5. Go to **Token management**.
6. Give the token a name, for example `macaroni-messenger`.
7. Enable the **Repositories** checkbox.
8. Click **Generate token**.
9. Copy the token immediately after generation.

Official GitVerse documentation: [Tokens](https://gitverse.ru/docs/collaborative/authentification/tokens/).

## GitLab And Others

The token flow is similar, but each provider adapter must be implemented separately:

1. Open account settings.
2. Find access tokens / personal access tokens.
3. Create a token for one repository or project.
4. Grant minimal repository read/write permissions.
5. Copy the token immediately after creation.
6. Paste it into Macaroni Messenger.

If the provider asks for scopes, choose minimal repository read/write permissions.

## If The Token Leaks

1. Open token settings at the provider.
2. Revoke the old token.
3. Create a new one.
4. Update the token in Macaroni Messenger.

Git remembers.

The internet remembers.

But at least a token can be revoked.
