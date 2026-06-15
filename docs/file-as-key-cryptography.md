# Файл Как Ключ

> Обычная программа хранит ключ.
>
> Macaroni является ключом.

В нормальной разработке hardcoded secret внутри клиента - это катастрофа.

В Macaroni Messenger portable mode это становится моделью доступа.

Потому что `messenger.html` не является просто приложением.

Это artifact, который несёт capability:

```text
messenger.html =
  UI
  + repo URL
  + optional write token
  + CLIENT_ID
  + encryption plugin
  + shared secret
  + salt
  + settings
```

В обычном SaaS это идиотизм.

В мессенджере, который состоит из одного HTML-файла, это начинает работать.

## Главный Переворот

Обычный messenger:

```text
app публичный
ключи приватные
handshake сложный
```

Macaroni portable messenger:

```text
app приватный
ключ внутри app
handshake отсутствует
```

Мы не устанавливаем приложение и потом получаем ключ.

Мы получаем файл, который уже является ключом.

## Key Exchange Без Key Exchange

Macaroni не решает обмен ключами.

Macaroni выносит обмен ключами из сети.

Обмен ключами - это передача HTML-файла.

```text
сын записал messenger.html на флешку
сын отдал флешку маме
мама открыла messenger.html
handshake completed
```

Никаких:

- Diffie-Hellman;
- QR pairing;
- certificate pinning;
- key server;
- "введите код с другого устройства".

Физическая передача файла является key exchange.

Это тупо.

Именно поэтому это понятно.

## Capability Model

Можно сделать разные HTML-файлы с разными правами:

```text
messenger_full.html
  repo URL
  write token
  shared secret
  read/write UI

messenger_readonly.html
  repo URL
  shared secret
  no write token
  read-only UI

messenger_public_demo.html
  repo URL
  no token
  no secret
  demo/read-only UI
```

Права выдаются не аккаунту.

Права выдаются файлу.

```text
у кого файл - у того capability
```

Это не RBAC.

Это флешка.

## Почему Public Repo Больше Не Страшен

Если shared secret не хранится в git repository, публичный repo видит только encrypted payload:

```text
MACARONI1.01:...
MACARONI1.01:...
MACARONI1.01:...
```

Git остаётся source of truth.

Но Git больше не является readable truth для постороннего.

Публичность repo становится transport feature, а не privacy disaster.

Снаружи:

```text
Вот публичный repository.
В нём лежит каша.
Приятного анализа.
```

Внутри:

```text
Мам, свари макароны.
```

## Plugin И File Identity

Encryption plugin едет внутри того же HTML-файла.

Plugins MUST be inserted immediately before the closing `</html>` tag.

Значит crypto code, key material и UI compatibility распространяются одним artifact.

```text
получил файл = получил plugin
получил plugin = получил crypto behavior
получил secret = получил чат
```

Можно дополнительно считать file id:

```text
FILE_ID = hash или fnv от стабильной части messenger.html
```

И показывать его в UI:

```text
File ID: 7A3F
Crypto Profile: family-2026-06
```

Мама по телефону говорит:

> У меня File ID 7A3F.

Сын отвечает:

> Нормально. Это наш файл.

Это не PKI.

Это деревенский fingerprint.

Для Macaroni этого достаточно.

## Binding Crypto To File

Encryption material может включать file identity:

```text
secret
salt
file_id
repo_url
chat_id
message_id
created_at
length
```

Тогда один и тот же secret, случайно вставленный в другой portable build, не обязательно даёт тот же byte stream.

Это не делает систему "enterprise secure".

Это делает систему чуть менее тупой, не переставая быть тупой.

## Revocation

Если файл украли, украли capability.

Нужно:

1. Отозвать write token у provider.
2. Сгенерировать новый shared secret/salt.
3. Собрать новый `messenger.html`.
4. Раздать новый файл нормальным людям.
5. Старый файл считать мёртвым.

Никакого account recovery.

Никакого admin panel.

Никакого "мы отправили вам код подтверждения".

Старый файл умер.

Новый файл жив.

## Если Переписка Скомпрометирована

Git помнит.

Обычно это фича.

Если encrypted history или plaintext history скомпрометированы и вы хотите убрать их из remote branch, Macaroni recovery может быть таким:

```text
1. Собрать новый messenger.html с новым secret/token.
2. Создать новый clean history commit или squash старую историю.
3. Переписать branch.
4. Сделать push --force.
```

То есть:

```sh
git reset --soft <clean-start>
git commit -m "Macaroni: restart chat"
git push --force
```

Или любым другим способом сделать squash/rewrite history.

Это не магическое стирание.

Если кто-то уже сделал clone/fetch, у него старые objects могут остаться.

Если GitHub/GitLab успел закешировать данные, они могут жить где-то ещё.

Если secret уже украден, старые encrypted messages надо считать прочитанными.

Но для маленького семейного repo это нормальная аварийная ручка:

```text
сожгли старый файл
сожгли старую branch history
начали новый чат
```

Macaroni не обещает право на забвение.

Macaroni даёт кнопку "снести сарай и построить новый".

## Что Это Даёт Криптографии

Single-file architecture даёт странные преимущества:

- key exchange происходит вне сети;
- app, plugin и key version распространяются вместе;
- файл становится physical capability;
- можно делать per-chat HTML forks;
- public repo можно использовать как encrypted transport;
- revocation понятен обычному человеку: "старый файл больше не использовать";
- read-only/full-access режимы можно делать разными файлами;
- совместимость crypto version решается раздачей одного artifact.

Это не универсальная модель.

Это модель для маленьких групп.

Семья.

Друзья.

Подвал.

Команда, которая понимает, что делает.

## Атаки Из Старых Фильмов Про Хакеров

Macaroni не защищает от атак, где злоумышленник:

- украл ваш `messenger.html`;
- подменил hosted `messenger.html`;
- получил доступ к вашему компьютеру;
- достал старый portable bundle;
- угадал shared secret, потому что вы назвали его `123`.

На этом этапе это уже не криптография.

Это кино.

Если десант высадился с вертолёта, перекатился в окно, хакер прошёл лазерную комнату бэкфлипом, достал флешку из тайника за кактусом и унёс ваш `messenger.html`, он не "обошёл Macaroni Encryption".

Он добился цели.

Если священный файл украден, чат украден.

Если священный файл подменён, мессенджер подменён.

Если злоумышленник сидит за вашей клавиатурой, кипятите воду и ротируйте файл.

В терминах скучной безопасности это называется endpoint compromise.

В терминах Macaroni это называется "они добрались до флешки".

## Чего Это Не Даёт

Это не защищает, если:

- украли файл;
- украли localStorage;
- украли shared secret;
- украли write token;
- участник переслал файл дальше;
- provider сохранил старую историю;
- кто-то уже clone/fetch до force push;
- вы думаете, что HTML-файл заменил здравый смысл.

Файл надо хранить как ключ.

Потому что он и есть ключ.

## PGP-Sized Secret

Если в качестве `secret` и `salt` использован PGP-sized material, а файл с ключом безвозвратно удалён, восстановление практически невозможно.

Это уже не забытый пароль.

Это сгоревшая маленькая вселенная.

Короткий пароль можно пытаться вспомнить, угадать или перебрать.

PGP-sized secret не "восстанавливают".

Его либо хранят, либо оплакивают.

```text
новый ключ появится быстрее,
чем старый будет найден перебором
```

И это тоже часть file-as-key модели.

Нет сервера поддержки.

Нет кнопки "restore account".

Нет доброго админа, который "сейчас посмотрит в базе".

Если файл был capability artifact и он умер окончательно, чат для этого файла умер вместе с ним.

## Девиз

```text
Файл - это ключ.
Ключ - это файл.
Передал файл - добавил участника.
Потерял файл - потерял чат.
```

Macaroni не делает "настоящую приватность".

Macaroni делает честную приватность для людей, которые понимают, где лежит файл.
