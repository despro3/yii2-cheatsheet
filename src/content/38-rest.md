---
id: rest
title: REST API — быстрый старт
part: rest
summary: ActiveController за пять минут — контроллер, UrlRule с pluralize, parsers/formatters; ресурсы и fields()/extraFields(), ссылки HATEOAS; контроллеры yii\rest\Controller, actions() и checkAccess(); маршрутизация UrlRule с except/extraPatterns; Yii как микрофреймворк.
sources: rest-quick-start, rest-resources, rest-controllers, rest-routing, tutorial-yii-as-micro-framework
---

:::lead
`yii\rest` даёт CRUD-API поверх Active Record за десяток строк: `ActiveController` + одно правило `UrlRule` — и `GET /users`, `POST /users`, `PATCH /users/1` работают с пагинацией, сортировкой, валидацией, JSON/XML по `Accept`, кодами ошибок и HATEOAS-ссылками.
:::

## Быстрый старт

```php title="controllers/UserController.php"
namespace app\controllers;

use yii\rest\ActiveController;

class UserController extends ActiveController
{
    public $modelClass = 'app\models\User';
}
```

```php title="config/web.php"
'components' => [
    'request' => [
        'parsers' => ['application/json' => 'yii\web\JsonParser'],   // принимать JSON в теле
    ],
    'urlManager' => [
        'enablePrettyUrl' => true,
        'enableStrictParsing' => true,
        'showScriptName' => false,
        'rules' => [
            ['class' => 'yii\rest\UrlRule', 'controller' => 'user'],
        ],
    ],
],
```

Готово. Что получилось:

| Запрос | Действие | Результат |
|---|---|---|
| `GET /users` | `index` | список постранично, заголовки `X-Pagination-*`, `Link` |
| `HEAD /users` | `index` | только заголовки |
| `POST /users` | `create` | 201 + созданная модель; при ошибках 422 + список ошибок |
| `GET /users/123` | `view` | модель |
| `PUT`, `PATCH /users/123` | `update` | обновлённая модель |
| `DELETE /users/123` | `delete` | 204 |
| `OPTIONS /users` | `options` | разрешённые методы в `Allow` |
| `GET /users?fields=id,email&expand=profile` | `index` | выбор полей и связей |

```bash
curl -i -H "Accept: application/json" "http://localhost/users?page=2&per-page=10&sort=-id"
curl -X POST -H "Content-Type: application/json" -d '{"username":"sam","email":"s@x.io"}' http://localhost/users
```

Ответ — JSON по умолчанию, XML при `Accept: application/xml`. Ошибки валидации — HTTP 422 с массивом `[{field, message}]`.

## Ресурсы

Ресурс — объект `Arrayable` (все модели и AR). Что попадёт в ответ, решают:

```php
class User extends ActiveRecord
{
    public function fields()
    {
        $fields = parent::fields();               // все атрибуты
        // 🔐 убрать секреты
        unset($fields['auth_key'], $fields['password_hash'], $fields['password_reset_token']);
        $fields['full_name'] = function ($model) { return $model->first_name . ' ' . $model->last_name; };
        $fields['email_short'] = 'email';         // переименовать
        return $fields;
    }

    public function extraFields()
    {
        return ['profile', 'posts'];              // связи — только по ?expand=profile,posts
    }
}
```

`fields()` — по умолчанию в ответе; `extraFields()` — по запросу. Клиент управляет: `?fields=id,email` сужает, `?expand=profile` добавляет; можно вложенно: `expand=posts.comments`, `fields=posts.title`.

> [!GOTCHA]
> `fields()` у AR по умолчанию отдаёт **все** столбцы, включая `password_hash`. Переопределяйте в каждой модели, которая выходит наружу, или делайте отдельный ресурс-класс.

### Ссылки (HATEOAS)

```php
use yii\web\Link;
use yii\web\Linkable;
use yii\helpers\Url;

class User extends ActiveRecord implements Linkable
{
    public function getLinks()
    {
        return [
            Link::REL_SELF => Url::to(['user/view', 'id' => $this->id], true),
            'edit' => Url::to(['user/view', 'id' => $this->id], true),
        ];
    }
}
// в ответе появится: "_links": {"self": {"href": "http://…/users/1"}, ...}
```

### Коллекции

Действие `index` возвращает [провайдер данных](data-providers) → сериализатор выводит элементы, а пагинацию — в заголовки `X-Pagination-Total-Count`, `X-Pagination-Page-Count`, `X-Pagination-Current-Page`, `X-Pagination-Per-Page` и `Link`. Чтобы метаданные попали в тело:

```php
public $serializer = [
    'class' => 'yii\rest\Serializer',
    'collectionEnvelope' => 'items',   // {"items": [...], "_links": {...}, "_meta": {...}}
];
```

## Контроллеры

`yii\rest\Controller` — базовый, без привязки к модели; `ActiveController` — с готовыми CRUD-действиями. Оба уже подключают фильтры: `ContentNegotiator` (формат по `Accept`), `VerbFilter`, `AuthMethod` (если настроен), `RateLimiter`.

```php
class UserController extends ActiveController
{
    public $modelClass = 'app\models\User';

    public function actions()
    {
        $actions = parent::actions();
        unset($actions['delete'], $actions['create']);                       // убрать
        $actions['index']['prepareDataProvider'] = [$this, 'prepareDataProvider'];   // свой провайдер
        return $actions;
    }

    public function prepareDataProvider()
    {
        return new ActiveDataProvider([
            'query' => User::find()->where(['status' => 1]),
            'pagination' => ['pageSize' => 20],
        ]);
    }

    public function checkAccess($action, $model = null, $params = [])
    {
        if ($action === 'update' || $action === 'delete') {
            if ($model->created_by !== \Yii::$app->user->id) {
                throw new \yii\web\ForbiddenHttpException('Можно менять только свои записи');
            }
        }
    }
}
```

:::kv
`actions()` — `index` (IndexAction), `view`, `create`, `update`, `delete`, `options`; у `index` — `dataFilter` (2.0.13) для фильтрации коллекций
`checkAccess($action, $model, $params)` — вызывается каждым действием; бросайте `ForbiddenHttpException`
`createScenario`, `updateScenario` — сценарии моделей для create/update
`serializer` — как превращать модели в массив
`verbs()` — карта действий → HTTP-методов для `VerbFilter`
:::

Своё действие — обычный метод с `return $data`; массив/объект сериализуются автоматически:

```php
public function actionSearch($q)
{
    return new ActiveDataProvider(['query' => User::find()->where(['like', 'username', $q])]);
}
```

## Маршрутизация

`yii\rest\UrlRule` создаёт набор правил под контроллер:

```php
'rules' => [
    ['class' => 'yii\rest\UrlRule', 'controller' => 'user'],
    ['class' => 'yii\rest\UrlRule', 'controller' => ['user', 'post']],         // несколько
    ['class' => 'yii\rest\UrlRule', 'controller' => ['v1/user', 'v1/post']],   // в модуле
    [
        'class' => 'yii\rest\UrlRule',
        'controller' => ['users' => 'user'],       // свой URL-сегмент → контроллер
        'pluralize' => false,                      // не добавлять -s (по умолчанию user → users)
        'prefix' => 'api',                         // /api/users
        'except' => ['delete', 'create'],          // не создавать эти маршруты
        'only' => ['index', 'view'],
        'extraPatterns' => [                       // свои
            'GET search' => 'search',              // GET /users/search → user/search
            'POST {id}/activate' => 'activate',
        ],
        'tokens' => ['{id}' => '<id:\\d[\\d,]*>'], // формат ID: 1 или 1,2,3
    ],
],
```

Множественное число — через `Inflector::pluralize()` (`person` → `people`); нестандартное задавайте картой. Порядок: маршруты REST обычно выше остальных правил, `enableStrictParsing = true` отсекает всё, что не описано.

## Yii как микрофреймворк

Не обязательно брать шаблон приложения — можно собрать API из `composer require yiisoft/yii2` и одного файла:

```php title="index.php"
<?php
require __DIR__ . '/vendor/autoload.php';
require __DIR__ . '/vendor/yiisoft/yii2/Yii.php';

$config = [
    'id' => 'micro-app',
    'basePath' => __DIR__,
    'controllerNamespace' => 'micro\controllers',
    'aliases' => ['@micro' => __DIR__],
    'components' => [
        'db' => ['class' => 'yii\db\Connection', 'dsn' => 'sqlite:@micro/db.sqlite'],
        'urlManager' => [
            'enablePrettyUrl' => true, 'showScriptName' => false, 'enableStrictParsing' => true,
            'rules' => [['class' => 'yii\rest\UrlRule', 'controller' => 'post']],
        ],
    ],
];

(new yii\web\Application($config))->run();
```

`PostController extends ActiveController` с `$modelClass` — и `GET /posts` уже отвечает. Плюс минимальная модель, миграция через `./yii` — по сути тот же фреймворк, но без лишних папок. Хорошо для маленьких сервисов и чтобы понять, как устроено приложение.

:::quiz Проверь себя
Q: Что нужно, чтобы `POST /users` с телом JSON заполнил модель?
A: Парсер запроса: `'parsers' => ['application/json' => 'yii\web\JsonParser']` в компоненте `request`.
Q: Как скрыть `password_hash` из ответа API?
A: Переопределить `fields()` модели и убрать чувствительные поля; связи вынести в `extraFields()`.
Q: Чем отличаются `fields()` и `extraFields()`?
A: `fields()` возвращаются всегда (если клиент не сузил `?fields=`), `extraFields()` — только по `?expand=`.
Q: Где проверять, что пользователь может изменить конкретную запись?
A: В `checkAccess($action, $model)` контроллера; бросить `ForbiddenHttpException`.
Q: Как получить URL `/api/users` вместо `/users`?
A: Опция `prefix => 'api'` у `yii\rest\UrlRule` (или префикс модуля в `controller`).
:::
