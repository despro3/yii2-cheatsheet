---
id: first-app
title: Первое приложение
part: start
summary: Четыре шага из руководства «Первое знакомство» в одном месте: страница «Привет», форма с валидацией, список из базы данных и генерация CRUD в Gii.
sources: start-hello, start-forms, start-databases, start-gii
---

:::lead
Здесь весь путь новичка: действие и представление → модель и форма → Active Record с пагинацией → CRUD за минуту в Gii. Каждый шаг показывает одну часть MVC и знакомит с идеями, которые дальше разбираются подробно.
:::

## Шаг 1. Страница «Привет»: действие + представление

Действие — публичный метод контроллера с префиксом `action`. Параметры действия берутся из `$_GET` по имени.

```php title="controllers/SiteController.php"
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

```php title="views/site/say.php"
<?php use yii\helpers\Html; ?>
<?= Html::encode($message) ?>
```

Открываем `index.php?r=site/say&message=Привет+мир`. Параметр `r` — это **маршрут** вида `контроллер/действие`; `site/say` → `SiteController::actionSay()`.

> [!GOTCHA]
> Всё, что пришло от пользователя, перед выводом в HTML экранируйте через `Html::encode()`, иначе получите XSS. Это правило номер один для представлений.

Правила именования, которые нужно запомнить:

| Идентификатор | Класс / метод |
|---|---|
| контроллер `site` | `app\controllers\SiteController` |
| контроллер `post-comment` | `app\controllers\PostCommentController` |
| действие `say` | `actionSay()` |
| действие `create-comment` | `actionCreateComment()` |
| представление `say` контроллера `site` | `views/site/say.php` |

`render()` автоматически оборачивает результат в шаблон `views/layouts/main.php` — поэтому у новой страницы сразу есть шапка и подвал сайта.

## Шаг 2. Форма: модель + валидация

Модель формы наследует `yii\base\Model`: публичные свойства — это атрибуты, метод `rules()` — правила проверки.

```php title="models/EntryForm.php"
namespace app\models;

use yii\base\Model;

class EntryForm extends Model
{
    public $name;
    public $email;

    public function rules()
    {
        return [
            [['name', 'email'], 'required'],
            ['email', 'email'],
        ];
    }
}
```

```php title="controllers/SiteController.php"
public function actionEntry()
{
    $model = new EntryForm();

    // load() кладёт $_POST['EntryForm'] в атрибуты, validate() проверяет по rules()
    if ($model->load(Yii::$app->request->post()) && $model->validate()) {
        return $this->render('entry-confirm', ['model' => $model]);
    }

    return $this->render('entry', ['model' => $model]);   // первый показ или ошибки
}
```

```php title="views/site/entry.php"
<?php
use yii\helpers\Html;
use yii\widgets\ActiveForm;
?>
<?php $form = ActiveForm::begin(); ?>
    <?= $form->field($model, 'name')->label('Ваше имя') ?>
    <?= $form->field($model, 'email') ?>
    <div class="form-group">
        <?= Html::submitButton('Отправить', ['class' => 'btn btn-primary']) ?>
    </div>
<?php ActiveForm::end(); ?>
```

> [!WHY]
> Откуда «магия»? `ActiveForm` читает `rules()` модели, генерирует JavaScript-валидацию на клиенте и выводит ошибки под полями без перезагрузки. Серверная проверка в `actionEntry()` всё равно выполняется — на случай отключённого JS. Подписи полей берутся из имён атрибутов (`name` → «Name»), их меняют через `label()` или `attributeLabels()` в модели.

`Yii::$app` — глобальный объект приложения и одновременно Service Locator: через него доступны компоненты `request`, `response`, `db`, `user` и другие.

## Шаг 3. Данные из базы: Active Record + пагинация

Подключение описано в `config/db.php` и доступно как `Yii::$app->db`:

```php title="config/db.php"
return [
    'class' => 'yii\db\Connection',
    'dsn' => 'mysql:host=localhost;dbname=yii2basic',
    'username' => 'root',
    'password' => '',
    'charset' => 'utf8',
];
```

Класс Active Record без единой строки кода уже умеет всё — имя таблицы выводится из имени класса (`Country` → `country`):

```php title="models/Country.php"
namespace app\models;

use yii\db\ActiveRecord;

class Country extends ActiveRecord
{
}
```

```php
$countries = Country::find()->orderBy('name')->all();   // все строки как объекты
$country = Country::findOne('US');                       // по первичному ключу
$country->name = 'U.S.A.';
$country->save();                                        // UPDATE
```

Контроллер со списком и постраничной разбивкой:

```php title="controllers/CountryController.php"
namespace app\controllers;

use yii\web\Controller;
use yii\data\Pagination;
use app\models\Country;

class CountryController extends Controller
{
    public function actionIndex()
    {
        $query = Country::find();

        $pagination = new Pagination([
            'defaultPageSize' => 5,
            'totalCount' => $query->count(),
        ]);

        $countries = $query->orderBy('name')
            ->offset($pagination->offset)
            ->limit($pagination->limit)
            ->all();

        return $this->render('index', [
            'countries' => $countries,
            'pagination' => $pagination,
        ]);
    }
}
```

```php title="views/country/index.php"
<?php
use yii\helpers\Html;
use yii\widgets\LinkPager;
?>
<h1>Countries</h1>
<ul>
<?php foreach ($countries as $country): ?>
    <li><?= Html::encode("{$country->code} ({$country->name})") ?>: <?= $country->population ?></li>
<?php endforeach; ?>
</ul>
<?= LinkPager::widget(['pagination' => $pagination]) ?>
```

`Pagination` считает `LIMIT`/`OFFSET` по параметру `page` из URL, а `LinkPager` рисует кнопки страниц. Всё это подробно — в разделах [Active Record](active-record) и [Провайдеры данных](data-providers).

## Шаг 4. Gii: генерация модели и CRUD

Gii — модуль, включённый в `config/web.php` только для `YII_ENV_DEV`:

```php
if (YII_ENV_DEV) {
    $config['bootstrap'][] = 'gii';
    $config['modules']['gii'] = [
        'class' => 'yii\gii\Module',
        'allowedIPs' => ['127.0.0.1', '::1', '192.168.0.*'],   // по умолчанию только localhost
    ];
}
```

Открываем `index.php?r=gii` и:

:::steps
1. **Model Generator**: таблица `country` → класс `Country`. Кнопка *Preview* покажет файл, *diff* — отличия от существующего, флажок *overwrite* перезапишет.
2. **CRUD Generator**: `app\models\Country`, поисковая модель `app\models\CountrySearch`, контроллер `app\controllers\CountryController`.
3. Получаем `controllers/CountryController.php`, `models/CountrySearch.php` и `views/country/*.php` — таблицу с сортировкой и фильтрами, просмотр, создание, редактирование, удаление.
:::

> [!TIP]
> Gii — не «костыль для новичков», а обычный инструмент разработки: сгенерированный код отправляют в репозиторий и правят руками. Шаблоны генераторов можно менять под свой стиль — см. [Gii и отладчик](dev-tools).

:::quiz Проверь себя
Q: Как из маршрута `post-comment/create-reply` получить имя класса и метода?
A: `app\controllers\PostCommentController::actionCreateReply()` — дефисы убираются, слова капитализируются, добавляются суффикс `Controller` и префикс `action`.
Q: Что делает `$model->load(Yii::$app->request->post())` и что вернёт, если формы в POST нет?
A: Копирует `$_POST['EntryForm']` в безопасные атрибуты модели и возвращает `true`; если данных нет — `false`, и действие просто показывает форму.
Q: Где выполняется валидация формы, созданной через `ActiveForm`?
A: И на клиенте (JavaScript, сгенерированный из `rules()`), и на сервере при вызове `validate()`. Доверять можно только серверной.
Q: Что нужно, чтобы класс `Country extends ActiveRecord` заработал?
A: Только настроенное подключение `db` и таблица `country` в базе: имя таблицы, атрибуты и типы столбцов читаются из схемы автоматически.
Q: Почему Gii по умолчанию недоступен с чужого IP?
A: Из соображений безопасности: генератор пишет файлы на диск. Разрешённые адреса задаются в `allowedIPs`.
:::
