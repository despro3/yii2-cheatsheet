---
id: security
title: Безопасность
part: security
summary: Компонент security — хэширование паролей (password_hash/bcrypt), генерация случайных данных, шифрование и подпись (encryptByPassword/encryptByKey, hashData); защита от SQL-инъекций, XSS, CSRF, подделки файлов и утечек конфигурации; практики безопасной настройки сервера и cookie.
sources: security-overview, security-passwords, security-cryptography, security-best-practices
---

:::lead
Yii закрывает типовые дыры по умолчанию: параметры в SQL, CSRF-токены в формах, подписанные cookie, экранирование в `Html::encode()`. Ваша часть — не отключать защиту, правильно хранить пароли и не доверять входным данным. Всё криптографическое — в `Yii::$app->security`.
:::

## Пароли

```php
// при регистрации / смене пароля
$hash = Yii::$app->security->generatePasswordHash($password);   // bcrypt, соль внутри — хранить в password_hash
// при входе
if (Yii::$app->security->validatePassword($password, $hash)) { … }
```

Никаких `md5()`/`sha1()`: bcrypt медленный намеренно (`passwordHashCost`, по умолчанию 13). Пароль в открытом виде не хранится и не логируется. Для сброса пароля — случайный токен с ограниченным сроком (`generateRandomString()` + время).

## Случайные данные

```php
$key = Yii::$app->security->generateRandomString();     // 32 символа [A-Za-z0-9_-] — токены, authKey, соли
$key = Yii::$app->security->generateRandomString(64);
$bytes = Yii::$app->security->generateRandomKey(32);    // сырые байты
```

Используют `random_bytes()` — криптографически стойко. `rand()`/`mt_rand()`/`uniqid()` для секретов не годятся.

## Шифрование и подпись

```php
// шифрование по паролю (медленнее: пароль растягивается через PBKDF2)
$encrypted = Yii::$app->security->encryptByPassword($data, $secretKey);
$data = Yii::$app->security->decryptByPassword($encrypted, $secretKey);

// шифрование по ключу (ключ — случайные байты подходящей длины)
$encrypted = Yii::$app->security->encryptByKey($data, $key, $info);   // $info — контекст (например, ID пользователя)
$data = Yii::$app->security->decryptByKey($encrypted, $key, $info);

// подпись: гарантирует, что данные не изменены
$signed = Yii::$app->security->hashData($data, $key);      // hash + data
$data = Yii::$app->security->validateData($signed, $key);   // данные или false

// производные ключи
Yii::$app->security->hkdf('sha256', $inputKey, $salt, $info, $length);
Yii::$app->security->pbkdf2('sha256', $password, $salt, $iterations, $length);
Yii::$app->security->compareString($expected, $actual);     // сравнение за постоянное время
Yii::$app->security->maskToken($token); unmaskToken();       // защита от BREACH — так работают CSRF-токены
```

Шифрование — AES-128-CBC с HMAC (шифр настраивается: `cipher`). Ключи храните вне репозитория (переменные окружения, файлы вне webroot).

## Типичные угрозы и защита

### SQL-инъекции

```php
// плохо
$db->createCommand("SELECT * FROM user WHERE username = '$username'");
// хорошо
$db->createCommand('SELECT * FROM user WHERE username = :username', [':username' => $username]);
User::find()->where(['username' => $username]);            // Query Builder и AR привязывают сами
User::findOne(['id' => (int)$id]);                         // а не findOne($id) с пользовательскими данными
```

Имена столбцов и таблиц параметрами не передаются — только белый список.

### XSS

```php
<?= Html::encode($user->name) ?>                            // всегда для «чужого» текста
<?= HtmlPurifier::process($post->body) ?>                    // если нужен HTML (медленно — кэшируйте)
<?= Yii::$app->formatter->asHtml($post->body) ?>             // то же через форматтер
```

`GridView`/`DetailView` экранируют по умолчанию (формат `text`); `raw` — только для доверенного HTML. Twig и Smarty — тоже экранируют автоматически.

### CSRF

Включена по умолчанию: `ActiveForm` и `Html::beginForm()` добавляют скрытое поле `_csrf`, `yii.js` шлёт заголовок `X-CSRF-Token` в AJAX. Правила:

- **GET не меняет состояние** — удаление через ссылку `?action=delete` уязвимо; используйте POST (`data-method="post"`) или `VerbFilter`.
- Отключать только точечно: `$enableCsrfValidation = false` в контроллере или `beforeAction()` для webhook-эндпоинтов.
- Свой AJAX-код: `yii.getCsrfToken()` или мета-теги `<?= Html::csrfMetaTags() ?>`.

```php
public function beforeAction($action)
{
    if ($action->id === 'webhook') {
        $this->enableCsrfValidation = false;
    }
    return parent::beforeAction($action);
}
```

### Файлы

- Не отдавать файлы по пути из запроса (`../../etc/passwd`); проверяйте `realpath()` и белый список.
- Загрузки — только в папку без выполнения PHP; расширение проверять валидатором `file` с `checkExtensionByMimeType`; имя генерировать своё.
- Скрывать листинг каталогов и точечные файлы в конфигурации сервера.

### Утечки через отладку

- `YII_DEBUG = false` и `YII_ENV = 'prod'` на production: страница ошибки не покажет стек и код.
- Модули `debug` и `gii` — только в dev; в production они опасны даже с `allowedIPs`.
- Логи не должны содержать паролей и токенов.

## Cookie и сессии

- `cookieValidationKey` в конфигурации `request` — обязателен, длинный, случайный, вне репозитория; иначе cookie не подписаны.
- Cookie-флаги: `httpOnly` (по умолчанию `true`), `secure` для HTTPS, `sameSite` (2.0.21): `'sameSite' => Cookie::SAME_SITE_LAX`.
- Сессии: не хранить в PHP-файлах на shared-хостинге — `DbSession`/`CacheSession`; менять ID при входе (`Yii::$app->session->regenerateID()` вызывается фреймворком при `login()`).
- Токены в URL не передавать: попадают в логи и Referer.

## Настройка сервера

```php
// проверка Host-заголовка: иначе подмена в ссылках и письмах
'request' => [
    'hostInfo' => 'https://example.com',       // жёстко
    // или 'trustedHosts' => ['example.com', '*.example.com'],
],
```

- Веб-сервер должен отдавать только `web/`; `config/`, `runtime/`, `vendor/` — вне document root (так и в шаблонах).
- HTTPS везде; за прокси — `trustedHosts` + `secureHeaders`, чтобы `isSecureConnection` и IP определялись верно.
- `php.ini`: `expose_php = Off`, `display_errors = Off` на production.
- Обновляйте фреймворк и расширения — `composer outdated`; следите за уязвимостями.

## Чек-лист перед релизом

:::cards
- **Пароли** — `generatePasswordHash()` / `validatePassword()`, никакого md5
- **Секреты** — `cookieValidationKey`, ключи шифрования и БД вне git
- **Ввод** — валидация всех моделей, `Html::encode()` в выводе, параметры в SQL
- **CSRF** — включена; действия, меняющие данные, — только POST/DELETE
- **Ошибки** — `YII_DEBUG=false`, `YII_ENV=prod`, `errorAction` настроен
- **Файлы** — загрузки вне webroot или без исполнения, имена свои
- **Cookies** — `httpOnly`, `secure`, `sameSite`; сессии не в `/tmp`
- **Хост** — `hostInfo`/`trustedHosts`, HTTPS, актуальные версии зависимостей
:::

:::quiz Проверь себя
Q: Как правильно сохранить пароль пользователя?
A: `Yii::$app->security->generatePasswordHash($password)` (bcrypt) в `password_hash`; проверять `validatePassword()`.
Q: Почему `User::findOne($_GET['id'])` небезопасен?
A: Массив в `id` превращается в условие; приводите к `int` или пишите `findOne(['id' => $id])`.
Q: Где нужен `Html::encode()`?
A: При выводе любых данных, пришедших от пользователя или из БД, если это не заведомо безопасный HTML.
Q: Как отключить CSRF-проверку для одного действия-вебхука?
A: В `beforeAction()` контроллера: `$this->enableCsrfValidation = false` для нужного `$action->id`.
Q: Чем `encryptByKey()` отличается от `encryptByPassword()`?
A: По ключу — быстрее, ключ должен быть случайным и достаточной длины; по паролю — пароль растягивается через PBKDF2, поэтому медленнее.
:::
