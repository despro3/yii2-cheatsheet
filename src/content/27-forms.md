---
id: forms
title: Формы и ввод
part: input
summary: ActiveForm и ActiveField — поля, списки, шаблоны и подсказки; загрузка файлов через UploadedFile; табличный ввод (loadMultiple/validateMultiple) и несколько моделей в одной форме; JavaScript-API формы (валидация, события, динамические поля).
sources: input-forms, input-file-upload, input-tabular-input, input-multiple-models, input-form-javascript
---

:::lead
Форма в Yii — это **модель** (правила и подписи), **виджет ActiveForm** (HTML + клиентская валидация) и **контроллер** (`load()` → `validate()` → действие). Всё уже сцеплено: `$form->field($model, 'email')` сам рисует label, input с именем `LoginForm[email]`, подсказку, ошибку и подключает JS-правила из `rules()`.
:::

## Классическая тройка

```php title="models/EntryForm.php"
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

    if ($model->load(Yii::$app->request->post()) && $model->validate()) {
        // данные проверены — сохранить, отправить письмо…
        return $this->redirect(['entry-confirm']);   // PRG: редирект после POST
    }
    return $this->render('entry', ['model' => $model]);
}
```

```php title="views/site/entry.php"
<?php $form = ActiveForm::begin(['id' => 'entry-form']); ?>
    <?= $form->field($model, 'name') ?>
    <?= $form->field($model, 'email')->input('email') ?>
    <div class="form-group">
        <?= Html::submitButton('Отправить', ['class' => 'btn btn-primary']) ?>
    </div>
<?php ActiveForm::end(); ?>
```

`load()` берёт из POST массив по имени формы (`EntryForm`) и присваивает только безопасные (перечисленные в `rules()`) атрибуты. Форма отправляет CSRF-токен автоматически.

## ActiveField — виды полей

```php
$form->field($model, 'password')->passwordInput();
$form->field($model, 'bio')->textarea(['rows' => 6]);
$form->field($model, 'age')->input('number', ['min' => 18]);
$form->field($model, 'agree')->checkbox();
$form->field($model, 'id')->hiddenInput()->label(false);
$form->field($model, 'file')->fileInput();

$form->field($model, 'product_id')->dropDownList(
    ArrayHelper::map(Product::find()->all(), 'id', 'name'),        // [id => name]
    ['prompt' => 'Выберите товар']
);
$form->field($model, 'tags')->listBox($items, ['multiple' => true]);
$form->field($model, 'gender')->radioList(['m' => 'Муж.', 'f' => 'Жен.']);
$form->field($model, 'roles')->checkboxList($roles);

$form->field($model, 'date')->widget(DatePicker::class, ['dateFormat' => 'yyyy-MM-dd']);   // любой InputWidget

// оформление
$form->field($model, 'name')->label('Имя пользователя')->hint('Как в паспорте');
$form->field($model, 'name', ['template' => "{label}\n<div class=\"col-9\">{input}</div>\n{error}"]);
$form->field($model, 'name', ['inputOptions' => ['placeholder' => 'Иван']]);
```

Настройки формы целиком: `ActiveForm::begin(['fieldConfig' => ['template' => '…'], 'options' => ['enctype' => 'multipart/form-data'], 'enableClientValidation' => true, 'enableAjaxValidation' => false, 'validateOnBlur' => true])`.

### Списки: где взять данные

```php
use yii\helpers\ArrayHelper;

$items = ArrayHelper::map(Country::find()->orderBy('name')->all(), 'code', 'name');
// [ 'RU' => 'Россия', 'US' => 'США' ]
$items = ArrayHelper::map($rows, 'id', 'name', 'group');   // группы → <optgroup>
```

## Pjax и формы

```php
<?php Pjax::begin(['id' => 'pjax-form']) ?>
<?php $form = ActiveForm::begin(['options' => ['data-pjax' => true]]) ?>
    …
<?php ActiveForm::end() ?>
<?php Pjax::end() ?>
```

Атрибут `data-pjax` на форме — и отправка пройдёт без перезагрузки страницы, обновив только контейнер. Внутри Pjax не дублируйте ID формы; ссылки внутри тоже станут pjax-запросами.

## Загрузка файлов

```php title="models/UploadForm.php"
use yii\web\UploadedFile;

class UploadForm extends Model
{
    /** @var UploadedFile */
    public $imageFile;

    public function rules()
    {
        return [
            [['imageFile'], 'file', 'skipOnEmpty' => false, 'extensions' => 'png, jpg', 'maxSize' => 1024 * 1024],
            // 'image' — валидатор с проверкой размеров: 'minWidth', 'maxHeight'…
        ];
    }

    public function upload()
    {
        if ($this->validate()) {
            $file = $this->imageFile;
            $file->saveAs('@webroot/uploads/' . $file->baseName . '.' . $file->extension);
            return true;
        }
        return false;
    }
}
```

```php title="controllers/SiteController.php"
public function actionUpload()
{
    $model = new UploadForm();
    if (Yii::$app->request->isPost) {
        $model->imageFile = UploadedFile::getInstance($model, 'imageFile');
        if ($model->upload()) {
            return;   // файл сохранён
        }
    }
    return $this->render('upload', ['model' => $model]);
}
```

```php title="views/site/upload.php"
<?php $form = ActiveForm::begin(['options' => ['enctype' => 'multipart/form-data']]) ?>
    <?= $form->field($model, 'imageFile')->fileInput() ?>
    <button>Загрузить</button>
<?php ActiveForm::end() ?>
```

> [!GOTCHA]
> Три вещи, без которых не работает: `enctype="multipart/form-data"` у формы, `UploadedFile::getInstance()` в контроллере (через `load()` файл не придёт) и `skipOnEmpty => false`, если файл обязателен. И никогда не сохраняйте под именем, которое прислал клиент, — генерируйте своё.

### Несколько файлов

```php
public $imageFiles;   // массив UploadedFile

[['imageFiles'], 'file', 'skipOnEmpty' => false, 'extensions' => 'png, jpg', 'maxFiles' => 4],

// контроллер
$model->imageFiles = UploadedFile::getInstances($model, 'imageFiles');
foreach ($model->imageFiles as $file) {
    $file->saveAs('uploads/' . $file->baseName . '.' . $file->extension);
}

// представление: имя атрибута с [] и multiple
<?= $form->field($model, 'imageFiles[]')->fileInput(['multiple' => true, 'accept' => 'image/*']) ?>
```

`maxFiles => 0` снимает ограничение на количество.

## Табличный ввод — много одинаковых моделей

Редактируем сразу несколько записей (например, все настройки):

```php
public function actionBatchUpdate()
{
    $settings = Setting::find()->indexBy('id')->all();

    if (Model::loadMultiple($settings, Yii::$app->request->post()) && Model::validateMultiple($settings)) {
        foreach ($settings as $setting) {
            $setting->save(false);
        }
        return $this->redirect('index');
    }
    return $this->render('batch-update', ['settings' => $settings]);
}
```

```php
<?php foreach ($settings as $index => $setting): ?>
    <?= $form->field($setting, "[$index]value")->label($setting->name) ?>
<?php endforeach; ?>
```

Имя поля станет `Setting[1][value]`, `loadMultiple()` разложит их по объектам. Для создания N новых записей — заранее создать N объектов `new Setting()` (или расширить массив под количество пришедших строк) и то же самое.

## Несколько разных моделей в одной форме

```php
$user = User::findOne($id);
$profile = $user->profile;

if ($user->load(Yii::$app->request->post()) && $profile->load(Yii::$app->request->post())) {
    $isValid = $user->validate();
    $isValid = $profile->validate() && $isValid;       // валидировать обе, даже если первая упала
    if ($isValid) {
        $user->save(false);
        $profile->save(false);
        return $this->redirect(['user/view', 'id' => $id]);
    }
}
return $this->render('update', ['user' => $user, 'profile' => $profile]);
```

```php
<?= $form->field($user, 'username') ?>
<?= $form->field($profile, 'website') ?>
```

Разные классы — разные имена форм (`User[username]`, `Profile[website]`), конфликтов нет. Если классы одинаковые, задайте `formName()` или используйте индексы, как в табличном вводе.

## JavaScript-API ActiveForm

Виджет подключает `yii.activeForm.js` и передаёт ему правила из `clientValidateAttribute()` валидаторов.

### Настройка валидации

:::kv
`enableClientValidation` — JS-проверка по правилам (по умолчанию `true`)
`enableAjaxValidation` — проверка запросом на сервер (для `unique`, `exist` и других серверных правил)
`validateOnBlur`, `validateOnChange`, `validateOnType` (+`validationDelay`), `validateOnSubmit` — когда проверять
`validationUrl` — куда слать AJAX-валидацию (по умолчанию — action формы)
`errorCssClass`, `successCssClass`, `validatingCssClass`, `errorSummaryCssClass` — классы состояния
:::

Обработчик AJAX-валидации на сервере:

```php
if (Yii::$app->request->isAjax && $model->load(Yii::$app->request->post())) {
    Yii::$app->response->format = Response::FORMAT_JSON;
    return ActiveForm::validate($model);          // {"loginform-email": ["…"]}
}
```

### События

```js
$('#contact-form').on('beforeValidate', function (event, messages, deferreds) { });
$('#contact-form').on('afterValidate', function (event, messages, errorAttributes) { });
$('#contact-form').on('beforeValidateAttribute', function (event, attribute, messages, deferreds) { });
$('#contact-form').on('afterValidateAttribute', function (event, attribute, messages) { });
$('#contact-form').on('beforeSubmit', function () {
    // отправить через AJAX и не отправлять форму обычным способом
    $.post($(this).attr('action'), $(this).serialize()).done(function () { });
    return false;
});
$('#contact-form').on('ajaxBeforeSend', function (event, jqXHR, settings) { });
$('#contact-form').on('ajaxComplete', function (event, jqXHR, textStatus) { });
$('#contact-form').on('afterInit', function () { });
```

`deferreds` — массив, куда можно положить `$.Deferred()` для асинхронных проверок; `messages` — объект `{id: [ошибки]}`, туда можно дописать свою.

### Динамические поля

```js
$('#contact-form').yiiActiveForm('add', {
    id: 'address',
    name: 'address',
    container: '.field-address',
    input: '#address',
    error: '.help-block',
    validate: function (attribute, value, messages, deferred, $form) {
        yii.validation.required(value, messages, { message: 'Заполните адрес' });
    }
});
$('#contact-form').yiiActiveForm('remove', 'address');
$('#contact-form').yiiActiveForm('validate');               // проверить всю форму
$('#contact-form').yiiActiveForm('validate', true);         // только изменённые поля
$('#contact-form').yiiActiveForm('validateAttribute', 'contactform-email');
$('#contact-form').yiiActiveForm('updateAttribute', 'contactform-email', ['Занят']);   // показать ошибку
$('#contact-form').yiiActiveForm('updateMessages', { 'contactform-email': ['Занят'] }, true);
$('#contact-form').yiiActiveForm('resetForm');
$('#contact-form').yiiActiveForm('find', 'contactform-email');   // настройки атрибута
```

Правила и опции всех полей хранятся в `$('#form').yiiActiveForm('data')`.

:::quiz Проверь себя
Q: Почему после `load()` атрибут остался пустым, хотя поле было в POST?
A: Атрибут не «безопасный»: он не упомянут в `rules()` (или в правиле `safe`) для текущего сценария, и массовое присваивание его пропустило.
Q: Что нужно для загрузки файла помимо `fileInput()`?
A: `enctype="multipart/form-data"` у формы и `UploadedFile::getInstance($model, 'attr')` в контроллере; затем `saveAs()`.
Q: Как проверить `unique` на клиенте без перезагрузки страницы?
A: Включить `enableAjaxValidation` и в действии вернуть `ActiveForm::validate($model)` в формате JSON для AJAX-запроса.
Q: Как назвать поля, чтобы `Model::loadMultiple()` разложил их по объектам?
A: `$form->field($model, "[$index]attr")` — получится `Model[index][attr]`.
Q: Как отправить форму через AJAX, сохранив клиентскую валидацию?
A: Подписаться на событие `beforeSubmit`, отправить `$.post` и вернуть `false`.
:::
