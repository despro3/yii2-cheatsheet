---
id: widgets
title: Виджеты, фильтры, ресурсы
icon: 🧩
summary: Виджеты, стандартные фильтры (ACF, VerbFilter, CORS, кеш), asset bundles, расширения.
sources: structure-widgets, structure-filters, structure-assets, structure-extensions
---

# Виджеты, фильтры и ресурсы

## Виджеты

Виджет — переиспользуемый блок UI: класс + собственные представления + собственные ресурсы.

```php
// вариант 1: всё сразу
<?= \yii\widgets\Menu::widget([
    'items' => [
        ['label' => 'Главная', 'url' => ['site/index']],
        ['label' => 'Вход', 'url' => ['site/login'], 'visible' => Yii::$app->user->isGuest],
    ],
]) ?>

// вариант 2: виджет с содержимым между begin() и end()
<?php $form = \yii\widgets\ActiveForm::begin(['id' => 'login-form']); ?>
    <?= $form->field($model, 'username') ?>
<?php \yii\widgets\ActiveForm::end(); ?>
```

Свой виджет:

```php
namespace app\components;

use yii\base\Widget;
use yii\helpers\Html;

class HelloWidget extends Widget
{
    public $message;

    public function init()
    {
        parent::init();
        $this->message ??= 'Hello World';
        // ob_start();  // если нужен захват содержимого между begin() и end()
    }

    public function run()
    {
        return $this->render('hello', ['message' => $this->message]);
        // или: return Html::encode(ob_get_clean());
    }
}
```

Представления виджета лежат в `<папка класса>/views/`. Глобальные значения по умолчанию для
виджета задаются через DI-контейнер:

```php
Yii::$container->set('yii\widgets\LinkPager', ['maxButtonCount' => 5]);
```

**Встроенные виджеты:** `ActiveForm`, `GridView`, `ListView`, `DetailView`, `Menu`,
`Breadcrumbs`, `LinkPager`, `LinkSorter`, `Pjax`, `Block`, `ContentDecorator`,
`MaskedInput`, `Captcha`, `Spaceless` + наборы `yii2-bootstrap*` и `yii2-jui`.

## Фильтры

Фильтр — это особый вид [поведения](#concepts), который выполняется до и/или после действия.
Объявляется в `behaviors()` контроллера (или модуля/приложения — тогда действует на всё).

```php
use yii\filters\AccessControl;
use yii\filters\VerbFilter;

public function behaviors()
{
    return [
        'access' => [
            'class' => AccessControl::class,
            'only' => ['create', 'update', 'delete'],   // или except => [...]
            'rules' => [
                ['allow' => true, 'actions' => ['create'], 'roles' => ['@']],
                ['allow' => true, 'roles' => ['admin']],
                ['allow' => true, 'ips' => ['192.168.*'], 'roles' => ['?']],
            ],
        ],
        'verbs' => [
            'class' => VerbFilter::class,
            'actions' => [
                'index' => ['get'],
                'create' => ['get', 'post'],
                'update' => ['get', 'put', 'post'],
                'delete' => ['post', 'delete'],
            ],
        ],
    ];
}
```

Порядок: пре-фильтры приложения → модуля → контроллера (в порядке `behaviors()`), затем
действие, затем пост-фильтры в **обратном** порядке. Если пре-фильтр отменил выполнение,
дальше ничего не запускается.

### Стандартные фильтры

| Фильтр | Что делает |
|---|---|
| `AccessControl` | правила доступа: `roles` (`?` гость, `@` авторизован, имя роли RBAC), `ips`, `verbs`, `matchCallback`, `denyCallback` |
| `VerbFilter` | разрешённые HTTP-методы для действий; иначе 405 |
| `ContentNegotiator` | выбор формата ответа и языка по `Accept`/GET-параметрам |
| `HttpCache` | `Last-Modified` / `ETag` — кеш на стороне клиента |
| `PageCache` | кеш всей страницы на сервере (`duration`, `dependency`, `variations`) |
| `RateLimiter` | ограничение частоты запросов (для REST API) |
| `Cors` | CORS-заголовки; ставится **до** фильтров аутентификации |
| `auth\HttpBasicAuth`, `auth\HttpBearerAuth`, `auth\QueryParamAuth`, `auth\CompositeAuth` | способы аутентификации (REST) |

Свой фильтр:

```php
namespace app\components;

use yii\base\ActionFilter;

class ActionTimeFilter extends ActionFilter
{
    private $_start;

    public function beforeAction($action)
    {
        $this->_start = microtime(true);
        return parent::beforeAction($action);   // false → действие не выполнится
    }

    public function afterAction($action, $result)
    {
        \Yii::debug('Действие ' . $action->uniqueId . ': ' . (microtime(true) - $this->_start));
        return parent::afterAction($action, $result);
    }
}
```

CORS вместе с родительскими поведениями:

```php
use yii\filters\Cors;
use yii\helpers\ArrayHelper;

public function behaviors()
{
    return ArrayHelper::merge([
        ['class' => Cors::class, 'cors' => [
            'Origin' => ['https://app.example.com'],
            'Access-Control-Request-Method' => ['GET', 'POST', 'OPTIONS'],
            'Access-Control-Allow-Credentials' => true,
            'Access-Control-Max-Age' => 86400,
        ]],
    ], parent::behaviors());
}
```

## Ресурсы (asset bundles)

Комплект ресурсов — класс, описывающий набор CSS/JS и их зависимости.

```php
namespace app\assets;

use yii\web\AssetBundle;
use yii\web\View;

class AppAsset extends AssetBundle
{
    public $basePath = '@webroot';      // файлы уже в вебруте — публикация не нужна
    public $baseUrl = '@web';
    // public $sourcePath = '@bower/some-lib';   // файлы вне вебрута → будут опубликованы
    public $css = ['css/site.css'];
    public $js = ['js/app.js'];
    public $jsOptions = ['position' => View::POS_END];
    public $cssOptions = ['media' => 'screen'];
    public $depends = [
        'yii\web\YiiAsset',
        'yii\bootstrap5\BootstrapAsset',
    ];
}
```

Регистрация в представлении/layout:

```php
\app\assets\AppAsset::register($this);
```

| Свойство | Смысл |
|---|---|
| `sourcePath` | исходники вне вебрута → публикуются в `@webroot/assets` |
| `basePath` / `baseUrl` | где файлы уже лежат и по какому URL доступны |
| `css`, `js` | относительные пути или абсолютные URL (CDN) |
| `depends` | другие комплекты; подключаются **раньше** |
| `jsOptions`, `cssOptions` | опции для `registerJsFile()` / `registerCssFile()` (`position`, `condition`, `noscript`, `defer`) |
| `publishOptions` | `only`, `except`, `beforeCopy`, `forceCopy` при публикации |

Настройка и подмена комплектов через `assetManager`:

```php
'components' => [
    'assetManager' => [
        'appendTimestamp' => true,          // ?v=123 — сброс кеша браузера
        'linkAssets' => true,               // symlink вместо копирования
        'bundles' => [
            'yii\web\JqueryAsset' => [      // взять jQuery с CDN
                'sourcePath' => null,
                'js' => ['//code.jquery.com/jquery-3.7.1.min.js'],
            ],
            'yii\bootstrap5\BootstrapAsset' => false,   // отключить комплект
        ],
        'assetMap' => [                     // подменить файл во всех комплектах
            'jquery.js' => '//code.jquery.com/jquery-3.7.1.min.js',
        ],
    ],
],
```

Готовые комплекты ядра: `yii\web\YiiAsset` (`yii.js`: `data-method`, `data-confirm`,
pjax-хелперы), `yii\web\JqueryAsset`, `yii\bootstrap5\BootstrapAsset` /
`BootstrapPluginAsset`, `yii\jui\JuiAsset`.

**LESS/SCSS/TypeScript:** перечислите `css/site.less` или `js/site.ts` — `AssetConverter`
вызовет внешний компилятор (`lessc`, `tsc`), команды настраиваются через
`assetManager.converter.commands`.

**Объединение и минификация:**

```bash
yii asset/template assets.php   # создать конфиг
yii asset assets.php config/assets-prod.php
```

```php
'assetManager' => [
    'bundles' => require __DIR__ . '/' . (YII_ENV_PROD ? 'assets-prod.php' : 'assets-dev.php'),
],
```

> Совет: `@webroot/assets` — служебная папка менеджера ресурсов; её содержимое считается
> временным и может быть удалено. Не указывайте её как `sourcePath`.

Bower/NPM-пакеты ставятся через Composer (репозиторий
`https://asset-packagist.org`) и доступны по алиасам `@bower/<пакет>`, `@npm/<пакет>`.

## Расширения

Расширение — обычный Composer-пакет с `"type": "yii2-extension"`.

```bash
composer require yiisoft/yii2-imagine
```

```json
{
    "name": "vendor/yii2-mywidget",
    "type": "yii2-extension",
    "require": { "yiisoft/yii2": "~2.0.0" },
    "autoload": { "psr-4": { "vendor\\mywidget\\": "" } },
    "extra": { "bootstrap": "vendor\\mywidget\\Bootstrap" }
}
```

- `autoload.psr-4` → Yii автоматически создаёт алиас (`@vendor/mywidget`).
- `extra.bootstrap` → класс с `BootstrapInterface::bootstrap($app)` выполняется на каждом
  запросе (удобно для регистрации URL-правил, обработчиков событий).
- Не используйте `yii`, `yii2`, `yiisoft` как имя вендора — они зарезервированы.
- В расширении не привязывайтесь к `Yii::$app->db` — заводите настраиваемое свойство `db`.

Официальные расширения: `yii2-debug`, `yii2-gii`, `yii2-bootstrap5`, `yii2-jui`,
`yii2-imagine`, `yii2-httpclient`, `yii2-authclient`, `yii2-redis`, `yii2-mongodb`,
`yii2-elasticsearch`, `yii2-sphinx`, `yii2-faker`, `yii2-twig`, `yii2-smarty`,
`yii2-symfonymailer`, `yii2-apidoc`.
