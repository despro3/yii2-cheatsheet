---
id: modules
title: Модули
part: structure
summary: Как упаковать часть функциональности в самостоятельный модуль: структура, класс Module, маршруты, доступ к модулю, вложенность и URL-правила.
sources: structure-modules
---

:::lead
Модуль — это «приложение в приложении»: свои контроллеры, модели, представления, компоненты и параметры. Модули не запускаются отдельно, но их удобно переиспользовать между проектами: форум, блог, админка, версия API.
:::

## Структура

```text
modules/forum/
    Module.php                  класс модуля (обязателен, в корне модуля)
    controllers/
        DefaultController.php   контроллер по умолчанию
        PostController.php
    models/
    views/
        layouts/                шаблоны модуля
        default/index.php       представления контроллера default
        post/
    migrations/
    config.php                  необязательно: конфигурация модуля
```

## Класс модуля

```php title="modules/forum/Module.php"
namespace app\modules\forum;

class Module extends \yii\base\Module
{
    public $controllerNamespace = 'app\modules\forum\controllers';   // так и по умолчанию

    public function init()
    {
        parent::init();
        $this->params['foo'] = 'bar';
        \Yii::configure($this, require __DIR__ . '/config.php');   // components, params… из файла

        if (\Yii::$app instanceof \yii\console\Application) {
            $this->controllerNamespace = 'app\modules\forum\commands';   // консольные команды модуля
        }
    }
}
```

Модуль — тоже [Service Locator](di): в нём можно регистрировать компоненты (`'components' => [...]`) и параметры, доступные как `$module->params`.

## Контроллеры и представления модуля

```php title="modules/forum/controllers/PostController.php"
namespace app\modules\forum\controllers;

class PostController extends \yii\web\Controller
{
    public function actionIndex()
    {
        return $this->render('index');   // modules/forum/views/post/index.php
    }
}
```

Шаблон модуля задаётся свойством `layout` модуля и ищется в `views/layouts` модуля; если не задан — используется шаблон приложения. Соглашения об именах те же, что у [контроллеров](controllers) приложения; отклонения — через `controllerMap` модуля.

## Подключение и маршруты

```php title="config/web.php"
'modules' => [
    'forum' => [
        'class' => 'app\modules\forum\Module',
        'params' => ['postsPerPage' => 20],
    ],
],
```

Маршрут внутри модуля начинается с его ID: `forum/post/index` → `PostController::actionIndex()` модуля `forum`. Маршрут `forum` целиком → `defaultRoute` модуля (`default`) → `DefaultController::actionIndex()`.

> [!NOTE]
> Консольные команды модуля появятся, только если модуль подключён и в `config/console.php`.

## Доступ к модулю из кода

```php
$module = \Yii::$app->getModule('forum');          // по ID
$module = \Yii::$app->controller->module;          // модуль текущего контроллера
$module = \app\modules\forum\Module::getInstance();  // экземпляр, созданный для текущего запроса (или null)

$max = $module->params['postsPerPage'];
```

> [!TIP]
> Не зашивайте ID модуля в его код: приложение может подключить его под любым именем. Берите `$module->id` у экземпляра.

## Предзагрузка и URL-правила

Модуль создаётся лениво — при первом обращении по маршруту. Если он должен работать в каждом запросе (например, добавлять свои правила ЧПУ), укажите его в `bootstrap` и реализуйте `BootstrapInterface`:

```php
'bootstrap' => ['forum'],
```

```php
class Module extends \yii\base\Module implements \yii\base\BootstrapInterface
{
    public function bootstrap($app)
    {
        $app->urlManager->addRules([
            ['class' => 'yii\web\GroupUrlRule', 'prefix' => 'forum', 'rules' => [
                'posts' => 'post/index',
                'post/<id:\d+>' => 'post/view',
            ]],
        ], false);
    }
}
```

> [!GOTCHA]
> Добавлять правила в `init()` модуля бесполезно: к моменту создания модуля маршрут уже разобран. Только `bootstrap()`. Для модулей-версий API правила проще описать прямо в `urlManager` приложения.

## Вложенные модули

```php
class Module extends \yii\base\Module
{
    public function init()
    {
        parent::init();
        $this->modules = [
            'admin' => ['class' => 'app\modules\forum\modules\admin\Module'],
        ];
    }
}
```

Маршрут: `forum/admin/dashboard/index`. `getModule('admin')` работает только для прямых потомков; все загруженные модули — в `Yii::$app->loadedModules`.

## Когда нужны модули

- Крупное приложение, которое делится на области ответственности (каждую ведёт своя команда).
- Функциональность, которую вы будете переносить между проектами: пользователи, комментарии, платежи.
- Версии REST API (`v1`, `v2`) — см. [REST: версионирование](rest-advanced).

Если группировать контроллеры хочется, а всё остальное общее, — достаточно подпапки в `controllers/` (маршрут `admin/post`), модуль не нужен.

:::quiz Проверь себя
Q: Какой метод будет вызван для маршрута `forum` без контроллера и действия?
A: `defaultRoute` модуля (по умолчанию `default`) и `defaultAction` контроллера — `DefaultController::actionIndex()`.
Q: Почему URL-правила модуля нельзя добавить в `init()`?
A: Модуль создаётся при разборе маршрута, когда `UrlManager::parseRequest()` уже отработал. Правила добавляют в `bootstrap()` модуля, включённого в `bootstrap` приложения.
Q: Как получить экземпляр модуля, не зная, под каким ID его подключили?
A: `MyModule::getInstance()` — вернёт экземпляр, обслуживающий текущий запрос, или `Yii::$app->controller->module`.
Q: Что общего у модуля и приложения?
A: Приложение — потомок `yii\base\Module`: у обоих есть `components`, `params`, `modules`, `controllerNamespace`, `layout`, события `beforeAction`/`afterAction`.
:::
