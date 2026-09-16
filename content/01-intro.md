---
id: intro
title: Старт
icon: 🚀
summary: Что такое Yii2, установка, структура каталогов, входной скрипт, режимы окружения.
sources: intro-yii, start-prerequisites, start-installation, start-workflow, start-hello, start-forms, start-databases, start-gii, start-looking-ahead, structure-overview
---

# Старт: установка и первый запуск

Yii 2 — компонентный full-stack PHP-фреймворк на паттерне MVC. Требует **PHP 7.4+** (2.0.x
работает и на более новых версиях PHP). Ставится Composer'ом вместе с шаблоном приложения:
фреймворк и «скелет» проекта — это один установочный шаг.

## Установка за одну команду

```bash
# базовый шаблон — один сайт, самый простой старт
composer create-project --prefer-dist yiisoft/yii2-app-basic basic

# продвинутый шаблон — frontend + backend + common, для команд
composer create-project --prefer-dist yiisoft/yii2-app-advanced advanced
```

Проверка окружения и запуск встроенного сервера:

```bash
cd basic
php requirements.php          # проверка требований к PHP
php yii serve --port=8080     # http://localhost:8080
php yii                       # список всех консольных команд
```

> Важно: корнем веб-сервера должна быть папка `web/`, а не корень проекта. Иначе конфиги,
> исходники и `runtime/` окажутся доступны из интернета.

## Структура каталогов (basic)

| Путь | Что внутри |
|---|---|
| `config/web.php` | конфигурация веб-приложения |
| `config/console.php` | конфигурация консольного приложения |
| `config/db.php` | параметры подключения к БД |
| `config/params.php` | произвольные параметры (`Yii::$app->params`) |
| `controllers/` | контроллеры (`SiteController.php`) |
| `models/` | модели, формы, Active Record |
| `views/` | представления и `views/layouts/main.php` |
| `commands/` | консольные команды |
| `migrations/` | миграции БД |
| `runtime/` | логи, кеш, временные файлы (нужна запись) |
| `vendor/` | пакеты Composer, в том числе сам Yii |
| `web/index.php` | **единственная** точка входа для веба |
| `web/assets/` | опубликованные CSS/JS-ресурсы |
| `yii` | консольная точка входа (`php yii <маршрут>`) |

## Входной скрипт и константы окружения

```php
<?php
// web/index.php
defined('YII_DEBUG') or define('YII_DEBUG', true);
defined('YII_ENV') or define('YII_ENV', 'dev');

require __DIR__ . '/../vendor/autoload.php';           // автозагрузчик Composer
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';   // класс Yii

$config = require __DIR__ . '/../config/web.php';
(new yii\web\Application($config))->run();
```

| Константа | Значение по умолчанию | Смысл |
|---|---|---|
| `YII_DEBUG` | `false` | подробные ошибки и стек вызовов, больше логов. Только для разработки |
| `YII_ENV` | `'prod'` | окружение; даёт `YII_ENV_DEV`, `YII_ENV_PROD`, `YII_ENV_TEST` |
| `YII_ENABLE_ERROR_HANDLER` | `true` | включать ли обработчик ошибок Yii |

Консольная точка входа отличается только классом приложения:

```php
$application = new yii\console\Application($config);
exit($application->run());   // код возврата = exit code
```

## Настройка веб-сервера

**Nginx** (PHP-FPM):

```nginx
server {
    listen 80;
    server_name mysite.test;
    root /path/to/basic/web;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }
    location ~ \.php$ {
        include fastcgi.conf;
        fastcgi_pass 127.0.0.1:9000;
    }
    location ~ /\.(ht|svn|git) { deny all; }
}
```

**Apache** (`.htaccess` или конфиг хоста):

```apacheconf
DocumentRoot "path/to/basic/web"
<Directory "path/to/basic/web">
    RewriteEngine on
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . index.php
</Directory>
```

> Совет: при `nginx` + `fastcgi` поставьте `cgi.fix_pathinfo=0` в `php.ini`, а для HTTPS
> передавайте `fastcgi_param HTTPS on;`, иначе Yii не определит защищённое соединение.

## Жизненный цикл запроса — коротко

1. Запрос приходит в `web/index.php`.
2. Скрипт грузит конфиг и создаёт объект приложения.
3. Компонент `request` + `urlManager` разбирают URL в **маршрут** `контроллер/действие`.
4. Создаётся контроллер, затем действие; выполняются **фильтры** (`beforeAction`).
5. Действие работает с моделью и рендерит представление.
6. Результат попадает в компонент `response` и отправляется клиенту.

## Минимальный «Hello»: действие + представление

```php
// controllers/SiteController.php
namespace app\controllers;

use yii\web\Controller;

class SiteController extends Controller
{
    public function actionSay($message = 'Привет')
    {
        return $this->render('say', ['message' => $message]);
    }
}
```

```php
// views/site/say.php
<?php use yii\helpers\Html; ?>
<?= Html::encode($message) ?>
```

Открывается как `index.php?r=site/say&message=Мир`. Правила именования:

| Идентификатор | Класс / метод |
|---|---|
| контроллер `post-comment` | `app\controllers\PostCommentController` |
| контроллер `admin/post` | `app\controllers\admin\PostController` |
| действие `create-comment` | `public function actionCreateComment()` |

## Быстрый старт с БД

```php
// config/db.php
return [
    'class' => 'yii\db\Connection',
    'dsn' => 'mysql:host=localhost;dbname=yii2basic',
    'username' => 'root',
    'password' => '',
    'charset' => 'utf8mb4',
];
```

```php
// models/Country.php — таблица определяется по имени класса
namespace app\models;

class Country extends \yii\db\ActiveRecord {}
```

```php
$countries = Country::find()->orderBy('name')->all();
$country = Country::findOne('US');
$country->name = 'U.S.A.';
$country->save();
```

## Gii — генератор кода

Gii включён в шаблонах приложений в dev-режиме:

```php
// config/web.php
if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = [
        'class' => 'yii\gii\Module',
        'allowedIPs' => ['127.0.0.1', '::1', '192.168.0.*'],
    ];
}
```

Открывается по `index.php?r=gii`. Умеет генерировать:

- **Model Generator** — AR-класс по таблице;
- **CRUD Generator** — контроллер + `SearchModel` + views (index/create/update/view);
- генераторы модуля, формы, расширения, контроллера.

Есть и консольный вариант: `php yii gii/model --tableName=country --modelClass=Country`.

## Отладочная панель

Расширение `yiisoft/yii2-debug` (в шаблонах уже есть) показывает панель снизу страницы:
запросы к БД, логи, профилирование, таймлайн, конфигурацию, письма.

```php
if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'debug';
    $config['modules']['debug'] = [
        'class' => 'yii\debug\Module',
        'allowedIPs' => ['127.0.0.1', '::1'],
    ];
}
```

> Важно: `gii` и `debug` **никогда** не включаются на продакшене — это прямой доступ к
> генерации файлов и внутренностям приложения.
