# Macaroni Encryption 1.01

> Исправлена опечатка. И ещё кое-что по мелочи.

Macaroni Encryption 1.01 - это не новый протокол Macaroni.

Статус: реализовано в `messenger.html` как built-in plugin `macaroni-encryption-1.01`.

Macaroni Protocol v1 уже зафиксирован и остаётся как есть:

- `.macaroni/chats/<chat_id>/messages/.../<message_id>.json`;
- обычный Protocol v1 message;
- обычное поле `text`;
- обычный git transport;
- обычный local index.

Шифрование является **плагином**.

Плагин берёт `message.text`, превращает его в макаронную кашу и кладёт эту кашу обратно в `message.text`.

Core не знает и не должен знать, что внутри: обычный текст или `MACARONI1.01:...`.

Implementation contract: [docs/encryption-1.01-implementation.md](encryption-1.01-implementation.md).

## Главное Правило

Plugins MUST be inserted immediately before the closing `</html>` tag.

Encryption 1.01 тоже.

Не в `<head>`.

Не рядом с CSS.

Не отдельным bundle.

Перед `</html>`.

Потому что это один HTML-файл, а не фестиваль сборщиков.

## Что Это Такое

Macaroni Encryption 1.01 - это shared-secret encryption plugin.

У всех участников есть один и тот же секрет:

```js
const MACARONI_101_SECRET = "12345";
const MACARONI_101_SALT = "macaroni";
```

Секрет может:

- лежать hardcoded в portable `messenger.html`;
- храниться в `localStorage`;
- импортироваться из файла;
- экспортироваться в файл с прекрасным именем `SUPER_SECRET_PRIVATE_PGP_KEY.txt`.

Файл называется как PGP key, но PGP тут нет.

Это просто shared secret в плаще.

## Что Не Меняется

Не меняется:

- Macaroni Protocol v1;
- layout `.macaroni/`;
- message path;
- chat metadata;
- members;
- inbox;
- outbox;
- git provider adapters.

Шифрование не добавляет `type: encrypted` в базовый protocol.

Шифрование не требует migration.

Шифрование не ломает plaintext client.

Plaintext client увидит примерно такое:

```text
MACARONI1.01:eyJ2IjoiMS4wMSIsImFsZyI6ImVudHJvcHktbW9ub2xpdGgteG9yIiw...
```

Client с тем же plugin и тем же secret увидит:

```text
Мам, свари макароны.
```

## Включение И Выключение

Encryption 1.01 является режимом плагина.

Plugin добавляет в Settings checkbox с названием плагина.

Включён plugin или выключен - хранится в `localStorage`.

Настройки Encryption 1.01 хранятся отдельно от core profile:

```text
macaroni.plugin.macaroni-encryption-1.01.settings.v1
```

Пользователь может:

- включить шифрование;
- выключить шифрование;
- задать secret;
- очистить secret;
- импортировать secret из любого файла;
- экспортировать secret в `SUPER_SECRET_PRIVATE_PGP_KEY.txt`.

Если шифрование включено:

- outgoing messages шифруются перед записью в raw local cache/git;
- incoming messages хранятся в IndexedDB как raw Protocol v1 messages;
- incoming messages расшифровываются только перед показом в UI/search/export;
- repo хранит кашу.

Если шифрование выключено:

- core работает как раньше;
- новые messages уходят plaintext;
- старые encrypted messages остаются кашей и в git, и в local cache, пока plugin снова не включён.

## Файл - Это Ключ

В portable mode secret может быть hardcoded прямо в HTML.

Это намеренно.

Подробная модель описана отдельно: `docs/file-as-key-cryptography.md`.

Модель такая:

```text
Файл - это ключ.
Ключ - это файл.
Потерял файл - потерял чат.
```

Если вы дали `messenger.html` маме на флешке, мама может читать чат.

Если кто-то украл `messenger.html`, он тоже может читать чат.

Это не баг.

Это threat model.

## Алгоритм: Entropy Monolith XOR

Мы не используем PGP.

Мы не используем age.

Мы не используем TLS handshake.

Мы не используем WebCrypto как обязательную зависимость для Encryption 1.01.

Мы берём:

- shared secret;
- salt;
- repo URL;
- chat id;
- sender id;
- recipients;
- message id;
- created_at;
- plaintext length.

Собираем material:

```text
macaroni-1.01|secret|salt|repo|chat|from|to|message_id|created_at|length
```

Из material получаем seed.

Из seed получаем byte stream.

Byte stream XOR-ится с plaintext.

Получается ciphertext.

Ciphertext кладётся в `message.text`.

Это не "военная криптография".

Это криптография на коленке, у которой хотя бы есть коленка.

## Token Confetti

В обычном write-enabled Macaroni profile локальный write token уже есть: без него пользователь не пишет в git, а просто смотрит на макароны через витрину.

Encryption 1.01 использует этот token как источник локального confetti перед шифрованием.

В read-only/demo режимах token может отсутствовать. Это не ломает расшифровку, потому что confetti не является ключом.

Token Confetti:

- не покидает браузер;
- не пишется в git;
- не хешируется в публичные metadata;
- не требуется для расшифровки;
- может отличаться у каждого участника;
- отсутствует только в read-only/demo режимах.

Token Confetti - это не второй замок.

Это блёстки внутри закрытого конверта.

Plugin может добавить confetti в clear envelope до XOR stream encryption. После расшифровки получатель просто выбрасывает confetti и показывает text.

Разные tokens не ломают совместимость.

Отсутствие token в read-only/demo режиме не выключает расшифровку.

Token Confetti ничего не обещает.

Он просто портит паттерны.

## Почему Не Просто Повторять Ключ

Плохой вариант:

```js
cipher[i] = plain[i] ^ key[i % key.length]
```

Это repeating-key XOR.

Он слишком быстро становится не смешным.

Правильный макаронный вариант:

```text
material -> tiny deterministic PRNG -> byte stream -> XOR
```

PRNG может быть максимально тупым:

- FNV-1a для seed;
- xorshift32 или SFC32 для stream;
- XOR для encrypt/decrypt.

Это всё ещё велосипед.

Просто у велосипеда есть два колеса.

## Payload Format

Encrypted text хранится в `message.text`:

```text
MACARONI1.01:<base64-json>
```

Внутри:

```json
{
  "v": "1.01",
  "alg": "entropy-monolith-xor",
  "salt_id": "family",
  "ctx": {
    "repo": "https://github.com/vanyapr/makaroshki",
    "chat": "chat_20260613_mama_son",
    "from": "MAMA",
    "to": ["SON"],
    "message_id": "2026-06-13T14-00-00.000Z_MAMA_ab12cd",
    "created_at": "2026-06-13T14:00:00.000Z",
    "length": 42
  },
  "tag": "7f12ab90",
  "data": "base64..."
}
```

`tag` нужен не для военной уверенности.

Он нужен, чтобы отличить:

- неправильный key;
- битый payload;
- маму, которая пишет слишком загадочно.

## Что Защищаем

Encryption 1.01 защищает от человека, который:

- видит публичный git repository;
- читает `.macaroni/`;
- не имеет `messenger.html`;
- не знает shared secret.

Для него repo превращается в лапшу.

## Что Не Защищаем

Encryption 1.01 не защищает, если:

- украли `messenger.html` с hardcoded secret;
- украли `localStorage`;
- украли shared secret;
- украли GitHub/GitLab token и могут писать в repo;
- участник чата сам решил всё слить;
- вы используете secret `123`;
- вы ждёте от макарон поведения Signal.

Если вам нужна "настоящая приватность" - используйте PGP.

Если вам надо сказать маме "свари макароны", чтобы публичный repo не читал весь интернет, этого достаточно.

## UI Contract

В настройках появляется секция Encryption.

Минимальные controls:

- Enable encryption;
- Disable encryption;
- Set key;
- Clear key;
- Export key;
- Import key.

Key modal:

- принимает любой набор символов;
- честно говорит, что key хранится в `localStorage`;
- честно говорит, что hardcoded portable file является ключом.

Export:

```text
SUPER_SECRET_PRIVATE_PGP_KEY.txt
```

Import:

- любой file;
- contents file становятся shared secret;
- filename значения не имеет.

## Portable Mode

Portable `messenger.html` может содержать:

- repo URL;
- write token;
- `CLIENT_ID`;
- display name;
- encryption secret;
- encryption salt;
- encryption enabled flag.

Пользователь открывает файл и сразу видит чат.

Никаких:

- handshake;
- key exchange;
- password prompt;
- регистрации;
- серверов.

Файл всё знает.

Именно поэтому файл надо хранить нормально.

## Официальная Позиция

Macaroni Messenger не становится "приватным мессенджером".

Macaroni Messenger показывает, как может быть устроено простое шифрование без серверов, handshakes и посредников.

Мы не продаём иллюзий.

Мы не обещаем защиту от АНБ, ФСБ, GitHub, соседей или человека, который нашёл вашу флешку.

Мы утверждаем только это:

> Если у вас есть общий secret, а у постороннего есть только публичный repo, посторонний видит кашу.

Это достаточно.

Макароны стынут.
