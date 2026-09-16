---
id: widgets
title: Виджеты
part: structure
summary: Переиспользуемые блоки интерфейса: как использовать widget() и begin()/end(), как написать свой виджет с представлением и ресурсами, как задать умолчания через DI.
sources: structure-widgets
---

:::lead
Виджет — это класс, который рисует кусок интерфейса: форму, меню, таблицу, пагинатор, date picker. Он инкапсулирует разметку, логику и нужные JS/CSS, поэтому в представлении достаточно одной строки.
:::

## Использование

Два способа вызова:

```php
<?php
use yii\widgets\ActiveForm;
use yii\widgets\LinkPager;
use yii\helpers\Html;
?>

<!-- 1. widget(): конфигурация → готовый HTML -->
<?= LinkPager::widget(['pagination' => $pagination, 'maxButtonCount' => 5]) ?>

<!-- 2. begin()/end(): виджет с содержимым между вызовами -->
<?php $form = ActiveForm::begin(['id' => 'login-form']); ?>
    <?= $form->field($model, 'username') ?>
    <?= $form->field($model, 'password')->passwordInput() ?>
    <?= Html::submitButton('Войти', ['class' => 'btn btn-primary']) ?>
<?php ActiveForm::end(); ?>
```

`widget()` возвращает строку, `begin()` — экземпляр виджета (поэтому у `$form` можно вызывать `field()`), а `end()` выводит результат.

### Виджеты из коробки

| Виджет | Для чего |
|---|---|
| `ActiveForm`, `ActiveField` | формы на основе модели с клиентской валидацией — см. [Формы](forms) |
| `GridView`, `ListView`, `DetailView` | таблицы и списки из провайдера данных — см. [Виджеты данных](data-widgets) |
| `LinkPager`, `LinkSorter` | ссылки постраничной навигации и сортировки |
| `Menu`, `Breadcrumbs` | меню с подсветкой активного пункта, хлебные крошки |
| `Pjax` | обновление части страницы без перезагрузки |
| `FragmentCache` | кеширование фрагмента — обёртка `beginCache()`/`endCache()` |
| `MaskedInput`, `Captcha`, `InputWidget` | поля ввода |
| `yii\bootstrap*\*` | Alert, Modal, Nav, NavBar, Tabs, Dropdown и другие компоненты Bootstrap (расширение) |
| `yii\jui\*` | DatePicker, Autocomplete, Slider и другие jQuery UI (расширение) |

### Умолчания для всех виджетов

Через [DI-контейнер](di) можно задать свойства по умолчанию для любого класса — например, чтобы все пагинаторы показывали 5 кнопок:

```php
\Yii::$container->set('yii\widgets\LinkPager', ['maxButtonCount' => 5]);

// или в конфигурации приложения (с 2.0.11)
'container' => [
    'definitions' => [
        'yii\widgets\LinkPager' => ['maxButtonCount' => 5],
    ],
],
```

## Свой виджет

Наследуем `yii\base\Widget`: в `init()` нормализуем свойства, в `run()` возвращаем HTML.

```php title="components/HelloWidget.php"
namespace app\components;

use yii\base\Widget;
use yii\helpers\Html;

class HelloWidget extends Widget
{
    public $message;

    public function init()
    {
        parent::init();
        if ($this->message === null) {
            $this->message = 'Hello World';
        }
    }

    public function run()
    {
        return Html::encode($this->message);
    }
}
```

```php
<?= HelloWidget::widget(['message' => 'Доброе утро']) ?>
```

### Виджет с содержимым

Чтобы принять то, что написано между `begin()` и `end()`, включаем буферизацию вывода в `init()` и забираем её в `run()`:

```php
class HelloWidget extends Widget
{
    public function init()
    {
        parent::init();
        ob_start();
    }

    public function run()
    {
        $content = ob_get_clean();
        return Html::tag('div', Html::encode($content), ['class' => 'hello']);
    }
}
```

```php
<?php HelloWidget::begin(); ?>
    содержимое, которое может содержать <tag>'и
<?php HelloWidget::end(); ?>
```

> [!NOTE]
> `begin()` создаёт экземпляр и сразу вызывает `init()`; `end()` вызывает `run()` и выводит результат. Именно поэтому буфер открывают в `init()`.

### Виджет с представлением

Большую разметку удобнее держать в файле. Представления виджета лежат в `views/` рядом с классом (`@app/components/views/hello.php`); папку меняет `getViewPath()`.

```php
public function run()
{
    return $this->render('hello', ['message' => $this->message]);
}
```

### Виджет с ресурсами

Если виджету нужны CSS/JS, регистрируйте [пакет ресурсов](assets) в `$this->view` — тогда виджет остаётся самодостаточным:

```php
public function run()
{
    DatePickerAsset::register($this->view);
    $this->view->registerJs("jQuery('#{$this->id}').datepicker();");
    return Html::activeTextInput($this->model, $this->attribute, ['id' => $this->id]);
}
```

Для полей ввода, привязанных к модели, наследуйте `yii\widgets\InputWidget` — он уже умеет `model`/`attribute` или `name`/`value`.

## Лучшие практики

- Виджет следует MVC: логика в классе, разметка в представлении.
- Виджет должен работать «из коробки» после вставки в представление — все зависимости через asset bundles, никаких ручных `<script>`.
- Если виджет — только разметка без логики, возможно, достаточно частичного представления (`_item.php`). Виджет выигрывает, когда его нужно распространять как класс: между модулями, проектами, в расширении.

:::quiz Проверь себя
Q: Чем `Widget::widget()` отличается от `Widget::begin()`?
A: `widget()` сразу возвращает готовый HTML; `begin()` возвращает объект виджета и ждёт `end()`, между ними можно выводить содержимое (как в `ActiveForm`).
Q: Где по умолчанию виджет ищет свои файлы представлений?
A: В папке `views/` рядом с файлом класса виджета; изменить можно переопределив `getViewPath()`.
Q: Как одной строкой поменять значение по умолчанию свойства у всех экземпляров виджета?
A: Зарегистрировать конфигурацию в DI-контейнере: `Yii::$container->set(LinkPager::class, ['maxButtonCount' => 5])`.
Q: Куда виджет должен регистрировать свои скрипты?
A: В `$this->view` — объект представления, в котором он рендерится; лучше всего через пакет ресурсов `SomeAsset::register($this->view)`.
:::
