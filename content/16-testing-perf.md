---
id: testing
title: Тесты и производительность
icon: 🚀
summary: Codeception и фикстуры, оптимизация, деплой, Docker, микро-фреймворк, шаблонизаторы.
sources: test-overview, test-environment-setup, test-unit, test-functional, test-acceptance, test-fixtures, tutorial-performance-tuning, tutorial-shared-hosting, tutorial-docker, tutorial-template-engines, tutorial-yii-as-micro-framework, tutorial-yii-integration, tutorial-start-from-scratch
---

# Тестирование, производительность, эксплуатация

## Тестирование

Yii официально интегрирован с [Codeception](https://codeception.com/); в шаблонах
приложений тесты уже настроены.

| Тип | Что проверяет | Скорость |
|---|---|---|
| Модульные (unit) | отдельный класс/метод, PHPUnit | быстро |
| Функциональные | сценарий пользователя, приложение запускается из кода | средне |
| Приёмочные (acceptance) | сценарий через реальный браузер/PhpBrowser по HTTP | медленно |

```bash
composer require --dev codeception/codeception codeception/module-yii2 codeception/module-asserts
vendor/bin/codecept run
vendor/bin/codecept run unit
vendor/bin/codecept run functional
```

Для приёмочных тестов создают отдельный виртуальный хост, работающий через
`index-test.php` и отдельный конфиг тестовой БД.

### Фикстуры

```php
namespace app\tests\fixtures;

class UserFixture extends \yii\test\ActiveFixture
{
    public $modelClass = 'app\models\User';       // либо $tableName
}

class UserProfileFixture extends \yii\test\ActiveFixture
{
    public $modelClass = 'app\models\UserProfile';
    public $depends = [UserFixture::class];       // загрузится ПОСЛЕ UserFixture
}
```

Данные — `@app/tests/fixtures/data/user.php`:

```php
return [
    'user1' => ['username' => 'lmayert', 'email' => 'a@example.com', 'auth_key' => '...'],
    'user2' => ['username' => 'napoleon69', 'email' => 'b@example.com', 'auth_key' => '...'],
];
```

```php
public function fixtures()          // или globalFixtures() для общих
{
    return ['profiles' => UserProfileFixture::class];
}

$row = $this->profiles['user1'];    // строка данных
$model = $this->profiles('user1');  // AR-модель
```

```bash
yii fixture/load User
yii fixture "User, UserProfile"
yii fixture/load "*"
yii fixture "*, -DoNotLoadThisOne"
yii fixture/unload "*"
yii fixture User --namespace='app\tests\fixtures'
```

Генерация тестовых данных — расширение `yii2-faker`. Автозаполняемые столбцы в данных
указывать не нужно.

## Оптимизация производительности

| Что сделать | Как |
|---|---|
| Свежий PHP + OPcache | `opcache.enable=1`, `opcache.validate_timestamps=0` на проде |
| Отключить отладку | `YII_DEBUG = false`, `YII_ENV = 'prod'`, убрать `debug`/`gii` |
| Кеш схемы БД | `enableSchemaCache => true` в компоненте `db` |
| Кеширование данных и страниц | см. раздел «Кеширование» |
| Ресурсы | объединение и минификация (`yii asset`), `appendTimestamp` |
| Сессии | `DbSession`, `CacheSession` или `yii\redis\Session` вместо файлов |
| Индексы БД и `LIMIT` | индексы по полям фильтрации, VIEW для сложных запросов |
| Массивы вместо AR | `Post::find()->asArray()->all()` при выборке больших списков |
| Автозагрузчик Composer | `composer dumpautoload -o --no-dev` |
| Тяжёлые операции | в очередь (`yii2-queue`, RabbitMQ) или в cron |

```php
// узкие места ищем профайлером
Yii::beginProfile('heavy-block');
// ...
Yii::endProfile('heavy-block');
```

Инструменты: панель `yii2-debug` (запросы, логи, таймлайн), Xdebug Profiler, XHProf.

> Важно: `asArray()` экономит память и время, но отключает приведение типов, связи,
> геттеры и события AR — применяйте там, где нужны только данные для вывода.

## Деплой и окружения

```php
// web/index.php на продакшене
defined('YII_DEBUG') or define('YII_DEBUG', false);
defined('YII_ENV') or define('YII_ENV', 'prod');
```

Чек-лист перед продакшеном:

- корень веб-сервера — `web/`, доступ к `runtime/`, `config/`, `vendor/` закрыт;
- `YII_DEBUG = false`, `YII_ENV = 'prod'`, `gii`/`debug` выключены;
- `cookieValidationKey` задан и не лежит в репозитории (переменные окружения);
- `runtime/` и `web/assets/` доступны на запись процессу веб-сервера;
- HTTPS, `Cookie::secure`, `sameSite`;
- `composer install --no-dev -o`;
- миграции применены: `yii migrate --interactive=0`;
- кеши сброшены: `yii cache/flush-all`;
- логи и мониторинг настроены (`FileTarget`/`DbTarget` + уровень `error`).

### Виртуальный хостинг

Один webroot — берите шаблон `basic`: переименуйте `web` в `public_html`/`www`,
поправьте пути в `index.php`, положите `.htaccess` с `RewriteRule . index.php`.
Для `advanced` переносят входные скрипты в один webroot (`www` и `www/admin`) и
разделяют куки/сессии backend и frontend:

```php
'components' => [
    'request' => ['csrfParam' => '_backendCSRF', 'csrfCookie' => ['path' => '/admin']],
    'user' => ['identityCookie' => ['name' => '_backendIdentity', 'path' => '/admin']],
    'session' => ['name' => 'BACKENDSESSID', 'cookieParams' => ['path' => '/admin']],
],
```

### Docker

```bash
docker-compose up -d            # поднять стек
docker-compose ps               # список сервисов
docker-compose logs -f          # логи
docker-compose exec php bash    # шелл в работающем контейнере
docker-compose run --rm php composer install
docker-compose down -v          # остановить и удалить (осторожно с данными)
```

Базовые образы — [yiisoft/yii2-docker](https://github.com/yiisoft/yii2-docker);
в `yii2-app-basic` поддержка Docker уже есть.

## Yii как микро-фреймворк

Шаблоны приложений необязательны — достаточно `composer.json`, входного скрипта и конфига:

```json
{
    "require": { "yiisoft/yii2": "~2.0.0" },
    "repositories": [{ "type": "composer", "url": "https://asset-packagist.org" }]
}
```

```php
// config.php
return [
    'id' => 'micro-app',
    'basePath' => __DIR__,
    'controllerNamespace' => 'micro\controllers',
    'aliases' => ['@micro' => __DIR__],
    'components' => [
        'db' => ['class' => 'yii\db\Connection', 'dsn' => 'sqlite:@micro/database.sqlite'],
    ],
];
```

```php
// web/index.php
require __DIR__ . '/../vendor/autoload.php';
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';
(new yii\web\Application(require __DIR__ . '/../config.php'))->run();
```

```bash
vendor/bin/yii serve --docroot=./web
vendor/bin/yii migrate/create --appconfig=config.php create_post_table --fields="title:string,body:text"
```

Итоговая структура: `composer.json`, `config.php`, `web/index.php`, `controllers/`,
`models/`. Идеально для JSON API — контроллер на `yii\rest\ActiveController` и всё.

## Сторонний код и шаблонизаторы

```php
// библиотека без автозагрузчика, но с PSR-4
'aliases' => ['@xyz' => '@vendor/foo/bar'],

// совсем legacy — карта классов
Yii::$classMap['Class1'] = 'path/to/Class1.php';
```

Yii можно подключить внутрь чужой системы (WordPress, другой фреймворк) — создать объект
приложения, но **не вызывать** `run()`:

```php
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';
new yii\web\Application(require __DIR__ . '/../config/yii/web.php');  // без run()
```

Шаблонизаторы Twig/Smarty подключаются как рендереры представлений:

```php
'view' => [
    'renderers' => [
        'twig' => [
            'class' => 'yii\twig\ViewRenderer',
            'cachePath' => '@runtime/Twig/cache',
            'globals' => ['html' => '\yii\helpers\Html'],
        ],
    ],
],
```

Расширение выбирается по суффиксу файла представления (`index.twig`).
