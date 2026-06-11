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

## Rules

- Plugin ids must be unique.
- Plugins MUST be inserted immediately before the closing `</html>` tag.
- Plugins receive a cloned message object.
- A plugin must return a valid Protocol v1 message.
- The core validates the final message after plugin transforms.
- Plugins are local browser code. Macaroni does not load remote plugin code automatically.
- Plugins are not a privacy promise.

## Why This Shape

This is enough for future experiments like:

- encryption;
- custom formatting;
- local redaction;
- import/export transforms.

It is not a framework.

It is a hook point.
