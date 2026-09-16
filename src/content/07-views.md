---
id: views
title: Представления и шаблоны
part: structure
summary: PHP-шаблоны, правила поиска файлов, передача данных, layouts и блоки, компонент view, темизация и подключение Twig/Smarty.
sources: structure-views, output-theming, tutorial-template-engines
---

:::lead
Представление — обычный PHP-файл с HTML, в котором `$this` — это компонент `yii\web\View`. Контроллер вызывает `render()`, результат оборачивается в шаблон (layout) и уходит в ответ. Главное правило: всё пользовательское — через `Html::encode()`.
:::

## Как выглядит представление

```php title="views/site/login.php"
<?php
use yii\helpers\Html;
use yii\widgets\ActiveForm;

/** @var \yii\web\View $this */
/** @var \app\models\LoginForm $model */

$this->title = 'Вход';
?>
<h1><?= Html::encode($this->title) ?></h1>

<?php $form = ActiveForm::begin(); ?>
    <?= $form->field($model, 'username') ?>
    <?= $form->field($model, 'password')->passwordInput() ?>
    <?= Html::submitButton('Войти') ?>
<?php ActiveForm::end(); ?>
```

Переменные (`$model`, `$form`) приходят из контроллера. Докблок с `@var` в начале файла — не обязателен, но даёт автодополнение в IDE.

> [!GOTCHA]
> В Yii 1 `$this` в представлении был контроллером. В Yii 2 это объект `View`; контроллер доступен как `$this->context`.

### Безопасность вывода

```php
<?= Html::encode($user->name) ?>              <!-- текст: экранируем < > & " ' -->
<?= HtmlPurifier::process($post->text) ?>     <!-- HTML от пользователя: вырезаем опасное -->
```

`HtmlPurifier` надёжен, но медленный — результат стоит [кешировать](caching-output).

## Где лежат файлы

| Кто рендерит | Папка по умолчанию |
|---|---|
| контроллер `PostController` | `@app/views/post/` |
| контроллер `PostCommentController` | `@app/views/post-comment/` |
| контроллер модуля | `views/post/` внутри папки модуля |
| виджет | `views/` рядом с классом виджета |

Изменить папку можно, переопределив `getViewPath()` контроллера или виджета.

## Как рендерить

:::kv
`$this->render('view', $params)` — в контроллере: представление + шаблон
`$this->renderPartial('_item', $params)` — в контроллере: без шаблона (фрагменты, AJAX)
`$this->renderAjax('form', $params)` — без шаблона, но с зарегистрированными JS/CSS — для подгрузки модалок
`$this->renderFile('@app/views/site/license.php')` — по пути или псевдониму
`$this->render('_overview')` — внутри представления: `$this` уже `View`, ищет рядом с текущим файлом
`Yii::$app->view->renderFile(...)` — откуда угодно (письма, консоль)
:::

### Как разрешается имя представления

| Имя | Где ищется |
|---|---|
| `about` | в папке контекста: `@app/views/site/about.php` для `SiteController` |
| `_item` из `views/post/index.php` | рядом: `views/post/_item.php` |
| `/site/about` | в `viewPath` текущего модуля (или приложения) |
| `//site/about` | всегда в `@app/views/site/about.php` |
| `@app/views/site/about` | псевдоним — как есть |

Расширение `.php` можно не писать.

## Данные в представлении

```php
// явно — через второй параметр: массив превращается в переменные через extract()
return $this->render('report', ['foo' => 1, 'bar' => 2]);

// из контекста
ID контроллера: <?= $this->context->id ?>

// общие данные между представлением и шаблоном
$this->params['breadcrumbs'][] = 'О нас';     // в представлении
Breadcrumbs::widget(['links' => $this->params['breadcrumbs'] ?? []]);   // в шаблоне
```

Явная передача предпочтительнее: представление не зависит от того, кто его вызвал.

## Шаблоны (layouts)

Шаблон — тоже представление; в нём `$content` — результат рендеринга страницы. Лежат в `@app/views/layouts`, по умолчанию используется `main`.

```php title="views/layouts/main.php"
<?php
use yii\helpers\Html;
use app\assets\AppAsset;

AppAsset::register($this);
?>
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
    <header>Моя компания</header>
    <?= $content ?>
    <footer>&copy; <?= date('Y') ?></footer>
<?php $this->endBody() ?>
</body>
</html>
<?php $this->endPage() ?>
```

Пять служебных вызовов обязательны: `beginPage()`/`endPage()` оборачивают страницу, `head()` — место для мета-тегов и CSS, `beginBody()`/`endBody()` — для скриптов в начале и конце `<body>`. Без них зарегистрированные ресурсы не появятся.

### Какой шаблон применится

1. `layout` контроллера, если не `null`; иначе — первый не-`null` `layout` по цепочке модулей вверх до приложения.
2. Значение трактуется как: псевдоним (`@app/views/layouts/main`), абсолютный путь от папки шаблонов приложения (`/main`), относительный — от папки шаблонов модуля-контекста (`main`), либо `false` — без шаблона.

```php
class PostController extends Controller
{
    public $layout = 'post';       // @app/views/layouts/post.php только для этого контроллера
}
```

### Вложенные шаблоны и блоки

```php title="views/layouts/column2.php"
<?php $this->beginContent('@app/views/layouts/main.php'); ?>
<div class="row">
    <div class="col-8"><?= $content ?></div>
    <div class="col-4"><?= $this->blocks['sidebar'] ?? 'Боковая панель по умолчанию' ?></div>
</div>
<?php $this->endContent(); ?>
```

```php title="views/post/view.php"
<?php $this->beginBlock('sidebar'); ?>
    <h3>Похожие статьи</h3>
<?php $this->endBlock(); ?>
```

Блок «записывается» в представлении и выводится в шаблоне — так страница управляет частями общей разметки.

## Компонент view

```php
$this->title = 'Заголовок';                                             // → <title> в шаблоне
$this->registerMetaTag(['name' => 'description', 'content' => '…'], 'description');   // ключ = без дублей
$this->registerLinkTag(['rel' => 'alternate', 'type' => 'application/rss+xml', 'href' => '/rss']);
$this->registerCss('body { background: #fff }');
$this->registerJs("$('#btn').on('click', …);", View::POS_READY, 'btn-handler');
$this->registerCssFile('@web/css/print.css', ['media' => 'print']);
$this->registerJsFile('@web/js/main.js', ['depends' => [JqueryAsset::class]]);
AppAsset::register($this);                                              // лучший способ: пакеты ресурсов
```

Подробно о скриптах и стилях — в разделе [Ресурсы и клиентские скрипты](assets).

События `View`: `beforeRender`/`afterRender` (можно отменить или изменить вывод через `$event->output`), `beginPage`, `endPage`, `beginBody`, `endBody`:

```php
Yii::$app->view->on(View::EVENT_END_BODY, function () {
    echo '<!-- rendered ' . date('c') . ' -->';
});
```

### Статические страницы

Вместо десятка одинаковых `actionAbout()` — одно отдельное действие:

```php
public function actions()
{
    // ?r=site/page&view=about → views/site/pages/about.php
    return ['page' => ['class' => 'yii\web\ViewAction']];
}
```

## Темизация

Тема подменяет файлы представлений без правки кода. Настраивается у компонента `view`:

```php
'view' => [
    'theme' => [
        'basePath' => '@app/themes/basic',
        'baseUrl' => '@web/themes/basic',
        'pathMap' => [
            // views/site/about.php → themes/basic/site/about.php
            '@app/views' => '@app/themes/basic',
            '@app/modules' => '@app/themes/basic/modules',         // темизация модулей
            '@app/widgets' => '@app/themes/basic/widgets',         // темизация виджетов
        ],
    ],
],
```

Замена идёт по префиксу пути. Несколько значений в `pathMap` дают наследование тем — берётся первый существующий файл:

```php
'@app/views' => ['@app/themes/christmas', '@app/themes/basic'],
```

В представлении тема доступна как `$this->theme`: `$theme->getUrl('img/logo.png')`, `$theme->getPath(...)`.

## Twig и Smarty

Шаблонизаторы подключаются расширениями `yiisoft/yii2-twig` и `yiisoft/yii2-smarty` через рендереры по расширению файла:

```php
'view' => [
    'renderers' => [
        'twig' => [
            'class' => 'yii\twig\ViewRenderer',
            'cachePath' => '@runtime/Twig/cache',
            'options' => ['auto_reload' => true],
            'globals' => ['html' => '\yii\helpers\Html'],
        ],
        'tpl' => ['class' => 'yii\smarty\ViewRenderer'],
    ],
],
```

После этого `$this->render('index')` найдёт `index.twig` или `index.tpl`; файлы `.php` продолжают работать как раньше.

## Лучшие практики

- В представлении — только разметка и простой PHP для вывода; никаких запросов к БД и доступа к `$_GET`.
- Читать свойства моделей можно, менять — нет.
- Крупные представления дробите на части (`_item.php`, `_form.php`) и виджеты; форматирование выносите в хелперы.

:::quiz Проверь себя
Q: Чем `renderPartial()` отличается от `renderAjax()`?
A: Оба не применяют шаблон, но `renderAjax()` дополнительно выводит зарегистрированные JS/CSS — нужен для фрагментов, которые подгружаются по AJAX и содержат виджеты.
Q: Куда попадёт файл, если вызвать `$this->render('//site/error')` из контроллера модуля `admin`?
A: Двойной слеш всегда означает папку представлений приложения: `@app/views/site/error.php`, минуя модуль.
Q: Зачем в шаблоне вызывать `$this->head()`, `beginBody()` и `endBody()`?
A: Это точки, куда фреймворк подставляет зарегистрированные мета-теги, CSS и JS. Без них ресурсы, зарегистрированные представлениями и виджетами, на страницу не попадут.
Q: Как одному контроллеру дать другой шаблон, а одному действию — вовсе отключить его?
A: `public $layout = 'post';` в классе контроллера; для действия — `$this->layout = false;` перед `render()` или вернуть `renderPartial()`.
Q: Как передать заголовок и хлебные крошки из представления в шаблон?
A: Через `$this->title` и `$this->params['breadcrumbs']` — оба свойства компонента `View`, общего для представления и шаблона.
:::
