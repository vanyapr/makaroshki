# Browser Support Matrix

Macaroni Messenger supports browser features, not browser brands.

If a browser has all required features, it is supported.

If it does not, it is not funny enough.

## Required

| Requirement | Why |
| --- | --- |
| `file://` or `https://` origin storage | The main distribution opens as local or hosted `messenger.html`. |
| `localStorage` | Stores `CLIENT_ID`, profile, language, and token. |
| `IndexedDB` | Stores the local index, repo-file cache, and outbox. |
| `WebCrypto` | Minimal modern-browser boundary for future crypto/plugins. |

## Recommended

| Browser | Status |
| --- | --- |
| Chrome | Recommended |
| Chromium | Recommended |
| Edge | Recommended |

## Unsupported

- Browsers without persistent storage for `file://` or `https://` origin.
- Modes where `localStorage` or `IndexedDB` are disabled.
- Environments where WebCrypto is unavailable.

## We Do Not Do

We do not offer `localhost` as a workaround.

If a browser needs a server just to work, that browser is out.

The main joke is `messenger.html`, double click, works.

