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

## Plugin Settings

Если registered plugins есть, core показывает в Settings секцию `Plugins`.

Минимальная модель:

- core рисует checkbox с названием каждого plugin;
- core хранит только enabled/disabled state plugin в `localStorage`;
- каждый plugin хранит settings в своём namespace;
- plugin не пишет свои settings в git;
- reset local profile не обязан чистить plugin settings, потому что это не часть core profile.

Plugin снаружи примотан изолентой и в нужное отверстие осуществляет прокотологию.

Это архитектурное решение.

Рекомендуемый ключ:

```text
macaroni.plugin.<plugin_id>.settings.v1
```

Пример:

```text
macaroni.plugin.macaroni-encryption-1.01.settings.v1
```

Core не обязан понимать внутреннюю структуру plugin settings.

Core должен дать plugin checkbox в Settings и не мешать ему быть странным.

Если plugin хочет свои поля, buttons или warnings, он может реализовать:

```js
mountSettings(container, context) {
  // plugin-specific controls live here
}
```

Core создаёт container и передаёт context.

Дальше plugin сам осуществляет прокотологию.

Plugin читает и пишет свой namespace напрямую:

```js
var settings = JSON.parse(localStorage.getItem(key) || "{}")
localStorage.setItem(key, JSON.stringify(settings))
```

В одной вкладке `localStorage` синхронный, поэтому обычный settings flow не должен ловить race condition.

В нескольких вкладках последний write победит.

Это нормально.

Macaroni не строит distributed settings database поверх `localStorage`.

## Правила

- Plugin ids должны быть уникальными.
- Plugins MUST be inserted immediately before the closing `</html>` tag.
- Plugins получают clone message object.
- Plugin должен вернуть валидный Protocol v1 message.
- Core валидирует финальное сообщение после plugin transforms.
- Core хранит persisted message cache как raw Protocol v1. Incoming transforms применяются к view-model, а не мутируют IndexedDB history.
- Plugins являются локальным browser code. Macaroni не загружает remote plugin code автоматически.
- Plugins не являются обещанием приватности.

## Почему Так

Этого достаточно для будущих экспериментов:

- encryption;
- custom formatting;
- local redaction;
- import/export transforms.

Конкретный контракт shared-secret encryption описан в `docs/encryption-1.01.md`.

Implementation contract Encryption 1.01 описан в `docs/encryption-1.01-implementation.md`.

Это не framework.

Это hook point.
