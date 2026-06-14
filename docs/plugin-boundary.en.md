# Plugin Boundary

Macaroni Messenger keeps the core dumb.

Complex features belong to plugins.

In the browser build, a plugin is a small JavaScript object registered through:

```js
window.MacaroniPlugins.register({
  id: "example-plugin",
  name: "Example Plugin",
  transformOutgoingMessage(message, context) {
    return message
  },
  transformIncomingMessage(message, context) {
    return message
  }
})
```

## What Exists Now

The current boundary is intentionally small:

- `register(plugin)` registers a plugin object;
- `list()` returns registered plugin ids and names;
- `clear()` clears the registry for tests or manual reset;
- `applyOutgoingMessage(message, context)` runs outbound transforms;
- `applyIncomingMessage(message, context)` runs inbound transforms manually.

The composer uses `transformOutgoingMessage` before the message is written to local cache or git.

Inbound transforms are exposed as a boundary, but automatic decrypt/render integration is not part of this step yet.

## Plugin Settings

If registered plugins exist, the core shows a `Plugins` section in Settings.

Minimal model:

- the core renders a checkbox with each plugin name;
- the core stores only plugin enabled/disabled state in `localStorage`;
- every plugin stores settings in its own namespace;
- plugin does not write its settings to git;
- local profile reset does not need to clear plugin settings, because they are not part of the core profile.

The plugin is duct-taped from the outside and performs protocoloscopy through the correct hole.

This is an architectural decision.

Recommended key:

```text
macaroni.plugin.<plugin_id>.settings.v1
```

Example:

```text
macaroni.plugin.macaroni-encryption-1.01.settings.v1
```

The core does not need to understand plugin settings internals.

The core should give the plugin a checkbox in Settings and not prevent it from being strange.

If a plugin wants its own fields, buttons, or warnings, it may implement:

```js
mountSettings(container, context) {
  // plugin-specific controls live here
}
```

The core creates the container and passes context.

After that, the plugin renders its own controls and works with its own namespace.

The plugin reads and writes its own namespace directly:

```js
var settings = JSON.parse(localStorage.getItem(key) || "{}")
localStorage.setItem(key, JSON.stringify(settings))
```

Inside one tab, `localStorage` is synchronous, so a normal settings flow should not hit a race condition.

Across several tabs, the last write wins.

That is fine.

Macaroni is not building a distributed settings database on top of `localStorage`.

## Rules

- Plugin ids must be unique.
- Plugins MUST be inserted immediately before the closing `</html>` tag.
- Plugins receive a cloned message object.
- A plugin must return a valid Protocol v1 message.
- The core validates the final message after plugin transforms.
- The core stores persisted message cache as raw Protocol v1. Incoming transforms apply to the view model and do not mutate IndexedDB history.
- Plugins are local browser code. Macaroni does not load remote plugin code automatically.
- Plugins are not a privacy promise.

## Why This Shape

This is enough for future experiments like:

- encryption;
- custom formatting;
- local redaction;
- import/export transforms.

The concrete shared-secret encryption contract is documented in `docs/encryption-1.01.en.md`.

The Encryption 1.01 implementation contract is documented in `docs/encryption-1.01-implementation.en.md`.

It is not a framework.

It is a hook point.
