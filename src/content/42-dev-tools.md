---
id: dev-tools
title: Gii, отладчик и другие инструменты
part: tools
summary: Генератор кода Gii — установка, allowedIPs, генераторы Model/CRUD/Controller/Form/Module/Extension, консольный режим и свои шаблоны; панель отладки yii2-debug — панели, профилирование, allowedIPs; apidoc, встроенный сервер и полезные команды.
sources: start-gii
---

:::lead
Два расширения, которые в dev-режиме подключены в каждом шаблоне: **Gii** генерирует модели и CRUD по таблице, **Debug** показывает запросы, логи, время и память прямо под страницей. Плюс `apidoc` для документации по PHPDoc и мелочи вроде `./yii serve`.
:::

## Gii

### Подключение

```php title="config/web.php"
if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = [
        'class' => 'yii\gii\Module',
        'allowedIPs' => ['127.0.0.1', '::1', '192.168.0.*'],   // по умолчанию только localhost
        // 'generators' => ['crud' => ['class' => 'yii\gii\generators\crud\Generator', 'templates' => ['my' => '@app/gii/crud']]],
    ];
}
```

`composer require --dev yiisoft/yii2-gii` (в шаблонах уже есть). Открыть: `/index.php?r=gii` или `/gii` с красивыми URL. **Только dev** — генератор пишет файлы в проект.

### Генераторы

:::kv
**Model** — класс AR по таблице: `tableName()`, `rules()` по типам столбцов, `attributeLabels()`, связи по внешним ключам (`generateRelations`), опционально `Query`-класс и `{{%…}}`
**CRUD** — контроллер + `Search`-модель + представления `index/view/create/update/_form` с `GridView`/`DetailView`/`ActiveForm`; опции: виджет списка (GridView/ListView), Pjax, i18n, базовый класс контроллера
**Controller** — контроллер с действиями и пустыми представлениями
**Form** — представление формы по существующей модели
**Module** — каркас модуля: `Module.php`, `controllers/DefaultController.php`, `views/default/index.php`
**Extension** — каркас расширения с `composer.json`
:::

Каждый генератор показывает превью файлов и diff с существующими — можно выбрать, что перезаписать. Сгенерированный код — отправная точка: правила и подписи стоит проверить.

### Консольный режим

```bash
./yii help gii
./yii gii/model --tableName=post --modelClass=Post --ns=app\\models --generateRelations=all
./yii gii/crud --modelClass=app\\models\\Post --searchModelClass=app\\models\\PostSearch \
    --controllerClass=app\\controllers\\PostController --viewPath=@app/views/post --enablePjax=1
./yii gii/controller --controllerClass=app\\controllers\\ReportController --actions=index,export
./yii gii/module --moduleID=admin --moduleClass=app\\modules\\admin\\Module
```

Для консоли модуль `gii` подключают в `config/console.php`. Полезно в CI и скриптах инициализации.

### Свои шаблоны и генераторы

Скопировать `vendor/yiisoft/yii2-gii/src/generators/crud/default` в `@app/gii/crud`, поправить и указать в `templates` генератора — в форме появится выбор шаблона. Свой генератор — класс `extends yii\gii\Generator` с формой (`form.php`), `generate()` и `templates`; регистрируется в `generators` модуля.

## Панель отладки (yii2-debug)

```php title="config/web.php"
if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'debug';
    $config['modules']['debug'] = [
        'class' => 'yii\debug\Module',
        'allowedIPs' => ['127.0.0.1', '::1'],
        // 'panels' => ['queue' => ...], 'historySize' => 50, 'dataPath' => '@runtime/debug',
    ];
}
```

Внизу страницы — тулбар; клик открывает панели по последним запросам (`/debug`):

| Панель | Что показывает |
|---|---|
| Config | версии PHP/Yii, конфигурация приложения, phpinfo |
| Request | параметры, заголовки, сессия, cookies, тело ответа |
| Logs | всё из `Yii::info/warning/error/debug` с категориями и фильтром |
| Profiling | `Yii::beginProfile()`/`endProfile()` — время и память по блокам |
| Database | все SQL-запросы с временем; дубли; кнопка EXPLAIN |
| Asset Bundles | какие бандлы и файлы подключены |
| Mail | отправленные письма (при `useFileTransport`) |
| User | identity, роли/разрешения RBAC, переключение пользователя |
| Router | правила `urlManager`, какое сработало |
| Events, Timeline, Dump | события за запрос, шкала времени, переменные `Yii::debug()` |

```php
Yii::beginProfile('import');
// ...
Yii::endProfile('import');
Yii::debug($data, 'my.category');    // видно в панели Logs (и Dump)
```

AJAX-запросы тоже попадают в историю. В production модуль не подключают: даже с `allowedIPs` он раскрывает конфигурацию.

## Другие инструменты

:::kv
`./yii serve --port=8080 --docroot=web` — встроенный PHP-сервер для разработки
`./yii help` — все команды; `./yii help <cmd>` — параметры
`vendor/bin/apidoc api src docs/api` — HTML-документация по PHPDoc (`yiisoft/yii2-apidoc`); `apidoc guide` — рендер markdown-руководств в стиле yiiframework.com
`./yii cache/flush-all`, `./yii asset` — кэш и сборка ассетов
`Yii::getVersion()`, `phpinfo()` в панели Config — версии
`composer outdated`, `composer show yiisoft/*` — версии пакетов
:::

> [!TIP] Быстрый CRUD за пять минут
> Миграция (`migrate/create create_post_table --fields=…`) → `./yii migrate` → Gii Model → Gii CRUD → открыть `/post`. Дальше — правки под задачу: права в `behaviors()`, поля в `_form.php`, фильтры в `PostSearch`.

:::quiz Проверь себя
Q: Почему Gii и Debug открываются только с localhost?
A: `allowedIPs` по умолчанию `['127.0.0.1', '::1']`; для других адресов их нужно добавить явно, и только в dev.
Q: Что генерирует CRUD-генератор помимо контроллера?
A: Поисковую модель (`PostSearch`) и представления `index`, `view`, `create`, `update`, `_form`.
Q: Как сгенерировать модель из консоли?
A: `./yii gii/model --tableName=post --modelClass=Post` (модуль `gii` должен быть в консольной конфигурации).
Q: Где посмотреть все SQL-запросы страницы и их время?
A: Панель Database отладчика; дубликаты и EXPLAIN — там же.
Q: Как измерить время участка кода в панели Profiling?
A: Обернуть в `Yii::beginProfile('name')` / `Yii::endProfile('name')`.
:::
