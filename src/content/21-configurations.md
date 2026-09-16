---
id: configurations
title: Конфигурации, псевдонимы, автозагрузка
part: concepts
summary: Формат конфигурации (class, свойства, on, as), Yii::createObject() и Yii::configure(), конфигурационные файлы, константы окружения; псевдонимы путей @app/@web/@runtime; правила автозагрузки классов и карта классов.
sources: concept-configurations, concept-aliases, concept-autoloading
---

:::lead
В Yii объекты описывают массивами: класс, начальные свойства, обработчики событий, поведения. Такой массив передают в `Yii::createObject()`, в конструктор или в конфигурацию приложения. Пути и URL в конфигурации пишут псевдонимами (`@app/runtime`), а классы находятся автозагрузчиком по пространству имён — и всё это связано между собой.
:::

## Формат конфигурации

```php
$config = [
    'class' => 'app\components\SearchEngine',   // полное имя класса
    'apiKey' => 'xxxxxxxx',                      // публичное поле или свойство через сеттер
    'on search' => function ($event) {           // обработчик события
        Yii::info('Искали: ' . $event->keyword);
    },
    'as indexer' => [                            // поведение
        'class' => 'app\components\IndexerBehavior',
    ],
];

$engine = Yii::createObject($config);            // создать (через DI-контейнер)
Yii::configure($engine, ['apiKey' => 'yyy']);    // настроить существующий объект (без ключа class)
```

Так описываются компоненты приложения, модули, виджеты, поведения, валидаторы, цели логов — везде один формат. Для виджетов ключ `class` не нужен — класс уже известен:

```php
echo Menu::widget([
    'activateItems' => false,
    'items' => [
        ['label' => 'Home', 'url' => ['site/index']],
        ['label' => 'Login', 'url' => ['site/login'], 'visible' => Yii::$app->user->isGuest],
    ],
]);
```

## Конфигурация приложения

Самая большая: свойства приложения плюс `components`, `modules`, `params`. Обычно разбита на файлы, каждый возвращает массив:

```php title="config/web.php"
$params = require __DIR__ . '/params.php';
$db = require __DIR__ . '/db.php';

$config = [
    'id' => 'basic',
    'basePath' => dirname(__DIR__),
    'bootstrap' => ['log'],
    'aliases' => ['@bower' => '@vendor/bower-asset', '@npm' => '@vendor/npm-asset'],
    'components' => [
        'request' => ['cookieValidationKey' => '...'],
        'cache' => ['class' => 'yii\caching\FileCache'],
        'user' => ['identityClass' => 'app\models\User', 'enableAutoLogin' => true],
        'errorHandler' => ['errorAction' => 'site/error'],
        'log' => [
            'traceLevel' => YII_DEBUG ? 3 : 0,
            'targets' => [['class' => 'yii\log\FileTarget', 'levels' => ['error', 'warning']]],
        ],
        'db' => $db,
    ],
    'params' => $params,
];

if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'debug';
    $config['modules']['debug'] = 'yii\debug\Module';
    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = 'yii\gii\Module';
}

return $config;
```

Ключа `class` нет — класс задаёт входной скрипт: `new yii\web\Application($config)`.

### Умолчания для классов (DI)

Через свойство `container` (с 2.0.11) или `Yii::$container->set()` задаются значения, которые применятся ко **всем** объектам класса, созданным через `Yii::createObject()`:

```php
'container' => [
    'definitions' => [
        'yii\widgets\LinkPager' => ['maxButtonCount' => 5],
        'yii\mail\MailInterface' => 'yii\symfonymailer\Mailer',
    ],
    'singletons' => [],
],
```

Подробнее — в разделе [DI-контейнер](di).

### Константы окружения

`YII_ENV` во входном скрипте порождает `YII_ENV_PROD`, `YII_ENV_DEV`, `YII_ENV_TEST` — по ним ветвят конфигурацию (как `debug` и `gii` выше). В advanced-шаблоне для этого есть папка `environments/` и `php init`.

## Псевдонимы

Псевдоним начинается с `@` и заменяет абсолютный путь или URL:

```php
Yii::setAlias('@foo', '/path/to/foo');              // корневой псевдоним
Yii::setAlias('@bar', 'https://www.example.com');
Yii::setAlias('@foobar', '@foo/bar');                // на основе другого

Yii::getAlias('@foo/bar/file.php');                  // /path/to/foo/bar/file.php — производный
Yii::getAlias('@bar');                               // https://www.example.com
```

`getAlias()` не проверяет, что путь существует. Корневой псевдоним может содержать `/` — берётся самое длинное совпадение (`@foo/bar` приоритетнее `@foo`).

Задают их обычно в конфигурации: `'aliases' => ['@uploads' => '@webroot/uploads']`. Большинство свойств фреймворка принимают псевдонимы напрямую: `'cachePath' => '@runtime/cache'`.

### Предопределённые

| Псевдоним | Указывает на |
|---|---|
| `@yii` | папка фреймворка (`vendor/yiisoft/yii2`) |
| `@app` | `basePath` приложения |
| `@runtime` | `@app/runtime` |
| `@vendor` | `@app/vendor` |
| `@webroot` | папка с `index.php` (только web) |
| `@web` | базовый URL приложения (только web) |
| `@bower`, `@npm` | `@vendor/bower-asset`, `@vendor/npm-asset` (в шаблонах) |
| `@yii/jui`, `@yii/bootstrap`… | папки установленных расширений — из их `composer.json` |

В advanced-шаблоне дополнительно `@common`, `@frontend`, `@backend`, `@console`.

## Автозагрузка классов

Автозагрузчик Yii (PSR-4-совместимый, регистрируется в `Yii.php`) находит файл по двум правилам:

1. класс в пространстве имён: `foo\bar\MyClass`;
2. путь = псевдоним из имени класса: `@foo/bar/MyClass.php` — значит, `@foo` (или `@foo/bar`) должен быть корневым псевдонимом.

Поэтому `app\controllers\SiteController` живёт в `@app/controllers/SiteController.php`, а классы расширений находятся через их псевдонимы. Чтобы подключить библиотеку без автозагрузчика, достаточно объявить псевдоним для её корневого пространства имён.

```php
Yii::$classMap['foo\bar\MyClass'] = '@app/lib/MyClass.php';   // карта классов: без поиска, самый быстрый путь
```

Все классы самого фреймворка загружаются через карту классов. Автозагрузчик Composer подключается **до** `Yii.php`, чтобы автозагрузчик Yii был первым в очереди.

:::quiz Проверь себя
Q: Что означают ключи `on` и `as` в конфигурации?
A: `'on событие' => обработчик` подписывает на событие объекта, `'as имя' => конфиг` прикрепляет поведение.
Q: Чем `Yii::createObject()` отличается от `new Class($config)`?
A: `createObject()` идёт через DI-контейнер: применяет зарегистрированные умолчания и разрешает зависимости конструктора.
Q: Что вернёт `Yii::getAlias('@app/runtime/cache')`, если папки нет?
A: Путь всё равно вернётся — `getAlias()` не проверяет существование файлов.
Q: Почему класс `app\components\MyClass` находится без настройки автозагрузки?
A: `@app` — предопределённый псевдоним, а автозагрузчик ищет `@app/components/MyClass.php` по пространству имён.
Q: Как включить модуль только в режиме разработки?
A: Обернуть его подключение в `if (YII_ENV_DEV) { ... }` в конфигурации.
:::
