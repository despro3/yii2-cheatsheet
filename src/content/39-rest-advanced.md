---
id: rest-advanced
title: REST API — форматы, аутентификация, версии
part: rest
summary: ContentNegotiator и Serializer (JSON/XML, envelope, pretty print); аутентификация HttpBasicAuth/HttpBearerAuth/QueryParamAuth/CompositeAuth и findIdentityByAccessToken; ограничение частоты RateLimitInterface; версионирование модулями v1/v2; обработка ошибок и формат ответа; фильтрация коллекций DataFilter.
sources: rest-response-formatting, rest-authentication, rest-rate-limiting, rest-versioning, rest-error-handling, rest-filtering-collections
---

:::lead
После быстрого старта остаются вопросы взрослого API: как отвечать в нужном формате, как узнавать клиента без сессии, как не дать одному клиенту положить сервер, как выпускать v2, не ломая v1, и как отдавать ошибки единообразно. Всё это — фильтры и настройки `yii\rest`.
:::

## Формат ответа

Два шага: `ContentNegotiator` выбирает формат по `Accept`/GET-параметру, а `Response` с нужным `formatter` сериализует данные из `$response->data`.

```php
// yii\rest\Controller уже включает contentNegotiator; настройка:
public function behaviors()
{
    $behaviors = parent::behaviors();
    $behaviors['contentNegotiator']['formats'] = [
        'application/json' => Response::FORMAT_JSON,
        'application/xml' => Response::FORMAT_XML,
    ];
    $behaviors['contentNegotiator']['formatParam'] = '_format';   // ?_format=xml
    return $behaviors;
}
```

Поддерживаются `Accept: application/json; q=1.0, */*; q=0.1`. Форматы ответа настраиваются в `response.formatters`:

```php
'response' => [
    'formatters' => [
        'json' => [
            'class' => 'yii\web\JsonResponseFormatter',
            'prettyPrint' => YII_DEBUG,
            'encodeOptions' => JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE,
        ],
        'xml' => ['class' => 'yii\web\XmlResponseFormatter', 'rootTag' => 'response', 'itemTag' => 'item'],
    ],
],
```

### Сериализация данных

`yii\rest\Serializer` превращает `Arrayable` (модели) и `DataProviderInterface` (коллекции) в массивы с учётом `fields`/`expand`:

```php
public $serializer = [
    'class' => 'yii\rest\Serializer',
    'collectionEnvelope' => 'items',   // коллекция внутри {"items": …, "_links": …, "_meta": …}
    'fieldsParam' => 'fields', 'expandParam' => 'expand',
    'totalCountHeader' => 'X-Pagination-Total-Count', …
];
```

Свои объекты — реализуйте `Arrayable` или отдавайте массивы.

## Аутентификация

API обычно без сессий: клиент присылает токен в каждом запросе.

```php title="config/web.php"
'user' => [
    'identityClass' => 'app\models\User',
    'enableAutoLogin' => false,
    'enableSession' => false,           // не создавать сессии для API
    'loginUrl' => null,                 // не редиректить — отдавать 401
],
```

```php title="controllers/UserController.php"
use yii\filters\auth\HttpBearerAuth;

public function behaviors()
{
    $behaviors = parent::behaviors();
    $behaviors['authenticator'] = [
        'class' => HttpBearerAuth::class,
        // 'except' => ['login', 'options'],   // OPTIONS должен быть доступен для CORS
    ];
    return $behaviors;
}
```

```php title="models/User.php"
public static function findIdentityByAccessToken($token, $type = null)
{
    return static::findOne(['access_token' => $token, 'status' => self::STATUS_ACTIVE]);
}
```

:::kv
`HttpBasicAuth` — логин/пароль в заголовке `Authorization: Basic`; по умолчанию логин = токен, но можно `auth` — колбэк проверки пароля
`HttpBearerAuth` — `Authorization: Bearer <token>` — стандарт для API
`HttpHeaderAuth` — токен в произвольном заголовке (`header`, `pattern`), 2.0.14
`QueryParamAuth` — `?access-token=…` — только когда заголовки недоступны (утекает в логи)
`CompositeAuth` — попробовать несколько (`authMethods`) по очереди
:::

```php
$behaviors['authenticator'] = [
    'class' => CompositeAuth::class,
    'authMethods' => [HttpBasicAuth::class, HttpBearerAuth::class, QueryParamAuth::class],
];
```

Неудача — 401 Unauthorized. Аутентификатор вызывает `Yii::$app->user->loginByAccessToken($token, $type)` → `findIdentityByAccessToken()`; `$type` — класс аутентификатора, если токены разных видов.

> [!NOTE] Токены
> Токен — случайная строка (`generateRandomString()`), не хэш пароля и не ID. Храните с датой истечения; для OAuth2/JWT есть расширения (`yiisoft/yii2-authclient`, JWT-пакеты). При `CompositeAuth` порядок важен — первый успешный побеждает.

## Ограничение частоты (rate limiting)

```php title="models/User.php"
use yii\filters\RateLimitInterface;

class User extends ActiveRecord implements IdentityInterface, RateLimitInterface
{
    public function getRateLimit($request, $action)
    {
        return [100, 600];        // 100 запросов за 600 секунд
    }

    public function loadAllowance($request, $action)
    {
        return [$this->allowance, $this->allowance_updated_at];   // столбцы в таблице
    }

    public function saveAllowance($request, $action, $allowance, $timestamp)
    {
        $this->allowance = $allowance;
        $this->allowance_updated_at = $timestamp;
        $this->save(false);
    }
}
```

`RateLimiter` уже подключён в `yii\rest\Controller` и включается автоматически, если identity реализует интерфейс. Ответ при превышении — 429 Too Many Requests; в заголовках `X-Rate-Limit-Limit`, `X-Rate-Limit-Remaining`, `X-Rate-Limit-Reset`. Алгоритм — leaky bucket. Хранить allowance можно в кэше вместо БД.

## Версионирование

Версия в URL — самый прозрачный вариант: каждая версия — модуль.

```
api/
    modules/
        v1/
            controllers/UserController.php
            models/User.php
            Module.php
        v2/
            ...
```

```php
'modules' => [
    'v1' => ['class' => 'app\modules\v1\Module'],
    'v2' => ['class' => 'app\modules\v2\Module'],
],
'urlManager' => [
    'rules' => [
        ['class' => 'yii\rest\UrlRule', 'controller' => ['v1/user', 'v1/post']],
        ['class' => 'yii\rest\UrlRule', 'controller' => ['v2/user', 'v2/post']],
    ],
],
// → /v1/users, /v2/users
```

Общие модели — в `common`, версионные различия — в `fields()`/контроллерах модулей. **Минорные** изменения (новое поле, новый параметр) — совместимы, версия та же; **мажорные** — новая версия. Альтернатива — версия в заголовке `Accept: application/json; version=v2` и разбор в `ContentNegotiator`/фильтре, но URL проще для клиентов и кэшей.

## Обработка ошибок

Исключения превращаются в ответы автоматически:

| Ситуация | Код |
|---|---|
| Успех `GET`/`PUT`/`PATCH` | 200 |
| `POST` создал ресурс | 201 |
| `DELETE` успешно | 204 |
| Неверный запрос (JSON не разобран) | 400 |
| Нет аутентификации | 401 |
| Аутентифицирован, но нельзя (`ForbiddenHttpException`) | 403 |
| Не найдено (`NotFoundHttpException`) | 404 |
| Метод не поддерживается (`MethodNotAllowedHttpException`) | 405 |
| Формат не поддерживается | 415 |
| Ошибки валидации (`save()` вернул `false`) | 422 |
| Превышен лимит | 429 |
| Внутренняя ошибка | 500 |

Тело ошибки: `{"name": "Not Found", "message": "…", "code": 0, "status": 404}` (в debug — плюс `type`, `file`, `line`, стек). Свой формат — событием `beforeSend` ответа:

```php
'response' => [
    'class' => 'yii\web\Response',
    'on beforeSend' => function ($event) {
        $response = $event->sender;
        if ($response->data !== null && Yii::$app->request->get('suppress_response_code')) {
            $response->data = ['success' => $response->isSuccessful, 'data' => $response->data];
            $response->statusCode = 200;
        }
    },
],
```

## Фильтрация коллекций

С 2.0.13 у `IndexAction` есть `dataFilter` — безопасный разбор условий из запроса:

```php
public function actions()
{
    $actions = parent::actions();
    $actions['index']['dataFilter'] = [
        'class' => 'yii\data\ActiveDataFilter',
        'searchModel' => 'app\models\PostSearch',   // модель с rules(): какие атрибуты и какие типы допустимы
    ];
    return $actions;
}
```

```
GET /posts?filter[status]=1&filter[title][like]=yii&filter[id][in][]=1&filter[id][in][]=2
GET /posts?filter[or][0][author_id]=1&filter[or][1][created_at][gt]=1600000000
```

Операторы: `and`, `or`, `not`, `lt`, `gt`, `lte`, `gte`, `eq`, `neq`, `in`, `nin`, `like`. Модель поиска не обязана быть AR — достаточно `Model` с `rules()`. Без `searchModel` — `DataFilter` с настройкой `attributeMap`/`operatorTypes`. Условие превращается в `where` провайдера; недопустимое — 422.

Вручную то же самое: `prepareDataProvider` + `andFilterWhere` по `Yii::$app->request->get()`.

:::quiz Проверь себя
Q: Как API выбирает между JSON и XML?
A: Фильтр `ContentNegotiator` по заголовку `Accept` (или параметру `formatParam`) — если формат в списке `formats`.
Q: Какой метод модели вызывает `HttpBearerAuth`?
A: `findIdentityByAccessToken($token, $type)` через `Yii::$app->user->loginByAccessToken()`.
Q: Что нужно, чтобы включить ограничение частоты запросов?
A: Реализовать `RateLimitInterface` (`getRateLimit`, `loadAllowance`, `saveAllowance`) в identity-классе — `RateLimiter` уже подключён.
Q: Какой код вернёт API, если `save()` не прошёл валидацию?
A: 422 с массивом `[{"field": "…", "message": "…"}]`.
Q: Как разложить API по версиям?
A: Модуль на версию (`v1`, `v2`) с собственными контроллерами и правилами `yii\rest\UrlRule` с префиксом модуля.
:::
