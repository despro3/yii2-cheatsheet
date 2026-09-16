---
id: lifecycle
title: Запрос и ответ
icon: 🔄
summary: Маршрутизация и ЧПУ, Request, Response, сессии и куки, обработка ошибок, логирование.
sources: runtime-overview, runtime-bootstrapping, runtime-routing, runtime-requests, runtime-responses, runtime-sessions-cookies, runtime-handling-errors, runtime-logging
---

# Обработка запроса: роутинг, request, response

## Маршрутизация и генерация URL

Маршрут — это `[модуль/]контроллер/действие`. Разбором и генерацией URL занимается компонент
`urlManager`.

```php
'urlManager' => [
    'enablePrettyUrl' => true,      // ЧПУ вместо ?r=post/view
    'showScriptName' => false,      // убрать index.php из URL
    'enableStrictParsing' => false, // true → URL обязан совпасть с правилом, иначе 404
    'suffix' => '.html',            // необязательный суффикс
    'normalizer' => [               // слеши в конце: 301-редирект на канонический вид
        'class' => 'yii\web\UrlNormalizer',
    ],
    'rules' => [
        'posts' => 'post/index',
        'post/<id:\d+>' => 'post/view',
        'posts/<year:\d{4}>/<category>' => 'post/index',
        '<controller:(post|comment)>/<id:\d+>/<action:(create|update|delete)>' => '<controller>/<action>',
        'PUT,POST post/<id:\d+>' => 'post/create',          // привязка к HTTP-методам
        'http://<language:\w+>.example.com/posts' => 'post/index',   // имя сервера
        ['pattern' => 'posts', 'route' => 'post/index', 'suffix' => '.json'],
        ['pattern' => 'posts/<page:\d+>/<tag>', 'route' => 'post/index',
         'defaults' => ['page' => 1, 'tag' => '']],         // необязательные параметры
    ],
],
```

Правила проверяются **по порядку**, до первого совпадения — частые и узкие правила ставьте
выше. Общий префикс удобно группировать через `yii\web\GroupUrlRule`.

### Создание URL

```php
use yii\helpers\Url;

Url::to(['post/index']);                       // /index.php?r=post/index
Url::to(['post/view', 'id' => 100]);           // с параметром
Url::to(['post/view', 'id' => 1, '#' => 'c']); // с якорем
Url::to(['post/index'], true);                 // абсолютный URL
Url::to(['post/index'], 'https');              // абсолютный с указанной схемой
Url::toRoute('post/index');                    // то же, что to([...]) для маршрута
Url::current(['page' => 2]);                   // текущий маршрут + изменённые параметры
Url::home();  Url::base();  Url::canonical();
Url::remember();  Url::previous();             // запомнить/вернуть URL
```

Контекст маршрута: `['index']` — действие текущего контроллера, `['post/index']` —
относительно текущего модуля, `['/post/index']` — от корня приложения.

Своё правило URL — класс, реализующий `UrlRuleInterface` (`createUrl()`, `parseRequest()`).
Динамическое добавление правил — в `bootstrap()`:

```php
public function bootstrap($app)
{
    $app->getUrlManager()->addRules([/* правила модуля */], false);
}
```

Режим обслуживания: `'catchAll' => ['site/offline', 'param' => 'value']`.

## Request

```php
$request = Yii::$app->request;

$request->get('id', 1);            // $_GET с значением по умолчанию
$request->post('name');            // $_POST
$request->getBodyParam('id');      // тело PUT/PATCH/DELETE (см. parsers)
$request->bodyParams;              // все параметры тела
$request->getQueryParams();

$request->method;                  // GET, POST, ...
$request->isGet; $request->isPost; $request->isPut; $request->isAjax; $request->isPjax;
$request->isSecureConnection;

$request->url;          // /admin/index.php/product?id=100
$request->absoluteUrl;  // https://example.com/admin/index.php/product?id=100
$request->hostInfo;     // https://example.com
$request->pathInfo;     // /product
$request->queryString;  // id=100
$request->baseUrl; $request->scriptUrl; $request->serverName; $request->serverPort;

$request->headers->get('Accept');
$request->userAgent; $request->contentType;
$request->acceptableContentTypes; $request->acceptableLanguages;
$request->getPreferredLanguage(['ru-RU', 'en-US']);
$request->userIP; $request->userHost;
$request->getCsrfToken();
```

JSON-запросы (REST):

```php
'request' => [
    'parsers' => ['application/json' => 'yii\web\JsonParser'],
],
```

За reverse proxy настраиваются доверенные прокси, иначе IP и схема будут неверными:

```php
'request' => [
    'trustedHosts' => ['10.0.2.0/24'],
    // при нестандартных заголовках: ipHeaders, secureHeaders, secureProtocolHeaders
],
```

## Response

```php
$response = Yii::$app->response;

$response->statusCode = 201;
$response->headers->set('Pragma', 'no-cache');   // add() не перезаписывает
$response->content = 'hello';
$response->format = yii\web\Response::FORMAT_JSON;  // HTML | JSON | JSONP | XML | RAW
$response->data = ['message' => 'hello'];

// Файлы
Yii::$app->response->sendFile('/path/file.pdf');
Yii::$app->response->sendContentAsFile($csv, 'report.csv');
Yii::$app->response->sendStreamAsFile($handle, 'big.zip');
Yii::$app->response->xSendFile('/path/file.zip');   // отдаёт веб-сервер

// Редиректы
return $this->redirect(['post/view', 'id' => 1]);
return $this->redirect('https://example.com/new', 301);
Yii::$app->response->redirect($url)->send();        // вне действия — сразу send()
return $this->goHome();  return $this->goBack();  return $this->refresh();
```

HTTP-исключения (обработчик сам выставит нужный код):

| Исключение | Код |
|---|---|
| `BadRequestHttpException` | 400 |
| `UnauthorizedHttpException` | 401 |
| `ForbiddenHttpException` | 403 |
| `NotFoundHttpException` | 404 |
| `MethodNotAllowedHttpException` | 405 |
| `NotAcceptableHttpException` | 406 |
| `ConflictHttpException` | 409 |
| `GoneHttpException` | 410 |
| `UnsupportedMediaTypeHttpException` | 415 |
| `TooManyRequestsHttpException` | 429 |
| `ServerErrorHttpException` | 500 |

`send()` вызывается автоматически в конце `Application::run()`; повторный вызов
игнорируется. По пути поднимаются события `EVENT_BEFORE_SEND`, `EVENT_AFTER_PREPARE`,
`EVENT_AFTER_SEND`.

## Сессии и куки

```php
$session = Yii::$app->session;
$session->open(); $session->close(); $session->destroy();
$session->isActive;

$session->set('language', 'ru');    // или $session['language'] = 'ru';
$session->get('language', 'en');
$session->remove('language');
$session->has('language');

// Flash-сообщения — живут до следующего запроса
$session->setFlash('success', 'Сохранено');
$session->addFlash('alerts', 'Ещё сообщение');   // накапливает массив
echo $session->getFlash('success');
$session->hasFlash('success');
```

Хранилища сессии: файлы (по умолчанию), `yii\web\DbSession`, `yii\web\CacheSession`,
`yii\redis\Session`, `yii\mongodb\Session`.

> Важно: нельзя менять элемент массива в сессии напрямую (`$session['a']['b'] = 1` не
> сработает). Пишите массив целиком либо используйте ключи с префиксом `captcha.number`.

```php
// Чтение кук запроса
$cookies = Yii::$app->request->cookies;
$language = $cookies->getValue('language', 'ru');

// Отправка кук
Yii::$app->response->cookies->add(new \yii\web\Cookie([
    'name' => 'language',
    'value' => 'ru',
    'expire' => time() + 86400 * 30,
    'httpOnly' => true,
    'secure' => true,
    'sameSite' => \yii\web\Cookie::SAME_SITE_LAX,
]));
Yii::$app->response->cookies->remove('language');
```

Куки подписываются секретом `request.cookieValidationKey` — модифицированная на клиенте
кука не попадёт в коллекцию. Прямые `$_COOKIE` и `setcookie()` не валидируются.

## Обработка ошибок

Встроенный `errorHandler` превращает warning/notice в исключения, красиво печатает ошибки
в debug-режиме и умеет отдавать ошибку в формате ответа (JSON для API).

```php
'components' => [
    'errorHandler' => [
        'errorAction' => 'site/error',   // действие для показа ошибки
        'maxSourceLines' => 20,
    ],
],
```

```php
// Готовое действие
public function actions()
{
    return ['error' => ['class' => 'yii\web\ErrorAction']];
}
// или своё
public function actionError()
{
    $exception = Yii::$app->errorHandler->exception;
    return $this->render('error', ['exception' => $exception]);
}
```

В представлении `error.php` доступны `$name`, `$message`, `$exception`. Наследники
`yii\base\UserException` никогда не показывают стек вызовов. При формате ответа JSON
ошибка выглядит так: `{"name": ..., "message": ..., "code": ..., "status": 404}`, а
обёртку можно поменять в `response.on beforeSend`.

## Логирование и профилирование

```php
Yii::debug('сообщение', __METHOD__);     // уровень trace
Yii::info('инфо', 'app.payment');
Yii::warning('что-то странное');
Yii::error($exception);

Yii::beginProfile('block1');
// ... измеряемый код (вложенность обязана быть корректной)
Yii::endProfile('block1');
```

```php
'bootstrap' => ['log'],       // компонент log должен подниматься сразу
'components' => [
    'log' => [
        'traceLevel' => YII_DEBUG ? 3 : 0,
        'flushInterval' => 1000,
        'targets' => [
            [
                'class' => 'yii\log\FileTarget',
                'levels' => ['error', 'warning'],
                'categories' => ['yii\db\*', 'app\*'],
                'except' => ['yii\web\HttpException:404'],
                'logVars' => ['_SERVER'],
                'maskVars' => ['_SERVER.HTTP_X_PASSWORD', '_SERVER.*_SECRET'],
                'exportInterval' => 1000,
            ],
            [
                'class' => 'yii\log\EmailTarget',
                'levels' => ['error'],
                'message' => ['to' => ['admin@example.com'], 'subject' => 'Ошибка'],
            ],
        ],
    ],
],
```

Цели логов: `FileTarget`, `DbTarget`, `EmailTarget`, `SyslogTarget`. Уровни: `error`,
`warning`, `info`, `trace`, `profile`. Категория `yii\db\*` — маска по префиксу;
HTTP-ошибки логируются как `yii\web\HttpException:<код>`.

> Совет: в долгоживущих консольных командах ставьте `flushInterval` и `exportInterval`
> в 1 — иначе сообщения не увидите до конца работы. На проде так делать не стоит.
