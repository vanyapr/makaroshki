# Portable Version For Mom

Goal:

give mom one file that she can double-click and use to write:

> Please cook macaroni.

No registration.

No GitHub explanation.

No "personal access token" conversation.

At some point, the project has to stop explaining itself and start cooking pasta.

## What We Are Building

Take the normal:

```text
messenger.html
```

and make a personal copy:

```text
macaroni-mom.html
```

Inside that copy, prefill:

- display name;
- `CLIENT_ID`;
- language;
- git provider;
- repository URL;
- access token;
- privacy warning acceptance.

Then put the file on the desktop.

Mom opens the file.

The messenger is already configured.

## Important Warning

A portable file with a hardcoded token is the token.

Not "contains the token".

Is the token.

Anyone who gets this HTML file can write to the repository with that token's permissions.

This is not private.

This is not secure.

This is convenient.

Macaroni Messenger once again did exactly what it promised.

## The Right Token

For GitHub, use a fine-grained token:

- repository access: only the target repo;
- permissions: `Contents: Read and write`;
- metadata read access is added by GitHub automatically;
- expiration: your choice, but "forever" is not ideal if the file may travel on a flash drive.

If the portable file is lost:

1. Revoke the token.
2. Create a new token.
3. Build a new `macaroni-mom.html`.
4. Treat the old file as compromised.

## CLIENT_ID

Create a separate `CLIENT_ID` for each person.

Examples:

```text
MAMA
PAPA
AUNT
```

Technically, the protocol likes four characters from the funny alphabet.

Practically, `MAMA` explains who is writing.

If two people use the same `CLIENT_ID`, the chat becomes a family dinner identity incident.

Do not.

## How To Make The HTML

1. Copy `messenger.html`.
2. Name the copy:

```text
macaroni-mom.html
```

3. Open the copy in a text editor.
4. Find this line near the end:

```js
setClientIdText();
```

5. Insert this JS block before it.

Important: this location is already inside the main `<script>`, so do not add extra `<script>` tags.

```js
(function () {
  var PORTABLE_CLIENT_ID = "MAMA";
  var PORTABLE_PROFILE = {
    clientId: PORTABLE_CLIENT_ID,
    displayName: "Mom",
    language: "en",
    provider: "github",
    repo: "https://github.com/YOUR_LOGIN/YOUR_REPO",
    token: "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    privacyAccepted: true
  };

  try {
    localStorage.setItem("macaroni.client_id.v1", PORTABLE_CLIENT_ID);
    localStorage.setItem("macaroni.language.v1", PORTABLE_PROFILE.language);
    localStorage.setItem("macaroni.profile.v1", JSON.stringify(PORTABLE_PROFILE));
  } catch (error) {}
}());
```

6. Replace:

- `MAMA` with the target `CLIENT_ID`;
- `Mom` with the display name;
- `YOUR_LOGIN/YOUR_REPO` with the repository;
- `github_pat_xxx` with the token.

7. Save the file.

## Cleaner Variant

If you do not want to overwrite settings on every launch, use "first launch only":

```js
(function () {
  var PORTABLE_CLIENT_ID = "MAMA";
  var PORTABLE_PROFILE_KEY = "macaroni.profile.v1";

  if (localStorage.getItem(PORTABLE_PROFILE_KEY)) {
    return;
  }

  var PORTABLE_PROFILE = {
    clientId: PORTABLE_CLIENT_ID,
    displayName: "Mom",
    language: "en",
    provider: "github",
    repo: "https://github.com/YOUR_LOGIN/YOUR_REPO",
    token: "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    privacyAccepted: true
  };

  try {
    localStorage.setItem("macaroni.client_id.v1", PORTABLE_CLIENT_ID);
    localStorage.setItem("macaroni.language.v1", PORTABLE_PROFILE.language);
    localStorage.setItem(PORTABLE_PROFILE_KEY, JSON.stringify(PORTABLE_PROFILE));
  } catch (error) {}
}());
```

This is better for normal use.

Mom can change settings later, and the file will not keep saying:

> No, Mom, I know better.

## How To Check

Open `macaroni-mom.html` in Chrome / Chromium / Edge.

Check:

- `ID: MAMA` is shown;
- the first-run setup screen does not appear;
- the chat list opens;
- a test message can be sent;
- after 30 seconds or after `Refresh`, the message appears in git;
- after closing and reopening, history is rebuilt.

If you see the incompatibility screen:

the browser is not funny enough.

Open it in a normal browser.

Do not start `localhost`.

`localhost` kills the joke.

## Desktop Shortcut

### macOS

The simplest way:

1. Put `macaroni-mom.html` somewhere it will not be deleted.
2. Drag it to the Dock or desktop.
3. Rename the shortcut:

```text
Macaroni
```

If you want Chrome specifically:

1. Open the file in Chrome.
2. The address bar will show `file:///.../macaroni-mom.html`.
3. Drag the address from Chrome to the desktop.

You now have a shortcut to a local HTML file.

Future technology.

### Windows

Use a normal shortcut:

1. Put `macaroni-mom.html` in a clear folder.
2. Right-click the desktop.
3. `New` -> `Shortcut`.
4. Use this target:

```text
"C:\Program Files\Google\Chrome\Application\chrome.exe" "C:\Users\USER\Documents\macaroni-mom.html"
```

5. Name it:

```text
Macaroni
```

If Chrome is somewhere else, Windows won; find `chrome.exe`.

### Linux

Create:

```text
macaroni-mom.desktop
```

With:

```ini
[Desktop Entry]
Type=Application
Name=Macaroni
Exec=chromium /home/USER/macaroni-mom.html
Terminal=false
```

Make it executable:

```sh
chmod +x macaroni-mom.desktop
```

Put it on the desktop.

If you use Linux, you already knew `chmod` was coming.

## Updating The Portable File

When a new `messenger.html` is released:

1. Copy the new `messenger.html`.
2. Insert the prefill snippet again.
3. Check that token and `CLIENT_ID` are correct.
4. Give mom the new file.

Message history does not live in the file.

Message history lives in git.

The file can be replaced.

Git remembers.

## What Not To Do

Do not give the same portable file to multiple people.

Do not put the portable file in a public repository.

Do not attach the portable file to a group chat.

Do not name it:

```text
secret-token-final-final-mom.html
```

Do not explain GitHub to mom unless she asked.

## Normal Variant Without Hardcoded Token

There is a cleaner path:

1. Open the normal `messenger.html`.
2. Configure the profile manually.
3. Export settings from Settings.
4. Import settings on another device.

This is documented in [settings-export-import.en.md](settings-export-import.en.md).

But the portable file is funnier.

And the project is called Macaroni Messenger, not Enterprise Secure Family Communication Suite.
