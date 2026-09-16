---
id: assets
title: Ресурсы и клиентские скрипты
part: structure
summary: Asset bundles — единственно правильный способ подключать JS и CSS: зависимости, публикация, Bower/NPM через Composer, объединение и сжатие, а также registerJs/registerCss и yii.js.
sources: structure-assets, output-client-scripts
---

:::lead
Ресурсы (assets) — JS, CSS, картинки, шрифты. Yii управляет ими **пакетами** (`AssetBundle`): пакет знает, где лежат файлы, от каких других пакетов зависит, и сам публикует их в веб-доступную папку. Зарегистрировал пакет в представлении — теги `<link>` и `<script>` появились в нужном порядке.
:::

## Пакет ресурсов

```php title="assets/AppAsset.php"
namespace app\assets;

use yii\web\AssetBundle;

class AppAsset extends AssetBundle
{
    public $basePath = '@webroot';          // файлы уже доступны из веба
    public $baseUrl = '@web';
    public $css = ['css/site.css'];
    public $js = ['js/app.js'];
    public $depends = [
        'yii\web\YiiAsset',                 // jQuery + yii.js
        'yii\bootstrap5\BootstrapAsset',
    ];
}
```

```php title="views/layouts/main.php"
<?php
use app\assets\AppAsset;
AppAsset::register($this);   // $this — объект View; в виджете: $this->view
?>
```

:::kv
`sourcePath` — папка с исходниками **вне** веб-корня (расширения, `@bower/...`). Файлы будут опубликованы в `@webroot/assets`
`basePath` + `baseUrl` — файлы **уже** в веб-корне, публиковать не нужно. Так делают для ресурсов самого приложения
`js`, `css` — списки файлов: относительные пути или абсолютные URL (CDN). Порядок сохраняется
`depends` — пакеты, которые должны быть подключены **раньше**. Зависимости транзитивны
`jsOptions`, `cssOptions` — параметры для `registerJsFile()`/`registerCssFile()`: `['position' => View::POS_HEAD]`, `['media' => 'print']`, `['condition' => 'lte IE9']`, `['noscript' => true]`
`publishOptions` — что публиковать: `['only' => ['css/*', 'fonts/*']]`, `forceCopy`, `beforeCopy`
:::

> [!GOTCHA]
> Не используйте `@webroot/assets` как `sourcePath` — эта папка принадлежит менеджеру ресурсов и может быть очищена. И не меняйте свойства пакета в `init()` или после `register()`: такие изменения перекроют настройки `assetManager->bundles` и сломают объединение ресурсов.

### Три вида ресурсов

- **Исходные** — лежат рядом с PHP-кодом, недоступны из веба; при регистрации публикуются (копируются или линкуются) в `@webroot/assets/<hash>/`.
- **Опубликованные** — уже в веб-папке (`basePath`/`baseUrl`).
- **Внешние** — на CDN, задаются полным URL.

## Bower и NPM через Composer

Основной способ — репозиторий [asset-packagist](https://asset-packagist.org) (в шаблонах basic/advanced с 2.0.13 уже настроен):

```json title="composer.json"
"repositories": [
    {"type": "composer", "url": "https://asset-packagist.org"}
],
"require": {
    "bower-asset/jquery": "^3.6",
    "npm-asset/chart.js": "^4.0"
}
```

```php
'aliases' => [
    '@bower' => '@vendor/bower-asset',
    '@npm' => '@vendor/npm-asset',
],
```

Дальше пакет ссылается на них через `sourcePath = '@npm/chart.js/dist'`. Альтернатива — глобальный плагин `fxp/composer-asset-plugin`, но он заметно медленнее.

## Настройка через assetManager

Все пакеты можно перенастроить централизованно, не трогая их классы:

```php
'assetManager' => [
    'bundles' => [
        'yii\web\JqueryAsset' => [
            'sourcePath' => null,                         // не публиковать
            'js' => ['//code.jquery.com/jquery-3.7.1.min.js'],   // взять с CDN
        ],
        'yii\bootstrap5\BootstrapPluginAsset' => false,   // отключить пакет совсем
    ],
    'assetMap' => [
        'jquery.js' => '//code.jquery.com/jquery-3.7.1.min.js',   // заменить файл во всех пакетах
    ],
    'linkAssets' => true,        // публиковать симлинками, а не копированием
    'appendTimestamp' => true,   // /assets/abc/yii.js?v=1423448645 — сброс кеша браузера
],
```

`'bundles' => false` отключает все пакеты — полезно, когда фронтенд собирается отдельно.

## Препроцессоры

В `css`/`js` можно перечислять `.less`, `.scss`, `.styl`, `.coffee`, `.ts` — `AssetConverter` вызовет установленный компилятор (`lessc`, `sass`, `tsc`…) и подключит результат. Команды настраиваются в `assetManager.converter.commands`. Чаще, впрочем, сборку доверяют внешним инструментам и в пакет включают уже готовые файлы.

## Объединение и сжатие

На проде десятки файлов хочется склеить в один CSS и один JS. Идея: создать «сводный» пакет и заставить остальные зависеть от него с пустыми `js`/`css`. Команда `yii asset` делает это автоматически:

```bash
yii asset/template assets.php          # шаблон конфигурации
yii asset assets.php config/assets-prod.php   # объединить, сжать, сгенерировать конфиг пакетов
```

```php title="assets.php (фрагмент)"
return [
    'jsCompressor' => 'java -jar compiler.jar --js {from} --js_output_file {to}',
    'cssCompressor' => 'java -jar yuicompressor.jar --type css {from} -o {to}',
    'bundles' => ['app\assets\AppAsset', 'yii\web\YiiAsset'],
    'targets' => [
        'all' => [
            'class' => 'yii\web\AssetBundle',
            'basePath' => '@webroot/assets',
            'baseUrl' => '@web/assets',
            'js' => 'js/all-{hash}.js',
            'css' => 'css/all-{hash}.css',
        ],
    ],
    'assetManager' => ['basePath' => '@webroot/assets', 'baseUrl' => '@web/assets'],
];
```

Несколько `targets` (например, `allShared`, `allBackEnd`, `allFrontEnd`) группируют пакеты; цель с пустым `depends` собирает всё оставшееся. Результат подключают по окружению:

```php
'assetManager' => [
    'bundles' => require __DIR__ . '/' . (YII_ENV_PROD ? 'assets-prod.php' : 'assets-dev.php'),
],
```

## Регистрация скриптов и стилей напрямую

Для мелких динамических кусков — методы `View`:

```php
$this->registerJs(
    "$('#myButton').on('click', function () { alert('Clicked'); });",
    View::POS_READY,          // POS_HEAD | POS_BEGIN | POS_END | POS_READY (по умолчанию) | POS_LOAD
    'my-button-handler'       // ключ: повторная регистрация заменит, а не продублирует
);
$this->registerJsFile('@web/js/main.js', ['depends' => [\yii\web\JqueryAsset::class]]);
$this->registerCss('body { background: #f00; }');
$this->registerCssFile('@web/css/print.css', ['media' => 'print'], 'css-print');
```

`POS_READY` и `POS_LOAD` оборачивают код в `jQuery(function(){})` и автоматически подключают `JqueryAsset`.

### PHP-значения в JavaScript

Экранируйте через `Json::htmlEncode()` — иначе кавычки и `</script>` в данных сломают страницу:

```php
$options = ['baseUrl' => Yii::$app->request->baseUrl, 'language' => Yii::$app->language];
$this->registerJs('var appOptions = ' . \yii\helpers\Json::htmlEncode($options) . ';', View::POS_HEAD, 'app-options');
$this->registerJsVar('appOptions', $options, View::POS_HEAD);   // то же одной строкой (с 2.0.14)

$message = \yii\helpers\Json::htmlEncode(Yii::t('app', 'Button clicked!'));
$this->registerJs(<<<JS
    $('#myButton').on('click', function () { alert($message); });
JS);
```

> [!GOTCHA]
> В heredoc PHP подставит `$переменные` — это удобно для `$message`, но jQuery-вызовы вида `$('#id')` не пострадают: `$(` и `$.` PHP не трактует как переменные.

## Что даёт yii.js

`YiiAsset` подключает `yii.js` — небольшую библиотеку, на которой держатся встроенные виджеты:

- отправка CSRF-токена в AJAX-запросах (берётся из `Html::csrfMetaTags()`);
- атрибуты `data-method="post"` и `data-confirm="Точно удалить?"` на ссылках — так работает кнопка удаления в `GridView`;
- обработка заголовка `X-Redirect` для перенаправлений в AJAX-ответах;
- система модулей `yii.*` для клиентского кода виджетов (`yii.activeForm`, `yii.gridView`).

:::quiz Проверь себя
Q: Когда нужен `sourcePath`, а когда `basePath` + `baseUrl`?
A: `sourcePath` — если файлы лежат вне веб-корня и их надо опубликовать (расширения, npm-пакеты). `basePath`/`baseUrl` — если файлы уже в `web/` и публикация не нужна.
Q: Зачем указывать `depends`?
A: Чтобы гарантировать порядок подключения: файлы пакета выводятся после файлов всех его зависимостей (например, плагин после jQuery).
Q: Как заставить браузер забрать новую версию `site.css` после деплоя?
A: `'appendTimestamp' => true` у `assetManager` — к URL добавится `?v=<время изменения файла>`.
Q: Что делает третий аргумент `registerJs($code, $pos, $key)`?
A: Ключ блока: повторная регистрация с тем же ключом заменяет предыдущую, а не добавляет дубликат. Без ключа ключом служит сам код.
Q: Почему не стоит менять свойства пакета внутри `init()`?
A: Такие изменения имеют приоритет над `assetManager->bundles` и ломают централизованную перенастройку и объединение ресурсов командой `yii asset`.
:::
