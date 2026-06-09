# Electron/WebView Wrapper

Macaroni Messenger remains a single HTML file.

The Electron/WebView wrapper is not a separate application and does not contain a copy of the client.

It only opens:

```text
messenger.html
```

## What Exists Now

Minimal Electron entrypoint:

```text
wrappers/electron/main.js
```

It:

- creates a `BrowserWindow`;
- loads the root `messenger.html` through `loadFile`;
- does not enable `nodeIntegration`;
- enables `contextIsolation`;
- does not start `localhost`;
- does not add a backend.

## How To Run

If Electron is already installed in your environment:

```sh
electron wrappers/electron/main.js
```

The repository intentionally has no required `package.json` and no required Electron dependency. The main distribution remains `messenger.html`.

## Rule

The wrapper must not become the product center.

If a feature requires rewriting the client for Electron, the feature does not pass.

