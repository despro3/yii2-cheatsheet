---
id: authentication
title: Аутентификация
part: security
summary: Компонент user и IdentityInterface — findIdentity, findIdentityByAccessToken, getId, getAuthKey, validateAuthKey; login/logout/isGuest/identity, «запомнить меня» через cookie, тайм-ауты сессии, события beforeLogin/afterLogin, returnUrl, доступ только для авторизованных.
sources: security-authentication
---

:::lead
Аутентификация отвечает на вопрос «кто это?». В Yii за неё отвечает компонент `Yii::$app->user` (класс `yii\web\User`), а сведения о пользователе хранит **identity-класс**, реализующий `IdentityInterface`. Проверка пароля — ваша, остальное (сессия, cookie, тайм-ауты, события) — фреймворка.
:::

## Настройка

```php title="config/web.php"
'components' => [
    'user' => [
        'identityClass' => 'app\models\User',
        'enableAutoLogin' => true,          // «запомнить меня» через cookie
        'loginUrl' => ['site/login'],       // куда отправлять гостей
        'authTimeout' => 3600,              // выйти после часа бездействия (null — пока живёт сессия)
        'absoluteAuthTimeout' => 86400,     // выйти через сутки в любом случае
        // 'enableSession' => false,        // для REST — без сессии, только по токену
        // 'identityCookie' => ['name' => '_identity', 'httpOnly' => true],
    ],
],
```

## Identity-класс

```php title="models/User.php"
namespace app\models;

use yii\db\ActiveRecord;
use yii\web\IdentityInterface;

class User extends ActiveRecord implements IdentityInterface
{
    public static function tableName() { return 'user'; }

    public static function findIdentity($id)
    {
        return static::findOne($id);                          // по ID из сессии
    }

    public static function findIdentityByAccessToken($token, $type = null)
    {
        return static::findOne(['access_token' => $token]);   // для REST/API
    }

    public function getId() { return $this->id; }

    public function getAuthKey() { return $this->auth_key; }   // для cookie «запомнить меня»

    public function validateAuthKey($authKey) { return $this->getAuthKey() === $authKey; }

    // своё: проверка пароля и генерация ключа
    public function validatePassword($password)
    {
        return Yii::$app->security->validatePassword($password, $this->password_hash);
    }

    public function beforeSave($insert)
    {
        if (parent::beforeSave($insert)) {
            if ($this->isNewRecord) {
                $this->auth_key = Yii::$app->security->generateRandomString();
            }
            return true;
        }
        return false;
    }
}
```

:::kv
`findIdentity($id)` — найти пользователя по ID; вызывается при каждом запросе с сессией
`findIdentityByAccessToken($token, $type)` — по токену (REST); `$type` — класс аутентификатора
`getId()` — уникальный ID, кладётся в сессию
`getAuthKey()` — секрет для cookie автологина; храните в БД, генерируйте при регистрации, меняйте при смене пароля
`validateAuthKey($key)` — сверка ключа из cookie
:::

Identity не обязан быть Active Record — подойдёт любой класс (LDAP, внешний API, массив в конфиге).

## Вход и выход

```php
// LoginForm::login()
public function login()
{
    if ($this->validate()) {
        return Yii::$app->user->login($this->getUser(), $this->rememberMe ? 3600 * 24 * 30 : 0);
    }
    return false;
}

// контроллер
public function actionLogin()
{
    if (!Yii::$app->user->isGuest) {
        return $this->goHome();
    }
    $model = new LoginForm();
    if ($model->load(Yii::$app->request->post()) && $model->login()) {
        return $this->goBack();          // на returnUrl или домой
    }
    return $this->render('login', ['model' => $model]);
}

public function actionLogout()
{
    Yii::$app->user->logout();           // logout(false) — не уничтожать сессию целиком
    return $this->goHome();
}
```

`login($identity, $duration)`: при `$duration > 0` и `enableAutoLogin` ставится cookie с ID + authKey на указанный срок. Пароль проверяется в **вашем** коде (`validatePassword`) до вызова `login()`.

## Текущий пользователь

```php
Yii::$app->user->isGuest;                // не вошёл?
Yii::$app->user->id;                     // ID или null
Yii::$app->user->identity;               // объект User или null
Yii::$app->user->identity->username;

Yii::$app->user->getReturnUrl();         // куда вернуть после логина
Yii::$app->user->setReturnUrl($url);
Yii::$app->user->loginRequired();        // редирект на loginUrl с сохранением returnUrl
// 403 вместо редиректа — если клиент по заголовку Accept не ждёт HTML (например, просит JSON)
Yii::$app->user->switchIdentity($newUser, $duration);   // сменить пользователя (например, «войти как»)
```

`identity` загружается лениво один раз за запрос — `findIdentity()` вызовется только если к нему обратились.

## Доступ только для вошедших

```php
public function behaviors()
{
    return [
        'access' => [
            'class' => AccessControl::class,
            'only' => ['create', 'update', 'delete'],
            'rules' => [
                ['allow' => true, 'roles' => ['@']],   // '@' — аутентифицированные, '?' — гости
            ],
        ],
    ];
}
```

Гость получит редирект на `loginUrl`; после входа `goBack()` вернёт его туда, откуда он пришёл. Подробнее — в [авторизации](authorization).

## Как это работает под капотом

:::steps
1. Первый запрос: `user->login()` кладёт `getId()` в сессию (`__id`) и, при `$duration`, ставит identity-cookie `[id, authKey, duration]`.
2. Следующие запросы: `user->identity` читает ID из сессии → `findIdentity($id)`.
3. Сессии нет, но есть cookie: сравнивается `authKey` через `validateAuthKey()` → авто-вход, сессия продлевается (`autoRenewCookie`).
4. `authTimeout`/`absoluteAuthTimeout` проверяются на каждом запросе; истёк — `logout()`.
5. REST без сессии (`enableSession = false`): `findIdentityByAccessToken()` вызывает аутентификатор из фильтров (`HttpBearerAuth` и др.).
:::

## События

```php
'user' => [
    'on afterLogin' => function (\yii\web\UserEvent $event) {
        $event->identity->updateAttributes(['last_login_at' => time()]);
    },
],
```

:::kv
`beforeLogin` — `$event->isValid = false` отменяет вход; `$event->identity`, `$event->cookieBased`, `$event->duration`
`afterLogin` — вход выполнен
`beforeLogout` / `afterLogout` — аналогично
:::

> [!WARNING] Безопасность authKey
> `getAuthKey()` — фактически второй пароль в cookie. Генерируйте его криптографически (`generateRandomString()`), никогда не возвращайте константу, меняйте при смене пароля и выходе «со всех устройств». `access_token` для API — тоже случайная строка, не хэш ID.

:::quiz Проверь себя
Q: Какие методы требует `IdentityInterface`?
A: `findIdentity()`, `findIdentityByAccessToken()`, `getId()`, `getAuthKey()`, `validateAuthKey()`.
Q: Кто проверяет пароль при входе — фреймворк или ваш код?
A: Ваш код: `Yii::$app->security->validatePassword()` до вызова `Yii::$app->user->login()`.
Q: Что нужно для работы «запомнить меня»?
A: `enableAutoLogin = true`, `duration > 0` в `login()` и корректные `getAuthKey()`/`validateAuthKey()`.
Q: Чем `authTimeout` отличается от `absoluteAuthTimeout`?
A: Первый — выход после N секунд бездействия (продлевается каждым запросом), второй — через N секунд после входа независимо от активности.
Q: Как отправить гостя на страницу входа и вернуть обратно после?
A: `Yii::$app->user->loginRequired()` (или `AccessControl`) сохраняет `returnUrl`; после входа — `$this->goBack()`.
:::
