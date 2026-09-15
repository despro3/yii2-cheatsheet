---
id: rest
title: REST API
icon: 🌐
summary: ActiveController, маршруты, ресурсы и поля, форматы ответа, аутентификация, лимиты, версии, ошибки.
---

# REST API

## Минимальный API за три шага

```php
// 1. Контроллер
namespace app\controllers;

class UserController extends \yii\rest\ActiveController
{
    public $modelClass = 'app\models\User';
}
```

```php
// 2. Маршруты
'urlManager' => [
    'enablePrettyUrl' => true,
    'enableStrictParsing' => true,
    'showScriptName' => false,
    'rules' => [
        ['class' => 'yii\rest\UrlRule', 'controller' => 'user'],
    ],
],

// 3. Приём JSON
'request' => [
    'parsers' => ['application/json' => 'yii\web\JsonParser'],
],
```

Готовые точки входа:

| Метод и путь | Действие |
|---|---|
| `GET /users` | постраничный список |
| `HEAD /users` | метаданные списка |
| `POST /users` | создание |
| `GET /users/123` | одна запись |
| `PATCH|PUT /users/123` | обновление |
| `DELETE /users/123` | удаление |
| `OPTIONS /users`, `OPTIONS /users/123` | поддерживаемые методы |

`yii\rest\UrlRule` сам приводит ID контроллера к множественному числу
(`Inflector::pluralize()`), отключается через `'pluralize' => false`.

```php
[
    'class' => 'yii\rest\UrlRule',
    'controller' => ['u' => 'user'],          // явное имя в URL
    'except' => ['delete'],
    'extraPatterns' => ['GET search' => 'search'],
]
```

## Ресурсы: поля и ссылки

```php
class User extends ActiveRecord implements \yii\web\Linkable
{
    public function fields()
    {
        return [
            'id',
            'email' => 'email_address',                         // переименование
            'name' => fn () => $this->first_name . ' ' . $this->last_name,
        ];
    }

    public function extraFields()
    {
        return ['profile', 'orders'];        // доступны по ?expand=profile
    }

    public function getLinks()               // HATEOAS
    {
        return [\yii\web\Link::REL_SELF => \yii\helpers\Url::to(['user/view', 'id' => $this->id], true)];
    }
}
```

```
GET /users?fields=id,email
GET /users?expand=profile
GET /users?fields=id,email&expand=profile
GET /users?sort=-email
GET /users?filter[id][in][]=2&filter[title][like]=cheese
```

> Важно: по умолчанию в ответ попадают **все** атрибуты модели. Обязательно уберите
> `password_hash`, `auth_key`, `password_reset_token` — либо через `unset()` в `fields()`,
> либо явным перечислением полей.

Коллекции лучше возвращать провайдером данных — сериализатор добавит заголовки
`X-Pagination-Total-Count`, `X-Pagination-Page-Count`, `X-Pagination-Current-Page`,
`X-Pagination-Per-Page` и `Link`.

```php
public function actionIndex()
{
    return new ActiveDataProvider(['query' => Post::find()]);
}
```

## Контроллеры

`yii\rest\Controller` даёт согласование содержимого, проверку HTTP-методов,
аутентификацию и ограничение частоты запросов. `yii\rest\ActiveController` добавляет
готовые действия `index`, `view`, `create`, `update`, `delete`, `options` и проверку
доступа.

```php
public function actions()
{
    $actions = parent::actions();
    unset($actions['delete'], $actions['create']);
    $actions['index']['prepareDataProvider'] = [$this, 'prepareDataProvider'];
    return $actions;
}

public function checkAccess($action, $model = null, $params = [])
{
    if (in_array($action, ['update', 'delete'], true) && $model->author_id !== Yii::$app->user->id) {
        throw new \yii\web\ForbiddenHttpException('Можно менять только свои записи.');
    }
}
```

Фильтры выполняются в порядке: `contentNegotiator` → `verbFilter` → `authenticator` →
`rateLimiter`. Настраиваются переопределением `behaviors()`.

## Формат ответа

```php
public function behaviors()
{
    $behaviors = parent::behaviors();
    $behaviors['contentNegotiator']['formats']['text/html'] = \yii\web\Response::FORMAT_HTML;
    return $behaviors;
}
```

```php
// «конверт» для коллекции: items + _links + _meta в теле ответа
class UserController extends ActiveController
{
    public $modelClass = 'app\models\User';
    public $serializer = [
        'class' => 'yii\rest\Serializer',
        'collectionEnvelope' => 'items',
    ];
}
```

```php
'response' => [
    'formatters' => [
        \yii\web\Response::FORMAT_JSON => [
            'class' => 'yii\web\JsonResponseFormatter',
            'prettyPrint' => YII_DEBUG,
            'encodeOptions' => JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE,
        ],
    ],
],
```

## Аутентификация

1. `'user' => ['enableSession' => false]` — API не хранит состояние.
2. Настроить `authenticator` в контроллере.
3. Реализовать `findIdentityByAccessToken()` в identity-классе.

```php
use yii\filters\auth\{CompositeAuth, HttpBasicAuth, HttpBearerAuth, QueryParamAuth};

public function behaviors()
{
    $behaviors = parent::behaviors();
    $behaviors['authenticator'] = [
        'class' => CompositeAuth::class,
        'authMethods' => [
            HttpBasicAuth::class,
            HttpBearerAuth::class,
            QueryParamAuth::class,
        ],
        'except' => ['options'],
    ];
    return $behaviors;
}
```

Неудачная аутентификация → 401 (+ `WWW-Authenticate`). Авторизация — через
`checkAccess()` и/или RBAC.

> Важно: токен доступа в URL попадает в логи веб-сервера. Используйте заголовок
> `Authorization`, и только HTTPS — иначе токен перехватывается.

## Ограничение частоты запросов

Identity-класс реализует `yii\filters\RateLimitInterface`:

```php
public function getRateLimit($request, $action)  { return [100, 600]; }  // 100 запросов / 600 сек
public function loadAllowance($request, $action) { return [$this->allowance, $this->allowance_updated_at]; }
public function saveAllowance($request, $action, $allowance, $timestamp)
{
    $this->allowance = $allowance;
    $this->allowance_updated_at = $timestamp;
    $this->save();
}
```

Заголовки ответа: `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset`
(отключаются `$behaviors['rateLimiter']['enableRateLimitHeaders'] = false`). Превышение →
429 `TooManyRequestsHttpException`.

## Версионирование

Мажорные версии — отдельные модули (`v1`, `v2`), минорные — через заголовок `Accept`.

```php
'modules' => [
    'v1' => ['class' => 'app\modules\v1\Module'],
    'v2' => ['class' => 'app\modules\v2\Module'],
],
'urlManager' => ['rules' => [
    ['class' => 'yii\rest\UrlRule', 'controller' => ['v1/user', 'v1/post']],
    ['class' => 'yii\rest\UrlRule', 'controller' => ['v2/user', 'v2/post']],
]],
```

`Accept: application/json; version=v1` → `Yii::$app->response->acceptParams['version']`.

## Фильтрация коллекций

```php
$filter = new \yii\data\ActiveDataFilter([
    'searchModel' => (new \yii\base\DynamicModel(['id', 'title']))
        ->addRule(['id'], 'integer')
        ->addRule(['title'], 'string', ['min' => 2, 'max' => 200]),
    'attributeMap' => ['authorName' => '{{author}}.[[name]]'],
]);

$query = Post::find();
if ($filter->load(Yii::$app->request->get())) {
    $condition = $filter->build();
    if ($condition === false) { return $filter; }   // вернёт ошибки валидации фильтра
    $query->andWhere($condition);
}
return new ActiveDataProvider(['query' => $query]);
```

Ключевые слова: `and`, `or`, `not`, `lt`, `gt`, `lte`, `gte`, `eq`, `neq`, `in`, `nin`,
`like` (расширяется через `filterControls`). Обязателен `searchModel` — он и определяет,
по чему разрешено фильтровать.

## Коды ответов и ошибки

| Код | Когда |
|---|---|
| 200 | успех |
| 201 | создано (`POST`), в `Location` — URL ресурса |
| 204 | успех без содержимого (`DELETE`) |
| 304 | не изменялось |
| 400 | некорректный запрос |
| 401 | аутентификация не пройдена |
| 403 | доступ запрещён |
| 404 | ресурс не найден |
| 405 | метод не поддерживается (см. `Allow`) |
| 415 | неподдерживаемый тип/версия |
| 422 | ошибка валидации данных |
| 429 | слишком много запросов |
| 500 | ошибка сервера |

Тело ошибки по умолчанию: `{"name": ..., "message": ..., "code": ..., "status": 404}`.
Изменить формат можно в `response.on beforeSend`:

```php
'response' => [
    'on beforeSend' => function ($event) {
        $response = $event->sender;
        if ($response->data !== null && Yii::$app->request->get('suppress_response_code')) {
            $response->data = ['success' => $response->isSuccessful, 'data' => $response->data];
            $response->statusCode = 200;
        }
    },
],
```

> Совет: API лучше выносить в отдельное приложение или модуль — так проще не смешивать
> stateless-логику с сессиями веб-части.
