---
id: extensions
title: Расширения и сторонний код
part: structure
summary: Как ставить расширения через Composer, как оформить своё (composer.json, bootstrap-класс, ресурсы, миграции), список официальных расширений и как подружить Yii с чужими библиотеками и системами.
sources: structure-extensions, tutorial-yii-integration
---

:::lead
Расширение — Composer-пакет типа `yii2-extension`: виджеты, модули, хелперы, компоненты. Устанавливается одной командой, автозагружается сам, при необходимости регистрирует свой bootstrap-код. Обычные библиотеки (не для Yii) подключаются так же через Composer.
:::

## Установка

```bash
composer require yiisoft/yii2-imagine "~2.0.0"
```

```php
use yii\imagine\Image;

Image::thumbnail('@webroot/img/test-image.jpg', 120, 120)
    ->save(Yii::getAlias('@runtime/thumb.jpg'), ['quality' => 50]);
```

Composer обновляет `vendor/yiisoft/extensions.php` — из него приложение узнаёт о расширениях, их псевдонимах и bootstrap-классах. Классы загружаются автозагрузчиком без настройки.

### Вручную, без Composer

Распаковать в `vendor/`, подключить автозагрузчик библиотеки (если есть) или объявить псевдоним для PSR-4-совместимого кода:

```php
'aliases' => ['@myext' => '@vendor/mycompany/myext'],   // классы myext\Foo → vendor/mycompany/myext/Foo.php
```

## Официальные расширения

:::cards
- **Инструменты** — `yii2-debug` (панель отладки), `yii2-gii` (генератор кода), `yii2-apidoc` (документация API), `yii2-faker` (тестовые данные).
- **UI** — `yii2-bootstrap` / `yii2-bootstrap4` / `yii2-bootstrap5` (виджеты Bootstrap), `yii2-jui` (jQuery UI).
- **Данные** — `yii2-redis`, `yii2-mongodb`, `yii2-elasticsearch`, `yii2-sphinx`: Active Record, кеш, сессии для NoSQL-хранилищ.
- **Сервисы** — `yii2-httpclient` (HTTP-клиент), `yii2-authclient` (OAuth: Google, GitHub, Facebook…), `yii2-symfonymailer` / `yii2-swiftmailer` (почта), `yii2-imagine` (картинки).
- **Шаблонизаторы** — `yii2-twig`, `yii2-smarty`.
:::

Все — `yiisoft/yii2-*` на Packagist; каталог сообщества: [yiiframework.com/extensions](https://www.yiiframework.com/extensions/).

## Своё расширение

:::steps
1. **Репозиторий + `composer.json`.** Имя `vendor/yii2-name`, тип `yii2-extension`, зависимость от `yiisoft/yii2`, автозагрузка PSR-4.
2. **Пространство имён** `vendor\name` (без префикса `yii2-`). Слова `yii`, `yii2`, `yiisoft` в качестве vendor зарезервированы.
3. **Регистрация на Packagist** (или в своём репозитории Composer для приватных пакетов), теги версий по semver.
:::

```json title="composer.json"
{
    "name": "myname/yii2-mywidget",
    "type": "yii2-extension",
    "description": "Виджет для…",
    "license": "BSD-3-Clause",
    "require": {
        "yiisoft/yii2": "~2.0.0"
    },
    "autoload": {
        "psr-4": {"myname\\mywidget\\": "src/"}
    },
    "extra": {
        "bootstrap": "myname\\mywidget\\Bootstrap"
    }
}
```

Для каждого корневого пространства имён из `autoload` Yii создаст псевдоним (`@myname/mywidget`).

### Bootstrap-класс

Код, который должен выполняться при старте каждого запроса (регистрация URL-правил, обработчиков событий, зависимостей DI), выносят в класс с `BootstrapInterface` и указывают в `extra.bootstrap`:

```php
namespace myname\mywidget;

use yii\base\Application;
use yii\base\BootstrapInterface;

class Bootstrap implements BootstrapInterface
{
    public function bootstrap($app)
    {
        $app->on(Application::EVENT_BEFORE_REQUEST, function () {
            // ...
        });
        \Yii::$container->set('myname\mywidget\StorageInterface', 'myname\mywidget\FileStorage');
    }
}
```

### Рекомендации авторам

- **База данных**: не полагайтесь на `Yii::$app->db` — объявите свойство `db` (как у `yii\caching\DbCache`), чтобы пользователь мог подставить своё соединение. Схему меняйте [миграциями](migrations), без Active Record внутри них.
- **Ресурсы**: объявляйте [пакет ресурсов](assets) с `sourcePath` — публикация сделает файлы доступными из веба сама.
- **i18n**: пользовательские строки оборачивайте в `Yii::t()`, числа и даты форматируйте через `Formatter`.
- **Тесты, changelog, readme, upgrade.md**, документированный код в стиле ядра.

## Сторонние библиотеки в Yii

Пакеты Composer работают сразу — автозагрузчик `vendor/autoload.php` подключён во входном скрипте. Для библиотек без Composer:

- есть свой автозагрузчик — подключить его во входном скрипте до `Yii.php`;
- классы по PSR-4 — объявить псевдоним корневого пространства имён (`'@xyz' => '@vendor/foo/bar'`);
- совсем без автозагрузки — заполнить карту классов: `Yii::$classMap['Class1'] = 'path/to/Class1.php'`.

## Yii внутри другой системы

Active Record, хелперы, кеш и прочее можно использовать в WordPress, Joomla или приложении на другом фреймворке:

```bash
composer require yiisoft/yii2
```

```php title="входной скрипт сторонней системы"
require __DIR__ . '/../vendor/yiisoft/yii2/Yii.php';

$yiiConfig = require __DIR__ . '/../config/yii/web.php';
new yii\web\Application($yiiConfig);   // НЕ вызывать run(): обработка запроса остаётся за хост-системой
```

После этого доступен `Yii::$app` со всеми компонентами из конфигурации — например, `db` с настройками базы хост-системы. Если ресурсы (Bower/NPM) не нужны, пригодится пакет `cebe/assetfree-yii2`.

### Yii 2 рядом с Yii 1

Оба фреймворка используют класс `Yii`, поэтому нужен объединённый класс: наследник `yii\BaseYii`, куда скопирован код `YiiBase` из 1.x. Затем во входном скрипте создаётся приложение Yii 2 (без `run()`), а Yii 1 запускается как обычно. В коде: `Yii::$app` — приложение Yii 2, `Yii::app()` — Yii 1. Полный рецепт — в главе руководства «Работа со сторонним кодом».

:::quiz Проверь себя
Q: Зачем расширению тип пакета `yii2-extension`?
A: При установке Composer добавит его в `vendor/yiisoft/extensions.php`, и Yii узнает о псевдонимах и bootstrap-классе расширения автоматически.
Q: Как расширение может выполнить код при старте каждого запроса без правки конфигурации приложения?
A: Через класс, реализующий `BootstrapInterface`, указанный в `extra.bootstrap` файла `composer.json`.
Q: Почему в расширении не стоит писать `Yii::$app->db` напрямую?
A: Пользователь может держать данные в другом соединении; правильно — объявить настраиваемое свойство `db` компонента.
Q: Что нужно изменить во входном скрипте, чтобы использовать Yii как библиотеку в чужом приложении?
A: Создать `new yii\web\Application($config)`, но не вызывать `run()` — обработкой запроса занимается хост-система.
:::
