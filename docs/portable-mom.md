# Portable Версия Для Мамы

Цель:

дать маме один файл, по которому можно два раза кликнуть и написать:

> Свари макарошки.

Без регистрации.

Без объяснения GitHub.

Без слов "personal access token".

Потому что в какой-то момент проект должен перестать объяснять себя и начать варить макароны.

## Что Мы Делаем

Мы берём обычный:

```text
messenger.html
```

и делаем персональную копию:

```text
macaroni-mama.html
```

Внутри этой копии заранее прописываем:

- имя пользователя;
- `CLIENT_ID`;
- язык;
- git provider;
- repository URL;
- access token;
- acceptance privacy warning.

После этого файл можно положить на рабочий стол.

Мама открывает файл.

Мессенджер уже настроен.

## Важное Предупреждение

Portable-файл с захардкоженным token является token.

Не "содержит token".

Является token.

Если кто-то получил этот HTML-файл, он получил возможность писать в репозиторий с правами этого token.

Это не приватно.

Это не безопасно.

Это удобно.

Macaroni Messenger снова сделал ровно то, что обещал.

## Правильный Token

Для GitHub используйте fine-grained token:

- repository access: только нужный repo;
- permissions: `Contents: Read and write`;
- metadata read access GitHub добавит сам;
- expiration: по вкусу, но лучше не "навсегда", если файл планируется носить на флешке.

Если portable-файл потерялся:

1. Отзовите token.
2. Создайте новый token.
3. Сделайте новый `macaroni-mama.html`.
4. Старый файл считайте компрометированным.

## CLIENT_ID

Для каждого человека делайте отдельный `CLIENT_ID`.

Пример:

```text
MAMA
PAPA
TETA
```

Технически протокол любит четыре символа из смешного алфавита.

Практически `MAMA` тоже прекрасно объясняет, кто пишет.

Если два человека используют один `CLIENT_ID`, в чате начнётся социальная инженерия уровня семейного ужина.

Не надо.

## Как Сделать HTML

1. Скопируйте `messenger.html`.
2. Назовите копию:

```text
macaroni-mama.html
```

3. Откройте копию в текстовом редакторе.
4. Найдите в конце файла строку:

```js
setClientIdText();
```

5. Перед ней вставьте JS-блок.

Важно: это место уже находится внутри основного `<script>`, поэтому дополнительные теги `<script>` не нужны.

```js
(function () {
  var PORTABLE_CLIENT_ID = "MAMA";
  var PORTABLE_PROFILE = {
    clientId: PORTABLE_CLIENT_ID,
    displayName: "Мама",
    language: "ru",
    provider: "github",
    repo: "https://github.com/YOUR_LOGIN/YOUR_REPO",
    token: "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    privacyAccepted: true
  };

  try {
    localStorage.setItem("macaroni.client_id.v1", PORTABLE_CLIENT_ID);
    localStorage.setItem("macaroni.language.v1", PORTABLE_PROFILE.language);
    localStorage.setItem("macaroni.profile.v1", JSON.stringify(PORTABLE_PROFILE));
  } catch (error) {}
}());
```

6. Замените:

- `MAMA` на нужный `CLIENT_ID`;
- `Мама` на имя;
- `YOUR_LOGIN/YOUR_REPO` на репозиторий;
- `github_pat_xxx` на token.

7. Сохраните файл.

## Более Аккуратный Вариант

Если не хотите перезаписывать настройки при каждом открытии, используйте вариант "только при первом запуске":

```js
(function () {
  var PORTABLE_CLIENT_ID = "MAMA";
  var PORTABLE_PROFILE_KEY = "macaroni.profile.v1";

  if (localStorage.getItem(PORTABLE_PROFILE_KEY)) {
    return;
  }

  var PORTABLE_PROFILE = {
    clientId: PORTABLE_CLIENT_ID,
    displayName: "Мама",
    language: "ru",
    provider: "github",
    repo: "https://github.com/YOUR_LOGIN/YOUR_REPO",
    token: "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    privacyAccepted: true
  };

  try {
    localStorage.setItem("macaroni.client_id.v1", PORTABLE_CLIENT_ID);
    localStorage.setItem("macaroni.language.v1", PORTABLE_PROFILE.language);
    localStorage.setItem(PORTABLE_PROFILE_KEY, JSON.stringify(PORTABLE_PROFILE));
  } catch (error) {}
}());
```

Это лучше для нормального использования.

Мама может потом поменять настройки, а файл не будет каждый раз говорить:

> Нет, мама, я лучше знаю.

## Как Проверить

Откройте `macaroni-mama.html` в Chrome / Chromium / Edge.

Проверьте:

- показывается `ID: MAMA`;
- первый экран регистрации не появляется;
- открыт список чатов;
- можно отправить тестовое сообщение;
- через 30 секунд или после кнопки `Обновить` сообщение появляется в git;
- после закрытия и повторного открытия история восстанавливается.

Если видите экран несовместимости:

браузер недостаточно смешной.

Откройте нормальным браузером.

Не поднимайте `localhost`.

`localhost` убивает шутку.

## Ярлык На Рабочем Столе

### macOS

Самый простой способ:

1. Положите `macaroni-mama.html` в папку, где его не удалят.
2. Перетащите файл на Dock или рабочий стол.
3. Переименуйте ярлык в:

```text
Макарошки
```

Если хочется открыть именно Chrome:

1. Откройте файл в Chrome.
2. В адресной строке будет `file:///.../macaroni-mama.html`.
3. Перетащите адрес из Chrome на рабочий стол.

Получится ярлык на локальный HTML.

Технология будущего.

### Windows

Вариант с обычным ярлыком:

1. Положите `macaroni-mama.html` в понятную папку.
2. Правый клик по рабочему столу.
3. `Создать` -> `Ярлык`.
4. В путь укажите:

```text
"C:\Program Files\Google\Chrome\Application\chrome.exe" "C:\Users\USER\Documents\macaroni-mama.html"
```

5. Назовите ярлык:

```text
Макарошки
```

Если Chrome стоит в другом месте, Windows победил, найдите `chrome.exe`.

### Linux

Создайте файл:

```text
macaroni-mama.desktop
```

С содержимым:

```ini
[Desktop Entry]
Type=Application
Name=Макарошки
Exec=chromium /home/USER/macaroni-mama.html
Terminal=false
```

Сделайте исполняемым:

```sh
chmod +x macaroni-mama.desktop
```

Положите на рабочий стол.

Если у вас Linux, вы уже знали, что будет `chmod`.

## Как Обновлять Portable-Файл

Когда вышла новая версия `messenger.html`:

1. Скопируйте новый `messenger.html`.
2. Снова вставьте prefill snippet.
3. Проверьте, что token и `CLIENT_ID` на месте.
4. Отдайте маме новый файл.

История сообщений не живёт в файле.

История живёт в git.

Файл можно заменить.

Git помнит.

## Чего Не Делать

Не отправляйте один и тот же portable-файл нескольким людям.

Не кладите portable-файл в публичный репозиторий.

Не прикрепляйте portable-файл в общий чат.

Не называйте файл:

```text
secret-token-final-final-mama.html
```

Не объясняйте маме GitHub, если она не просила.

## Нормальный Вариант Без Захардкоженного Token

Есть более аккуратный путь:

1. Открыть обычный `messenger.html`.
2. Настроить профиль руками.
3. Экспортировать настройки через Settings.
4. Импортировать настройки на другом устройстве.

Это описано в [settings-export-import.md](settings-export-import.md).

Но portable-файл смешнее.

А проект называется Macaroni Messenger, а не Enterprise Secure Family Communication Suite.
