---
id: filters
title: Фильтры
part: structure
summary: Код до и после действия: как подключать фильтры, в каком порядке они срабатывают, как написать свой и что умеют встроенные — AccessControl, VerbFilter, HttpCache, PageCache, Cors и другие.
sources: structure-filters
---

:::lead
Фильтр — это [поведение](behaviors), которое вклинивается в `beforeAction()` и `afterAction()` контроллера. Пре-фильтр может остановить выполнение (доступ запрещён, метод не тот), пост-фильтр — обработать результат (кеш, сжатие).
:::

## Подключение

Фильтры объявляют в `behaviors()` контроллера, модуля или приложения:

```php
use yii\filters\HttpCache;

public function behaviors()
{
    return [
        [
            'class' => HttpCache::class,
            'only' => ['index', 'view'],             // только эти действия
            'except' => [],                         // или все, кроме перечисленных
            'lastModified' => function ($action, $params) {
                return (new \yii\db\Query())->from('user')->max('updated_at');
            },
        ],
    ];
}
```

> [!NOTE]
> В модуле и приложении фильтр применяется ко **всем** контроллерам, а в `only`/`except` нужно указывать маршруты (`post/index`), а не ID действий — иначе они неоднозначны.

### Порядок выполнения

:::steps
1. **Пре-фильтры приложения** в порядке объявления в `behaviors()`.
2. **Пре-фильтры модуля**, затем **контроллера** — тоже по порядку. Любой вернул `false` — стоп, остальные фильтры и действие пропускаются.
3. **Действие.**
4. **Пост-фильтры** в обратном порядке: контроллер → модуль → приложение.
:::

## Свой фильтр

Наследуем `yii\base\ActionFilter`, переопределяем `beforeAction()` и/или `afterAction()`:

```php title="components/ActionTimeFilter.php"
namespace app\components;

use Yii;
use yii\base\ActionFilter;

class ActionTimeFilter extends ActionFilter
{
    private $_startTime;

    public function beforeAction($action)
    {
        $this->_startTime = microtime(true);
        return parent::beforeAction($action);      // true — выполнять действие
    }

    public function afterAction($action, $result)
    {
        Yii::debug("{$action->uniqueId}: " . (microtime(true) - $this->_startTime) . ' c');
        return parent::afterAction($action, $result);   // можно подменить $result
    }
}
```

## Встроенные фильтры

### AccessControl — кто может

```php
use yii\filters\AccessControl;

'access' => [
    'class' => AccessControl::class,
    'only' => ['create', 'update', 'delete'],
    'rules' => [
        ['allow' => true, 'actions' => ['create'], 'roles' => ['@']],          // @ — аутентифицирован
        ['allow' => true, 'actions' => ['update', 'delete'], 'roles' => ['admin']],   // роль RBAC
        ['allow' => false, 'ips' => ['10.0.0.*']],
        // всё, что не совпало ни с одним правилом, — запрещено
    ],
    'denyCallback' => function ($rule, $action) {
        throw new \yii\web\ForbiddenHttpException('Нельзя');
    },
],
```

Правила проверяются сверху вниз до первого совпадения. `?` — гость, `@` — вошедший; другие роли уходят в `Yii::$app->user->can()`. Детали и RBAC — в разделе [Авторизация](authorization).

### VerbFilter — какими HTTP-методами

```php
use yii\filters\VerbFilter;

'verbs' => [
    'class' => VerbFilter::class,
    'actions' => [
        'index'  => ['GET'],
        'create' => ['GET', 'POST'],
        'delete' => ['POST', 'DELETE'],   // иначе 405 Method Not Allowed
    ],
],
```

### Аутентификация: HttpBasicAuth, HttpBearerAuth, QueryParamAuth, CompositeAuth

Живут в `yii\filters\auth` и нужны в основном для [REST API](rest-advanced). Класс identity должен реализовать `findIdentityByAccessToken()`:

```php
'authenticator' => ['class' => \yii\filters\auth\HttpBearerAuth::class],
```

### ContentNegotiator — формат ответа и язык

Смотрит на `Accept`, `GET`-параметры и выставляет `Response::format` и `Yii::$app->language`. Можно повесить и как компонент `bootstrap`, чтобы формат определился в самом начале запроса:

```php
use yii\filters\ContentNegotiator;
use yii\web\Response;

[
    'class' => ContentNegotiator::class,
    'formats' => [
        'application/json' => Response::FORMAT_JSON,
        'application/xml' => Response::FORMAT_XML,
    ],
    'languages' => ['ru', 'en-US'],   // первый — по умолчанию
],
```

### HttpCache и PageCache — кеширование

```php
use yii\filters\PageCache;
use yii\caching\DbDependency;

'pageCache' => [
    'class' => PageCache::class,
    'only' => ['index'],
    'duration' => 60,
    'dependency' => ['class' => DbDependency::class, 'sql' => 'SELECT COUNT(*) FROM post'],
    'variations' => [\Yii::$app->language],
],
```

`HttpCache` шлёт `Last-Modified`/`ETag`, чтобы браузер не качал страницу заново; `PageCache` хранит готовый HTML на сервере. Подробно — в [Кеширование вывода](caching-output).

### RateLimiter — не чаще N запросов

Реализует «дырявое ведро»; identity должен реализовать `RateLimitInterface`. См. [REST: лимиты](rest-advanced).

### Cors — запросы с других доменов

Ставьте **перед** фильтрами аутентификации, иначе заголовки CORS не дойдут до preflight-запроса:

```php
use yii\filters\Cors;
use yii\helpers\ArrayHelper;

public function behaviors()
{
    return ArrayHelper::merge([
        [
            'class' => Cors::class,
            'cors' => [
                'Origin' => ['https://app.example.com'],
                'Access-Control-Request-Method' => ['GET', 'POST', 'OPTIONS'],
                'Access-Control-Request-Headers' => ['*'],
                'Access-Control-Allow-Credentials' => true,
                'Access-Control-Max-Age' => 86400,
            ],
            'actions' => [
                'login' => ['Access-Control-Allow-Credentials' => true],   // переопределение для действия
            ],
        ],
    ], parent::behaviors());
}
```

### HostControl — защита от подмены заголовка Host

Уровень приложения, если нельзя настроить веб-сервер:

```php
'as hostControl' => [
    'class' => 'yii\filters\HostControl',
    'allowedHosts' => ['example.com', '*.example.com'],
    'fallbackHostInfo' => 'https://example.com',
],
```

## Шпаргалка по фильтрам

| Фильтр | Задача | Типичное место |
|---|---|---|
| `AccessControl` | доступ по ролям, IP, методам, callback | контроллеры с CRUD |
| `VerbFilter` | ограничить HTTP-методы | `delete` только POST |
| `auth\*` | аутентификация по токену | REST-контроллеры |
| `ContentNegotiator` | JSON/XML и язык по `Accept` | REST, bootstrap |
| `HttpCache` | кеш в браузере | публичные страницы |
| `PageCache` | кеш страницы на сервере | тяжёлые страницы |
| `RateLimiter` | лимит запросов | REST |
| `Cors` | кросс-доменные запросы | API для SPA |
| `HostControl` | белый список хостов | конфигурация приложения |

:::quiz Проверь себя
Q: Что произойдёт, если `beforeAction()` одного из фильтров вернёт `false`?
A: Остальные пре-фильтры и само действие не выполнятся; пост-фильтры тоже пропускаются.
Q: Почему `Cors` нужно объявлять раньше `authenticator`?
A: Браузер сначала шлёт preflight-запрос `OPTIONS` без токена; если аутентификация сработает первой, она вернёт 401 и CORS-заголовки не уйдут.
Q: В каком порядке выполняются пост-фильтры контроллера, модуля и приложения?
A: В обратном относительно пре-фильтров: сначала контроллер, потом модуль, потом приложение.
Q: Как фильтром запретить удаление через GET-запрос?
A: `VerbFilter` с `'delete' => ['POST', 'DELETE']` — на GET вернётся 405.
Q: Чем `HttpCache` отличается от `PageCache`?
A: `HttpCache` управляет кешем на стороне клиента заголовками `Last-Modified`/`ETag`; `PageCache` хранит готовый HTML на сервере в компоненте кеша.
:::
