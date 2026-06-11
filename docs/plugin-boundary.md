# Plugin Boundary

Macaroni Messenger держит ядро тупым.

Сложные фичи живут в плагинах.

В browser build плагин - это маленький JavaScript-объект, зарегистрированный через:

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

## Что Уже Есть

Текущая граница намеренно маленькая:

- `register(plugin)` регистрирует plugin object;
- `list()` возвращает id и names зарегистрированных plugins;
- `clear()` очищает registry для тестов или ручного сброса;
- `applyOutgoingMessage(message, context)` запускает outbound transforms;
- `applyIncomingMessage(message, context)` запускает inbound transforms вручную.

Composer использует `transformOutgoingMessage` перед записью сообщения в локальный кеш или git.

Inbound transforms уже выставлены как boundary, но автоматическая интеграция decrypt/render пока не входит в этот шаг.

## Правила

- Plugin ids должны быть уникальными.
- Plugins MUST be inserted immediately before the closing `</html>` tag.
- Plugins получают clone message object.
- Plugin должен вернуть валидный Protocol v1 message.
- Core валидирует финальное сообщение после plugin transforms.
- Plugins являются локальным browser code. Macaroni не загружает remote plugin code автоматически.
- Plugins не являются обещанием приватности.

## Почему Так

Этого достаточно для будущих экспериментов:

- encryption;
- custom formatting;
- local redaction;
- import/export transforms.

Это не framework.

Это hook point.
