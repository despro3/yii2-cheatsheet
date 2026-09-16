---
id: install
title: Установка и запуск
part: start
summary: Ставим Yii через Composer, разбираем структуру шаблона basic, настраиваем Apache/Nginx, окружения, Docker и виртуальный хостинг.
sources: start-installation, start-workflow, tutorial-shared-hosting, tutorial-docker, tutorial-start-from-scratch
---

:::lead
Yii ставится одной командой Composer вместе с готовым шаблоном приложения. После установки у вас уже есть работающий сайт с формой входа, обратной связью, отладочной панелью и консольным скриптом — дальше это целиком ваш код.
:::

## Установка

:::tabs
=== Composer (рекомендуется)
```bash
# шаблон basic — один сайт, простая структура
composer create-project --prefer-dist yiisoft/yii2-app-basic basic

# шаблон advanced — frontend + backend + console, окружения, регистрация из коробки
composer create-project --prefer-dist yiisoft/yii2-app-advanced advanced
cd advanced && php init          # выбрать окружение (Development / Production)
```

Composer сам сгенерирует `cookieValidationKey`. Нестабильную версию можно поставить с `--stability=dev`, но на боевых серверах так делать не стоит.
=== Из архива
1. Скачайте архив с [yiiframework.com/download](https://www.yiiframework.com/download/).
2. Распакуйте в папку, доступную веб-серверу.
3. В `config/web.php` впишите секретный ключ в `cookieValidationKey` — без него куки не валидируются.
:::

> [!NOTE]
> При установке Composer делает много запросов к GitHub API и может упереться в лимит — тогда он попросит логин или токен. Проще заранее настроить [токен доступа](https://getcomposer.org/doc/articles/troubleshooting.md#api-rate-limit-and-oauth-tokens).

### Проверка

Откройте `http://localhost/basic/web/index.php` — должна появиться страница «Congratulations!». Если нет, проверьте требования:

```bash
cd basic && php requirements.php     # или откройте /requirements.php в браузере
```

Минимум — PHP с расширением PDO и драйвером вашей СУБД. Тестовые данные для входа в шаблоне: `admin` / `admin`.

## Структура шаблона basic

```text
basic/
    composer.json       описание проекта и зависимостей
    config/             конфигурация
        web.php         веб-приложение
        console.php     консольное приложение
        db.php          подключение к БД
        params.php      произвольные параметры (Yii::$app->params)
    commands/           консольные команды
    controllers/        контроллеры
    models/             модели
    views/              представления и шаблоны (layouts/)
    web/                корень для веб-сервера — единственная папка, доступная снаружи
        assets/         опубликованные ресурсы (JS/CSS), создаётся автоматически
        index.php       входной скрипт
    runtime/            логи, кеш, временные файлы — должна быть доступна на запись
    vendor/             пакеты Composer, включая сам фреймворк
    yii                 консольный входной скрипт: ./yii help
```

Два класса файлов: то, что лежит в `web/`, доступно по HTTP; всё остальное — нет и не должно быть. Именно поэтому корнем сайта делают `basic/web`, а не `basic`.

:::cols
=== basic
- одно приложение, один `web/`;
- удобен для небольших проектов и обучения;
- всё в пространстве имён `app\`.
=== advanced
- три приложения: `frontend`, `backend`, `console`, общий код в `common`;
- окружения через `php init` и папку `environments/`;
- регистрация, восстановление пароля и миграция пользователей из коробки;
- псевдонимы `@frontend`, `@backend`, `@common`, `@console`.
:::

## Настройка веб-сервера

На проде URL `https://example.com/basic/web/index.php` хочется превратить в `https://example.com/`. Для этого корень сервера указывают на `basic/web`, а `index.php` прячут правилами перезаписи (см. [ЧПУ](routing)).

:::tabs
=== Nginx
```nginx
server {
    charset utf-8;
    client_max_body_size 128M;
    listen 80;
    server_name mysite.test;
    root        /path/to/basic/web;
    index       index.php;

    location / {
        # всё, чего нет на диске, отдаём index.php
        try_files $uri $uri/ /index.php$is_args$args;
    }

    location ~ \.php$ {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass 127.0.0.1:9000;      # или unix:/var/run/php-fpm.sock
        try_files $uri =404;
    }

    location ~* /\. { deny all; }
}
```

В `php.ini` поставьте `cgi.fix_pathinfo=0`, а при HTTPS добавьте `fastcgi_param HTTPS on;`, иначе Yii не поймёт, что соединение защищённое.
=== Apache
```apache
DocumentRoot "/path/to/basic/web"

<Directory "/path/to/basic/web">
    RewriteEngine on
    # существующие файлы и папки отдаём как есть
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    # остальное — на index.php
    RewriteRule . index.php
</Directory>
```

Тот же блок правил можно положить в `web/.htaccess`, если нет доступа к конфигу сервера.
:::

## Режимы и окружения

Входной скрипт `web/index.php` задаёт две константы до загрузки фреймворка:

```php
defined('YII_DEBUG') or define('YII_DEBUG', true);   // подробные ошибки, отладочная панель
defined('YII_ENV') or define('YII_ENV', 'dev');      // dev | prod | test
```

| Константа | Что даёт |
|---|---|
| `YII_DEBUG = true` | подробные страницы ошибок со стеком, больше логов. На проде — `false` |
| `YII_ENV = 'dev'` | `YII_ENV_DEV === true`: в конфиге включаются модули `debug` и `gii` |
| `YII_ENV = 'prod'` | значение по умолчанию, `YII_ENV_PROD === true` |
| `YII_ENV = 'test'` | окружение для тестов, `YII_ENV_TEST === true` |

> [!GOTCHA]
> Не выкладывайте `YII_DEBUG = true` на боевой сервер: страница ошибки покажет посетителю исходный код и параметры окружения. В шаблоне advanced это решается `php init --env=Production`.

## Что уже есть в приложении

- Четыре страницы: главная, About, Contact (форма обратной связи, шлёт письмо) и Login.
- Внизу каждой страницы в режиме `dev` — панель [отладчика](dev-tools): запросы к БД, логи, профилирование.
- Консольный скрипт `./yii` для миграций, генерации кода и своих команд — см. [Консольные команды](console).

## Виртуальный хостинг

На shared-хостинге обычно один webroot (`www`, `htdocs`, `public_html`) и нет доступа к конфигу сервера:

:::steps
1. **Переименуйте `web/`** в имя webroot хостинга (например, `public_html`) ещё локально, а остальные папки загрузите на уровень выше.
2. **Для Apache положите `.htaccess`** с правилами перезаписи рядом с `index.php` (см. выше). Для Nginx ничего не нужно.
3. **Проверьте требования**, скопировав `requirements.php` в webroot, и удалите его после проверки.
4. **Для advanced** сведите два webroot в один: содержимое `frontend/web` → `www/`, `backend/web` → `www/admin/`, поправив пути в `index.php`. Разведите куки и сессии бэкенда — свои `csrfParam`, имя `identityCookie`, имя сессии и `path => '/admin'` — иначе они пересекутся с фронтендом.
:::

## Docker

Официальные образы — [yii2-docker](https://github.com/yiisoft/yii2-docker); шаблон basic поддерживает Docker из коробки.

```bash
docker-compose up -d                          # поднять все сервисы в фоне
docker-compose ps                             # что запущено
docker-compose logs -f                        # хвост логов
docker-compose run --rm php composer install  # разовая команда в новом контейнере
docker-compose exec php bash                  # шелл в работающем контейнере
docker-compose stop                           # остановить
docker-compose down -v                        # остановить и удалить вместе с томами (данные!)
```

## Свой шаблон проекта

Шаблон — это обычный репозиторий с `composer.json`, зарегистрированный как пакет. Клонируйте `yii2-app-basic`, удалите `.git`, поправьте `name`, `description`, `require`, обновите README, опубликуйте на Packagist (или в своём репозитории Composer) — и создавайте проекты через `composer create-project vendor/yii2-app-mytemplate`. В `extra.writable` composer.json перечисляют папки, которым после установки нужны права на запись.

:::quiz Проверь себя
Q: Почему корнем веб-сервера делают `basic/web`, а не `basic`?
A: Снаружи должен быть доступен только входной скрипт и статика. Конфиги, код, `runtime/` и `vendor/` остаются недосягаемыми по HTTP.
Q: Что произойдёт, если оставить `YII_DEBUG = true` на боевом сервере?
A: Страницы ошибок будут показывать стек вызовов и фрагменты исходного кода всем посетителям — утечка информации о внутренностях приложения.
Q: Чем шаблон advanced отличается от basic?
A: Три отдельных приложения (frontend, backend, console) с общим `common`, механизм окружений `php init`, готовые регистрация и восстановление пароля.
Q: Зачем на Nginx ставить `fastcgi_param HTTPS on`?
A: Чтобы `Yii::$app->request->isSecureConnection` возвращал `true` и генерировались правильные абсолютные URL при HTTPS.
Q: Как одной командой проверить, подходит ли сервер под требования Yii?
A: `php requirements.php` в корне проекта (или открыть `/requirements.php` в браузере).
:::
