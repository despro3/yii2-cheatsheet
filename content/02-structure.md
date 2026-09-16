---
id: structure
title: Структура (MVC)
icon: 🏛️
summary: Приложение и его конфиг, компоненты, контроллеры, модели, представления, layout, модули.
sources: structure-entry-scripts, structure-applications, structure-application-components, structure-controllers, structure-models, structure-views, structure-modules
---

# Структура приложения: MVC по-Yii-евски

Приложение — глобальный объект-одиночка `Yii::$app`. Он же **Service Locator**: через него
достаются все компоненты (`Yii::$app->db`, `->user`, `->cache`, …). Всё приложение
описывается одним массивом конфигурации.

## Конфигурация приложения

```php
// config/web.php
return [
    'id' => 'basic',                       // обязателен: уникальный идентификатор
    'basePath' => dirname(__DIR__),        // обязателен: корень приложения (@app)
    'language' => 'ru-RU',
    'sourceLanguage' => 'en-US',
    'timeZone' => 'Europe/Kyiv',
    'defaultRoute' => 'site/index',
    'bootstrap' => ['log'],                // что грузить при каждом запросе
    'aliases' => ['@images' => '@webroot/images'],
    'components' => [
        'db' => require __DIR__ . '/db.php',
        'cache' => ['class' => 'yii\caching\FileCache'],
        'user' => [
            'identityClass' => 'app\models\User',
            'enableAutoLogin' => true,
        ],
        'urlManager' => [
            'enablePrettyUrl' => true,
            'showScriptName' => false,
            'rules' => ['post/<id:\d+>' => 'post/view'],
        ],
        'request' => ['cookieValidationKey' => 'секрет-из-переменной-окружения'],
    ],
    'modules' => ['admin' => ['class' => 'app\modules\admin\Module']],
    'params' => require __DIR__ . '/params.php',
];
```

### Основные свойства приложения

| Свойство | Назначение |
|---|---|
| `id`, `basePath` | обязательные: идентификатор и корень (даёт алиас `@app`) |
| `bootstrap` | компоненты/модули/классы, создаваемые на каждом запросе |
| `components` | реестр компонентов приложения |
| `modules` | подключённые модули |
| `params` | произвольные параметры: `Yii::$app->params['x']` |
| `controllerNamespace` | по умолчанию `app\controllers` |
| `controllerMap` | ручное сопоставление `id => класс контроллера` |
| `defaultRoute` | маршрут при пустом запросе (`site` для веба, `help` для консоли) |
| `layout`, `layoutPath`, `viewPath` | шаблоны и представления |
| `runtimePath`, `vendorPath` | алиасы `@runtime`, `@vendor` |
| `catchAll` | режим обслуживания: `['site/offline']` для всех запросов |
| `language`, `sourceLanguage`, `timeZone`, `charset` | локаль и окружение |

### События приложения

```php
// В конфиге — синтаксис "on <имя события>"
'on beforeRequest' => function ($event) { /* ... */ },

// Или в коде
Yii::$app->on(yii\base\Application::EVENT_BEFORE_ACTION, function ($event) {
    if (!$ok) { $event->isValid = false; }   // отменить выполнение действия
});
```

`EVENT_BEFORE_REQUEST` → `EVENT_BEFORE_ACTION` → действие → `EVENT_AFTER_ACTION` →
`EVENT_AFTER_REQUEST`. `beforeAction` поднимается в порядке приложение → модуль → контроллер,
`afterAction` — в обратном.

## Компоненты приложения

Регистрируются в `components`, создаются **лениво** — при первом обращении, дальше возвращается
тот же экземпляр (синглтон в рамках запроса).

```php
'components' => [
    'cache' => 'yii\caching\ApcCache',               // просто класс
    'db' => ['class' => 'yii\db\Connection', 'dsn' => '...'],   // конфиг-массив
    'search' => function () { return new app\components\SolrService; },  // фабрика
],
```

Встроенные компоненты, которые есть почти всегда:

| Компонент | Класс | Зачем |
|---|---|---|
| `request` | `yii\web\Request` | параметры запроса, заголовки, куки |
| `response` | `yii\web\Response` | код, заголовки, формат, тело ответа |
| `db` | `yii\db\Connection` | соединение с БД |
| `user` | `yii\web\User` | аутентификация, `identity`, `can()` |
| `session` | `yii\web\Session` | сессия и flash-сообщения |
| `urlManager` | `yii\web\UrlManager` | разбор и генерация URL |
| `view` | `yii\web\View` | рендеринг, регистрация JS/CSS |
| `assetManager` | `yii\web\AssetManager` | публикация ресурсов |
| `cache` | `yii\caching\*Cache` | кеш |
| `log` | `yii\log\Dispatcher` | логи |
| `errorHandler` | `yii\web\ErrorHandler` | ошибки и исключения |
| `formatter` | `yii\i18n\Formatter` | форматирование дат, чисел, размеров |
| `i18n` | `yii\i18n\I18N` | переводы `Yii::t()` |
| `mailer` | `yii\symfonymailer\Mailer` | почта |
| `security` | `yii\base\Security` | хеши, шифрование, токены |

> Совет: компоненты приложения — это глобальные переменные. Не выносите в них всё: локальный
> объект, созданный в нужном месте, обычно лучше для тестируемости.

## Контроллеры

```php
namespace app\controllers;

use Yii;
use yii\web\Controller;
use yii\web\NotFoundHttpException;
use app\models\Post;

class PostController extends Controller
{
    public $layout = 'post';              // свой layout для всего контроллера
    public $defaultAction = 'index';      // действие по умолчанию

    public function actions()             // «отдельные» действия классами
    {
        return [
            'error' => ['class' => 'yii\web\ErrorAction'],
            'captcha' => ['class' => 'yii\captcha\CaptchaAction'],
        ];
    }

    public function actionView($id, $version = null)   // параметры берутся из $_GET
    {
        $model = Post::findOne($id);
        if ($model === null) {
            throw new NotFoundHttpException('Пост не найден.');
        }
        return $this->render('view', ['model' => $model]);
    }

    public function actionCreate()
    {
        $model = new Post();
        if ($model->load(Yii::$app->request->post()) && $model->save()) {
            Yii::$app->session->setFlash('success', 'Сохранено');
            return $this->redirect(['view', 'id' => $model->id]);
        }
        return $this->render('create', ['model' => $model]);
    }
}
```

**Что может вернуть действие:**

| Возврат | Результат |
|---|---|
| строка | тело ответа (HTML) |
| массив/объект | будет отформатирован согласно `response->format` (JSON/XML) |
| `$this->render(...)` | представление + layout |
| `$this->renderPartial(...)` | представление без layout |
| `$this->renderAjax(...)` | без layout, но с зарегистрированными JS/CSS |
| `$this->redirect([...])` | объект `Response` с заголовком `Location` |
| `$this->goHome()`, `$this->goBack()` | редирект на главную / на запомненный URL |
| `$this->refresh()` | перезагрузка текущего URL |
| число (консоль) | exit code (`ExitCode::OK`) |

**Отдельное действие** (переиспользуемое):

```php
namespace app\components;

use yii\base\Action;

class HelloWorldAction extends Action
{
    public function run()        // роль та же, что у actionXxx()
    {
        return 'Hello World';
    }
}
```

### Жизненный цикл контроллера

1. `init()` после создания и конфигурирования;
2. создаётся действие (по `actions()` или методу `actionXxx`), иначе `InvalidRouteException`;
3. `beforeAction()` приложения → модуля → контроллера (`false` отменяет выполнение);
4. параметры действия заполняются из запроса, действие выполняется;
5. `afterAction()` контроллера → модуля → приложения;
6. результат передаётся в `response`.

> Важно: контроллеры должны быть тонкими — читать запрос, дёргать модели, отдавать
> представление. Обработка данных живёт в моделях, разметка — в представлениях.

## Модели

Наследуются от `yii\base\Model` (форма) или `yii\db\ActiveRecord` (таблица).
Дают: атрибуты, метки, сценарии, правила валидации, массовое присвоение, экспорт в массив.

```php
namespace app\models;

use yii\base\Model;

class ContactForm extends Model
{
    public $name;
    public $email;
    public $body;
    public $verifyCode;

    public function rules()
    {
        return [
            [['name', 'email', 'body'], 'required'],
            ['email', 'email'],
            ['verifyCode', 'captcha'],
        ];
    }

    public function attributeLabels()
    {
        return [
            'name' => Yii::t('app', 'Ваше имя'),
            'email' => Yii::t('app', 'Email'),
        ];
    }
}
```

```php
$model = new ContactForm();
$model->load(Yii::$app->request->post());    // массовое присвоение по имени класса
if ($model->validate()) { /* ... */ }
$errors = $model->errors;                    // ['email' => ['Email некорректен.']]
$model->hasErrors('email');
$model->getFirstError('email');
```

### Сценарии и безопасные атрибуты

```php
class User extends ActiveRecord
{
    const SCENARIO_LOGIN = 'login';
    const SCENARIO_REGISTER = 'register';

    public function scenarios()
    {
        return [
            self::SCENARIO_LOGIN => ['username', 'password'],
            self::SCENARIO_REGISTER => ['username', 'email', 'password', '!secret'],
        ];
    }

    public function rules()
    {
        return [
            [['username', 'email', 'password'], 'required', 'on' => self::SCENARIO_REGISTER],
            [['username', 'password'], 'required', 'on' => self::SCENARIO_LOGIN],
        ];
    }
}

$model = new User(['scenario' => User::SCENARIO_LOGIN]);
```

- Массовое присвоение (`load()`, `$model->attributes = [...]`) работает **только** для
  «безопасных» атрибутов — перечисленных в `scenarios()` текущего сценария.
- Префикс `!` («`!secret`») — атрибут валидируется, но массово не присваивается.
- Валидатор `safe` объявляет атрибут безопасным без проверки: `[['title'], 'safe']`.

### Экспорт данных

```php
$array = $model->attributes;                       // все атрибуты
$array = $model->toArray();                        // по fields()
$array = $model->toArray([], ['author', 'tags']);  // + extraFields()

public function fields()
{
    $fields = parent::fields();
    unset($fields['auth_key'], $fields['password_hash']);  // убрать секреты
    $fields['name'] = fn () => $this->first_name . ' ' . $this->last_name;
    return $fields;
}
```

> Важно: по умолчанию `toArray()`/REST-ответ отдаёт **все** атрибуты. Для моделей с
> паролями и токенами переопределяйте `fields()`.

## Представления и layout

```php
<?php
// views/post/view.php
use yii\helpers\Html;

/** @var yii\web\View $this */
/** @var app\models\Post $model */

$this->title = $model->title;
$this->params['breadcrumbs'][] = ['label' => 'Посты', 'url' => ['index']];
$this->params['breadcrumbs'][] = $this->title;
?>
<h1><?= Html::encode($model->title) ?></h1>
<div><?= \yii\helpers\HtmlPurifier::process($model->text) ?></div>
<?= $this->render('_comments', ['comments' => $model->comments]) ?>
```

| Метод | Где | Что делает |
|---|---|---|
| `$this->render($view, $params)` | контроллер | представление + layout |
| `$this->renderPartial()` | контроллер | без layout |
| `$this->renderAjax()` | контроллер | без layout, с JS/CSS |
| `$this->renderFile('@app/views/x.php')` | везде | по пути/алиасу |
| `$this->render()` | внутри вида/виджета | вложенный вид |

Поиск файла по имени вида: `about` → `@app/views/<controller-id>/about.php`,
`/about` → `views/` текущего модуля, `//site/about` → `@app/views/site/about.php`.

**Layout:**

```php
<?php $this->beginPage() ?>
<!DOCTYPE html>
<html lang="<?= Yii::$app->language ?>">
<head>
    <meta charset="<?= Yii::$app->charset ?>">
    <?= Html::csrfMetaTags() ?>
    <title><?= Html::encode($this->title) ?></title>
    <?php $this->head() ?>
</head>
<body>
<?php $this->beginBody() ?>
    <?= $content ?>
<?php $this->endBody() ?>
</body>
</html>
<?php $this->endPage() ?>
```

Выбор layout: `Controller::$layout` → ближайший модуль с заданным `layout` → приложение.
`false` отключает layout. Вложенные layout — `beginContent('@app/views/layouts/base.php')` …
`endContent()`.

**Полезное в представлениях:**

```php
$this->title = 'Заголовок';
$this->registerMetaTag(['name' => 'description', 'content' => '...'], 'description');
$this->registerLinkTag(['rel' => 'canonical', 'href' => Url::canonical()]);
$this->registerCss('.red { color: red }');
$this->registerJs('alert(1);', \yii\web\View::POS_READY);
$this->registerJsFile('@web/js/app.js', ['depends' => [\yii\web\YiiAsset::class]]);

// блоки: записать в виде, вывести в layout
$this->beginBlock('sidebar'); echo '...'; $this->endBlock();
echo $this->blocks['sidebar'] ?? '';

// данные между видом и layout
$this->params['breadcrumbs'][] = 'О нас';
```

> Важно: любой вывод пользовательских данных — через `Html::encode()`, а HTML от
> пользователя — через `HtmlPurifier::process()` (медленно, кешируйте результат).

## Модули

Мини-приложение внутри приложения: свои контроллеры, представления, модели, layout.

```
modules/admin/
    Module.php
    controllers/DefaultController.php
    models/
    views/layouts/  views/default/index.php
```

```php
namespace app\modules\admin;

class Module extends \yii\base\Module
{
    public $layout = 'admin';
    public $defaultRoute = 'default';

    public function init()
    {
        parent::init();
        \Yii::configure($this, require __DIR__ . '/config.php');

        if (\Yii::$app instanceof \yii\console\Application) {
            $this->controllerNamespace = 'app\modules\admin\commands';
        }
    }
}
```

```php
// подключение
'modules' => ['admin' => ['class' => 'app\modules\admin\Module']],
```

- Маршрут: `admin/default/index`; только `admin` → `defaultRoute` (`default`) → `defaultAction`.
- Доступ к модулю: `Yii::$app->getModule('admin')`, `Module::getInstance()`,
  `Yii::$app->controller->module`.
- Модули вкладываются друг в друга: `forum/admin/dashboard/index`.
- URL-правила модуля добавляются в `bootstrap()` (реализуйте `BootstrapInterface`), а не
  в `init()` — иначе они опоздают к разбору запроса.
