---
id: security
title: Безопасность
icon: 🔐
summary: Аутентификация, ACF и RBAC, пароли, криптография, защита от SQL-инъекций, XSS, CSRF.
sources: security-overview, security-authentication, security-authorization, security-passwords, security-cryptography, security-best-practices
---

# Безопасность

Два базовых принципа: **фильтровать ввод** и **экранировать вывод**.

## Аутентификация

```php
'components' => [
    'user' => [
        'identityClass' => 'app\models\User',
        'enableAutoLogin' => true,        // «запомнить меня» через cookie
        'enableSession' => true,          // false для stateless REST API
        'loginUrl' => ['site/login'],
        'authTimeout' => 3600,
    ],
],
```

Класс идентификации реализует `yii\web\IdentityInterface`:

```php
class User extends ActiveRecord implements \yii\web\IdentityInterface
{
    public static function findIdentity($id) { return static::findOne($id); }

    public static function findIdentityByAccessToken($token, $type = null)
    {
        return static::findOne(['access_token' => $token]);
    }

    public function getId() { return $this->id; }
    public function getAuthKey() { return $this->auth_key; }
    public function validateAuthKey($authKey) { return $this->getAuthKey() === $authKey; }

    public function beforeSave($insert)
    {
        if (!parent::beforeSave($insert)) { return false; }
        if ($this->isNewRecord) {
            $this->auth_key = Yii::$app->security->generateRandomString();
        }
        return true;
    }
}
```

```php
Yii::$app->user->identity;     // объект identity или null
Yii::$app->user->id;
Yii::$app->user->isGuest;

Yii::$app->user->login($identity, 3600 * 24 * 30);   // второй аргумент — срок cookie
Yii::$app->user->logout();          // logout(false) — сохранить данные сессии
Yii::$app->user->loginRequired();
```

События: `EVENT_BEFORE_LOGIN` (можно отменить через `$event->isValid = false`),
`EVENT_AFTER_LOGIN`, `EVENT_BEFORE_LOGOUT`, `EVENT_AFTER_LOGOUT`.

> Важно: не путайте `app\models\User` (identity — логика и хранилище пользователя) и
> `yii\web\User` (компонент, управляющий состоянием аутентификации).

## Авторизация: ACF

```php
use yii\filters\AccessControl;

public function behaviors()
{
    return [
        'access' => [
            'class' => AccessControl::class,
            'only' => ['login', 'logout', 'signup', 'admin'],
            'denyCallback' => fn ($rule, $action) => throw new \yii\web\ForbiddenHttpException('Нет доступа'),
            'rules' => [
                ['allow' => true, 'actions' => ['login', 'signup'], 'roles' => ['?']],   // гости
                ['allow' => true, 'actions' => ['logout'], 'roles' => ['@']],            // авторизованные
                ['allow' => true, 'actions' => ['admin'], 'roles' => ['admin'],          // роль RBAC
                 'ips' => ['192.168.*'], 'verbs' => ['GET', 'POST'],
                 'matchCallback' => fn ($rule, $action) => date('N') < 6],
            ],
        ],
    ];
}
```

Правила проверяются сверху вниз до первого совпадения; если ни одно не подошло — доступ
запрещён. Гостя по умолчанию отправят на `loginUrl`, авторизованный получит 403.
Свойства правила: `allow`, `actions`, `controllers`, `roles`, `permissions`, `ips`,
`verbs`, `matchCallback`, `denyCallback`.

## Авторизация: RBAC

```php
'components' => [
    'authManager' => [
        'class' => 'yii\rbac\DbManager',        // или yii\rbac\PhpManager (файлы в @app/rbac)
        'defaultRoles' => ['guest'],
    ],
],
```

Для `DbManager` нужны таблицы: `yii migrate --migrationPath=@yii/rbac/migrations`
(`auth_item`, `auth_item_child`, `auth_assignment`, `auth_rule`).

```php
// консольная команда инициализации
$auth = Yii::$app->authManager;

$createPost = $auth->createPermission('createPost');
$createPost->description = 'Создание поста';
$auth->add($createPost);

$updatePost = $auth->createPermission('updatePost');
$auth->add($updatePost);

$author = $auth->createRole('author');
$auth->add($author);
$auth->addChild($author, $createPost);

$admin = $auth->createRole('admin');
$auth->add($admin);
$auth->addChild($admin, $updatePost);
$auth->addChild($admin, $author);       // роль включает другую роль

$auth->assign($author, 2);              // ID пользователя из getId()
$auth->assign($admin, 1);
```

**Правило** (rule) — дополнительная проверка во время авторизации:

```php
namespace app\rbac;

class AuthorRule extends \yii\rbac\Rule
{
    public $name = 'isAuthor';

    public function execute($user, $item, $params)
    {
        return isset($params['post']) ? $params['post']->createdBy == $user : false;
    }
}
```

```php
$rule = new \app\rbac\AuthorRule();
$auth->add($rule);

$updateOwnPost = $auth->createPermission('updateOwnPost');
$updateOwnPost->ruleName = $rule->name;
$auth->add($updateOwnPost);
$auth->addChild($updateOwnPost, $updatePost);
$auth->addChild($author, $updateOwnPost);
```

Проверка доступа:

```php
if (Yii::$app->user->can('createPost')) { /* ... */ }
if (Yii::$app->user->can('updatePost', ['post' => $post])) { /* ... */ }
Yii::$app->authManager->checkAccess($userId, 'updatePost', ['post' => $post]);
```

**Роли по умолчанию** (`defaultRoles`) назначаются всем неявно — обычно вместе с правилом,
которое определяет принадлежность пользователя к роли (например, по колонке `group`).

> Совет: если права выдаются «пакетом» на весь CRUD, проще завести одно разрешение
> `managePost` и проверять его в `beforeAction()`, а не расписывать правило на каждое
> действие.

## Пароли

```php
$hash = Yii::$app->security->generatePasswordHash($password);   // bcrypt
if (Yii::$app->security->validatePassword($password, $hash)) { /* ok */ }
```

Никогда не `md5()`/`sha1()` — они подбираются перебором на современном железе.

## Криптография

```php
$security = Yii::$app->security;

$security->generateRandomString(32);        // токены сброса пароля и т.п.
$security->generateRandomKey(32);

$encrypted = $security->encryptByPassword($data, $password);
$data = $security->decryptByPassword($encrypted, $password);
$encrypted = $security->encryptByKey($data, $key);
$data = $security->decryptByKey($encrypted, $key);

$signed = $security->hashData($data, $secretKey);         // подпись целостности
$data = $security->validateData($signed, $secretKey);     // false, если подделали

$security->compareString($expected, $actual);             // сравнение без утечки по времени
```

## Типовые угрозы и защита

| Угроза | Защита в Yii |
|---|---|
| SQL-инъекция | подготовленные запросы: AR, `where(['col' => $v])`, `bindValue()`. Имена столбцов — только по белому списку, экранирование `[[col]]`, `{{table}}` |
| XSS | `Html::encode()` для текста, `HtmlPurifier::process()` для HTML от пользователя |
| CSRF | включено по умолчанию: `Html::csrfMetaTags()` в layout, скрытое поле в `ActiveForm`; GET не должен менять состояние |
| Массовое присвоение лишних полей | сценарии и `scenarios()`, `safe`-атрибуты |
| Подделка cookie | `request.cookieValidationKey` + валидация кук |
| Утечка внутренностей | `YII_DEBUG = false` и `YII_ENV = 'prod'` на продакшене |
| Gii/Debug на проде | не включать вообще; в крайнем случае — `allowedIPs` |
| Доступ к файлам вне `web/` | корень веб-сервера — только `web/` |
| Host-header атака | настройка веб-сервера или фильтр `yii\filters\HostControl` |
| Незащищённый транспорт | HTTPS/TLS, `Cookie::secure`, `sameSite` |

```php
// глобальный фильтр допустимых хостов
'as hostControl' => [
    'class' => 'yii\filters\HostControl',
    'allowedHosts' => ['example.com', '*.example.com'],
    'fallbackHostInfo' => 'https://example.com',
],
```

```php
// белый список вместо подстановки имени столбца из запроса
public function actionList($orderBy = null)
{
    if (!in_array($orderBy, ['name', 'status'], true)) {
        throw new \yii\web\BadRequestHttpException('Недопустимая сортировка.');
    }
}
```

За reverse proxy обязательно настройте `request.trustedHosts`, иначе IP и схема
соединения будут подделываемыми.
