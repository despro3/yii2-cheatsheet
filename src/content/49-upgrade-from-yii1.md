---
id: upgrade-from-yii1
title: Переход с Yii 1.1
part: extra
summary: Что изменилось между Yii 1.1 и 2.0 — PHP 5.4+ и пространства имён, Yii::app() → Yii::$app, BaseObject/Component, события через on(), псевдонимы с @, представления и виджеты, модели и сценарии, контроллеры возвращают результат, Active Record без model(), Composer вместо копирования, совместная работа 1.1 и 2.0.
sources: intro-upgrade-from-v1
---

:::lead
Yii 2 — не апгрейд, а переписанный фреймворк: код 1.1 нужно переносить, а не мигрировать. Зато идеи те же — компоненты, AR, виджеты — и большинство изменений сводятся к таблице «было → стало». Обе версии могут работать в одном приложении, пока идёт переезд.
:::

## Основа

| Yii 1.1 | Yii 2 |
|---|---|
| PHP 5.1+, без namespace, классы с префиксом `C` (`CController`) | PHP 5.4+ (реально 7.x/8.x), namespaces (`yii\web\Controller`), PSR-4 |
| `Yii::app()` | `Yii::$app` |
| `Yii::import()`, `Yii::app()->getComponent()` | автозагрузчик по namespace; `Yii::$app->db` |
| `CComponent` — всё: свойства, события, поведения | `yii\base\BaseObject` (свойства) и `yii\base\Component` (+события, поведения) |
| `Yii::createComponent($config)` | `Yii::createObject($config)` (через DI-контейнер) |
| `protected/`, `index.php` в корне | `web/index.php` отдельно от кода; `app\` namespace |
| копирование `framework/` | Composer: `yiisoft/yii2` + расширения `yiisoft/yii2-*` |
| `yiic` | `./yii` |

## События, свойства, поведения

```php
// Yii 1.1
$component->onClick = $callback;                 // подписка
$component->onClick(new CEvent($this));          // вызов
// Yii 2
$component->on('click', $callback);
$component->trigger('click', new Event(['sender' => $this]));
$component->off('click', $callback);
Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, $handler);   // уровень класса — новое
```

- Свойства через `getX()/setX()` работают так же, но объявляются в `BaseObject`; конструктор принимает `$config` и вызывает `init()`.
- Поведения — `yii\base\Behavior` с `events()` вместо `CBehavior::events()`... концепция та же, `attachBehavior()` сохранён.
- Псевдонимы: `application.models.User` → `@app/models/User`; символ `@` обязателен; `Yii::getAlias()`.

## Представления и виджеты

| Yii 1.1 | Yii 2 |
|---|---|
| `$this` в представлении — контроллер | `$this` — объект `yii\web\View`; контроллер — `$this->context` |
| `$this->renderPartial()` в представлении | `$this->render()` — файл; `renderPartial()` тоже есть (без layout) в контроллере |
| `echo $this->render()` в действии | `return $this->render()` — действие **возвращает** результат |
| `$this->widget('CMenu', [...])` | `echo Menu::widget([...])`; `ActiveForm::begin()`/`end()` |
| `$this->beginWidget()/endWidget()` | `Widget::begin()` / `Widget::end()` |
| `CHtml::encode()`, `CHtml::link()` | `Html::encode()`, `Html::a()` |
| `Yii::app()->clientScript->registerScriptFile()` | Asset Bundles + `$this->registerJsFile()` в View |
| темы через `themeManager` | `view.theme` с `pathMap` |

Layout: `$content` остался; `<?php $this->head() ?>`, `beginBody()`, `endBody()`, `beginPage()`, `endPage()` — обязательны для ассетов.

## Модели

| Yii 1.1 | Yii 2 |
|---|---|
| `CModel`, `CFormModel` | `yii\base\Model` — и для форм |
| `$model->attributes = $_POST['Form']` | `$model->load(Yii::$app->request->post())` |
| `safeAttributes()`/сценарии через `rules` | `scenarios()` + `rules()` с `on`; безопасные атрибуты — из активных правил |
| `CValidator` | `yii\validators\Validator`; inline-валидаторы с той же сигнатурой |
| `CActiveRecord`, `User::model()->findByPk(1)` | `yii\db\ActiveRecord`, `User::findOne(1)` — статические методы, `model()` нет |
| `CDbCriteria`, `findAll($criteria)` | `User::find()->where([...])->all()` — Query Builder |
| `relations()` с `self::HAS_MANY` | `getOrders()` → `$this->hasMany(Order::class, ['customer_id' => 'id'])` |
| `with('orders')`, `together()` | `with('orders')` (отдельный запрос), `joinWith('orders')` (JOIN) |
| `$model->isNewRecord`, `save()`, `beforeSave()` | то же; события `EVENT_BEFORE_INSERT` и др. |
| `CDbConnection`, `createCommand()` | `yii\db\Connection` — почти тот же API; `{{%table}}`, `[[column]]` |

## Контроллеры и маршрутизация

- Действия — `actionIndex()` как раньше, но **возвращают** результат (`return $this->render(...)`), могут вернуть строку, `Response`, массив (для JSON).
- `filters()` + `accessRules()` → `behaviors()` с `AccessControl`, `VerbFilter`.
- `CUrlManager` → `yii\web\UrlManager`; правила похожи; `enablePrettyUrl`, `showScriptName`.
- `Yii::app()->user->checkAccess()` → `Yii::$app->user->can()`; `CWebUser` → `yii\web\User` + `IdentityInterface` (реализуется моделью `User`, а не `UserIdentity`).
- `CUserIdentity::authenticate()` — нет; проверка пароля в вашей `LoginForm`, затем `Yii::$app->user->login($identity, $duration)`.
- `CHttpRequest` → `yii\web\Request` (`Yii::$app->request->post()`), ответ — `yii\web\Response` (`Yii::$app->response`).

## Прочее

| Yii 1.1 | Yii 2 |
|---|---|
| `Yii::t('app', ...)` | то же, но формат ICU (`{n, plural, ...}`), источники в `i18n` |
| `CFormatter`, `Yii::app()->format` | `Yii::$app->formatter` |
| `CCache` | `yii\caching\*`; те же зависимости, `getOrSet()` |
| `CConsoleCommand` | `yii\console\Controller` — действия и опции |
| `CAssetManager::publish()` | Asset Bundles — классы с `sourcePath`, `css`, `js`, `depends` |
| `Gii`, `yii-debug-toolbar` | `yii2-gii`, `yii2-debug` |
| `CJavaScript::encode` | `Json::encode` + `JsExpression` |
| `CDbMigration` | `yii\db\Migration` — `safeUp()`, `migrate/create` с шаблонами |
| `yiilite.php` | нет — используйте opcache |
| `CJSON`, `CVarDumper` | `Json`, `VarDumper` |

## Yii 1.1 и 2.0 в одном приложении

Переезжать можно постепенно: старое приложение остаётся на 1.1, новые части пишутся на 2.0. Оба фреймворка используют класс `Yii`, поэтому нужен один общий, обслуживающий обе версии:

```php title="components/Yii.php"
$yii2path = '/path/to/yii2';
require $yii2path . '/BaseYii.php';     // Yii 2.x

$yii1path = '/path/to/yii1';
require $yii1path . '/YiiBase.php';     // Yii 1.x

class Yii extends \yii\BaseYii
{
    // скопировать сюда код YiiBase из Yii 1.x
}

Yii::$classMap = include $yii2path . '/classes.php';
Yii::registerAutoloader(['Yii', 'autoload']);   // автозагрузчик Yii 2 через Yii 1
Yii::$container = new yii\di\Container;
```

```php title="index.php"
require __DIR__ . '/../components/Yii.php';

$yii2Config = require __DIR__ . '/../config/yii2/web.php';
new yii\web\Application($yii2Config);          // создать, но НЕ вызывать run()

$yii1Config = require __DIR__ . '/../config/yii1/main.php';
Yii::createWebApplication($yii1Config)->run();  // запускается приложение 1.1
```

После этого `Yii::app()` — приложение 1.1 (`CWebApplication`), а `Yii::$app` — приложение 2.0, и из старого кода можно вызывать модели, компоненты и хелперы 2.0. Подробности — в разделе [расширения и интеграция](extensions).

> [!TIP] Порядок переезда
> Сначала — новые фичи на Yii 2 (отдельный модуль/приложение с общей БД), затем модели (AR почти совместимы), затем контроллеры и представления. Тесты на функциональность до и после. Составить список расширений 1.1 и найти их аналоги в 2.0 (большинство есть).

:::quiz Проверь себя
Q: Как теперь получить экземпляр приложения?
A: `Yii::$app` вместо `Yii::app()`.
Q: Что заменило `User::model()->findByPk($id)`?
A: Статический `User::findOne($id)`; сложные запросы — `User::find()->where(...)->all()`.
Q: Что изменилось в действиях контроллера?
A: Они возвращают результат (`return $this->render(...)`) вместо `echo`; результат становится ответом.
Q: Как объявляются связи AR в Yii 2?
A: Геттерами: `getOrders()` возвращает `$this->hasMany(Order::class, ['customer_id' => 'id'])`.
Q: Куда делся `CUserIdentity`?
A: Его заменил `IdentityInterface`, который реализует модель пользователя; проверка пароля — в форме входа.
:::
