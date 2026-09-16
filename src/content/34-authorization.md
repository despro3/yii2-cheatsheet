---
id: authorization
title: Авторизация: ACF и RBAC
part: security
summary: Фильтр AccessControl с правилами allow/deny по ролям, IP, методам и колбэкам; RBAC — роли, разрешения, иерархия, правила (Rule), PhpManager и DbManager, консольная инициализация, назначение ролей, проверка can(), роли по умолчанию.
sources: security-authorization
---

:::lead
Аутентификация сказала, *кто* пользователь; авторизация решает, *что ему можно*. Два инструмента: **ACF** (Access Control Filter) — простые правила у контроллера, и **RBAC** — управление доступом на основе ролей с иерархией и правилами, когда прав много и они зависят от данных.
:::

## Access Control Filter

```php
use yii\filters\AccessControl;

class SiteController extends Controller
{
    public function behaviors()
    {
        return [
            'access' => [
                'class' => AccessControl::class,
                'only' => ['login', 'logout', 'signup'],   // к каким действиям применять
                'rules' => [
                    [
                        'allow' => true,
                        'actions' => ['login', 'signup'],
                        'roles' => ['?'],                   // только гости
                    ],
                    [
                        'allow' => true,
                        'actions' => ['logout'],
                        'roles' => ['@'],                   // только вошедшие
                    ],
                ],
                'denyCallback' => function ($rule, $action) {
                    throw new \Exception('Вам сюда нельзя');
                },
            ],
        ];
    }
}
```

Правила проверяются **сверху вниз до первого совпадения**. Совпало `allow` — пропустить, `deny` — запретить. Ни одно не совпало — **запретить** (гостю — редирект на логин, вошедшему — 403).

### Опции правила

:::kv
`allow` — `true` разрешить / `false` запретить
`actions` — ID действий; пусто — все
`controllers` — ID контроллеров (с модулем: `admin/user`); пусто — текущий
`roles` — `?` гость, `@` аутентифицирован, иначе — роль/разрешение RBAC (`Yii::$app->user->can()`)
`roleParams` — параметры для `can()` (массив или замыкание)
`ips` — IP клиента, с `*` в конце (`192.168.*`)
`verbs` — HTTP-методы (`GET`, `POST`)
`matchCallback` — `function ($rule, $action)` — любое условие
`denyCallback` — что делать при запрете (переопределяет общий)
:::

```php
[
    'allow' => true,
    'actions' => ['special-callback'],
    'matchCallback' => function ($rule, $action) {
        return date('d-m') === '31-10';   // только в Хэллоуин
    },
],
[
    'allow' => true,
    'actions' => ['update'],
    'roles' => ['updatePost'],
    'roleParams' => function ($rule) {
        return ['post' => Post::findOne(['id' => Yii::$app->request->get('id')])];
    },
],
```

## RBAC

Модель: **разрешение** (permission) — действие («создать пост»), **роль** (role) — набор разрешений и других ролей, **правило** (rule) — дополнительная проверка с параметрами («автор ли пользователь этого поста»). Пользователю назначаются роли/разрешения; проверка — `Yii::$app->user->can('updatePost', ['post' => $post])`.

### Настройка

```php
'components' => [
    'authManager' => [
        'class' => 'yii\rbac\DbManager',     // таблицы: auth_item, auth_item_child, auth_assignment, auth_rule
        // 'class' => 'yii\rbac\PhpManager', // файлы в @app/rbac — для небольших статичных схем
        // 'defaultRoles' => ['guest'],
        // 'cache' => 'cache',               // кэшировать иерархию (DbManager)
    ],
],
```

Для `DbManager`: `./yii migrate --migrationPath=@yii/rbac/migrations`. Компонент должен быть в **обеих** конфигурациях — web и console.

### Построение иерархии

```php title="commands/RbacController.php"
class RbacController extends \yii\console\Controller
{
    public function actionInit()
    {
        $auth = Yii::$app->authManager;
        $auth->removeAll();

        // разрешения
        $createPost = $auth->createPermission('createPost');
        $createPost->description = 'Создание постов';
        $auth->add($createPost);

        $updatePost = $auth->createPermission('updatePost');
        $auth->add($updatePost);

        // роли
        $author = $auth->createRole('author');
        $auth->add($author);
        $auth->addChild($author, $createPost);

        $admin = $auth->createRole('admin');
        $auth->add($admin);
        $auth->addChild($admin, $updatePost);
        $auth->addChild($admin, $author);          // admin наследует всё от author

        // назначения (обычно — при регистрации)
        $auth->assign($author, 2);
        $auth->assign($admin, 1);
    }
}
```

```bash
./yii rbac/init
```

Иерархия: `admin` → `author` → `createPost`; `admin` → `updatePost`. `can('createPost')` для admin вернёт `true` через цепочку.

### Правила — доступ с учётом данных

«Автор может редактировать *свой* пост»:

```php title="rbac/AuthorRule.php"
namespace app\rbac;

use yii\rbac\Rule;

class AuthorRule extends Rule
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
$updateOwnPost->description = 'Редактирование своего поста';
$updateOwnPost->ruleName = $rule->name;
$auth->add($updateOwnPost);

$auth->addChild($updateOwnPost, $updatePost);   // updateOwnPost «использует» updatePost
$auth->addChild($author, $updateOwnPost);
```

```php
// проверка
if (Yii::$app->user->can('updatePost', ['post' => $post])) { … }
```

Для автора цепочка `author → updateOwnPost(правило) → updatePost` — правило проверит `createdBy`. Для admin путь `admin → updatePost` без правила — можно всегда.

### Назначение ролей

```php
$auth->assign($auth->getRole('author'), $user->id);       // при регистрации — в afterSave или в контроллере
$auth->revoke($role, $userId);
$auth->revokeAll($userId);
$auth->getRolesByUser($userId);
$auth->getPermissionsByUser($userId);
$auth->getUserIdsByRole('admin');
$auth->checkAccess($userId, 'updatePost', $params);        // то же, что user->can(), но для любого ID
```

### Роли по умолчанию

Роль, которая есть у всех (в т.ч. гостей) без записи в `auth_assignment` — через `defaultRoles` и правило:

```php
class UserGroupRule extends Rule
{
    public $name = 'userGroup';

    public function execute($user, $item, $params)
    {
        if (Yii::$app->user->isGuest) return false;
        $group = Yii::$app->user->identity->group;
        return $item->name === 'admin' ? $group == 1 : ($item->name === 'author' ? $group == 1 || $group == 2 : false);
    }
}

// authManager: 'defaultRoles' => ['admin', 'author'],
```

Так роль определяется полем `group` пользователя, а не таблицей назначений.

## Проверка в коде

```php
if (Yii::$app->user->can('createPost')) { … }              // роль или разрешение
if (Yii::$app->user->can('updatePost', ['post' => $post])) { … }
if (!Yii::$app->user->can('admin')) {
    throw new \yii\web\ForbiddenHttpException('Нет доступа');
}

// в представлении
<?php if (Yii::$app->user->can('updatePost', ['post' => $model])): ?>
    <?= Html::a('Редактировать', ['update', 'id' => $model->id]) ?>
<?php endif ?>
```

`can()` для гостя (`user->id === null`) проверяет только `defaultRoles`.

## ACF или RBAC?

:::cols
=== ACF
- права зависят только от «гость/вошёл», IP, метода, действия;
- маленькое приложение, 1–2 роли;
- нужно быстро закрыть контроллер.
=== RBAC
- много ролей и разрешений, иерархия;
- доступ зависит от данных (свой/чужой объект);
- права меняются администратором без деплоя (DbManager).
:::

Они совместимы: в `roles` правила ACF пишут имена RBAC-элементов, и фильтр вызовет `can()`.

> [!TIP]
> Проверяйте **разрешения**, а не роли: `can('updatePost')` переживёт переименование ролей и появление новых. Роли — для назначения, разрешения — для проверки.

:::quiz Проверь себя
Q: Что произойдёт, если ни одно правило ACF не совпало с запросом?
A: Доступ запрещён: гость — редирект на `loginUrl`, вошедший — `ForbiddenHttpException` (403).
Q: Что означают роли `?` и `@` в правилах ACF?
A: `?` — неаутентифицированный пользователь, `@` — аутентифицированный.
Q: В чём разница между ролью и разрешением в RBAC?
A: Разрешение — конкретное действие; роль — набор разрешений и ролей. Проверять лучше разрешения, назначать — роли.
Q: Зачем нужен класс `Rule`?
A: Для условий, зависящих от параметров: например, `updateOwnPost` проверяет, что автор поста — текущий пользователь.
Q: Как дать роль всем пользователям без записи в `auth_assignment`?
A: Через `defaultRoles` менеджера и правило, определяющее роль по данным пользователя.
:::
