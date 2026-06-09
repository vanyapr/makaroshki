# Settings Export/Import

Macaroni Messenger can export the local profile into a JSON file and import it back.

This is useful for moving settings between browsers or for manual backup.

## What Export Includes

The file contains:

- `CLIENT_ID`;
- display name;
- UI language;
- provider;
- repo URL;
- access token;
- privacy warning acceptance.

The file does not contain:

- messages;
- IndexedDB index;
- local test repo cache;
- outbox;
- read markers.

Messages should live in git. IndexedDB remains a cache.

## Important Warning

Settings export includes the access token.

This is convenient.

This is not safe.

Store the file the same way you store the token.

## CLIENT_ID

If the imported file contains a different `CLIENT_ID`, the client saves it to `localStorage` and reloads the page.

That is required because `CLIENT_ID` is read when `messenger.html` starts.

