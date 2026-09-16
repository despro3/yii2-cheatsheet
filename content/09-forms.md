---
id: forms
title: Формы и валидация
icon: 📝
summary: ActiveForm, поля ввода, все встроенные валидаторы, свои валидаторы, AJAX-валидация, загрузка файлов.
sources: input-forms, input-validation, tutorial-core-validators, input-file-upload, input-tabular-input, input-multiple-models, input-form-javascript
---

# Формы и проверка данных

## ActiveForm

```php
<?php
use yii\helpers\Html;
use yii\widgets\ActiveForm;

$form = ActiveForm::begin([
    'id' => 'login-form',
    'options' => ['class' => 'form-horizontal', 'enctype' => 'multipart/form-data'],
    'enableClientValidation' => true,
    'enableAjaxValidation' => false,
    'validateOnBlur' => true,
    'fieldConfig' => ['template' => "{label}\n{input}\n{hint}\n{error}"],
]) ?>

    <?= $form->field($model, 'username')->textInput(['maxlength' => true, 'autofocus' => true]) ?>
    <?= $form->field($model, 'password')->passwordInput() ?>
    <?= $form->field($model, 'email')->input('email')->hint('Например, user@example.com') ?>
    <?= $form->field($model, 'rememberMe')->checkbox() ?>
    <?= $form->field($model, 'about')->textarea(['rows' => 6]) ?>
    <?= $form->field($model, 'category_id')->dropDownList($items, ['prompt' => 'Выберите…']) ?>
    <?= $form->field($model, 'tags[]')->checkboxList($items) ?>
    <?= $form->field($model, 'type')->radioList($items) ?>
    <?= $form->field($model, 'file')->fileInput() ?>
    <?= $form->field($model, 'code')->widget(\yii\captcha\Captcha::class) ?>
    <?= $form->field($model, 'name')->label('Ваше имя')->error(['class' => 'help-block']) ?>
    <?= $form->errorSummary($model) ?>

    <?= Html::submitButton('Войти', ['class' => 'btn btn-primary']) ?>

<?php ActiveForm::end() ?>
```

Имя поля строится как `ИмяМоделиБезПространстваИмён[атрибут]`, поэтому на сервере данные
приходят как `$_POST['LoginForm']['username']`, а `$model->load(Yii::$app->request->post())`
всё раскладывает сам. Переопределив `formName()` в модели на пустую строку, получите
«плоские» имена (удобно для фильтров в GridView и красивых URL).

Множественные значения — добавьте `[]` к имени атрибута:

```php
echo $form->field($model, 'uploadFile[]')->fileInput(['multiple' => true]);
echo $form->field($model, 'items[]')->checkboxList(['a' => 'A', 'b' => 'B']);
```

> Совет: для Bootstrap используйте `yii\bootstrap5\ActiveForm` — он расставит нужные
> CSS-классы. Для обновления части страницы оберните форму в `Pjax` и добавьте
> `'options' => ['data' => ['pjax' => true]]`.

## Правила валидации

```php
public function rules()
{
    return [
        [['name', 'email'], 'required'],
        ['email', 'email'],
        ['age', 'integer', 'min' => 18, 'max' => 120],
        ['username', 'string', 'length' => [4, 24]],
        ['username', 'unique', 'targetClass' => User::class],
        ['password_repeat', 'compare', 'compareAttribute' => 'password'],
        ['status', 'in', 'range' => array_keys(self::statuses())],
        [['created_at'], 'safe'],
        // только в сценарии, с условием и своим сообщением
        ['state', 'required', 'on' => self::SCENARIO_REGISTER,
            'message' => 'Укажите регион',
            'when' => fn ($model) => $model->country === 'USA',
            'whenClient' => "function (attribute, value) { return $('#country').val() == 'USA'; }"],
    ];
}
```

Формат правила: `[атрибуты, валидатор, on => сценарии, except => сценарии, свойства…]`.
Правило применяется, если атрибут активен в текущем сценарии. Правилам можно давать
ключи-имена, чтобы наследники могли их убрать (`unset($rules['password'])`).

```php
$model->validate();                       // все активные атрибуты
$model->validate(['email']);              // только указанные
$model->hasErrors();  $model->errors;  $model->getFirstErrors();
$model->addError('email', 'Занят');
$model->clearErrors();
```

События: `beforeValidate()` / `EVENT_BEFORE_VALIDATE` (вернуть `false` — отменить),
`afterValidate()` / `EVENT_AFTER_VALIDATE`.

## Встроенные валидаторы

| Псевдоним | Что проверяет / делает | Ключевые свойства |
|---|---|---|
| `required` | значение не пусто | `requiredValue`, `strict` |
| `safe` | помечает атрибут безопасным (без проверки) | — |
| `boolean` | равно `trueValue`/`falseValue` | `trueValue`, `falseValue`, `strict` |
| `string` | строка нужной длины | `length`, `min`, `max`, `encoding` |
| `integer` | целое число | `min`, `max` |
| `number`, `double` | число (float) | `min`, `max` |
| `match` | соответствие регулярке | `pattern`, `not` |
| `in` | входит в список | `range`, `strict`, `not`, `allowArray` |
| `compare` | сравнение с атрибутом/значением | `compareAttribute`, `compareValue`, `operator`, `type` |
| `date`, `datetime`, `time` | формат даты/времени | `format`, `timestampAttribute`, `min`, `max` |
| `email` | email | `allowName`, `checkDNS`, `enableIDN` |
| `url` | URL | `validSchemes`, `defaultScheme`, `enableIDN` |
| `ip` | IPv4/IPv6/подсеть | `ipv4`, `ipv6`, `subnet`, `ranges`, `normalize`, `expandIPv6`, `negation` |
| `unique` | уникальность в таблице (AR) | `targetClass`, `targetAttribute`, `filter` |
| `exist` | значение существует в таблице (AR) | `targetClass`, `targetAttribute`, `filter`, `allowArray` |
| `file` | загруженный файл | `extensions`, `mimeTypes`, `minSize`, `maxSize`, `maxFiles`, `checkExtensionByMimeType` |
| `image` | файл-изображение (+ всё от `file`) | `minWidth`, `maxWidth`, `minHeight`, `maxHeight` |
| `captcha` | совпадение с кодом CAPTCHA | `caseSensitive`, `captchaAction` |
| `default` | подставляет значение, если пусто | `value` (значение или callback) |
| `filter` | преобразует значение | `filter` (callable), `skipOnArray` |
| `trim` | обрезает пробелы | — |
| `each` | применяет правило к каждому элементу массива | `rule`, `allowMessageFromRule` |

```php
// самые частые комбинации
[['username', 'email'], 'trim'],
[['from_date', 'to_date'], 'default', 'value' => null],
['phone', 'filter', 'filter' => fn ($v) => preg_replace('/\D/', '', $v)],
['tags', 'each', 'rule' => ['integer']],
['email', 'unique', 'targetClass' => User::class, 'filter' => ['status' => 10]],
['category_id', 'exist', 'targetClass' => Category::class, 'targetAttribute' => 'id'],
['age', 'compare', 'compareValue' => 30, 'operator' => '>=', 'type' => 'number'],
```

> Важно: большинство валидаторов пропускают пустые значения (`skipOnEmpty = true`).
> Пустые значения обрабатывают только `captcha`, `default`, `filter`, `required`, `trim`.
> Порядок важен: сначала `trim`/`default`, потом проверки.

## Свои валидаторы

**Встроенный (inline)** — метод модели или анонимная функция:

```php
public function rules()
{
    return [
        ['country', 'validateCountry'],
        ['token', function ($attribute, $params, $validator) {
            if (!ctype_alnum($this->$attribute)) {
                $this->addError($attribute, 'Только буквы и цифры.');
            }
        }, 'skipOnEmpty' => false, 'skipOnError' => false],
    ];
}

public function validateCountry($attribute, $params)
{
    if (!in_array($this->$attribute, ['USA', 'Indonesia'], true)) {
        $this->addError($attribute, 'Недопустимая страна.');
    }
}
```

**Автономный** — класс-наследник `yii\validators\Validator`:

```php
namespace app\components;

use yii\validators\Validator;

class CountryValidator extends Validator
{
    public function init()
    {
        parent::init();
        $this->message = $this->message ?? 'Недопустимая страна.';
    }

    public function validateAttribute($model, $attribute)
    {
        if (!in_array($model->$attribute, ['USA', 'Indonesia'], true)) {
            $this->addError($model, $attribute, $this->message);
        }
    }

    // для проверки значения без модели
    protected function validateValue($value)
    {
        return in_array($value, ['USA', 'Indonesia'], true) ? null : [$this->message, []];
    }

    // клиентская часть
    public function clientValidateAttribute($model, $attribute, $view)
    {
        $message = json_encode($this->message, JSON_UNESCAPED_UNICODE);
        return "if ($.inArray(value, ['USA','Indonesia']) === -1) { messages.push($message); }";
    }
}
```

В клиентском JS доступны `attribute`, `value`, `messages`, `deferred` (для асинхронных
проверок: `deferred.add(function (def) { … def.resolve(); })`).

## Валидация без модели

```php
// один валидатор
$validator = new \yii\validators\EmailValidator();
if ($validator->validate($email, $error)) { /* ok */ } else { echo $error; }

// набор правил «на лету»
$model = \yii\base\DynamicModel::validateData(compact('name', 'email'), [
    [['name', 'email'], 'string', 'max' => 128],
    ['email', 'email'],
]);
if ($model->hasErrors()) { /* ... */ }
```

## AJAX-валидация

```php
// представление
$form = ActiveForm::begin(['id' => 'registration-form', 'enableAjaxValidation' => true]);
echo $form->field($model, 'username', ['enableAjaxValidation' => true]);
```

```php
// действие
if (Yii::$app->request->isAjax && $model->load(Yii::$app->request->post())) {
    Yii::$app->response->format = Response::FORMAT_JSON;
    return ActiveForm::validate($model);
}
```

Клиентская валидация отключается через `enableClientValidation => false` (у формы или у
отдельного поля).

> Важно: клиентская валидация — только для удобства пользователя. Серверная
> `validate()` обязательна всегда.

## Загрузка файлов

```php
class UploadForm extends \yii\base\Model
{
    /** @var \yii\web\UploadedFile[] */
    public $imageFiles;

    public function rules()
    {
        return [[['imageFiles'], 'file', 'skipOnEmpty' => false,
                 'extensions' => 'png, jpg', 'maxFiles' => 4]];
    }

    public function upload()
    {
        if (!$this->validate()) { return false; }
        foreach ($this->imageFiles as $file) {
            $file->saveAs('uploads/' . $file->baseName . '.' . $file->extension);
        }
        return true;
    }
}
```

```php
// представление
<?= $form->field($model, 'imageFiles[]')->fileInput(['multiple' => true, 'accept' => 'image/*']) ?>
```

```php
// контроллер
$model->imageFiles = UploadedFile::getInstances($model, 'imageFiles');  // getInstance() для одного
```

`ActiveForm` с 2.0.8 сам добавляет `enctype="multipart/form-data"`, если в форме есть
`fileInput()`. Для AR-моделей файл обычно не сохраняют в атрибут напрямую — валидируйте
через отдельную форму либо через `UploadedFile::getInstance($model, 'file')` в сценарии.

## Несколько моделей и табличный ввод

```php
// одна форма — несколько разных моделей
if ($user->load(Yii::$app->request->post()) && $profile->load(Yii::$app->request->post())
    && Model::validate([$user, $profile])) {
    // сохраняем в транзакции
}
```

```php
// табличный ввод: массив однотипных моделей
$models = Item::findAll($ids);
if (Model::loadMultiple($models, Yii::$app->request->post())
    && Model::validateMultiple($models)) {
    foreach ($models as $model) { $model->save(false); }
}
```

```php
// в представлении — индексы в именах полей
foreach ($models as $i => $model) {
    echo $form->field($model, "[$i]name");
}
```
