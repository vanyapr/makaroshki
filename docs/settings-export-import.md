# Export/Import Настроек

Macaroni Messenger может экспортировать локальный профиль в JSON-файл и импортировать его обратно.

Это нужно для переноса настроек между браузерами или для ручного backup.

## Что Входит В Export

Файл содержит:

- `CLIENT_ID`;
- отображаемое имя;
- язык интерфейса;
- provider;
- repo URL;
- access token;
- acceptance privacy warning.

Файл не содержит:

- сообщения;
- IndexedDB index;
- local test repo cache;
- outbox;
- read markers.

Сообщения должны жить в git. IndexedDB остаётся кешем.

## Важное Предупреждение

Settings export включает access token.

Это удобно.

Это не безопасно.

Храните файл так, как храните token.

## CLIENT_ID

Если импортированный файл содержит другой `CLIENT_ID`, клиент сохраняет его в `localStorage` и перезагружает страницу.

Это нужно потому, что `CLIENT_ID` читается при старте `messenger.html`.

