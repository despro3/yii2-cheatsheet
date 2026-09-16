---
id: errors-logging
title: Ошибки и логирование
part: runtime
summary: Обработчик ошибок и своя страница ошибки, HTTP-исключения, формат ошибок для API; уровни и категории логов, цели (файл, БД, email), фильтрация и профилирование.
sources: runtime-handling-errors, runtime-logging
---

:::lead
Yii превращает все PHP-ошибки в исключения, показывает их с исходным кодом в режиме отладки и красивой страницей в проде. Логи пишутся через `Yii::error()`/`warning()`/`info()`/`debug()` и разводятся **целями** по файлам, базе, почте.
:::

## Обработка ошибок

Компонент `errorHandler` включён по умолчанию (отключается константой `YII_ENABLE_ERROR_HANDLER = false`).

- Не фатальные ошибки (warning, notice) становятся `yii\base\ErrorException` — их можно ловить.
- При `YII_DEBUG = true` показывается стек вызовов и код; при `false` — только сообщение.
- Исключения-наследники `yii\base\UserException` показываются без стека всегда: это «ошибки пользователя».

```php
try {
    10 / 0;
} catch (\yii\base\ErrorException $e) {
    Yii::warning('Деление на ноль');
}

throw new \yii\web\NotFoundHttpException('Такой страницы нет');   // → 404 с правильным статусом
```

### Своя страница ошибки

Лучший способ — действие контроллера:

```php
'components' => [
    'errorHandler' => [
        'errorAction' => 'site/error',
        // 'maxSourceLines' => 20,  'errorView', 'exceptionView' — свои шаблоны
    ],
],
```

```php
public function actions()
{
    return ['error' => ['class' => 'yii\web\ErrorAction']];   // рендерит views/site/error.php
}
```

В представлении доступны `$name`, `$message`, `$exception` (с `statusCode`). Шаблоны basic и advanced уже содержат это действие.

### Ошибки в формате API

Если `response->format` не HTML, обработчик кладёт в `response->data` массив с полями `name`, `message`, `code`, `status` — он уходит как JSON/XML. Формат можно менять на событии `beforeSend`:

```php
'response' => [
    'on beforeSend' => function ($event) {
        $response = $event->sender;
        if ($response->data !== null) {
            $response->data = ['success' => $response->isSuccessful, 'data' => $response->data];
            $response->statusCode = 200;
        }
    },
],
```

## Логирование

### Запись

```php
Yii::debug('начало расчёта', __METHOD__);      // уровень trace — только при разработке
Yii::info('пользователь вошёл', 'app\auth');
Yii::warning('неожиданное состояние');
Yii::error('не удалось отправить письмо', __METHOD__);
```

Второй аргумент — **категория**. `__METHOD__` даёт `app\controllers\SiteController::actionLogin` — так категории образуют иерархию, по которой удобно фильтровать (`yii\db\*`). Сообщение может быть строкой, массивом или объектом (будет экспортирован `VarDumper`).

### Цели

Компонент `log` должен быть в `bootstrap`, чтобы ловить сообщения с самого начала запроса:

```php
return [
    'bootstrap' => ['log'],
    'timeZone' => 'Europe/Moscow',
    'components' => [
        'log' => [
            'traceLevel' => YII_DEBUG ? 3 : 0,   // сколько строк стека добавлять к сообщению
            'flushInterval' => 1000,             // передавать целям каждые N сообщений (и в конце запроса)
            'targets' => [
                'file' => [
                    'class' => 'yii\log\FileTarget',
                    'levels' => ['error', 'warning'],
                    'categories' => ['yii\db\*', 'yii\web\HttpException:*'],
                    'except' => ['yii\web\HttpException:404'],
                    'logVars' => ['_SERVER'],        // какие глобальные массивы прикладывать; [] — никакие
                    'maskVars' => ['_SERVER.HTTP_X_PASSWORD', '_SERVER.*_SECRET'],
                    'exportInterval' => 1000,        // писать в хранилище каждые N отфильтрованных сообщений
                    'prefix' => function ($message) {
                        return '[' . (Yii::$app->user->id ?? '-') . ']';
                    },
                ],
                'email' => [
                    'class' => 'yii\log\EmailTarget',
                    'levels' => ['error'],
                    'categories' => ['yii\db\*'],
                    'message' => [
                        'from' => ['log@example.com'], 'to' => ['admin@example.com'], 'subject' => 'Ошибки БД',
                    ],
                ],
            ],
        ],
    ],
];
```

| Цель | Куда |
|---|---|
| `FileTarget` | `runtime/log/app.log` (ротация по размеру) |
| `DbTarget` | таблица БД (`yii migrate --migrationPath=@yii/log/migrations`) |
| `EmailTarget` | письмо через `mailer` |
| `SyslogTarget` | системный `syslog()` |

Уровни: `error`, `warning`, `info`, `trace` (это `Yii::debug()`), `profile`. Без `levels` цель берёт всё. Формат строки: `время [IP][ID пользователя][ID сессии][уровень][категория] текст`.

> [!GOTCHA]
> В длинных консольных командах сообщения появляются в файле не сразу — они буферизуются. Для немедленной записи поставьте `flushInterval` и `exportInterval` в 1 (ценой производительности).

Отключить цель на лету: `Yii::$app->log->targets['file']->enabled = false`. Своя цель — наследник `yii\log\Target` с методом `export()`.

### Профилирование

```php
Yii::beginProfile('import');
    // код
    Yii::beginProfile('parse');   // вложенные пары должны быть сбалансированы
    Yii::endProfile('parse');
Yii::endProfile('import');
```

Результаты — сообщения уровня `profile`; их показывает панель [отладчика](dev-tools). Так, например, `yii\db\Command` замеряет каждый SQL-запрос.

:::quiz Проверь себя
Q: Как показывать посетителям свою страницу ошибки вместо стандартной?
A: Указать `errorAction => 'site/error'` у `errorHandler` и объявить действие `error` через `yii\web\ErrorAction` с представлением `views/site/error.php`.
Q: Почему `log` нужно добавлять в `bootstrap`?
A: Компоненты создаются лениво; без bootstrap сообщения, записанные до первого обращения к `log`, могли бы потеряться.
Q: Как залогировать все ошибки БД по почте, но не 404?
A: Цель с `levels => ['error']`, `categories => ['yii\db\*']`; для 404 используют `except => ['yii\web\HttpException:404']`.
Q: Чем `Yii::debug()` отличается от `Yii::info()`?
A: Уровнем: `debug` пишет `trace`-сообщения для разработки, `info` — информационные, которые уместны и в проде.
Q: Что делает `traceLevel`?
A: Сколько уровней стека вызовов прикладывать к каждому сообщению; дорого, поэтому включают только при `YII_DEBUG`.
:::
