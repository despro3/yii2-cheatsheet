---
id: validation
title: Валидация
part: input
summary: Правила rules(), сценарии и on/except, пустые значения и skipOnEmpty/skipOnError, условная валидация when/whenClient, фильтрация данных, ad hoc-валидация через DynamicModel, свои валидаторы (inline и класс), клиентская, отложенная и AJAX-валидация.
sources: input-validation
---

:::lead
Данные извне не проверены, пока не прошли `validate()`. Правила описываются декларативно в `rules()`, ошибки собираются в модели, а те же правила автоматически превращаются в клиентскую JavaScript-проверку. Это единый механизм для форм, REST-запросов и консольных команд.
:::

## rules()

```php
public function rules()
{
    return [
        // [атрибуты, валидатор, опции...]
        [['username', 'email', 'password'], 'required'],
        ['email', 'email'],
        ['username', 'string', 'min' => 2, 'max' => 24],
        ['username', 'unique', 'targetClass' => User::class],
        ['age', 'integer', 'min' => 18, 'message' => 'Только для взрослых'],
        ['status', 'in', 'range' => [self::STATUS_ACTIVE, self::STATUS_DELETED]],
        ['status', 'default', 'value' => self::STATUS_ACTIVE],
        ['website', 'url', 'defaultScheme' => 'https'],
        ['password_repeat', 'compare', 'compareAttribute' => 'password'],
        [['first_name', 'last_name'], 'trim'],
        ['title', 'filter', 'filter' => 'strip_tags'],
        ['title', 'validateTitle'],                       // inline-валидатор — метод модели
        ['country', \app\components\validators\CountryValidator::class],   // свой класс
        ['tags', 'safe'],                                 // без проверки, но разрешить load()
        ['token', 'required', 'on' => 'register'],        // только в сценарии
        ['email', 'unique', 'except' => 'update'],        // во всех, кроме
    ];
}
```

Валидатор указывается коротким именем ([встроенные валидаторы](validators)), именем класса, объектом или именем метода модели. Правила применяются **по порядку**, атрибут проверяется всеми правилами, где он упомянут.

## Запуск и ошибки

```php
$model = new ContactForm();
$model->load(Yii::$app->request->post());

if ($model->validate()) {                 // все атрибуты активного сценария
    // ok
} else {
    $model->errors;                       // ['email' => ['…', '…'], 'name' => ['…']]
    $model->getFirstErrors();             // ['email' => '…']
    $model->getFirstError('email');
    $model->getErrorSummary(true);        // плоский список
    $model->hasErrors('email');
}

$model->validate(['email', 'name']);      // только эти атрибуты
$model->addError('email', 'Такой уже есть');   // ошибка вручную
$model->clearErrors();
```

`ActiveRecord::save()` вызывает `validate()` сам. В сообщениях доступны `{attribute}` (подпись из `attributeLabels()`) и `{value}`, у конкретных валидаторов — свои плейсхолдеры (`{min}`, `{max}`…).

### Активные правила и атрибуты

```php
$model->scenario = 'register';
$model->activeAttributes();     // атрибуты, участвующие в сценарии
$model->getActiveValidators();  // валидаторы сценария
$model->getActiveValidators('email');
$model->validators;             // ArrayObject всех валидаторов — можно добавить объект на лету
```

Правило активно, если сценарий модели попадает в `on` (или `on` не задан) и не попадает в `except`. Атрибуты активных правил становятся *безопасными* для `load()` — кроме тех, что помечены восклицательным знаком в `scenarios()`.

## Пустые значения

По умолчанию валидатор **пропускает пустой** атрибут (`null`, `''`, `[]`) — проверяет только `required`. Меняется опцией:

```php
['email', 'email', 'skipOnEmpty' => false],
['tags', 'each', 'rule' => ['string'], 'isEmpty' => function ($value) { return $value === [] || $value === null; }],
```

По умолчанию `Validator::isEmpty()` считает пустыми `null`, `''` и `[]`. Ошибка при первом правиле атрибута приводит к пропуску остальных — `skipOnError => false` отключает это.

## Условная валидация

```php
['state', 'required', 'when' => function ($model) {
    return $model->country == 'USA';
}, 'whenClient' => "function (attribute, value) {
    return $('#country').val() == 'USA';
}"],
```

`when` — серверное условие; `whenClient` — то же на JS, чтобы клиентская валидация не спорила с серверной.

## Фильтрация — не проверка, а преобразование

```php
[['username', 'email'], 'trim'],
['username', 'filter', 'filter' => 'strtolower'],
['title', 'filter', 'filter' => function ($value) { return mb_substr($value, 0, 100); }],
['status', 'default', 'value' => 1],       // если пусто
['is_active', 'boolean'],                  // не преобразует! только проверяет
```

`trim`, `filter`, `default` меняют значение атрибута. Ставьте их перед проверяющими правилами.

## Ad hoc-валидация

Проверить значения без класса модели — `DynamicModel`:

```php
public function actionSearch($name, $email)
{
    $model = DynamicModel::validateData(compact('name', 'email'), [
        [['name', 'email'], 'string', 'max' => 128],
        ['email', 'email'],
    ]);

    if ($model->hasErrors()) {
        // …
    }
}

// или одно значение
$validator = new EmailValidator();
if ($validator->validate($email, $error)) { } else { echo $error; }
```

`DynamicModel` можно создать и вручную: `new DynamicModel(compact('name', 'email'))` → `addRule('email', 'email')` → `validate()`.

## Свои валидаторы

### Inline — метод модели

```php
public function rules()
{
    return [
        ['country', 'validateCountry'],
        ['token', function ($attribute, $params, $validator) {
            if ($this->$attribute !== 'a') {
                $this->addError($attribute, 'Неверный токен');
            }
        }],
    ];
}

public function validateCountry($attribute, $params, $validator)
{
    if (!in_array($this->$attribute, ['USA', 'Indonesia'])) {
        $validator->addError($this, $attribute, '{attribute} должна быть "USA" или "Indonesia".');
    }
}
```

Inline-валидаторы **не** имеют клиентской части и, как и все, пропускают пустые значения, если не задан `skipOnEmpty => false`. С 2.0.11 удобнее `$validator->addError($this, $attribute, $message)` — работает с плейсхолдерами.

### Отдельный класс

```php
namespace app\components;

use yii\validators\Validator;

class CountryValidator extends Validator
{
    public function validateAttribute($model, $attribute)
    {
        if (!in_array($model->$attribute, ['USA', 'Indonesia'])) {
            $this->addError($model, $attribute, '{attribute} должна быть "USA" или "Indonesia".');
        }
    }

    // чтобы валидатор работал и вне модели ($validator->validate($value, $error))
    protected function validateValue($value)
    {
        return in_array($value, ['USA', 'Indonesia']) ? null : ['{attribute} должна быть "USA" или "Indonesia".', []];
    }
}
```

Достаточно переопределить `validateValue()` — `validateAttribute()` по умолчанию вызывает его. Если у валидатора есть опции, объявите их публичными свойствами и задайте умолчания в `init()`.

### Валидатор с несколькими атрибутами

```php
class MigrationRule extends Validator
{
    public function validateAttribute($model, $attribute)
    {
        if ($model->$attribute == $model->otherAttribute) { … }
    }
}
// применить один раз, а не для каждого атрибута:
[['from', 'to'], MigrationRule::class],   // validateAttribute вызовется дважды
['from', MigrationRule::class],           // один раз — ошибки добавить обоим вручную
```

## Клиентская валидация

Встроенные валидаторы (кроме `unique`, `exist`, `file` частично и inline) генерируют JS через `clientValidateAttribute()`. Свой:

```php
public function clientValidateAttribute($model, $attribute, $view)
{
    $statuses = json_encode(Status::find()->select('id')->column());
    $message = json_encode($this->message);
    return <<<JS
if ($.inArray(value, $statuses) === -1) {
    messages.push($message);
}
JS;
}
```

В JS доступны `attribute`, `value`, `messages`, `deferred`, `$form`. Отключить: `enableClientValidation => false` у формы или `'enableClientValidation' => false` в правиле.

> [!TIP]
> С 2.0.11 у валидаторов есть `getClientOptions()` — можно отдать опции клиентскому коду без генерации JS-строк, а `yii.validation.*` (`required`, `string`, `email`, `number`, `compare`…) вызываются из вашего JS так же, как из сгенерированного.

### Отложенная (deferred) валидация

Для асинхронных проверок на клиенте (например, размер изображения):

```js
var def = $.Deferred();
var img = new Image();
img.onload = function () {
    if (this.width > 150) messages.push('Слишком широкое');
    def.resolve();
};
img.src = URL.createObjectURL(file);
deferred.push(def);
```

Форма ждёт все `deferred`, прежде чем показать результат.

### AJAX-валидация

Когда клиентской логики недостаточно (`unique`, сложные проверки):

```php
// форма
$form = ActiveForm::begin(['enableAjaxValidation' => true]);
$form->field($model, 'username', ['enableAjaxValidation' => true]);   // или для одного поля

// действие
if (Yii::$app->request->isAjax && $model->load(Yii::$app->request->post())) {
    Yii::$app->response->format = Response::FORMAT_JSON;
    return ActiveForm::validate($model);
}
```

`ActiveForm::validate($model, 'attr1', 'attr2')` вернёт ошибки в формате, который ждёт JS формы. Для табличного ввода — `ActiveForm::validateMultiple($models)`.

## Порядок выполнения на практике

:::steps
1. `load()` — массовое присваивание безопасных атрибутов сценария.
2. `validate()` → `beforeValidate()`; `false` — прерывание.
3. Для каждого правила по порядку: пропуск пустых (`skipOnEmpty`), пропуск с ошибками (`skipOnError`), условие `when`, затем проверка или фильтрация.
4. `afterValidate()`; результат — `!hasErrors()`.
:::

:::quiz Проверь себя
Q: Почему валидатор `email` не ругается на пустое поле?
A: По умолчанию `skipOnEmpty = true`: пустые значения проверяет только `required`. Задайте `'skipOnEmpty' => false`, если нужно.
Q: Как проверить несколько значений без создания класса модели?
A: `DynamicModel::validateData($data, $rules)` или `new DynamicModel()` с `addRule()`.
Q: Как сделать правило обязательным только при определённом значении другого поля?
A: Опцией `when` (и `whenClient` для JS): `'when' => function ($model) { return $model->country == 'USA'; }`.
Q: Что нужно, чтобы свой валидатор работал через `$validator->validate($value)` вне модели?
A: Реализовать `validateValue($value)`, возвращающий `null` либо `[сообщение, параметры]`.
Q: Почему inline-валидатор не проверяет данные на клиенте?
A: У него нет `clientValidateAttribute()`; используйте класс-валидатор с JS-кодом или AJAX-валидацию.
:::
