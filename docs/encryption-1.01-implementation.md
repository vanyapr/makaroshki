# Macaroni Encryption 1.01 Implementation Contract

Этот документ - мост между манифестом Encryption 1.01 и кодом.

Статус: реализовано в `messenger.html` как built-in plugin `macaroni-encryption-1.01`.

Цель: написать максимально примитивное решение, которое тупейшим образом работает, но не лишено логики и здравого смысла.

Не делаем новый Macaroni Protocol.

Не меняем `.macaroni/`.

Не добавляем dependency.

Не тащим чужой crypto protocol.

Пишем велосипед.

Если велосипед можно изобрести - изобретём.

Квадратные колёса являются фичей, пока они едут.

## Scope

Encryption 1.01 реализуется как plugin.

Plugin вставляется перед закрывающим `</html>` tag.

Plugin использует:

- `window.MacaroniPlugins.register(...)`;
- `transformOutgoingMessage(message, context)`;
- `transformIncomingMessage(message, context)`;
- `mountSettings(container, context)` или такой же примитивный hook для plugin-specific controls;
- `localStorage`;
- `TextEncoder`;
- `TextDecoder`;
- `btoa`;
- `atob`.

Plugin не использует:

- WebCrypto как обязательную зависимость;
- PGP;
- age;
- OpenSSL;
- external bundle;
- package manager;
- handshake;
- key server.

## Core Settings Contract

Если в файле есть plugins, core показывает в Settings секцию:

```text
Plugins
```

Для каждого registered plugin core показывает checkbox с названием plugin.

Минимальная модель:

```text
[x] Macaroni Encryption 1.01
```

Core не рисует plugin-specific form.

Core не понимает plugin-specific settings.

Core только:

1. показывает plugin checkbox;
2. читает enabled state из `localStorage`;
3. пишет enabled state в `localStorage`;
4. сообщает plugin context при transforms.

Plugin-specific UI монтирует сам plugin через `mountSettings(container, context)` или аналог.

Для 1.01 достаточно checkbox от core и отдельных import/export/secret controls, если plugin сам их примонтирует.

## Plugin Settings Storage

Настройки plugin не хранятся в core profile.

Это значит:

- core profile остаётся core profile;
- plugin settings живут отдельно;
- plugin сам читает и пишет свой namespace;
- plugin settings не пишутся в git;
- plugin settings не экспортируются вместе с core profile, пока отдельная фича этого не сделает.

Recommended key:

```text
macaroni.plugin.<plugin_id>.settings.v1
```

Encryption 1.01 key:

```text
macaroni.plugin.macaroni-encryption-1.01.settings.v1
```

Чтение:

```js
JSON.parse(localStorage.getItem(key) || "{}")
```

Запись:

```js
localStorage.setItem(key, JSON.stringify(settings))
```

Никакой магии.

## LocalStorage Race Conditions

В одной browser tab `localStorage.getItem` и `localStorage.setItem` синхронные.

То есть внутри одного submit/send flow race condition не ожидается.

Между несколькими вкладками:

- `localStorage` не является distributed database;
- последний write победит;
- `storage` event может помочь позже, но не является частью 1.01;
- если два окна одновременно меняют plugin settings, они сами устроили себе маленький GitHub без Git.

Для Encryption 1.01 это нормально.

Settings меняются редко.

Messages идут через git/outbox.

Макароны не биржевой терминал.

## Encryption Settings Schema

Значение `macaroni.plugin.macaroni-encryption-1.01.settings.v1`:

```json
{
  "enabled": true,
  "secret": "12345",
  "salt": "macaroni",
  "salt_id": "family",
  "confetti_counter": 42,
  "debug": false,
  "updated_at": "2026-06-13T12:00:00.000Z"
}
```

Fields:

- `enabled` - включает outgoing encryption и incoming decrypt attempt.
- `secret` - shared secret. Любая строка.
- `salt` - shared salt. Любая строка.
- `salt_id` - публичное имя salt/profile для UI/debug, не secret.
- `confetti_counter` - локальный счётчик Token Confetti.
- `debug` - development-only console logs.
- `updated_at` - timestamp последнего изменения settings.

Default:

```json
{
  "enabled": false,
  "secret": "12345",
  "salt": "macaroni",
  "salt_id": "default",
  "confetti_counter": 0,
  "debug": false
}
```

Default secret/salt специально выглядят как пароль от роутера на даче.

Если `enabled === true`, но `secret` или `salt` пустые, plugin не шифрует и не расшифровывает.

Он возвращает message как есть.

## Payload Format

Core Protocol v1 message остаётся обычным:

```json
{
  "type": "text",
  "text": "MACARONI1.01:<base64-json>"
}
```

Encrypted payload marker:

```text
MACARONI1.01:
```

Outer encrypted payload:

```json
{
  "v": "1.01",
  "alg": "entropy-monolith-xor-tiny-prng",
  "ctx": {
    "repo": "https://github.com/vanyapr/makaroshki",
    "chat": "chat_20260613_mama_son",
    "from": "MAMA",
    "to": ["SON"],
    "message_id": "2026-06-13T14-00-00.000Z_MAMA_ab12cd",
    "created_at": "2026-06-13T14:00:00.000Z",
    "length": 42
  },
  "data": "base64..."
}
```

`data` содержит encrypted clear envelope.

Clear envelope до encryption:

```json
[
  "1.01",
  "base64-token-confetti",
  "Мам, свари макароны"
]
```

Почему array?

Потому что он короче, тупее и не делает вид, что мы проектируем банковский JSON API.

Поля:

1. version marker;
2. Token Confetti;
3. plaintext.

Token Confetti может быть пустой строкой.

## Context Binding

Plugin не меняет Macaroni Protocol, поэтому сам protocol не мешает кому-то переложить file в другой chat path.

Plugin должен быть скучнее и подозрительнее.

При decrypt plugin сверяет outer Protocol v1 message с payload `ctx`:

- `message.chat_id === ctx.chat`;
- `message.from === ctx.from`;
- `message.id === ctx.message_id`;
- `message.created_at === ctx.created_at`;
- `message.to` после sort совпадает с `ctx.to` после sort.

Если context не совпал:

- plugin не расшифровывает;
- plugin возвращает original message;
- UI показывает `MACARONI1.01:...` как обычный plaintext;
- в development mode можно написать `console.debug`.

Мы не объясняем пользователю, что "protocol не работает".

Protocol работает.

Кто-то просто принёс кашу не в тот чат.

## Tiny PRNG

Алгоритм называется Tiny PRNG.

Это наш велосипед.

Он нужен, чтобы из shared secret, salt и message context получить byte stream для XOR.

Идея:

```text
material -> FNV-1a -> xorshift32 -> byte stream -> XOR
```

Pseudocode:

```js
function fnv1a(str, seed) {
  var h = seed >>> 0;

  for (var i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }

  return h >>> 0;
}

function xorshift32(seed) {
  var x = seed >>> 0 || 0x6d2b79f5;

  return function () {
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    return x >>> 0;
  };
}

function xorTinyPrng(bytes, material) {
  var out = new Uint8Array(bytes.length);
  var random = xorshift32(fnv1a(material, 0x811c9dc5));
  var word = 0;
  var used = 4;

  for (var i = 0; i < bytes.length; i++) {
    if (used >= 4) {
      word = random();
      used = 0;
    }

    out[i] = bytes[i] ^ ((word >>> (used * 8)) & 255);
    used++;
  }

  return out;
}
```

Encrypt и decrypt - одна функция.

Потому что XOR.

Квадратные колёса, но едут.

## Encryption Material

Material:

```text
macaroni-1.01
secret
salt
repo
chat
from
to_sorted
message_id
created_at
plaintext_length
```

Joined with `|`.

Plaintext itself не входит в material.

Получатель не знает plaintext до decrypt.

Не заставляем маму решать рекурсию.

## Token Confetti

В write-enabled profile token есть штатно.

Token Confetti использует token только локально.

Token:

- не сериализуется;
- не пишется в git;
- не хешируется в public metadata;
- не требуется для decrypt.

Token Confetti живёт внутри clear envelope.

Получатель после decrypt просто выбрасывает его.

Implementation detail intentionally stays boring in docs:

```text
token + message context + local counter -> bytes
```

Код может быть смешнее документации.

Если кто-то читает implementation и роняет кофе на клавиатуру, это не bug report.

## Incoming Behavior

Если incoming `message.text` не начинается с `MACARONI1.01:`, plugin возвращает message как есть.

Core хранит incoming messages в IndexedDB как raw Protocol v1 documents.

Plugin decrypt не пишет plaintext обратно в cache.

Decrypt применяется как view transform перед UI/search/export.

Чекбокс plugin должен менять отображение, а не переписывать историю. Git помнит кашу, IndexedDB кеширует кашу, пользователь видит макароны только когда сам включил вилку.

Если starts with `MACARONI1.01:`, но:

- plugin выключен;
- нет secret/salt;
- payload malformed;
- decrypt failed;
- clear envelope malformed;
- context mismatch;
- unsupported version;

plugin возвращает original message.

UI показывает то, что пришло.

Никаких красных экранов.

Никаких "ваша криптография сломалась".

Macaroni не психотерапевт.

В development mode plugin может писать:

```js
console.debug("[macaroni-encryption-1.01]", reason)
```

К релизу эти logs выключены по default.

## Outgoing Behavior

Если plugin выключен или нет secret/salt:

- outgoing message не меняется.

Если plugin включен:

1. plugin берёт plaintext из `message.text`;
2. строит ctx из Protocol v1 message и profile/repo context;
3. делает Token Confetti, если есть token;
4. собирает clear envelope;
5. UTF-8 encodes clear envelope;
6. XOR через Tiny PRNG stream;
7. base64 encodes result;
8. заменяет `message.text` на `MACARONI1.01:<base64-json>`;
9. возвращает валидный Protocol v1 message.

## Temporary Verification

Постоянные tests в repo пока не добавляем.

Если нужны проверки во время разработки:

- пишем scratch script в `/tmp` или `/private/tmp`;
- проверяем roundtrip;
- проверяем Cyrillic/emoji;
- проверяем, что одинаковое `"1"` два раза даёт разные payload при confetti;
- проверяем, что разные sender tokens не ломают decrypt;
- проверяем, что no-token read-only decrypt работает;
- проверяем, что wrong secret возвращает original message;
- после проверки удаляем scratch script.

В repo не оставляем тестовую простыню. Если нужен smoke - он живёт во временной директории, делает своё дело и уходит в закат.

## Portable Docs

`docs/portable-mom.md` и `docs/portable-mom.en.md` обновляются после реализации фичи.

Там нужно будет описать:

- hardcoded encryption settings;
- full file vs read-only file;
- secret/salt placement;
- token placement;
- file-as-key warning;
- rotation after compromise.

До реализации не врём, что portable crypto уже есть.
