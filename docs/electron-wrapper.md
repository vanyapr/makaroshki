# Electron/WebView Wrapper

Macaroni Messenger остаётся одним HTML-файлом.

Electron/WebView wrapper не является отдельным приложением и не содержит копию клиента.

Он просто открывает:

```text
messenger.html
```

## Что Есть Сейчас

Минимальный Electron entrypoint:

```text
wrappers/electron/main.js
```

Он:

- создаёт `BrowserWindow`;
- грузит корневой `messenger.html` через `loadFile`;
- не включает `nodeIntegration`;
- включает `contextIsolation`;
- не поднимает `localhost`;
- не добавляет backend.

## Как Запустить

Если Electron уже установлен в вашем окружении:

```sh
electron wrappers/electron/main.js
```

В репозитории намеренно нет обязательного `package.json` и обязательной dependency на Electron. Основной дистрибутив по-прежнему `messenger.html`.

## Правило

Wrapper не должен становиться продуктовым центром.

Если фича требует переписать клиент под Electron, фича не проходит.

