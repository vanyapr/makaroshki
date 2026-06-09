# Browser Support Matrix

Macaroni Messenger поддерживает не бренды браузеров, а набор browser features.

Если браузер умеет всё нужное, он поддерживается.

Если не умеет, он недостаточно смешной.

## Требуется

| Requirement | Зачем |
| --- | --- |
| `file://` или `https://` origin storage | Основной дистрибутив открывается как локальный или hosted `messenger.html`. |
| `localStorage` | Хранит `CLIENT_ID`, профиль, язык и token. |
| `IndexedDB` | Хранит локальный индекс, кеш repo files и outbox. |
| `WebCrypto` | Минимальная modern-browser граница для будущих crypto/plugins. |

## Рекомендуется

| Browser | Status |
| --- | --- |
| Chrome | Recommended |
| Chromium | Recommended |
| Edge | Recommended |

## Не Поддерживается

- Браузеры без persistent storage для `file://` или `https://` origin.
- Режимы, где `localStorage` или `IndexedDB` отключены.
- Окружения, где WebCrypto недоступен.

## Не Делаем

Мы не предлагаем `localhost` как workaround.

Если ради браузера нужно поднимать сервер, браузер идёт мимо.

Главная шутка проекта - `messenger.html`, double click, работает.

