---
id: models
title: Модели
part: structure
summary: Атрибуты и метки, сценарии, правила валидации, безопасное массовое присваивание и экспорт модели в массив.
sources: structure-models
---

:::lead
Модель — это данные + правила их проверки + бизнес-логика. Базовый класс `yii\base\Model` даёт атрибуты, метки, сценарии, валидацию, массовое присваивание и `toArray()`. [Active Record](active-record) наследует всё это и добавляет работу с таблицей.
:::

## Атрибуты

Атрибуты — это *публичные нестатические* свойства класса. К ним можно обращаться и как к свойствам, и как к элементам массива:

```php
class ContactForm extends \yii\base\Model
{
    public $name;
    public $email;
    public $subject;
    public $body;
}

$model = new ContactForm();
$model->name = 'Иван';
$model['email'] = 'ivan@example.com';        // ArrayAccess
foreach ($model as $attr => $value) { }      // Traversable
```

Список атрибутов возвращает `attributes()`; Active Record переопределяет его и берёт имена столбцов таблицы.

### Метки и подсказки

По умолчанию метка генерируется из имени: `firstName` → «First Name». Явно — в `attributeLabels()`; подсказки для форм — в `attributeHints()`:

```php
public function attributeLabels()
{
    return [
        'name' => Yii::t('app', 'Ваше имя'),
        'email' => Yii::t('app', 'E-mail'),
    ];
}

public function attributeHints()
{
    return ['email' => 'Мы не будем присылать спам'];
}

echo $model->getAttributeLabel('name');   // Ваше имя
```

## Сценарии

Одна модель — разные ситуации: при регистрации `email` обязателен, при входе — нет. Сценарий хранится в свойстве `scenario` (по умолчанию `default`):

```php
$model = new User(['scenario' => User::SCENARIO_LOGIN]);
// или
$model->scenario = User::SCENARIO_LOGIN;
```

Сценарий определяет **активные атрибуты** — те, что проходят валидацию и могут быть присвоены массово. По умолчанию сценарии выводятся из правил `rules()` (ключи `on`/`except`), но их можно объявить явно:

```php
class User extends ActiveRecord
{
    const SCENARIO_LOGIN = 'login';
    const SCENARIO_REGISTER = 'register';

    public function scenarios()
    {
        $scenarios = parent::scenarios();                       // сохраняем сценарии из rules()
        $scenarios[self::SCENARIO_LOGIN] = ['username', 'password'];
        $scenarios[self::SCENARIO_REGISTER] = ['username', 'email', 'password'];
        return $scenarios;
    }

    public function rules()
    {
        return [
            [['username', 'email', 'password'], 'required', 'on' => self::SCENARIO_REGISTER],
            [['username', 'password'], 'required', 'on' => self::SCENARIO_LOGIN],
            ['email', 'email'],                                 // во всех сценариях
        ];
    }
}
```

> [!GOTCHA]
> Атрибут валидируется только если он **активен в текущем сценарии** и для него есть **активное правило**. Правило с `on => 'register'` в сценарии `default` молча не сработает. Если `validate()` «ничего не проверяет» — первым делом смотрите сценарий.

## Правила валидации

```php
public function rules()
{
    return [
        [['name', 'email', 'subject', 'body'], 'required'],
        ['email', 'email'],
        ['subject', 'string', 'max' => 100, 'on' => 'contact'],
        'password' => [['password'], 'string', 'min' => 8],     // именованное правило — легко удалить в наследнике
    ];
}

if ($model->validate()) {
    // всё хорошо
} else {
    $errors = $model->errors;               // ['email' => ['Email is not a valid email address.']]
    $model->getFirstError('email');
    $model->hasErrors();
}
```

Формат правила: `[атрибуты, валидатор, 'on' => сценарии, 'except' => сценарии, свойство => значение…]`. Валидатор — псевдоним встроенного (`required`, `email`, `string`…), имя метода модели или класс. Полный разбор — в разделах [Валидация](validation) и [Встроенные валидаторы](validators).

## Массовое присваивание

Одной строкой вместо десятка `$model->x = $data['x']`:

```php
$model->attributes = Yii::$app->request->post('ContactForm');   // напрямую
$model->load(Yii::$app->request->post());                       // то же, но сам возьмёт $_POST[formName()]
```

`load()` возвращает `true`, если данные для модели вообще были в массиве — это удобно для «показать форму или обработать».

### Безопасные атрибуты

Массово присваиваются только **безопасные** атрибуты — активные в текущем сценарии. Остальные молча игнорируются. Так пользователь не сможет через форму выставить себе `role = admin`.

```php
public function rules()
{
    return [
        [['title', 'description'], 'safe'],   // безопасны без проверки
    ];
}

public function scenarios()
{
    return [
        self::SCENARIO_LOGIN => ['username', 'password', '!secret'],   // ! — проверять, но не присваивать массово
    ];
}
$model->secret = $value;   // только явно
```

> [!WHY]
> Без сценариев и безопасных атрибутов любое поле таблицы можно было бы перезаписать, подсунув в POST лишний параметр (mass assignment). В Yii защита включена по умолчанию: нет правила — нет присваивания.

## Экспорт в массив

```php
$array = $model->attributes;                          // все атрибуты
$array = $model->toArray();                           // поля из fields()
$array = $model->toArray([], ['prettyName', 'fullAddress']);   // + поля из extraFields()
```

`fields()` определяет, что попадёт в массив по умолчанию, `extraFields()` — что можно запросить дополнительно (так работает `?expand=` в [REST](rest-advanced)):

```php
public function fields()
{
    return [
        'id',
        'email' => 'email_address',                    // переименование
        'name' => function () {                        // вычисляемое поле
            return $this->first_name . ' ' . $this->last_name;
        },
    ];
}

// или: взять родительские поля и убрать чувствительные
public function fields()
{
    $fields = parent::fields();
    unset($fields['auth_key'], $fields['password_hash'], $fields['password_reset_token']);
    return $fields;
}
```

> [!WARNING]
> По умолчанию в массив попадают **все** атрибуты. У моделей с паролями и токенами обязательно переопределяйте `fields()` — иначе они утекут в JSON-ответ REST API.

## Лучшие практики

- Модели — толстые, контроллеры — тонкие: бизнес-логика живёт здесь.
- Модель не должна лезть в `$_GET`, сессию или запрос — эти данные ей передаёт контроллер.
- Никакого HTML в моделях.
- Не плодите сценарии в одной модели; для сложных форм заводите отдельные классы (`LoginForm`, `SignupForm`).
- В больших проектах: базовая модель в `common\models\Post` с общими правилами, наследники `frontend\models\Post` и `backend\models\Post` — со своей спецификой.

:::quiz Проверь себя
Q: Что делает `$model->load($data)` и чем отличается от `$model->attributes = $data`?
A: `load()` сам находит данные по имени формы (`$data['ContactForm']`) и возвращает `false`, если их нет; присваивание `attributes` работает с уже «распакованным» массивом. Оба присваивают только безопасные атрибуты.
Q: Почему атрибут без правил в `rules()` нельзя заполнить через форму?
A: Он не является безопасным: безопасные атрибуты — это активные атрибуты текущего сценария, а по умолчанию сценарии строятся из правил. Добавьте правило `safe`.
Q: Что означает `!secret` в списке атрибутов сценария?
A: Атрибут валидируется, но не присваивается массово — только явно через `$model->secret = ...`.
Q: Как исключить `password_hash` из JSON-ответа API?
A: Переопределить `fields()` и убрать поле из массива родительской реализации.
Q: В каком методе объявить, что одна и та же модель по-разному проверяется при входе и регистрации?
A: В `rules()` через `'on' => 'login'` / `'on' => 'register'` или явно перечислив активные атрибуты в `scenarios()`.
:::
