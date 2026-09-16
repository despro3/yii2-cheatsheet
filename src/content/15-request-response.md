---
id: request-response
title: Запрос и ответ
part: runtime
summary: Компоненты request и response — параметры, заголовки, URL, доверенные прокси, коды состояния, форматы ответа, редиректы и отправка файлов.
sources: runtime-requests, runtime-responses
---

:::lead
`Yii::$app->request` — всё о входящем запросе: параметры, метод, заголовки, куки, IP. `Yii::$app->response` — всё об ответе: код, заголовки, тело, формат. Работайте с ними, а не с `$_GET`/`header()`: так код тестируется и не зависит от окружения.
:::

## Запрос {#zapros-request}

### Параметры

```php
$request = Yii::$app->request;

$request->get();                 // весь $_GET
$request->get('id');             // $_GET['id'] или null
$request->get('id', 1);          // со значением по умолчанию
$request->post('name', '');      // то же для $_POST

$request->bodyParams;            // тело PUT/PATCH/JSON-запроса
$request->getBodyParam('id');
$request->queryParams;           // = get()
```

Чтобы тело JSON-запросов разбиралось автоматически (нужно REST API):

```php
'request' => [
    'parsers' => ['application/json' => 'yii\web\JsonParser'],
],
```

### Метод, URL, заголовки, клиент

```php
$request->method;                                   // 'GET', 'POST'…
$request->isGet; $request->isPost; $request->isPut; $request->isAjax; $request->isPjax;

// для https://example.com/admin/index.php/product?id=100
$request->url;             // /admin/index.php/product?id=100
$request->absoluteUrl;     // https://example.com/admin/index.php/product?id=100
$request->hostInfo;        // https://example.com
$request->pathInfo;        // product
$request->queryString;     // id=100
$request->baseUrl;         // /admin
$request->scriptUrl;       // /admin/index.php
$request->serverName;      // example.com
$request->isSecureConnection;

$headers = $request->headers;                       // HeaderCollection
$headers->get('Accept'); $headers->has('User-Agent');
$request->userAgent; $request->contentType;
$request->acceptableContentTypes;                   // по убыванию q
$request->acceptableLanguages;
$request->getPreferredLanguage(['ru', 'en']);       // лучший из поддерживаемых

$request->userIP; $request->userHost;
$request->cookies;                                  // см. раздел о куках
$request->csrfToken;                                // для ручных AJAX-запросов
```

### За обратным прокси

Заголовкам `X-Forwarded-*` нельзя верить по умолчанию — их подставит любой клиент. Перечислите доверенные прокси:

```php
'request' => [
    'trustedHosts' => ['10.0.2.0/24'],   // только их X-Forwarded-For / X-Forwarded-Proto учитываются
    // если прокси шлёт нестандартные заголовки:
    // 'trustedHosts' => ['10.0.2.0/24' => ['X-ProxyUser-Ip', 'Front-End-Https']],
    // 'ipHeaders' => ['X-ProxyUser-Ip'],
    // 'secureProtocolHeaders' => ['Front-End-Https' => ['on']],
],
```

Без этой настройки за прокси `userIP` будет адресом прокси, а `isSecureConnection` — `false`.

## Ответ {#otvet-response}

### Код состояния

```php
Yii::$app->response->statusCode = 201;    // по умолчанию 200
throw new \yii\web\NotFoundHttpException();   // обработчик ошибок сам выставит 404
throw new \yii\web\HttpException(402, 'Payment required');
```

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

### Заголовки

```php
$headers = Yii::$app->response->headers;
$headers->add('Pragma', 'no-cache');     // добавить (существующие сохраняются)
$headers->set('Pragma', 'no-cache');     // заменить
$headers->remove('Pragma');
```

Имена регистронезависимы; отправятся при `send()`.

### Тело и формат

```php
// готовая строка
Yii::$app->response->content = 'hello';

// данные + формат: отформатирует JsonResponseFormatter
$response = Yii::$app->response;
// FORMAT_HTML | FORMAT_XML | FORMAT_JSON | FORMAT_JSONP | FORMAT_RAW
$response->format = \yii\web\Response::FORMAT_JSON;
$response->data = ['message' => 'hello'];

// обычно проще вернуть данные из действия
public function actionInfo()
{
    return $this->asJson(['message' => 'hello', 'code' => 100]);
}
```

Свои форматтеры добавляются в `response->formatters`. Настройка JSON (например, читаемый вывод в отладке):

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

Можно вернуть из действия и собственный объект `Response`, созданный через `Yii::createObject()`, — но он не получит настроек компонента `response` из конфигурации.

### Перенаправление

```php
public function actionOld()
{
    return $this->redirect(['post/view', 'id' => 1]);          // 302
    return $this->redirect('https://example.com/new', 301);    // навсегда
    return $this->goHome();   // $this->goBack();   $this->refresh();
}

// вне действия — сразу отправить
Yii::$app->response->redirect($url)->send();
```

Для AJAX-запросов вместо `Location` уходит заголовок `X-Redirect`; `yii.js` из `YiiAsset` обрабатывает его автоматически.

### Отправка файлов

```php
return Yii::$app->response->sendFile('/path/to/report.pdf');                    // существующий файл
return Yii::$app->response->sendContentAsFile($csv, 'export.csv');              // строка как файл
return Yii::$app->response->sendStreamAsFile($stream, 'big.zip');               // поток — для больших файлов
// отдачу делает веб-сервер (X-Sendfile / X-Accel-Redirect)
return Yii::$app->response->xSendFile('/path/to/file');
```

Все поддерживают заголовок `Range` (докачку).

### Как отправляется ответ

`send()` вызывается автоматически в конце `run()`, но его можно вызвать и раньше; повторный вызов игнорируется:

1. событие `beforeSend`;
2. `prepare()` — `data` форматируется в `content`;
3. событие `afterPrepare`;
4. `sendHeaders()`;
5. `sendContent()`;
6. событие `afterSend`.

События удобны, чтобы, например, обернуть все JSON-ответы в единый конверт — см. [Ошибки и логирование](errors-logging).

:::quiz Проверь себя
Q: Как получить параметры `PUT`-запроса с JSON-телом?
A: Настроить парсер `'application/json' => 'yii\web\JsonParser'` и читать `Yii::$app->request->bodyParams` / `getBodyParam('id')`.
Q: Что вернёт `Yii::$app->request->userIP` за обратным прокси без настройки `trustedHosts`?
A: IP самого прокси — заголовки `X-Forwarded-For` игнорируются, пока прокси не объявлен доверенным.
Q: Как из действия вернуть JSON, не трогая шаблон?
A: `return $this->asJson($data)` или установить `response->format = FORMAT_JSON` и вернуть массив.
Q: Чем `sendStreamAsFile()` лучше `sendFile()`?
A: Не загружает файл в память целиком — подходит для больших файлов; ещё эффективнее `xSendFile()`, если веб-сервер поддерживает X-Sendfile.
Q: Почему после `redirect()` вне действия нужно вызвать `send()`?
A: Чтобы ответ ушёл немедленно и к нему не добавился вывод последующего кода.
:::
