# -*- coding: utf-8 -*-
"""Содержимое «Справочника Yii 2»: темы, их вкладки и блоки.

Блок — кортеж, первый элемент задаёт тип:
  ('p', текст)                         абзац; поддерживает `код`, **жирный**, [ссылка](url)
  ('h', текст)                         подзаголовок внутри вкладки
  ('code', lang, title|None, код)      блок кода с подсветкой
  ('svg', разметка, подпись)           схема
  ('ref', [ {n, d, o, c} ])            перечень встроенного с фильтром
  ('kv', [(ключ, значение)])           таблица «ключ — значение»
  ('steps', [шаг, ...])                нумерованная последовательность
  ('note', kind, заголовок, текст)     врезка: tip | warn | trap
  ('demo', id)                         интерактивная вставка
"""

# Порядок групп — это порядок, в котором узлы встречаются на пути запроса,
# поэтому сквозная нумерация идёт слева направо и сверху вниз по схеме-карте.
GROUPS = [
    ('http',   'Запрос и доступ',   'Что пришло от браузера, какому действию это отдать и кого туда пускать'),
    ('data',   'Данные и правила',  'Что приходит от пользователя и что с этим делает модель'),
    ('db',     'База данных',       'Запросы, записи, связи'),
    ('view',   'Вывод и состояние', 'Чем рисуется страница и что живёт дольше одного запроса'),
    ('object', 'Объектная модель',  'Из чего собран фреймворк и как в него встроиться'),
]

TOPICS = []


def topic(**kw):
    TOPICS.append(kw)
    return kw


# --------------------------------------------------------------------------- Модель

topic(
    id='model', group='data',
    title='Модель',
    cls='yii\\base\\Model',
    lead='Набор атрибутов с правилами, подписями и ошибками. Основа форм и Active Record.',
    badge='11 методов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Модель — это объект с **атрибутами** (публичные свойства или столбцы таблицы), '
                  '**правилами** их проверки и **ошибками**, которые накопились после проверки. '
                  'Всё остальное в формах Yii строится поверх этих трёх вещей.'),
            ('svg', '''<svg viewBox="0 0 760 210" role="img" aria-label="Путь данных формы: POST, load, валидация, сохранение или показ ошибок" class="dg">
<defs><marker id="m-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr)" opacity=".55">
<path d="M132 46h36"/><path d="M290 46h36"/><path d="M448 46h36"/>
<path d="M566 70v34h-80"/><path d="M406 70v58"/>
</g>
<g class="dg-box"><rect x="16" y="24" width="116" height="44" rx="8"/><text x="74" y="43">POST</text><text x="74" y="59" class="dg-sub">сырые данные</text></g>
<g class="dg-box"><rect x="168" y="24" width="122" height="44" rx="8"/><text x="229" y="43">load()</text><text x="229" y="59" class="dg-sub">только безопасные</text></g>
<g class="dg-box"><rect x="326" y="24" width="122" height="44" rx="8"/><text x="387" y="43">validate()</text><text x="387" y="59" class="dg-sub">правила rules()</text></g>
<g class="dg-box dg-ok"><rect x="486" y="24" width="160" height="44" rx="8"/><text x="566" y="43">save() / отправка</text><text x="566" y="59" class="dg-sub">данные проверены</text></g>
<g class="dg-box dg-bad"><rect x="326" y="128" width="160" height="44" rx="8"/><text x="406" y="147">errors</text><text x="406" y="163" class="dg-sub">снова показать форму</text></g>
<text x="516" y="98" class="dg-note" text-anchor="middle">false</text>
<text x="420" y="104" class="dg-note">не прошло</text>
</svg>''', 'Один и тот же путь у формы обратной связи и у Active Record: разница только в последнем шаге.'),
            ('code', 'php', 'models/ContactForm.php', r'''use yii\base\Model;

class ContactForm extends Model
{
    public $name;
    public $email;
    public $body;

    public function rules()
    {
        return [
            [['name', 'email', 'body'], 'required'],
            ['email', 'email'],
        ];
    }

    public function attributeLabels()
    {
        return ['email' => 'Электронная почта'];
    }

    public function attributeHints()
    {
        return ['body' => 'Опишите проблему подробно'];
    }
}'''),
            ('h', 'Ежедневный набор методов'),
            ('kv', [
                ('$model->attributes', 'все атрибуты массивом; присваивание работает как массовое'),
                ('load($data, $formName = null)', 'взять из `$_POST[\'ContactForm\']`, присвоить только безопасные атрибуты, вернуть `true`, если данные были'),
                ('validate($attrs = null)', 'проверить и вернуть `true` или `false`'),
                ('errors / getFirstErrors()', 'все ошибки по атрибутам или по одной на атрибут'),
                ('hasErrors($attr = null)', 'есть ли ошибки вообще или у конкретного атрибута'),
                ('addError($attr, $msg)', 'добавить ошибку руками, например после проверки во внешнем сервисе'),
                ('clearErrors()', 'сбросить накопленные ошибки'),
                ('formName()', 'имя ключа в POST; по умолчанию короткое имя класса'),
                ('safeAttributes()', 'какие атрибуты пустит внутрь `load()` в текущем сценарии'),
                ('activeAttributes()', 'какие атрибуты проверяются в текущем сценарии'),
                ('toArray()', 'наружу как массив; для API переопределяют `fields()`'),
            ]),
            ('note', 'trap', 'Атрибут молча не присвоился',
             'Если атрибута нет ни в одном правиле активного сценария, `load()` его пропустит без ошибки. '
             'Это защита от массового присваивания, а не баг. Нужен атрибут без проверки — добавьте правило `safe`.'),
        ]),
        ('all', 'Что даёт базовый класс', [
            ('p', '`Model` наследует `Component`, поэтому получает свойства через геттеры, события и поведения. '
                  'Плюс реализует три интерфейса, на которые опирается остальной фреймворк.'),
            ('ref', [
                {'n': 'Configurable', 'd': 'Последний параметр конструктора — массив настроек. Благодаря этому модель создаётся через `Yii::createObject()` и настраивается из конфигурации.', 'o': 'от BaseObject', 'c': "new ContactForm(['scenario' => 'guest'])"},
                {'n': 'ArrayAccess', 'd': 'Доступ к атрибутам как к элементам массива. Используется в шаблонах и хелперах.', 'o': 'от Model', 'c': "$model['email']"},
                {'n': 'IteratorAggregate', 'd': 'Модель можно обойти в `foreach` по её атрибутам.', 'o': 'от Model', 'c': "foreach ($model as $name => $value) { }"},
                {'n': 'Arrayable', 'd': 'Превращение в массив с управлением набором полей. На нём стоит весь REST-слой.', 'o': 'fields(), extraFields(), toArray()', 'c': "public function fields()\n{\n    $f = parent::fields();\n    unset($f['password_hash']);\n    return $f;\n}"},
                {'n': 'События модели', 'd': 'Две точки встраивания вокруг проверки. Отмена — через `$event->isValid = false`.', 'o': 'EVENT_BEFORE_VALIDATE, EVENT_AFTER_VALIDATE', 'c': "public function beforeValidate()\n{\n    $this->email = mb_strtolower((string) $this->email);\n    return parent::beforeValidate();\n}"},
                {'n': 'DynamicModel', 'd': 'Модель без класса: правила и атрибуты задаются на месте. Для разовой проверки параметров запроса или данных из внешнего API.', 'o': 'validateData(), addRule()', 'c': "$m = DynamicModel::validateData(compact('name', 'email'), [\n    [['name', 'email'], 'string', 'max' => 128],\n    ['email', 'email'],\n]);\nif ($m->hasErrors()) { /* … */ }"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Вычисляемый атрибут через геттер'),
            ('code', 'php', None, r'''class User extends Model
{
    public $firstName;
    public $lastName;

    // читается как обычное свойство: $user->fullName
    public function getFullName()
    {
        return trim($this->firstName . ' ' . $this->lastName);
    }
}'''),
            ('h', 'Общая база для всех моделей проекта'),
            ('code', 'php', 'models/BaseModel.php', r'''abstract class BaseModel extends \yii\base\Model
{
    // единое сообщение об ошибке и общий сценарий поиска
    public function addErrors($items)
    {
        foreach ($items as $attribute => $message) {
            $this->addError($attribute, $message);
        }
    }

    public function firstErrorText()
    {
        $errors = $this->getFirstErrors();
        return $errors ? reset($errors) : null;
    }
}'''),
            ('h', 'Модель поверх чужого API, без базы данных'),
            ('code', 'php', None, r'''class WeatherForm extends Model
{
    public $city;
    public $days;

    public function rules()
    {
        return [
            ['city', 'required'],
            ['city', 'string', 'min' => 2, 'max' => 64],
            ['days', 'integer', 'min' => 1, 'max' => 14],
            ['days', 'default', 'value' => 3],
        ];
    }

    public function fetch()
    {
        if (!$this->validate()) {
            return null;
        }
        return Yii::$app->weatherService->forecast($this->city, $this->days);
    }
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'formName() и данные из API',
             'REST-клиент шлёт плоский JSON без обёртки `ContactForm`. Тогда `load($data)` ничего не найдёт. '
             'Передайте пустое имя формы: `$model->load($data, \'\')`.'),
            ('note', 'trap', 'Проверили одну модель, забыли вторую',
             'При двух моделях в форме `$a->validate() && $b->validate()` остановится на первой упавшей, и пользователь увидит только половину ошибок. '
             'Считайте обе: `$ok = $a->validate(); $ok = $b->validate() && $ok;`'),
            ('note', 'warn', 'errors против getFirstErrors()',
             '`errors` возвращает массив массивов, по нему нельзя просто пройти `implode`. '
             'Для короткого сообщения берите `getFirstErrors()` или `getErrorSummary(true)`.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Правила и валидаторы

topic(
    id='rules', group='data',
    title='Правила и валидаторы',
    cls='rules()',
    lead='Декларативная проверка входных данных. Те же правила автоматически работают в браузере.',
    badge='24 встроенных',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Правило — массив `[атрибуты, валидатор, опции…]`. Правила применяются **по порядку**, '
                  'атрибут проходит через все правила, где он упомянут. '
                  'Атрибуты из активных правил становятся безопасными для `load()`.'),
            ('svg', '''<svg viewBox="0 0 760 232" role="img" aria-label="Что происходит с каждым правилом: пустое значение, предыдущая ошибка, условие when, затем проверка" class="dg">
<defs><marker id="m-arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr2)" opacity=".55">
<path d="M126 52h30"/><path d="M270 52h30"/><path d="M414 52h30"/><path d="M558 52h30"/>
<path d="M357 110v18"/>
</g>
<g stroke="currentColor" stroke-width="1.5" fill="none" opacity=".4">
<path d="M213 74v36"/><path d="M357 74v36"/><path d="M501 74v36"/><path d="M213 110h288"/>
</g>
<g class="dg-box"><rect x="16" y="30" width="110" height="44" rx="8"/><text x="71" y="49">значение</text><text x="71" y="65" class="dg-sub">из формы</text></g>
<g class="dg-box"><rect x="156" y="30" width="114" height="44" rx="8"/><text x="213" y="49">пустое?</text><text x="213" y="65" class="dg-sub">skipOnEmpty</text></g>
<g class="dg-box"><rect x="300" y="30" width="114" height="44" rx="8"/><text x="357" y="49">была ошибка?</text><text x="357" y="65" class="dg-sub">skipOnError</text></g>
<g class="dg-box"><rect x="444" y="30" width="114" height="44" rx="8"/><text x="501" y="49">условие</text><text x="501" y="65" class="dg-sub">when</text></g>
<g class="dg-box dg-live"><rect x="588" y="30" width="140" height="44" rx="8"/><text x="658" y="49">проверка</text><text x="658" y="65" class="dg-sub">validateAttribute()</text></g>
<g class="dg-box dg-muted"><rect x="277" y="150" width="160" height="40" rx="8"/><text x="357" y="175">правило пропущено</text></g>
</svg>''', 'Три причины, по которым правило может не сработать. Чаще всего виновато первое: пустое значение проверяет только required.'),
            ('demo', 'validator-lab'),
            ('h', 'Запуск и разбор ошибок'),
            ('code', 'php', None, r'''$model->load(Yii::$app->request->post());

if ($model->validate()) {
    // данные проверены
} else {
    $model->errors;             // ['email' => ['Неверный формат', …]]
    $model->getFirstErrors();   // ['email' => 'Неверный формат']
    $model->getFirstError('email');
    $model->getErrorSummary(true);
}

$model->validate(['email', 'name']);   // только эти атрибуты'''),
            ('note', 'trap', 'Пустое значение проходит мимо правила',
             'По умолчанию любой валидатор кроме `required` пропускает `null`, `\'\'` и `[]`. '
             'Хотите проверять и пустые — добавьте `\'skipOnEmpty\' => false`.'),
        ]),
        ('all', 'Все 24 валидатора', [
            ('p', 'Каждый валидатор — класс в `yii\\validators`, но в правилах пишут короткое имя. '
                  'Общие опции у всех: `message`, `on`, `except`, `skipOnEmpty`, `skipOnError`, `when`, `whenClient`, `enableClientValidation`.'),
            ('ref', [
                {'n': 'required', 'd': 'Значение не пустое. Единственный валидатор, который не пропускает пустые значения.', 'o': 'requiredValue — ждать конкретное значение; strict — сравнивать строго', 'c': "[['username', 'password'], 'required'],\n['accept', 'required', 'requiredValue' => 1,\n    'message' => 'Примите условия'],"},
                {'n': 'safe', 'd': 'Ничего не проверяет, но делает атрибут безопасным для массового присваивания через load().', 'o': 'без опций', 'c': "['notes', 'safe'],"},
                {'n': 'default', 'd': 'Подставляет значение, если атрибут пуст. Не проверяет, а заполняет — ставьте до проверяющих правил.', 'o': 'value — значение или замыкание', 'c': "['status', 'default', 'value' => 1],\n['created_at', 'default',\n    'value' => function ($m) { return time(); }],"},
                {'n': 'filter', 'd': 'Прогоняет значение через callback и записывает результат обратно в атрибут.', 'o': 'filter — строка, замыкание или [класс, метод]; skipOnArray', 'c': "['username', 'filter', 'filter' => 'strtolower'],\n['phone', 'filter', 'filter' => function ($v) {\n    return preg_replace('/\\D/', '', $v);\n}],"},
                {'n': 'trim', 'd': 'Обрезает пробелы по краям. Частный случай filter, но с клиентской частью.', 'o': 'chars — какие символы резать', 'c': "[['title', 'body'], 'trim'],"},
                {'n': 'string', 'd': 'Строка заданной длины. Длина считается в символах с учётом кодировки.', 'o': 'min, max, length, encoding, tooShort, tooLong', 'c': "['username', 'string', 'min' => 2, 'max' => 24],\n['code', 'string', 'length' => 6],\n['title', 'string', 'length' => [4, 120]],"},
                {'n': 'email', 'd': 'Адрес электронной почты.', 'o': 'allowName — разрешить «Иван &lt;i@x.io&gt;»; checkDNS — проверить MX-запись; enableIDN — домены не на латинице', 'c': "['email', 'email'],\n['email', 'email', 'checkDNS' => true,\n    'enableIDN' => true],"},
                {'n': 'url', 'd': 'Адрес страницы. Умеет дописывать схему, если пользователь её не ввёл.', 'o': 'validSchemes, defaultScheme, enableIDN', 'c': "['website', 'url', 'defaultScheme' => 'https'],\n['api', 'url',\n    'validSchemes' => ['http', 'https']],"},
                {'n': 'ip', 'd': 'IP-адрес или подсеть, с белыми и чёрными списками диапазонов.', 'o': 'ipv4, ipv6, subnet, normalize, ranges, negation, expandIPv6', 'c': "['ip', 'ip'],\n['ip', 'ip', 'ipv6' => false,\n    'ranges' => ['10.0.0.0/8', '!any']],"},
                {'n': 'match', 'd': 'Совпадение с регулярным выражением. Опция not переворачивает смысл.', 'o': 'pattern, not', 'c': "['login', 'match',\n    'pattern' => '/^[a-z]\\w*$/i'],\n['login', 'match', 'pattern' => '/^admin$/',\n    'not' => true, 'message' => 'Имя занято'],"},
                {'n': 'integer', 'd': 'Целое число в заданных границах.', 'o': 'min, max, tooSmall, tooBig, integerPattern', 'c': "['age', 'integer', 'min' => 18],\n['page', 'integer', 'min' => 1, 'max' => 1000],"},
                {'n': 'number', 'd': 'Любое число, целое или дробное. Синоним — double.', 'o': 'min, max, numberPattern', 'c': "['price', 'number', 'min' => 0],\n['rate', 'double'],"},
                {'n': 'boolean', 'd': 'Одно из двух значений. Обратите внимание: проверяет, но не приводит тип.', 'o': 'trueValue, falseValue, strict', 'c': "['is_active', 'boolean'],\n['flag', 'boolean', 'trueValue' => true,\n    'falseValue' => false, 'strict' => true],"},
                {'n': 'compare', 'd': 'Сравнение с другим атрибутом или с фиксированным значением.', 'o': 'compareAttribute, compareValue, operator, type (string | number)', 'c': "['password_repeat', 'compare',\n    'compareAttribute' => 'password'],\n['age', 'compare', 'compareValue' => 30,\n    'operator' => '>=', 'type' => 'number'],"},
                {'n': 'in', 'd': 'Значение из списка допустимых. Умеет проверять каждый элемент массива.', 'o': 'range, strict, not, allowArray', 'c': "['status', 'in', 'range' => [0, 1, 2]],\n['tags', 'in', 'range' => $allowed,\n    'allowArray' => true],"},
                {'n': 'date', 'd': 'Дата в заданном формате. Умеет попутно записать разобранное время в другой атрибут.', 'o': 'format, timestampAttribute, timestampAttributeFormat, min, max, timeZone, locale', 'c': "['birthday', 'date', 'format' => 'php:d.m.Y',\n    'timestampAttribute' => 'birthday_ts'],\n['start', 'date', 'min' => date('Y-m-d'),\n    'tooSmall' => 'Дата уже прошла'],"},
                {'n': 'datetime', 'd': 'То же самое, но с временем. Формат по умолчанию берётся из компонента formatter.', 'o': 'те же, что у date', 'c': "['created', 'datetime',\n    'format' => 'php:Y-m-d H:i:s'],"},
                {'n': 'time', 'd': 'Только время суток.', 'o': 'те же, что у date', 'c': "['opens_at', 'time', 'format' => 'php:H:i'],"},
                {'n': 'each', 'd': 'Применяет вложенное правило к каждому элементу массива. Один уровень вложенности.', 'o': 'rule, allowMessageFromRule, stopOnFirstError', 'c': "['ids', 'each', 'rule' => ['integer']],\n['emails', 'each', 'rule' => ['email'],\n    'allowMessageFromRule' => false,\n    'message' => 'Один из адресов неверен'],"},
                {'n': 'exist', 'd': 'Такая запись есть в базе. Клиентской проверки нет, нужна AJAX-валидация.', 'o': 'targetClass, targetAttribute, filter, allowArray, targetRelation', 'c': "['category_id', 'exist',\n    'targetClass' => Category::class,\n    'targetAttribute' => 'id'],\n['user_id', 'exist', 'targetRelation' => 'user'],"},
                {'n': 'unique', 'd': 'Такой записи ещё нет. При обновлении сама себя из проверки исключает.', 'o': 'targetClass, targetAttribute, filter, comboNotUnique', 'c': "['username', 'unique'],\n[['slug', 'lang'], 'unique',\n    'targetAttribute' => ['slug', 'lang']],"},
                {'n': 'file', 'd': 'Загруженный файл: расширение, тип, размер, количество.', 'o': 'extensions, mimeTypes, minSize, maxSize, maxFiles, checkExtensionByMimeType', 'c': "['doc', 'file', 'extensions' => ['pdf', 'docx'],\n    'maxSize' => 5 * 1024 * 1024,\n    'skipOnEmpty' => false],\n['docs', 'file', 'maxFiles' => 10],"},
                {'n': 'image', 'd': 'Всё, что умеет file, плюс размеры картинки в пикселях.', 'o': 'minWidth, maxWidth, minHeight, maxHeight, notImage', 'c': "['avatar', 'image', 'extensions' => 'png, jpg',\n    'minWidth' => 100, 'maxWidth' => 2000],"},
                {'n': 'captcha', 'd': 'Сверяет ввод с картинкой, которую отдаёт CaptchaAction. Нужен GD или ImageMagick.', 'o': 'captchaAction, caseSensitive', 'c': "['verifyCode', 'captcha'],\n// в контроллере:\n'captcha' => ['class' => CaptchaAction::class],"},
            ]),
        ]),
        ('own', 'Свой валидатор', [
            ('h', 'Способ первый: метод модели'),
            ('p', 'Быстро и локально. Клиентской части нет, пустые значения пропускаются по общим правилам.'),
            ('code', 'php', None, r'''public function rules()
{
    return [
        ['country', 'validateCountry'],
    ];
}

public function validateCountry($attribute, $params, $validator)
{
    if (!in_array($this->$attribute, ['USA', 'Indonesia'], true)) {
        $this->addError($attribute, 'Страна должна быть USA или Indonesia.');
    }
}'''),
            ('h', 'Способ второй: отдельный класс'),
            ('p', 'Переиспользуется между моделями, умеет работать без модели и может отдать код для браузера.'),
            ('code', 'php', 'components/CountryValidator.php', r'''use yii\validators\Validator;

class CountryValidator extends Validator
{
    public $countries = ['USA', 'Indonesia'];

    public function init()
    {
        parent::init();
        $this->message = $this->message ?: 'Недопустимая страна.';
    }

    // вызывается для атрибута модели
    public function validateAttribute($model, $attribute)
    {
        if (!in_array($model->$attribute, $this->countries, true)) {
            $this->addError($model, $attribute, $this->message);
        }
    }

    // позволяет проверять голое значение: $v->validate($value, $error)
    protected function validateValue($value)
    {
        return in_array($value, $this->countries, true)
            ? null
            : [$this->message, []];
    }

    // проверка прямо в браузере
    public function clientValidateAttribute($model, $attribute, $view)
    {
        $list = json_encode($this->countries);
        $message = json_encode($this->message);
        return "if (!$list.includes(value)) { messages.push($message); }";
    }
}'''),
            ('h', 'Подключение'),
            ('code', 'php', None, r'''['country', CountryValidator::class],
['country', CountryValidator::class, 'countries' => ['RU', 'KZ']],

// и то же самое вне модели
$validator = new CountryValidator();
if (!$validator->validate($value, $error)) {
    echo $error;
}'''),
            ('note', 'tip', 'Правило зависит от другого поля',
             'Не пишите свой валидатор ради условия. Опция `when` решает это в одну строку, '
             'а `whenClient` повторяет то же условие в браузере, чтобы проверки не спорили.'),
            ('code', 'php', None, r'''['state', 'required',
    'when' => function ($model) {
        return $model->country === 'USA';
    },
    'whenClient' => "function (attribute, value) {
        return $('#country').val() === 'USA';
    }",
],'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'compare сравнивает строки',
             'По умолчанию `compare` работает побайтово, поэтому `\'10\' < \'9\'`. '
             'Для чисел и дат обязательно указывайте `\'type\' => \'number\'`.'),
            ('note', 'trap', 'unique и exist не работают в браузере',
             'У них нет клиентской реализации, и это нельзя починить опциями. '
             'Включайте AJAX-валидацию: `enableAjaxValidation` у формы и `ActiveForm::validate($model)` в действии.'),
            ('note', 'trap', 'filter меняет данные',
             '`filter`, `trim` и `default` записывают результат обратно в атрибут. '
             'Если поставить их после проверяющих правил, проверка увидит старое значение.'),
            ('note', 'warn', 'each не дружит с unique',
             'Валидатор `each` прогоняет вложенное правило по элементам, но `unique` и `exist` '
             'внутри него ведут себя непредсказуемо: им нужен контекст модели. Проверяйте список отдельным запросом.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Сценарии

topic(
    id='scenarios', group='data',
    title='Сценарии',
    cls='scenarios()',
    lead='Один класс модели, разные наборы проверяемых и разрешённых полей.',
    badge='2 способа',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Сценарий отвечает на два вопроса: **какие правила применять** и **какие атрибуты пустить внутрь** `load()`. '
                  'По умолчанию сценарий один и называется `default`.'),
            ('demo', 'scenario-lab'),
            ('h', 'Способ первый: on и except прямо в правилах'),
            ('code', 'php', None, r'''public function rules()
{
    return [
        [['username', 'email'], 'required'],
        ['password', 'required', 'on' => 'register'],
        ['captcha', 'captcha', 'on' => 'register'],
        ['email', 'unique', 'except' => 'update'],
    ];
}

// применение
$model = new User(['scenario' => 'register']);
// или
$model->scenario = 'register';'''),
            ('h', 'Способ второй: явный список в scenarios()'),
            ('code', 'php', None, r'''public function scenarios()
{
    return [
        'register' => ['username', 'email', 'password'],
        'profile'  => ['username', 'about'],
        'admin'    => ['username', 'email', 'status', '!role'],
    ];
}'''),
            ('p', 'Восклицательный знак перед именем означает: атрибут **проверяется, но не присваивается** через `load()`. '
                  'Так поле роли нельзя подделать из формы, но его можно выставить в коде.'),
            ('note', 'tip', 'Не потеряйте базовые сценарии',
             'Если нужно добавить сценарий, а не заменить все, начинайте с `parent::scenarios()` и дополняйте массив.'),
            ('code', 'php', None, r'''public function scenarios()
{
    $scenarios = parent::scenarios();
    $scenarios['register'] = ['username', 'email', 'password'];
    return $scenarios;
}'''),
        ]),
        ('all', 'Где сценарий срабатывает', [
            ('ref', [
                {'n': 'load()', 'd': 'Присваивает только безопасные атрибуты сценария. Остальные молча игнорируются.', 'o': 'safeAttributes()', 'c': "$model->scenario = 'profile';\n$model->load($post);   // status и role не пройдут"},
                {'n': 'validate()', 'd': 'Применяет только активные правила сценария.', 'o': 'activeAttributes(), getActiveValidators()', 'c': "$model->getActiveValidators('email');"},
                {'n': 'ActiveForm', 'd': 'Поля формы рисуются по активным атрибутам, клиентские правила берутся оттуда же.', 'o': '', 'c': "echo $form->field($model, 'password');\n// в сценарии profile правил не будет"},
                {'n': 'ActiveRecord::save()', 'd': 'Валидация внутри save() тоже смотрит на сценарий.', 'o': 'createScenario, updateScenario у rest-контроллеров', 'c': "public $createScenario = 'create';\npublic $updateScenario = 'update';"},
                {'n': 'transactions()', 'd': 'Active Record умеет оборачивать операции в транзакцию для конкретного сценария.', 'o': 'OP_INSERT, OP_UPDATE, OP_DELETE, OP_ALL', 'c': "public function transactions()\n{\n    return ['api' => self::OP_ALL];\n}"},
                {'n': 'Поведения', 'd': 'Внутри поведения доступен `$this->owner->scenario`, так что поведение может вести себя по-разному.', 'o': '', 'c': "if ($this->owner->scenario === 'import') {\n    return;   // не трогаем метки времени\n}"},
            ]),
        ]),
        ('own', 'Практика', [
            ('h', 'Регистрация, редактирование и импорт в одной модели'),
            ('code', 'php', 'models/User.php', r'''class User extends ActiveRecord
{
    const SCENARIO_REGISTER = 'register';
    const SCENARIO_PROFILE  = 'profile';
    const SCENARIO_IMPORT   = 'import';

    public $password;
    public $passwordRepeat;

    public function rules()
    {
        return [
            [['username', 'email'], 'required'],
            ['email', 'email'],
            ['email', 'unique', 'except' => self::SCENARIO_IMPORT],

            [['password', 'passwordRepeat'], 'required',
                'on' => self::SCENARIO_REGISTER],
            ['passwordRepeat', 'compare',
                'compareAttribute' => 'password',
                'on' => self::SCENARIO_REGISTER],

            ['about', 'string', 'max' => 500,
                'on' => self::SCENARIO_PROFILE],
        ];
    }

    public function scenarios()
    {
        $scenarios = parent::scenarios();
        $scenarios[self::SCENARIO_IMPORT] = ['username', 'email', '!status'];
        return $scenarios;
    }
}'''),
            ('h', 'Использование в контроллере'),
            ('code', 'php', None, r'''public function actionSignup()
{
    $model = new User(['scenario' => User::SCENARIO_REGISTER]);

    if ($model->load(Yii::$app->request->post()) && $model->validate()) {
        $model->setPassword($model->password);
        $model->status = User::STATUS_ACTIVE;   // руками, не из формы
        $model->save(false);
        return $this->goHome();
    }

    return $this->render('signup', ['model' => $model]);
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Задали scenarios() и всё сломалось',
             'Возврат своего массива **заменяет** список целиком, включая `default`. '
             'Атрибуты, которых нет в новом списке, перестают присваиваться через `load()` во всех сценариях.'),
            ('note', 'trap', 'Сценарий выставили после load()',
             'Порядок важен: сначала `$model->scenario = ...`, потом `load()`. Иначе присвоение пойдёт по старому набору безопасных атрибутов.'),
            ('note', 'warn', 'Восклицательный знак работает только в scenarios()',
             'Синтаксис `\'!role\'` понимает именно метод `scenarios()`. В `rules()` его писать бесполезно.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Компоненты и свойства

topic(
    id='components', group='object',
    title='Компоненты и свойства',
    cls='yii\\base\\Component',
    lead='Кирпич, из которого собран весь фреймворк: настройка массивом, свойства через методы, события и поведения.',
    badge='18 компонентов приложения',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'В основании два класса. `BaseObject` даёт настройку массивом и свойства через геттеры и сеттеры. '
                  '`Component` добавляет к этому события и поведения. Почти всё в Yii наследует второй.'),
            ('svg', '''<svg viewBox="0 0 700 270" role="img" aria-label="Иерархия: BaseObject даёт свойства и конфигурацию, Component добавляет события и поведения" class="dg">
<defs><marker id="m-arr3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr3)" opacity=".55">
<path d="M350 74v34"/><path d="M350 160v34"/>
</g>
<g class="dg-box"><rect x="230" y="24" width="240" height="50" rx="8"/><text x="350" y="45">BaseObject</text><text x="350" y="62" class="dg-sub">конструктор с $config, init(), свойства</text></g>
<g class="dg-box dg-live"><rect x="230" y="108" width="240" height="52" rx="8"/><text x="350" y="130">Component</text><text x="350" y="147" class="dg-sub">+ события, + поведения</text></g>
<g class="dg-box dg-muted"><rect x="34" y="194" width="140" height="44" rx="8"/><text x="104" y="213">Model</text><text x="104" y="229" class="dg-sub">формы, AR</text></g>
<g class="dg-box dg-muted"><rect x="190" y="194" width="140" height="44" rx="8"/><text x="260" y="213">Widget</text><text x="260" y="229" class="dg-sub">GridView…</text></g>
<g class="dg-box dg-muted"><rect x="346" y="194" width="150" height="44" rx="8"/><text x="421" y="213">Connection</text><text x="421" y="229" class="dg-sub">db, cache, mailer</text></g>
<g class="dg-box dg-muted"><rect x="512" y="194" width="150" height="44" rx="8"/><text x="587" y="213">Controller</text><text x="587" y="229" class="dg-sub">Module, Application</text></g>
<g stroke="currentColor" stroke-width="1.2" fill="none" opacity=".35"><path d="M104 194v-20h483v20"/><path d="M260 194v-20"/><path d="M421 194v-20"/></g>
</svg>''', 'Почему настройка массивом работает одинаково для модели, виджета и соединения с базой: у них общий предок.'),
            ('h', 'Свойство через геттер и сеттер'),
            ('code', 'php', None, r'''class Post extends Component
{
    private $_slug;

    public function getSlug()
    {
        return $this->_slug;
    }

    public function setSlug($value)
    {
        $this->_slug = Inflector::slug($value);
    }
}

$post = new Post();
$post->slug = 'Привет мир';   // вызовет setSlug()
echo $post->slug;             // вызовет getSlug() → privet-mir

// только геттер — свойство доступно на чтение, запись бросит исключение
isset($post->slug);           // проверит через геттер
unset($post->slug);           // вызовет setSlug(null)'''),
            ('note', 'trap', 'Свойства через методы чувствительны к регистру наполовину',
             'Имя свойства регистронезависимо (`$post->Slug` тоже сработает), а вот имя метода должно быть ровно `getSlug`. '
             'И такие свойства не видны в `get_object_vars()` и в `json_encode()`.'),
            ('h', 'Настройка массивом'),
            ('code', 'php', None, r'''$engine = Yii::createObject([
    'class' => SearchEngine::class,
    'apiKey' => 'xxxx',                  // публичное поле или сеттер
    'on search' => function ($event) {   // подписка на событие
        Yii::info($event->keyword);
    },
    'as logger' => [                      // поведение
        'class' => LogBehavior::class,
    ],
]);

Yii::configure($engine, ['apiKey' => 'yyyy']);   // настроить готовый объект'''),
        ]),
        ('all', 'Компоненты приложения', [
            ('p', 'Компонент приложения — это объект в `Yii::$app`, созданный **лениво**, при первом обращении. '
                  'Задаются в ключе `components` конфигурации.'),
            ('ref', [
                {'n': 'db', 'd': 'Соединение с базой данных. Через него работают DAO, Query Builder и Active Record.', 'o': 'yii\\db\\Connection', 'c': "'db' => [\n    'class' => yii\\db\\Connection::class,\n    'dsn' => 'mysql:host=localhost;dbname=app',\n    'username' => 'root',\n    'charset' => 'utf8mb4',\n    'enableSchemaCache' => !YII_DEBUG,\n],"},
                {'n': 'request', 'd': 'Входящий запрос: параметры, заголовки, тело, куки, проверка CSRF.', 'o': 'yii\\web\\Request', 'c': "'request' => [\n    'cookieValidationKey' => '…',\n    'parsers' => [\n        'application/json' => yii\\web\\JsonParser::class,\n    ],\n],"},
                {'n': 'response', 'd': 'Ответ: код, заголовки, формат, отправка файла.', 'o': 'yii\\web\\Response', 'c': "'response' => [\n    'formatters' => [\n        'json' => ['class' => yii\\web\\JsonResponseFormatter::class,\n                   'prettyPrint' => YII_DEBUG],\n    ],\n],"},
                {'n': 'user', 'd': 'Текущий пользователь: вход, выход, проверка прав.', 'o': 'yii\\web\\User', 'c': "'user' => [\n    'identityClass' => app\\models\\User::class,\n    'enableAutoLogin' => true,\n    'authTimeout' => 3600,\n],"},
                {'n': 'session', 'd': 'Сессия и флеш-сообщения.', 'o': 'yii\\web\\Session, DbSession, CacheSession', 'c': "'session' => [\n    'class' => yii\\web\\DbSession::class,\n    'sessionTable' => 'session',\n],"},
                {'n': 'cache', 'd': 'Кэш данных. Его же используют схема базы, RBAC и правила маршрутов.', 'o': 'yii\\caching\\FileCache и другие', 'c': "'cache' => [\n    'class' => yii\\caching\\FileCache::class,\n    'keyPrefix' => 'myapp',\n],"},
                {'n': 'urlManager', 'd': 'Разбор и построение адресов.', 'o': 'yii\\web\\UrlManager', 'c': "'urlManager' => [\n    'enablePrettyUrl' => true,\n    'showScriptName' => false,\n    'rules' => ['post/<id:\\d+>' => 'post/view'],\n],"},
                {'n': 'errorHandler', 'd': 'Перехват исключений и ошибок PHP, страница ошибки.', 'o': 'yii\\web\\ErrorHandler', 'c': "'errorHandler' => [\n    'errorAction' => 'site/error',\n],"},
                {'n': 'log', 'd': 'Маршрутизация сообщений журнала по целям: файл, база, почта.', 'o': 'yii\\log\\Dispatcher', 'c': "'log' => [\n    'traceLevel' => YII_DEBUG ? 3 : 0,\n    'targets' => [[\n        'class' => yii\\log\\FileTarget::class,\n        'levels' => ['error', 'warning'],\n    ]],\n],"},
                {'n': 'mailer', 'd': 'Отправка писем, в разработке — запись в файлы.', 'o': 'yii\\symfonymailer\\Mailer', 'c': "'mailer' => [\n    'class' => yii\\symfonymailer\\Mailer::class,\n    'useFileTransport' => YII_ENV_DEV,\n],"},
                {'n': 'formatter', 'd': 'Вывод дат, чисел, денег, размеров по локали.', 'o': 'yii\\i18n\\Formatter', 'c': "'formatter' => [\n    'locale' => 'ru-RU',\n    'timeZone' => 'Europe/Moscow',\n    'nullDisplay' => '—',\n],"},
                {'n': 'i18n', 'd': 'Источники переводов для Yii::t().', 'o': 'yii\\i18n\\I18N', 'c': "'i18n' => [\n    'translations' => [\n        'app*' => ['class' => yii\\i18n\\PhpMessageSource::class],\n    ],\n],"},
                {'n': 'assetManager', 'd': 'Публикация и склейка ресурсов, подмена пакетов.', 'o': 'yii\\web\\AssetManager', 'c': "'assetManager' => [\n    'appendTimestamp' => true,\n    'linkAssets' => true,\n],"},
                {'n': 'view', 'd': 'Рендеринг представлений, регистрация скриптов и стилей, темы.', 'o': 'yii\\web\\View', 'c': "'view' => [\n    'theme' => [\n        'pathMap' => ['@app/views' => '@app/themes/dark'],\n    ],\n],"},
                {'n': 'authManager', 'd': 'RBAC: роли, разрешения, правила.', 'o': 'yii\\rbac\\DbManager или PhpManager', 'c': "'authManager' => [\n    'class' => yii\\rbac\\DbManager::class,\n    'cache' => 'cache',\n],"},
                {'n': 'security', 'd': 'Хэши паролей, случайные строки, шифрование и подпись.', 'o': 'yii\\base\\Security', 'c': "'security' => [\n    'passwordHashCost' => 13,\n],"},
                {'n': 'assetConverter', 'd': 'Компиляция LESS, SCSS, TypeScript при публикации ресурсов.', 'o': 'yii\\web\\AssetConverter', 'c': "'assetConverter' => [\n    'commands' => [\n        'scss' => ['css', 'sass {from} {to}'],\n    ],\n],"},
                {'n': 'Свой компонент', 'd': 'Любой класс можно положить в components и обращаться к нему как к части фреймворка.', 'o': 'доступ через Yii::$app->id', 'c': "'components' => [\n    'sms' => [\n        'class' => app\\components\\SmsSender::class,\n        'token' => getenv('SMS_TOKEN'),\n    ],\n],\n\n// Yii::$app->sms->send($phone, $text);"},
            ]),
        ]),
        ('own', 'Свой компонент', [
            ('code', 'php', 'components/SmsSender.php', r'''namespace app\components;

use yii\base\Component;
use yii\base\InvalidConfigException;

class SmsSender extends Component
{
    public $token;
    public $from = 'MyShop';

    const EVENT_SENT = 'sent';

    public function init()
    {
        parent::init();
        if ($this->token === null) {
            throw new InvalidConfigException('SmsSender: нужен token.');
        }
    }

    public function send($phone, $text)
    {
        // ...обращение к шлюзу...
        $this->trigger(self::EVENT_SENT);
        return true;
    }
}'''),
            ('h', 'Подключение и использование'),
            ('code', 'php', 'config/web.php', r''''components' => [
    'sms' => [
        'class' => app\components\SmsSender::class,
        'token' => getenv('SMS_TOKEN'),
        'from' => 'Shop',
    ],
],'''),
            ('code', 'php', None, r'''Yii::$app->sms->send('+79990000000', 'Заказ собран');'''),
            ('note', 'tip', 'Подсказка для IDE',
             'Чтобы редактор знал про `Yii::$app->sms`, заведите файл со сводным описанием приложения.'),
            ('code', 'php', 'components/Application.php (только для IDE)', r'''/**
 * @property \app\components\SmsSender $sms
 */
class Application extends \yii\web\Application
{
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Тяжёлая работа в init()',
             'Компонент создаётся при первом обращении, но если он попал в `bootstrap`, то создаётся на каждом запросе. '
             'Соединения и чтение файлов в `init()` бьют по каждому запросу, даже когда компонент не нужен.'),
            ('note', 'trap', 'new вместо Yii::createObject()',
             'Прямой `new` обходит DI-контейнер: не применятся умолчания из `container.definitions` и не разрешатся зависимости конструктора.'),
            ('note', 'warn', 'Свойство есть, а в json_encode() его нет',
             'Свойства через геттеры не видны стандартной сериализации. Для API перечислите их в `fields()`.'),
        ]),
    ],
)



# --------------------------------------------------------------------------- DI-контейнер

topic(
    id='di', group='object',
    title='DI-контейнер',
    cls='yii\\di\\Container',
    lead='Кто на самом деле собирает объекты фреймворка: читает типы конструктора, подставляет зависимости и применяет ваши умолчания.',
    badge='16 приёмов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'В Yii два разных механизма, и их легко перепутать. **Service Locator** (`Yii::$app`, любой модуль) '
                  'хранит именованные компоненты и отдаёт их по ID. **DI-контейнер** (`Yii::$container`) умеет создавать '
                  'объекты, сам подставляя зависимости по типам параметров конструктора. Локатор построен поверх '
                  'контейнера: когда `Yii::$app->db` создаётся впервые, объект собирает именно контейнер.'),
            ('svg', '''<svg viewBox="0 0 700 334" role="img" aria-label="К контейнеру ведут два пути: обращение к компоненту по имени через Service Locator и вызов Yii::createObject из ядра; контейнер читает типы конструктора и создаёт объект со всеми зависимостями" class="dg">
<defs><marker id="m-di" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-di)" opacity=".55">
<path d="M175 66v20"/><path d="M175 154v28"/><path d="M525 66v114"/><path d="M350 260v20"/>
</g>
<g class="dg-box"><rect x="14" y="14" width="322" height="52" rx="8"/><text x="175" y="36">Yii::$app-&gt;db</text><text x="175" y="53" class="dg-sub">обращение к компоненту по имени</text></g>
<g class="dg-box"><rect x="364" y="14" width="322" height="52" rx="8"/><text x="525" y="36">Yii::createObject()</text><text x="525" y="53" class="dg-sub">ядро: виджеты, правила, поведения</text></g>
<g class="dg-box"><rect x="14" y="90" width="322" height="64" rx="8"/><text x="175" y="112">Service Locator</text><text x="175" y="129" class="dg-sub">ключ components в конфигурации</text><text x="175" y="145" class="dg-sub">создан — отдаёт тот же экземпляр</text></g>
<g class="dg-box dg-live"><rect x="140" y="186" width="420" height="74" rx="8"/><text x="350" y="208">Yii::$container</text><text x="350" y="226" class="dg-sub">читает типы параметров конструктора</text><text x="350" y="243" class="dg-sub">и применяет умолчания из container.definitions</text></g>
<g class="dg-box dg-muted"><rect x="250" y="284" width="200" height="34" rx="8"/><text x="350" y="306">new Connection(…)</text></g>
</svg>''', 'Почти всё ядро создаётся через Yii::createObject(), а он идёт в контейнер. Поэтому умолчание, заданное там один раз, действует на весь проект.'),
            ('h', 'Зависимость по типу конструктора'),
            ('code', 'php', None, r'''class UserFinder extends BaseObject
{
    public $db;

    public function __construct(Connection $db, $config = [])
    {
        $this->db = $db;
        parent::__construct($config);
    }
}

$finder = Yii::$container->get(UserFinder::class);
// контейнер увидел тип Connection и подставил его сам:
// == new UserFinder(Yii::$container->get(Connection::class))'''),
            ('p', 'Разрешение рекурсивное: если `Connection` тоже требует что-то в конструкторе, контейнер соберёт и это. '
                  'Цепочка любой длины строится без единого `new`.'),
            ('h', 'Интерфейс вместо класса'),
            ('code', 'php', 'config/web.php', r''''container' => [
    'definitions' => [
        app\components\BookingInterface::class => app\components\BookingService::class,
    ],
],'''),
            ('code', 'php', 'controllers/HotelController.php', r'''class HotelController extends Controller
{
    protected $booking;

    public function __construct($id, $module, BookingInterface $booking, $config = [])
    {
        $this->booking = $booking;
        parent::__construct($id, $module, $config);
    }
}'''),
            ('p', 'Класс просит интерфейс и ничего не знает о реализации. В тестах на то же место подставляется заглушка — '
                  'ради этого всё и затевалось.'),
            ('note', 'tip', 'Регистрируйте как можно раньше',
             'Приложение — в конфигурации, ключ `container`. Расширение — в своём bootstrap-классе. '
             'Регистрация после того, как объект уже создан, ни на что не повлияет.'),
        ]),
        ('all', 'Регистрация и разрешение', [
            ('h', 'Регистрация'),
            ('ref', [
                {'n': 'set($class)', 'd': 'Класс как есть. Регистрировать не обязательно: контейнер создаст любой класс и без этого.', 'o': 'нужно, только если хочется явности', 'c': "Yii::$container->set(yii\\db\\Connection::class);"},
                {'n': 'set($interface, $class)', 'd': 'Интерфейс → реализация. Главный приём: классы просят интерфейс, подстановкой занимается контейнер.', 'o': 'вместо класса можно указать псевдоним', 'c': "Yii::$container->set(\n    yii\\mail\\MailerInterface::class,\n    yii\\symfonymailer\\Mailer::class\n);"},
                {'n': 'set($alias, $class)', 'd': 'Псевдоним: короткое имя для класса.', 'o': 'get() принимает и то и другое', 'c': "Yii::$container->set('foo', yii\\db\\Connection::class);\n\n$db = Yii::$container->get('foo');"},
                {'n': 'set($class, $config)', 'd': 'Умолчания для класса: значения свойств, которые применятся при каждом создании.', 'o': 'явный аргумент при вызове сильнее умолчания', 'c': "Yii::$container->set(yii\\widgets\\LinkPager::class, [\n    'maxButtonCount' => 5,\n]);\n\necho LinkPager::widget();                         // 5 кнопок\necho LinkPager::widget(['maxButtonCount' => 20]);  // 20"},
                {'n': "set($name, ['class' => ...])", 'd': 'Псевдоним вместе с конфигурацией: имя, класс и свойства одной записью.', 'o': 'ключ class обязателен', 'c': "Yii::$container->set('db', [\n    'class' => yii\\db\\Connection::class,\n    'dsn' => 'mysql:host=localhost;dbname=app',\n]);"},
                {'n': 'set($name, $object)', 'd': 'Готовый экземпляр. Контейнер будет отдавать именно его, ничего не создавая.', 'o': 'по сути ручной синглтон', 'c': "Yii::$container->set('pageCache', new FileCache());"},
                {'n': 'set($name, $closure)', 'd': 'Фабрика: полный контроль над созданием. Замыкание получает контейнер, параметры и конфигурацию.', 'o': 'function ($container, $params, $config)', 'c': "Yii::$container->set('search', function ($container, $params, $config) {\n    $solr = new SolrService('127.0.0.1');\n    // ...сложная инициализация...\n    return $solr;\n});"},
                {'n': 'setSingleton()', 'd': 'То же, что set(), но объект создаётся один раз на всё приложение. У set() каждый get() даёт новый объект.', 'o': 'принимает те же формы определения', 'c': "Yii::$container->setSingleton(yii\\db\\Connection::class, [\n    'dsn' => 'mysql:host=localhost;dbname=app',\n]);"},
                {'n': 'setDefinitions() и setSingletons()', 'd': 'Массовая регистрация. Значение — определение либо пара «определение, параметры конструктора».', 'o': 'то же доступно в конфигурации: container.definitions и container.singletons', 'c': "Yii::$container->setDefinitions([\n    yii\\web\\Response::class => [\n        'class' => app\\components\\Response::class,\n        'format' => 'json',\n    ],\n    app\\storage\\DocumentsReader::class => [\n        ['class' => app\\storage\\DocumentsReader::class],\n        [Instance::of('tempFileStorage')],   // параметры конструктора\n    ],\n]);"},
            ]),
            ('h', 'Разрешение'),
            ('ref', [
                {'n': 'get($name, $params, $config)', 'd': 'Создать объект: $params — позиционные аргументы конструктора, $config — значения свойств.', 'o': 'вернёт тот же экземпляр, если имя зарегистрировано через setSingleton()', 'c': "$engine = Yii::$container->get(SearchEngine::class,\n    [$apiKey, $apiSecret],   // аргументы конструктора\n    ['type' => 1]            // свойства\n);\n// == new SearchEngine($apiKey, $apiSecret, ['type' => 1])"},
                {'n': 'Внедрение через конструктор', 'd': 'Основной способ: контейнер смотрит типы параметров и создаёт их сам. Регистрировать ничего не нужно, пока это конкретные классы.', 'o': 'интерфейс без регистрации создать нельзя', 'c': "public function __construct(Connection $db, CacheInterface $cache)\n{\n    // оба аргумента придут из контейнера\n}"},
                {'n': 'Внедрение через свойства', 'd': 'Когда трогать конструктор нельзя: зависимости передаются третьим аргументом get() как обычная конфигурация.', 'o': 'работает через сеттеры и публичные поля', 'c': "Yii::$container->get(Foo::class, [], [\n    'bar' => Yii::$container->get(Bar::class),\n]);"},
                {'n': 'invoke($callable, $params)', 'd': 'Внедрение в отдельный метод: то, что не нашлось в $params, контейнер добирает по типам параметров.', 'o': 'так же вызываются действия контроллеров', 'c': "Yii::$container->invoke([$report, 'build'], ['period' => 'month']);\n// параметр Connection $db придёт из контейнера"},
                {'n': 'Instance::of($id)', 'd': 'Ленивая ссылка на другую зависимость по имени. Нужна там, где объект передать нельзя — в описании параметров конструктора.', 'o': 'yii\\di\\Instance', 'c': "use yii\\di\\Instance;\n\nYii::$container->setSingletons([\n    'tempFileStorage' => [\n        ['class' => app\\storage\\FileStorage::class],\n        ['/var/tempfiles'],\n    ],\n    'reader' => [\n        ['class' => app\\storage\\DocumentsReader::class],\n        [Instance::of('tempFileStorage')],\n    ],\n]);"},
                {'n': 'Instance::ensure($ref, $type)', 'd': 'Принять и ID компонента, и конфигурацию, и готовый объект — вернуть объект нужного класса. Так написаны почти все свойства-зависимости в ядре.', 'o': 'бросает исключение, если тип не совпал', 'c': "public $db = 'db';\n\npublic function init()\n{\n    parent::init();\n    // 'db' | ['class' => ...] | объект — на выходе Connection\n    $this->db = Instance::ensure($this->db, Connection::class);\n}"},
                {'n': 'Yii::createObject()', 'd': 'Вход в контейнер из ядра. Через него создаются виджеты, валидаторы, поведения, компоненты — поэтому умолчания контейнера действуют на них всех.', 'o': 'принимает строку, массив с ключом class или замыкание', 'c': "$engine = Yii::createObject([\n    'class' => SearchEngine::class,\n    'apiKey' => 'xxxx',\n]);\n\n$db = Yii::createObject(Connection::class, [$dsn]);"},
            ]),
        ]),
        ('own', 'Приёмы', [
            ('h', 'Подменить класс ядра на свой'),
            ('code', 'php', 'config/web.php', r''''container' => [
    'definitions' => [
        yii\web\Request::class => app\components\Request::class,
        yii\web\Response::class => [
            'class' => app\components\Response::class,
            'format' => yii\web\Response::FORMAT_JSON,
        ],
    ],
],'''),
            ('h', 'Одно умолчание на весь проект'),
            ('p', 'Полезно, когда одна и та же настройка повторяется в десятках представлений.'),
            ('code', 'php', 'config/web.php', r''''container' => [
    'definitions' => [
        yii\widgets\LinkPager::class => ['maxButtonCount' => 5],
        yii\grid\GridView::class => [
            'tableOptions' => ['class' => 'table table-sm'],
        ],
    ],
],'''),
            ('h', 'Свой сервис за интерфейсом'),
            ('code', 'php', 'components/BookingInterface.php', r'''namespace app\components;

interface BookingInterface
{
    public function book($hotelId, $from, $to);
}'''),
            ('code', 'php', 'config/web.php', r''''container' => [
    'singletons' => [
        app\components\BookingInterface::class => app\components\BookingService::class,
    ],
],'''),
            ('code', 'php', 'controllers/HotelController.php', r'''class HotelController extends Controller
{
    protected $booking;

    public function __construct($id, $module, BookingInterface $booking, $config = [])
    {
        $this->booking = $booking;
        parent::__construct($id, $module, $config);
    }

    public function actionBook($hotelId)
    {
        $this->booking->book($hotelId, '2025-06-01', '2025-06-07');
    }
}'''),
            ('note', 'tip', 'Ради чего это всё',
             'В тесте достаточно одной строки — и контроллер работает с заглушкой, не трогая внешний сервис: '
             '`Yii::$container->set(BookingInterface::class, BookingStub::class)`.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'new в обход контейнера',
             'Прямой `new SomeWidget()` не применит ни умолчания из `container.definitions`, ни разрешение зависимостей. '
             'Если класс должен подчиняться настройкам проекта — создавайте его через `Yii::createObject()`.'),
            ('note', 'trap', 'Интерфейс в конструкторе без регистрации',
             'Контейнер не может угадать реализацию — будет ошибка создания объекта. '
             'Нужен `set(Interface::class, Impl::class)`, и обязательно до первого обращения.'),
            ('note', 'trap', 'setSingleton() для объекта с состоянием',
             'Синглтон живёт весь запрос и достаётся всем. Если объект накапливает состояние, оно протечёт между не связанными местами кода. '
             'Синглтон уместен для дорогих и неизменяемых вещей — соединений, обёрток над хранилищем.'),
            ('note', 'warn', 'Зависимость от контейнера вместо зависимости от типа',
             'Вызов `Yii::$container->get(...)` внутри класса возвращает нас к тому, от чего уходили: '
             'класс снова сам знает, где брать зависимость, и его снова нельзя подменить в тесте. Просите тип в конструкторе.'),
            ('note', 'warn', 'Yii::$app и Yii::$container — разные вещи',
             '`Yii::$app->db` — компонент по имени из локатора. `Yii::$container->get(Connection::class)` — объект из контейнера, '
             'и это не тот же самый экземпляр. Настройки в `components` не влияют на `container`, и наоборот.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Поведения

topic(
    id='behaviors', group='object',
    title='Поведения',
    cls='yii\\base\\Behavior',
    lead='Подмешивают компоненту методы, свойства и реакции на его события — без наследования.',
    badge='7 встроенных',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Поведение — отдельный объект, прикреплённый к компоненту. Его публичные методы и свойства '
                  'становятся доступны у владельца, а метод `events()` подписывает его на события владельца. '
                  'Внутри поведения владелец доступен как `$this->owner`.'),
            ('svg', '''<svg viewBox="0 0 720 250" role="img" aria-label="Поведение прикрепляется к компоненту: его методы видны у владельца, а events подписывает его на события" class="dg">
<defs><marker id="m-arr4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g class="dg-box"><rect x="24" y="30" width="240" height="180" rx="10"/><text x="144" y="56">Post (владелец)</text></g>
<g class="dg-chip"><rect x="48" y="74" width="192" height="30" rx="6"/><text x="144" y="94">$title, $body</text></g>
<g class="dg-chip"><rect x="48" y="112" width="192" height="30" rx="6"/><text x="144" y="132">save()</text></g>
<g class="dg-chip dg-live"><rect x="48" y="150" width="192" height="30" rx="6"/><text x="144" y="170">touch() ← от поведения</text></g>
<g class="dg-box dg-live"><rect x="456" y="30" width="240" height="180" rx="10"/><text x="576" y="56">TimestampBehavior</text></g>
<g class="dg-chip"><rect x="480" y="74" width="192" height="30" rx="6"/><text x="576" y="94">events()</text></g>
<g class="dg-chip"><rect x="480" y="112" width="192" height="30" rx="6"/><text x="576" y="132">evaluateAttributes()</text></g>
<g class="dg-chip"><rect x="480" y="150" width="192" height="30" rx="6"/><text x="576" y="170">touch()</text></g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr4)" opacity=".6">
<path d="M264 100h184"/><path d="M448 165H272"/>
</g>
<text x="356" y="92" class="dg-note" text-anchor="middle">EVENT_BEFORE_INSERT</text>
<text x="356" y="186" class="dg-note" text-anchor="middle">заполняет created_at</text>
</svg>''', 'Поведение слушает события владельца и одновременно отдаёт ему свои методы. Связь двусторонняя.'),
            ('h', 'Прикрепление'),
            ('code', 'php', None, r'''public function behaviors()
{
    return [
        TimestampBehavior::class,                    // без имени
        'slug' => SluggableBehavior::class,          // с именем
        [                                            // с настройкой
            'class' => BlameableBehavior::class,
            'createdByAttribute' => 'author_id',
        ],
    ];
}

// на лету
$model->attachBehavior('slug', new SluggableBehavior(['attribute' => 'title']));
$model->detachBehavior('slug');
$model->getBehavior('slug');

// в конфигурации компонента — ключ «as имя»
'db' => [
    'class' => yii\db\Connection::class,
    'as profiling' => ['class' => app\components\SlowQueryBehavior::class],
],'''),
            ('note', 'tip', 'Поведение против трейта',
             'Трейт — чистое переиспользование кода, быстрее и понятнее IDE. '
             'Поведение — когда нужны настройка из конфигурации, подключение во время выполнения и реакция на события.'),
        ]),
        ('all', 'Все 7 встроенных', [
            ('ref', [
                {'n': 'TimestampBehavior', 'd': 'Проставляет время создания и изменения. Самое частое поведение в проектах.', 'o': 'createdAtAttribute, updatedAtAttribute, value, attributes', 'c': "[\n    'class' => TimestampBehavior::class,\n    // по умолчанию created_at и updated_at, int-время\n    // для колонок DATETIME:\n    'value' => new Expression('NOW()'),\n],\n\n$post->touch('published_at');   // проставить и сохранить"},
                {'n': 'BlameableBehavior', 'd': 'Записывает идентификатор текущего пользователя в поля автора и редактора.', 'o': 'createdByAttribute, updatedByAttribute, defaultValue', 'c': "[\n    'class' => BlameableBehavior::class,\n    'createdByAttribute' => 'author_id',\n    'updatedByAttribute' => 'editor_id',\n    'defaultValue' => 0,   // для консоли, где пользователя нет\n],"},
                {'n': 'SluggableBehavior', 'd': 'Делает адресную часть из заголовка: «Привет мир» превращается в privet-mir.', 'o': 'attribute, slugAttribute, ensureUnique, immutable, uniqueValidator, value', 'c': "[\n    'class' => SluggableBehavior::class,\n    'attribute' => 'title',\n    'slugAttribute' => 'slug',\n    'ensureUnique' => true,   // допишет -2, -3 при совпадении\n    'immutable' => true,      // не менять после первого раза\n],"},
                {'n': 'AttributeBehavior', 'd': 'Общий предок предыдущих трёх: записывает значение в атрибуты по выбранным событиям. Берите, когда нужна своя логика заполнения.', 'o': 'attributes, value, preserveNonEmptyValues', 'c': "[\n    'class' => AttributeBehavior::class,\n    'attributes' => [\n        ActiveRecord::EVENT_BEFORE_INSERT => 'uuid',\n    ],\n    'value' => function ($event) {\n        return Yii::$app->security->generateRandomString(32);\n    },\n],"},
                {'n': 'AttributeTypecastBehavior', 'd': 'Приводит типы атрибутов: база отдаёт строки, а в модели нужны int и bool.', 'o': 'attributeTypes, typecastAfterValidate, typecastBeforeSave, typecastAfterFind, typecastAfterSave', 'c': "[\n    'class' => AttributeTypecastBehavior::class,\n    'attributeTypes' => [\n        'id' => AttributeTypecastBehavior::TYPE_INTEGER,\n        'amount' => AttributeTypecastBehavior::TYPE_FLOAT,\n        'is_active' => AttributeTypecastBehavior::TYPE_BOOLEAN,\n    ],\n    'typecastAfterFind' => true,\n],"},
                {'n': 'OptimisticLockBehavior', 'd': 'Автоматически подставляет номер версии записи, чтобы двое не перезаписали правки друг друга.', 'o': 'работает вместе с optimisticLock()', 'c': "// в модели\npublic function optimisticLock()\n{\n    return 'version';\n}\n\npublic function behaviors()\n{\n    return [OptimisticLockBehavior::class];\n}\n// при конфликте save() бросит StaleObjectException"},
                {'n': 'CacheableWidgetBehavior', 'd': 'Кэширует вывод виджета целиком. Прикрепляется к виджету, а не к модели.', 'o': 'cache, cacheDuration, cacheDependency, cacheKeyVariations, cacheEnabled', 'c': "class MenuWidget extends Widget\n{\n    public function behaviors()\n    {\n        return [[\n            'class' => CacheableWidgetBehavior::class,\n            'cacheDuration' => 3600,\n            'cacheKeyVariations' => [Yii::$app->language],\n        ]];\n    }\n}"},
            ]),
            ('note', 'tip', 'Часто нужные, но не встроенные',
             'Мягкое удаление и древовидные структуры живут в расширениях: `yii2tech/ar-softdelete` и `creocoder/yii2-nested-sets`. '
             'Они устроены так же и прикрепляются через тот же `behaviors()`.'),
        ]),
        ('own', 'Своё поведение', [
            ('code', 'php', 'components/PurifyBehavior.php', r'''namespace app\components;

use yii\base\Behavior;
use yii\db\ActiveRecord;
use yii\helpers\HtmlPurifier;

class PurifyBehavior extends Behavior
{
    /** @var string[] какие атрибуты чистить */
    public $attributes = [];

    public function events()
    {
        return [
            ActiveRecord::EVENT_BEFORE_INSERT => 'purify',
            ActiveRecord::EVENT_BEFORE_UPDATE => 'purify',
        ];
    }

    public function purify($event)
    {
        foreach ($this->attributes as $attribute) {
            $value = $this->owner->$attribute;
            if (is_string($value) && $value !== '') {
                $this->owner->$attribute = HtmlPurifier::process($value);
            }
        }
    }

    // публичный метод поведения становится методом владельца
    public function purifyNow()
    {
        $this->purify(null);
        return $this->owner;
    }
}'''),
            ('h', 'Подключение'),
            ('code', 'php', None, r'''public function behaviors()
{
    return [
        [
            'class' => PurifyBehavior::class,
            'attributes' => ['body', 'announce'],
        ],
    ];
}

// метод поведения доступен у модели
$post->purifyNow()->save();'''),
            ('h', 'Обработчиком может быть не только имя метода'),
            ('code', 'php', None, r'''public function events()
{
    return [
        ActiveRecord::EVENT_AFTER_INSERT => 'onInsert',              // метод поведения
        ActiveRecord::EVENT_AFTER_DELETE => [$this, 'onDelete'],     // явный callable
        ActiveRecord::EVENT_AFTER_FIND => function ($event) {        // замыкание
            Yii::debug('загружено: ' . $event->sender->id);
        },
    ];
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Массовые операции проходят мимо поведений',
             '`updateAll()`, `deleteAll()` и `updateAllCounters()` не создают объектов и не вызывают событий. '
             '`TimestampBehavior` при них не сработает, `updated_at` останется прежним.'),
            ('note', 'trap', 'Два поведения объявили одинаковый метод',
             'Побеждает то, что прикреплено раньше, молча. Давайте поведениям имена, чтобы конфликт было видно и можно было отцепить лишнее.'),
            ('note', 'warn', 'Поведение и консоль',
             '`BlameableBehavior` в консольной команде упадёт или запишет null: пользователя там нет. '
             'Задавайте `defaultValue` или отключайте поведение для сценария импорта.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- События

topic(
    id='events', group='object',
    title='События',
    cls='on() / trigger()',
    lead='Точки, где чужой код может вклиниться в работу компонента, ничего не наследуя.',
    badge='40+ точек в ядре',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Компонент вызывает `trigger()`, а подписчики регистрируются через `on()`. '
                  'Обработчики выполняются в порядке подписки; `$event->handled = true` останавливает цепочку.'),
            ('svg', '''<svg viewBox="0 0 740 236" role="img" aria-label="Порядок обработчиков: сначала обработчики экземпляра, затем класса, затем интерфейса" class="dg">
<defs><marker id="m-arr5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr5)" opacity=".55">
<path d="M158 56h40"/><path d="M340 56h40"/><path d="M522 56h40"/>
<path d="M270 78v46"/><path d="M452 78v46"/>
</g>
<g class="dg-box dg-live"><rect x="18" y="32" width="140" height="48" rx="8"/><text x="88" y="52">trigger()</text><text x="88" y="68" class="dg-sub">$post->save()</text></g>
<g class="dg-box"><rect x="198" y="32" width="142" height="48" rx="8"/><text x="269" y="52">экземпляр</text><text x="269" y="68" class="dg-sub">$post->on(...)</text></g>
<g class="dg-box"><rect x="380" y="32" width="142" height="48" rx="8"/><text x="451" y="52">класс</text><text x="451" y="68" class="dg-sub">Event::on(Post::class, ...)</text></g>
<g class="dg-box"><rect x="562" y="32" width="160" height="48" rx="8"/><text x="642" y="52">интерфейс</text><text x="642" y="68" class="dg-sub">Event::on(Iface::class, ...)</text></g>
<g class="dg-box dg-bad"><rect x="192" y="124" width="156" height="44" rx="8"/><text x="270" y="151">handled = true</text></g>
<g class="dg-box dg-bad"><rect x="374" y="124" width="156" height="44" rx="8"/><text x="452" y="151">цепочка обрывается</text></g>
<text x="370" y="200" class="dg-note" text-anchor="middle">у отменяемых событий отдельный флаг: $event-&gt;isValid = false</text>
</svg>''', 'Три уровня подписки срабатывают именно в этом порядке, и любой из них может остановить остальные.'),
            ('h', 'Подписка'),
            ('code', 'php', None, r'''// на конкретный объект
$post->on(Post::EVENT_AFTER_INSERT, function ($event) {
    $event->sender;   // сам объект
    $event->data;     // данные, переданные третьим аргументом on()
});

// с дополнительными данными и вставкой в начало очереди
$post->on(Post::EVENT_AFTER_INSERT, $handler, ['source' => 'admin'], false);

// на все объекты класса и его потомков
Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, function ($e) {
    Yii::debug(get_class($e->sender) . ' создан');
});

// отписка
$post->off(Post::EVENT_AFTER_INSERT, $handler);
$post->off(Post::EVENT_AFTER_INSERT);            // все обработчики
Event::off(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT);'''),
            ('h', 'В конфигурации — ключ «on имяСобытия»'),
            ('code', 'php', 'config/web.php', r''''components' => [
    'db' => [
        'class' => yii\db\Connection::class,
        'on afterOpen' => function ($event) {
            $event->sender->createCommand("SET time_zone = '+00:00'")->execute();
        },
    ],
],'''),
        ]),
        ('all', 'Каталог событий ядра', [
            ('p', 'Самые полезные точки встраивания, сгруппированные по классу. '
                  'Имена даны константами, как их пишут в коде.'),
            ('ref', [
                {'n': 'Application', 'd': 'Вокруг всего запроса и вокруг действия. Удобно для замера времени и общей подготовки.', 'o': 'EVENT_BEFORE_REQUEST, EVENT_AFTER_REQUEST, EVENT_BEFORE_ACTION, EVENT_AFTER_ACTION', 'c': "Yii::$app->on(Application::EVENT_BEFORE_REQUEST, function () {\n    Yii::$app->language = Yii::$app->request->getPreferredLanguage(\n        ['ru-RU', 'en-US']\n    );\n});"},
                {'n': 'Controller', 'd': 'То же на уровне контроллера и модуля. Возврат false из beforeAction отменяет действие.', 'o': 'EVENT_BEFORE_ACTION, EVENT_AFTER_ACTION', 'c': "public function beforeAction($action)\n{\n    if ($action->id === 'webhook') {\n        $this->enableCsrfValidation = false;\n    }\n    return parent::beforeAction($action);\n}"},
                {'n': 'Model', 'd': 'Вокруг проверки. Отмена через $event->isValid = false.', 'o': 'EVENT_BEFORE_VALIDATE, EVENT_AFTER_VALIDATE', 'c': "public function beforeValidate()\n{\n    $this->slug = $this->slug ?: Inflector::slug($this->title);\n    return parent::beforeValidate();\n}"},
                {'n': 'ActiveRecord', 'd': 'Полный жизненный цикл записи. Сюда же подключаются все встроенные поведения.', 'o': 'EVENT_INIT, EVENT_AFTER_FIND, EVENT_BEFORE_INSERT, EVENT_AFTER_INSERT, EVENT_BEFORE_UPDATE, EVENT_AFTER_UPDATE, EVENT_BEFORE_DELETE, EVENT_AFTER_DELETE, EVENT_AFTER_REFRESH', 'c': "public function afterSave($insert, $changedAttributes)\n{\n    parent::afterSave($insert, $changedAttributes);\n    if ($insert) {\n        Yii::$app->queue->push(new IndexJob(['id' => $this->id]));\n    }\n}"},
                {'n': 'View', 'd': 'Вокруг рендеринга и в ключевых точках разметки страницы.', 'o': 'EVENT_BEFORE_RENDER, EVENT_AFTER_RENDER, EVENT_BEGIN_PAGE, EVENT_END_PAGE, EVENT_BEGIN_BODY, EVENT_END_BODY', 'c': "Yii::$app->view->on(View::EVENT_END_BODY, function () {\n    echo '<!-- собрано ' . date('c') . ' -->';\n});"},
                {'n': 'User', 'd': 'Вход и выход. beforeLogin умеет запретить вход через isValid.', 'o': 'EVENT_BEFORE_LOGIN, EVENT_AFTER_LOGIN, EVENT_BEFORE_LOGOUT, EVENT_AFTER_LOGOUT', 'c': "'user' => [\n    'identityClass' => User::class,\n    'on afterLogin' => function ($event) {\n        $event->identity->updateAttributes([\n            'last_login_at' => time(),\n        ]);\n    },\n],"},
                {'n': 'Response', 'd': 'Перед отправкой ответа можно переписать тело и заголовки: единый формат API, обёртки, метрики.', 'o': 'EVENT_BEFORE_SEND, EVENT_AFTER_PREPARE, EVENT_AFTER_SEND', 'c': "'response' => [\n    'on beforeSend' => function ($event) {\n        $r = $event->sender;\n        if ($r->format === Response::FORMAT_JSON) {\n            $r->data = ['ok' => $r->isSuccessful, 'data' => $r->data];\n        }\n    },\n],"},
                {'n': 'Connection', 'd': 'Открытие соединения и границы транзакций.', 'o': 'EVENT_AFTER_OPEN, EVENT_BEGIN_TRANSACTION, EVENT_COMMIT_TRANSACTION, EVENT_ROLLBACK_TRANSACTION', 'c': "'db' => [\n    'on afterOpen' => function ($e) {\n        $e->sender->createCommand('SET NAMES utf8mb4')->execute();\n    },\n],"},
                {'n': 'Widget', 'd': 'Вокруг работы любого виджета: GridView, ActiveForm, Menu.', 'o': 'EVENT_INIT, EVENT_BEFORE_RUN, EVENT_AFTER_RUN', 'c': "Event::on(GridView::class, GridView::EVENT_BEFORE_RUN, function ($e) {\n    $e->sender->tableOptions = ['class' => 'table table-sm'];\n});"},
                {'n': 'BaseMailer', 'd': 'Вокруг отправки письма. beforeSend умеет отменить отправку.', 'o': 'EVENT_BEFORE_SEND, EVENT_AFTER_SEND', 'c': "'mailer' => [\n    'on beforeSend' => function ($event) {\n        if (YII_ENV_DEV) {\n            $event->message->setTo('dev@example.com');\n        }\n    },\n],"},
                {'n': 'Module', 'd': 'Модуль тоже компонент и тоже пропускает через себя действия своих контроллеров.', 'o': 'EVENT_BEFORE_ACTION, EVENT_AFTER_ACTION', 'c': "Yii::$app->getModule('admin')->on(\n    Module::EVENT_BEFORE_ACTION,\n    function ($event) { Yii::info('вход в админку'); }\n);"},
                {'n': 'MessageSource', 'd': 'Срабатывает, когда перевода нет. Удобно собирать недостающие строки.', 'o': 'EVENT_MISSING_TRANSLATION', 'c': "'i18n' => ['translations' => ['app*' => [\n    'class' => PhpMessageSource::class,\n    'on missingTranslation' => function ($event) {\n        Yii::warning('нет перевода: ' . $event->message);\n    },\n]]],"},
            ]),
        ]),
        ('own', 'Своё событие', [
            ('code', 'php', 'components/OrderService.php', r'''use yii\base\Component;
use yii\base\Event;

class OrderPaidEvent extends Event
{
    public $order;
    public $amount;
}

class OrderService extends Component
{
    // имя константой: не опечатаешься и видно поиском по проекту
    const EVENT_PAID = 'orderPaid';

    public function markPaid(Order $order, $amount)
    {
        $order->updateAttributes(['status' => Order::STATUS_PAID]);

        $this->trigger(self::EVENT_PAID, new OrderPaidEvent([
            'order' => $order,
            'amount' => $amount,
        ]));
    }
}'''),
            ('h', 'Подписка в одном месте при старте приложения'),
            ('code', 'php', 'config/web.php', r''''bootstrap' => ['log', 'app\components\EventBootstrap'],'''),
            ('code', 'php', 'components/EventBootstrap.php', r'''use yii\base\BootstrapInterface;

class EventBootstrap implements BootstrapInterface
{
    public function bootstrap($app)
    {
        Event::on(OrderService::class, OrderService::EVENT_PAID,
            [NotifyListener::class, 'onOrderPaid']);

        Event::on(OrderService::class, OrderService::EVENT_PAID,
            [StatsListener::class, 'onOrderPaid']);
    }
}'''),
            ('h', 'Глобальное событие через приложение'),
            ('code', 'php', None, r'''Yii::$app->on('app.cache.warmed', function ($event) { /* … */ });
Yii::$app->trigger('app.cache.warmed');'''),
            ('note', 'tip', 'Событие или прямой вызов',
             'События хороши, когда реакций может быть несколько и они не должны знать друг о друге: письмо, метрика, индексация. '
             'Если реакция ровно одна и обязательна, честнее вызвать метод напрямую — это видно в коде и проще отлаживать.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Event::on на BaseObject или Component',
             'Подписка на общий базовый класс сработает для тысяч объектов за запрос. Это незаметно съедает время. '
             'Подписывайтесь на конкретный класс или интерфейс.'),
            ('note', 'trap', 'Замыкание нельзя отцепить',
             'Чтобы вызвать `off()`, нужна та же самая ссылка на обработчик. Анонимную функцию сохраняйте в переменную при подписке.'),
            ('note', 'warn', 'handled и isValid — разные вещи',
             '`handled = true` останавливает остальные обработчики. `isValid = false` отменяет саму операцию. '
             'Их путают, и тогда сохранение продолжается, хотя код «запретил».'),
            ('note', 'trap', 'Исключение в обработчике ломает основную операцию',
             'Обработчик выполняется внутри `save()`. Ошибка в отправке письма из `afterSave` уронит сохранение. '
             'Заворачивайте побочные действия в try/catch или отдавайте в очередь.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Active Record

topic(
    id='ar', group='db',
    title='Active Record',
    cls='yii\\db\\ActiveRecord',
    lead='Таблица — класс, строка — объект, внешние ключи — связи. Плюс жизненный цикл, куда встраиваются поведения.',
    badge='9 событий',
    tabs=[
        ('how', 'Жизненный цикл', [
            ('p', 'Каждое сохранение проходит одну и ту же цепочку. Ровно в эти точки подключаются поведения '
                  'и ваши переопределения. Нажмите на кнопку и посмотрите порядок.'),
            ('demo', 'lifecycle-lab'),
            ('h', 'Чтение'),
            ('code', 'php', None, r'''Post::findOne(1);                      // по первичному ключу
Post::findOne(['slug' => $slug]);      // по условию
Post::findAll(['status' => 1]);        // массив записей

Post::find()
    ->where(['status' => Post::STATUS_PUBLISHED])
    ->with('author', 'tags')            // жадная загрузка связей
    ->orderBy(['created_at' => SORT_DESC])
    ->limit(10)
    ->all();

Post::find()->where(...)->exists();
Post::find()->count();
Post::find()->asArray()->all();         // массивы вместо объектов, быстрее

foreach (Post::find()->batch(100) as $posts) { /* по 100 штук */ }'''),
            ('h', 'Запись'),
            ('code', 'php', None, r'''$post = new Post();
$post->title = 'Привет';
$post->save();            // валидация + INSERT; false, если правила не прошли
$post->save(false);       // без валидации

$post->dirtyAttributes;   // что реально изменилось, только это уйдёт в UPDATE
$post->oldAttributes;     // значения на момент загрузки

$post->updateCounters(['views' => 1]);   // атомарный инкремент, без гонок
$post->delete();
$post->refresh();

// массовые операции: быстро, но без событий и поведений
Post::updateAll(['status' => 0], ['<', 'created_at', $ts]);
Post::deleteAll(['status' => 0]);'''),
            ('note', 'trap', 'findOne() с данными из запроса',
             '`Post::findOne(Yii::$app->request->get(\'id\'))` опасен: массив в параметре превращается в условие. '
             'Приводите к числу или пишите условие явно: `findOne([\'id\' => (int) $id])`.'),
        ]),
        ('all', 'Связи и всё, что вокруг', [
            ('ref', [
                {'n': 'hasOne()', 'd': 'Одна связанная запись. Массив читается как «столбец чужой таблицы ⇒ столбец текущей» — самая частая путаница.', 'o': 'возвращает ActiveQuery, можно достраивать', 'c': "public function getAuthor()\n{\n    return $this->hasOne(User::class, ['id' => 'author_id']);\n}\n\n$post->author;          // объект или null\n$post->getAuthor();     // ActiveQuery для достройки"},
                {'n': 'hasMany()', 'd': 'Много связанных записей. Отдаёт массив объектов.', 'o': 'indexBy(), where(), orderBy()', 'c': "public function getComments()\n{\n    return $this->hasMany(Comment::class, ['post_id' => 'id'])\n        ->orderBy(['created_at' => SORT_DESC]);\n}"},
                {'n': 'viaTable()', 'd': 'Связь через промежуточную таблицу без отдельного класса модели.', 'o': 'имя таблицы + соответствие столбцов', 'c': "public function getTags()\n{\n    return $this->hasMany(Tag::class, ['id' => 'tag_id'])\n        ->viaTable('post_tag', ['post_id' => 'id']);\n}"},
                {'n': 'via()', 'd': 'То же через другую объявленную связь: когда у промежуточной таблицы есть своя модель и свои поля.', 'o': 'имя связи', 'c': "public function getOrderItems()\n{\n    return $this->hasMany(OrderItem::class, ['order_id' => 'id']);\n}\npublic function getItems()\n{\n    return $this->hasMany(Item::class, ['id' => 'item_id'])\n        ->via('orderItems');\n}"},
                {'n': 'with()', 'd': 'Жадная загрузка: отдельный запрос на связь для всех записей сразу. Лечит проблему N+1.', 'o': 'вложенность через точку, настройка замыканием', 'c': "Post::find()->with('author', 'tags')->all();\nPost::find()->with('comments.author')->all();\nPost::find()->with([\n    'comments' => function ($q) {\n        $q->andWhere(['approved' => 1]);\n    },\n])->all();"},
                {'n': 'joinWith()', 'd': 'Добавляет JOIN, поэтому позволяет фильтровать и сортировать по столбцам связанной таблицы. with() так не умеет.', 'o': 'innerJoinWith(), второй аргумент отключает загрузку', 'c': "Post::find()\n    ->joinWith('author')\n    ->where(['user.status' => 1])\n    ->orderBy('user.name')\n    ->all();\n\nPost::find()->joinWith('author', false);   // только JOIN"},
                {'n': 'inverseOf()', 'd': 'Указывает обратную связь, чтобы не делать лишний запрос при обходе в обе стороны.', 'o': 'имя связи на той стороне', 'c': "public function getComments()\n{\n    return $this->hasMany(Comment::class, ['post_id' => 'id'])\n        ->inverseOf('post');\n}\n\n$comments = $post->comments;\n$comments[0]->post === $post;   // true, без запроса"},
                {'n': 'onCondition()', 'd': 'Дополнительное условие связи. Попадает в ON при JOIN и в WHERE при ленивой загрузке.', 'o': 'массив условия', 'c': "public function getActiveComments()\n{\n    return $this->hasMany(Comment::class, ['post_id' => 'id'])\n        ->onCondition(['approved' => 1]);\n}"},
                {'n': 'link() / unlink()', 'd': 'Связать или развязать две записи, в том числе через промежуточную таблицу.', 'o': 'третий аргумент unlink удаляет саму связь', 'c': "$post->link('tags', $tag);          // добавит строку в post_tag\n$post->unlink('tags', $tag, true);  // и удалит её\n$comment->link('post', $post);      // проставит post_id и сохранит"},
                {'n': 'Свой ActiveQuery', 'd': 'Общие условия выборки в одном месте, доступны и в связях.', 'o': 'переопределить find()', 'c': "class PostQuery extends ActiveQuery\n{\n    public function published()\n    {\n        return $this->andWhere(['status' => Post::STATUS_PUBLISHED]);\n    }\n}\n\n// в модели\npublic static function find()\n{\n    return new PostQuery(static::class);\n}\n\nPost::find()->published()->all();\n$user->getPosts()->published()->all();"},
                {'n': 'transactions()', 'd': 'Декларативно оборачивает операции в транзакцию для выбранного сценария.', 'o': 'OP_INSERT, OP_UPDATE, OP_DELETE, OP_ALL', 'c': "public function transactions()\n{\n    return [\n        'api' => self::OP_ALL,\n        'admin' => self::OP_INSERT | self::OP_UPDATE,\n    ];\n}"},
                {'n': 'optimisticLock()', 'd': 'Защита от того, что двое одновременно правят одну запись.', 'o': 'нужен целочисленный столбец версии', 'c': "public function optimisticLock()\n{\n    return 'version';\n}\n\n// в форме\necho $form->field($model, 'version')->hiddenInput();\n\ntry { $model->save(); }\ncatch (StaleObjectException $e) { /* запись уже изменили */ }"},
                {'n': 'Дополнительные поля из запроса', 'd': 'Публичное свойство класса заполняется из псевдонима в SELECT: агрегаты и вычисляемые значения.', 'o': 'обычное public-свойство', 'c': "class User extends ActiveRecord\n{\n    public $postCount;\n}\n\nUser::find()\n    ->select(['user.*', 'postCount' => 'COUNT(p.id)'])\n    ->joinWith('posts p', false)\n    ->groupBy('user.id')\n    ->all();"},
            ]),
        ]),
        ('own', 'Точки переопределения', [
            ('p', 'Каждый метод парный: `before…` может отменить операцию, вернув `false`, `after…` уже ничего не отменит. '
                  'Всегда вызывайте родительский метод, иначе не сработают события и поведения.'),
            ('code', 'php', 'models/Post.php', r'''class Post extends ActiveRecord
{
    public static function tableName()
    {
        return '{{%post}}';
    }

    public function behaviors()
    {
        return [TimestampBehavior::class, BlameableBehavior::class];
    }

    public function beforeValidate()
    {
        if (!parent::beforeValidate()) {
            return false;
        }
        $this->slug = $this->slug ?: Inflector::slug($this->title);
        return true;
    }

    public function beforeSave($insert)
    {
        if (!parent::beforeSave($insert)) {
            return false;
        }
        if ($insert) {
            $this->token = Yii::$app->security->generateRandomString();
        }
        return true;
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);

        // сработает только когда статус реально изменился
        if (array_key_exists('status', $changedAttributes)) {
            Yii::$app->queue->push(new ReindexJob(['id' => $this->id]));
        }
    }

    public function beforeDelete()
    {
        if (!parent::beforeDelete()) {
            return false;
        }
        return !$this->hasPaidOrders();   // запретить удаление
    }

    public function afterFind()
    {
        parent::afterFind();
        $this->_meta = json_decode((string) $this->meta_json, true) ?: [];
    }
}'''),
            ('note', 'tip', 'changedAttributes хранит старые значения',
             'В `afterSave()` массив `$changedAttributes` содержит значения **до** изменения. '
             'Поэтому «было и стало» доступно так: `$changedAttributes[\'status\']` и `$this->status`.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Проблема N+1',
             'Цикл по ста записям с обращением к `$post->author` даст сто один запрос. '
             'Лечится одним словом: `->with(\'author\')`. Проверяйте панелью Database в отладчике.'),
            ('note', 'trap', 'joinWith с hasMany размножает строки',
             'JOIN к таблице «многих» дублирует строки основной таблицы, и `count()` с `limit` начинают врать. '
             'Добавьте `groupBy` по первичному ключу или комбинируйте `joinWith(\'rel\', false)` с `with(\'rel\')`.'),
            ('note', 'trap', 'save() вернул false без исключения',
             'Это не сбой базы, а непройденная валидация. Смотрите `$model->errors`. '
             'Если данные уже проверены выше, зовите `save(false)`.'),
            ('note', 'warn', 'Порядок столбцов в связи',
             '`hasMany(Comment::class, [\'post_id\' => \'id\'])` — сначала столбец **чужой** таблицы, потом своей. '
             'Перепутанный порядок даёт пустую связь или ошибку про неизвестный столбец.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Query Builder

topic(
    id='query', group='db',
    title='Query Builder',
    cls='yii\\db\\Query',
    lead='Сборка SQL объектом: экранирование имён, привязка параметров и совместимость с любой СУБД бесплатно.',
    badge='16 операторов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Методы построения возвращают тот же объект, поэтому их можно вызывать в любом порядке. '
                  'Запрос выполняется только на завершающем методе: `all()`, `one()`, `scalar()` и подобных.'),
            ('demo', 'query-lab'),
            ('h', 'Завершающие методы'),
            ('kv', [
                ('all()', 'все строки'),
                ('one()', 'первая строка или false; просто добавляет LIMIT 1'),
                ('column()', 'массив значений первого столбца'),
                ('scalar()', 'одно значение из первой строки'),
                ('exists()', 'есть ли хоть одна строка'),
                ('count(), sum(), average(), max(), min()', 'агрегаты; сохраняют where и join, но игнорируют orderBy, limit и offset'),
                ('batch($n), each($n)', 'чтение курсором порциями, чтобы не держать всё в памяти'),
                ('createCommand()', 'не выполнять, а получить готовую команду и посмотреть SQL'),
            ]),
            ('code', 'php', None, r'''$sql = (new Query())->from('post')->where(['status' => 1])
    ->createCommand()->getRawSql();
// SELECT * FROM `post` WHERE `status`=1'''),
        ]),
        ('all', 'Все форматы условий', [
            ('p', 'Три формата `where()`. Строковый — только для условий без пользовательских данных. '
                  'Хеш и операторный привязывают значения параметрами, поэтому безопасны.'),
            ('ref', [
                {'n': 'хеш: столбец ⇒ значение', 'd': 'Самый частый формат. Сам подставляет IN для массива и IS NULL для null.', 'o': 'равенство, IN, IS NULL, подзапрос', 'c': "->where([\n    'status' => 1,\n    'id' => [4, 8, 15],      // IN (4, 8, 15)\n    'deleted_at' => null,    // IS NULL\n    'author_id' => $subQuery,\n])"},
                {'n': 'and / or', 'd': 'Склейка условий любой вложенности. Операнды — условия в любом формате.', 'o': 'вложенность не ограничена', 'c': "->where([\n    'and',\n    ['status' => 1],\n    ['or', ['type' => 1], ['>', 'created_at', $ts]],\n])"},
                {'n': 'not', 'd': 'Отрицание вложенного условия.', 'o': '', 'c': "->where(['not', ['status' => 1]])"},
                {'n': 'between / not between', 'd': 'Диапазон включительно.', 'o': 'столбец, от, до', 'c': "->where(['between', 'created_at', $from, $to])"},
                {'n': 'in / not in', 'd': 'Список значений или подзапрос. Умеет составной ключ.', 'o': 'составной ключ массивом', 'c': "->where(['in', 'id', [1, 2, 3]])\n->where(['in', ['lang', 'slug'], [\n    ['lang' => 'ru', 'slug' => 'privet'],\n]])"},
                {'n': 'like / not like', 'd': 'Поиск подстроки. Проценты добавляются сами, а спецсимволы экранируются.', 'o': 'третий аргумент false отключает экранирование', 'c': "->where(['like', 'title', 'yii'])\n// title LIKE '%yii%'\n->where(['like', 'title', ['php', 'yii']])\n// две подстроки через AND\n->where(['like', 'code', '%-2024', false])"},
                {'n': 'or like / or not like', 'd': 'То же, но подстроки склеиваются через OR.', 'o': '', 'c': "->where(['or like', 'title', ['php', 'yii']])"},
                {'n': 'exists / not exists', 'd': 'Проверка наличия строк в подзапросе.', 'o': 'принимает Query', 'c': "->where(['exists',\n    (new Query())->from('order')\n        ->where('order.user_id = user.id')\n])"},
                {'n': 'сравнения', 'd': 'Операторы >, >=, <, <=, =, != и <> в операторном формате.', 'o': '', 'c': "->where(['>=', 'price', 100])\n->where(['!=', 'status', 0])"},
                {'n': 'filterWhere()', 'd': 'Пропускает условия с пустыми значениями. Создан ровно для форм поиска.', 'o': 'andFilterWhere(), orFilterWhere(), andFilterCompare()', 'c': "->filterWhere([\n    'status' => $status,      // пропустится, если пусто\n])\n->andFilterWhere(['like', 'title', $q])\n->andFilterCompare('price', '>=100')"},
                {'n': 'Expression', 'd': 'Кусок SQL как есть, когда нужна функция базы. Пользовательские данные — только параметрами.', 'o': 'второй аргумент — параметры', 'c': "use yii\\db\\Expression;\n\n->select(['id', new Expression('NOW() AS now')])\n->where(new Expression('YEAR(created_at) = :y', [':y' => 2024]))\n->orderBy(new Expression('RAND()'))"},
                {'n': 'join', 'd': 'Все виды соединений; таблицей может быть подзапрос.', 'o': 'innerJoin, leftJoin, rightJoin, join', 'c': "->leftJoin('user u', 'u.id = post.author_id')\n->innerJoin(['t' => $subQuery], 't.post_id = post.id')"},
                {'n': 'select / from', 'd': 'Псевдонимы столбцов и таблиц, подзапросы, DISTINCT.', 'o': 'addSelect, distinct', 'c': "->select(['id', 'author' => 'u.name'])\n->select([\"CONCAT(a, ' ', b) AS full\"])\n->from(['p' => 'post'])\n->from(['t' => $subQuery])\n->distinct()"},
                {'n': 'group / having', 'd': 'Группировка и условие по агрегату. having понимает те же форматы, что where.', 'o': 'addGroupBy, andHaving, filterHaving', 'c': "->groupBy(['author_id'])\n->having(['>', 'COUNT(*)', 5])"},
                {'n': 'orderBy / limit', 'd': 'Сортировка массивом или строкой, срез результата.', 'o': 'addOrderBy, offset', 'c': "->orderBy(['created_at' => SORT_DESC, 'id' => SORT_ASC])\n->limit(20)->offset(40)"},
                {'n': 'union / withQuery', 'd': 'Объединение выборок и общие табличные выражения.', 'o': 'union($q, $all), withQuery($q, $alias)', 'c': "$a->union($b, true);   // UNION ALL\n\n$q->withQuery($cte, 'recent')\n  ->from('recent');"},
            ]),
        ]),
        ('own', 'Приёмы', [
            ('h', 'Пакетная выборка для экспорта'),
            ('code', 'php', None, r'''$query = (new Query())->from('order')->orderBy('id');

foreach ($query->batch(500) as $rows) {
    // по 500 строк за итерацию, память не растёт
    fputcsv($handle, $rows);
}

foreach ($query->each(500) as $row) {
    // по одной строке, порция всё равно 500
}'''),
            ('note', 'warn', 'MySQL и пакетная выборка',
             'По-настоящему курсор работает только на небуферизованном соединении: '
             '`PDO::MYSQL_ATTR_USE_BUFFERED_QUERY => false`. Пока такой курсор открыт, другие запросы на этом соединении делать нельзя — '
             'заведите второе соединение специально для выгрузок.'),
            ('h', 'Индексация результата'),
            ('code', 'php', None, r'''$byId = (new Query())->from('user')->indexBy('id')->all();
// ['12' => ['id' => 12, …], …]

$byKey = (new Query())->from('user')
    ->indexBy(function ($row) {
        return $row['lang'] . '-' . $row['id'];
    })->all();'''),
            ('h', 'Кэширование запроса'),
            ('code', 'php', None, r'''$rows = (new Query())->from('city')->cache(3600)->all();

// или на уровне соединения, с зависимостью
$result = Yii::$app->db->cache(function ($db) {
    return (new Query())->from('city')->all();
}, 3600, new DbDependency(['sql' => 'SELECT MAX(updated_at) FROM city']));'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Конкатенация вместо параметров',
             '`"WHERE name = \'$name\'"` — это внедрение SQL. Всегда хеш-формат или плейсхолдеры. '
             'Имя столбца параметром передать нельзя: проверяйте его по белому списку.'),
            ('note', 'trap', 'count() игнорирует limit',
             'Агрегаты специально отбрасывают `limit`, `offset` и `orderBy`, чтобы считать общее количество для постраничной навигации. '
             'Это не баг, но удивляет.'),
            ('note', 'warn', 'one() не проверяет единственность',
             'Метод просто добавляет `LIMIT 1` и отдаёт первую попавшуюся строку. Если вы рассчитывали на одну запись, проверяйте это сами.'),
            ('note', 'trap', 'Пустой массив в IN',
             '`[\'id\' => []]` превращается в условие, которое не выполнится никогда. Обычно это верно, но иногда неожиданно: '
             'проверяйте массив перед добавлением условия или используйте `filterWhere`.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Запрос и ответ

topic(
    id='http', group='http',
    title='Запрос и ответ',
    cls='request / response',
    lead='Что пришло от браузера и что уходит обратно: параметры, заголовки, формат, файлы, редиректы.',
    badge='2 компонента',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Два компонента приложения. `request` разбирает входящий HTTP-запрос, `response` собирает исходящий. '
                  'Действие контроллера может вернуть строку, массив или объект ответа — остальное фреймворк сделает сам.'),
            ('svg', '''<svg viewBox="0 0 760 200" role="img" aria-label="Путь от браузера через запрос, действие и ответ обратно в браузер" class="dg">
<defs><marker id="m-arr6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr6)" opacity=".55">
<path d="M148 52h44"/><path d="M336 52h44"/><path d="M524 52h44"/>
<path d="M648 76v44H100V76"/>
</g>
<g class="dg-box"><rect x="24" y="28" width="124" height="48" rx="8"/><text x="86" y="48">браузер</text><text x="86" y="64" class="dg-sub">GET /post/7</text></g>
<g class="dg-box"><rect x="192" y="28" width="144" height="48" rx="8"/><text x="264" y="48">request</text><text x="264" y="64" class="dg-sub">get(), post(), headers</text></g>
<g class="dg-box dg-live"><rect x="380" y="28" width="144" height="48" rx="8"/><text x="452" y="48">действие</text><text x="452" y="64" class="dg-sub">return …</text></g>
<g class="dg-box"><rect x="568" y="28" width="160" height="48" rx="8"/><text x="648" y="48">response</text><text x="648" y="64" class="dg-sub">формат, код, заголовки</text></g>
<text x="374" y="140" class="dg-note" text-anchor="middle">строка → HTML · массив → JSON · Response → как есть</text>
</svg>''', 'Тип возвращённого значения решает, чем станет ответ: отдельного «вернуть JSON» вызывать не нужно.'),
            ('h', 'Чтение запроса'),
            ('code', 'php', None, r'''$request = Yii::$app->request;

$request->get('id');                 // ?id=7, второй аргумент — значение по умолчанию
$request->post('name', 'аноним');
$request->getBodyParams();           // всё тело, разобранное парсером
$request->getRawBody();              // как есть, для подписи вебхуков
$request->getQueryParams();

$request->isPost;  $request->isGet;  $request->isAjax;  $request->isPjax;
$request->method;                    // GET, POST, PUT…
$request->url;                       // /post/7?src=ad
$request->absoluteUrl;
$request->referrer;  $request->userAgent;  $request->userIP;
$request->isSecureConnection;
$request->headers->get('X-Api-Key');
$request->getAuthCredentials();      // [логин, пароль] из Basic
$request->getPreferredLanguage(['ru-RU', 'en-US']);'''),
            ('h', 'Формирование ответа'),
            ('code', 'php', None, r'''return $this->render('view', ['model' => $model]);      // HTML в layout
return $this->renderPartial('_row', ['item' => $item]); // без layout
return $this->asJson(['ok' => true]);                    // JSON
return $this->redirect(['post/view', 'id' => 7]);
return $this->goBack();                                  // на returnUrl
return $this->goHome();
return $this->refresh();

$response = Yii::$app->response;
$response->statusCode = 201;
$response->headers->set('X-Total-Count', $count);
$response->format = Response::FORMAT_JSON;
$response->data = ['items' => $items];

return $response->sendFile('/path/report.pdf');
return $response->sendContentAsFile($csv, 'export.csv');
return $response->xSendFile('/path/big.zip');            // отдаёт веб-сервер'''),
        ]),
        ('all', 'Настройки и форматы', [
            ('ref', [
                {'n': 'parsers', 'd': 'Разбор тела запроса по типу содержимого. Без этого JSON от клиента не попадёт в post().', 'o': 'JsonParser, MultipartFormDataParser', 'c': "'request' => [\n    'parsers' => [\n        'application/json' => yii\\web\\JsonParser::class,\n    ],\n],"},
                {'n': 'cookieValidationKey', 'd': 'Ключ подписи куки. Без него приложение не запустится, и это правильно.', 'o': 'длинная случайная строка вне репозитория', 'c': "'request' => [\n    'cookieValidationKey' => getenv('COOKIE_KEY'),\n],"},
                {'n': 'enableCsrfValidation', 'd': 'Проверка токена для небезопасных методов. Включена по умолчанию.', 'o': 'csrfParam, csrfCookie', 'c': "// точечно отключить для вебхука\npublic function beforeAction($action)\n{\n    if ($action->id === 'webhook') {\n        $this->enableCsrfValidation = false;\n    }\n    return parent::beforeAction($action);\n}"},
                {'n': 'trustedHosts', 'd': 'Кому верить в заголовках прокси. Без настройки за балансировщиком вы увидите чужой IP и схему.', 'o': 'secureHeaders, ipHeaders, hostInfo', 'c': "'request' => [\n    'trustedHosts' => ['10.0.0.0/8'],\n    'hostInfo' => 'https://example.com',\n],"},
                {'n': 'FORMAT_HTML', 'd': 'Формат по умолчанию для веб-приложения.', 'o': '', 'c': "$response->format = Response::FORMAT_HTML;"},
                {'n': 'FORMAT_JSON', 'd': 'Массивы и объекты Arrayable превращаются в JSON.', 'o': 'JsonResponseFormatter: prettyPrint, encodeOptions', 'c': "'response' => ['formatters' => [\n    'json' => [\n        'class' => yii\\web\\JsonResponseFormatter::class,\n        'prettyPrint' => YII_DEBUG,\n        'encodeOptions' => JSON_UNESCAPED_UNICODE,\n    ],\n]],"},
                {'n': 'FORMAT_XML', 'd': 'То же самое в XML, для клиентов, которым нужен именно он.', 'o': 'XmlResponseFormatter: rootTag, itemTag', 'c': "'xml' => [\n    'class' => yii\\web\\XmlResponseFormatter::class,\n    'rootTag' => 'response',\n],"},
                {'n': 'FORMAT_JSONP', 'd': 'JSON в обёртке callback. Сейчас нужен редко.', 'o': 'data = [data, callback]', 'c': "$response->format = Response::FORMAT_JSONP;\n$response->data = ['data' => $rows, 'callback' => 'cb'];"},
                {'n': 'FORMAT_RAW', 'd': 'Отдать содержимое как есть, без обработки.', 'o': '', 'c': "$response->format = Response::FORMAT_RAW;\n$response->content = $svg;\n$response->headers->set('Content-Type', 'image/svg+xml');"},
                {'n': 'Исключения как коды ответа', 'd': 'Любое HttpException превращается в правильный код и страницу ошибки.', 'o': 'BadRequest 400, Unauthorized 401, Forbidden 403, NotFound 404, MethodNotAllowed 405, Conflict 409, UnprocessableEntity 422, TooManyRequests 429, ServerError 500', 'c': "throw new NotFoundHttpException('Пост не найден');\nthrow new ForbiddenHttpException('Нет доступа');\nthrow new BadRequestHttpException();\n\n// сообщение видно пользователю и не в debug-режиме\nthrow new UserException('Заказ уже оплачен');"},
                {'n': 'on beforeSend', 'd': 'Последний шанс переписать ответ целиком: единая обёртка API, метрики, заголовки.', 'o': 'событие Response', 'c': "'response' => [\n    'on beforeSend' => function ($event) {\n        $r = $event->sender;\n        $r->headers->set('X-Request-Id', Yii::$app->requestId);\n    },\n],"},
            ]),
        ]),
        ('own', 'Рецепты', [
            ('h', 'Одинаковый формат ошибок для API'),
            ('code', 'php', 'config/web.php', r''''response' => [
    'class' => yii\web\Response::class,
    'on beforeSend' => function ($event) {
        $response = $event->sender;
        if ($response->format !== yii\web\Response::FORMAT_JSON) {
            return;
        }
        $response->data = [
            'success' => $response->isSuccessful,
            'status' => $response->statusCode,
            'data' => $response->data,
        ];
    },
],'''),
            ('h', 'Отдача файла, которого нет на диске'),
            ('code', 'php', None, r'''public function actionExport()
{
    $csv = "id;name\n";
    foreach (User::find()->batch(500) as $users) {
        foreach ($users as $user) {
            $csv .= $user->id . ';' . $user->username . "\n";
        }
    }

    return Yii::$app->response->sendContentAsFile($csv, 'users.csv', [
        'mimeType' => 'text/csv',
    ]);
}'''),
            ('h', 'Разный ответ на обычный и AJAX-запрос'),
            ('code', 'php', None, r'''public function actionDelete($id)
{
    $this->findModel($id)->delete();

    if (Yii::$app->request->isAjax) {
        Yii::$app->response->statusCode = 204;
        return null;
    }

    Yii::$app->session->setFlash('success', 'Удалено');
    return $this->redirect(['index']);
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'JSON пришёл, а post() пустой',
             'Без `parsers` тело с типом `application/json` не разбирается. Добавьте `JsonParser` в компонент `request`.'),
            ('note', 'trap', 'Вывод после return',
             'Любой `echo` или лишний пробел вне тегов PHP попадёт в тело ответа и сломает JSON и отдачу файлов. '
             'Не ставьте закрывающий `?>` в конце файлов классов.'),
            ('note', 'warn', 'sendFile не завершает скрипт',
             'После `sendFile()` код продолжит выполняться. Всегда возвращайте результат из действия, а не вызывайте метод посреди логики.'),
            ('note', 'trap', 'Неверный IP за прокси',
             'Без `trustedHosts` компонент `request` не доверяет заголовкам `X-Forwarded-For`, и `userIP` покажет адрес балансировщика, '
             'а `isSecureConnection` вернёт false даже на HTTPS.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Сессии, куки и кэш

topic(
    id='state', group='view',
    title='Сессии, куки и кэш',
    cls='session / cookies / cache',
    lead='Всё, что живёт дольше одного запроса: данные пользователя, метки в браузере и сохранённые результаты.',
    badge='10 хранилищ кэша',
    tabs=[
        ('how', 'Как устроено', [
            ('h', 'Сессия'),
            ('code', 'php', None, r'''$session = Yii::$app->session;

$session->open();                     // обычно не нужно: откроется сама
$session->set('cart', $items);
$session->get('cart', []);            // со значением по умолчанию
$session['cart'] = $items;            // то же через ArrayAccess
$session->has('cart');
$session->remove('cart');
$session->removeAll();
$session->destroy();
$session->regenerateID(true);         // после входа, против фиксации сессии'''),
            ('h', 'Флеш-сообщения: живут ровно до следующего показа'),
            ('code', 'php', None, r'''Yii::$app->session->setFlash('success', 'Заказ оформлен');

// в layout
foreach (Yii::$app->session->getAllFlashes() as $type => $message) {
    echo Alert::widget(['options' => ['class' => 'alert-' . $type],
                        'body' => $message]);
}'''),
            ('h', 'Куки: читаем из запроса, пишем в ответ'),
            ('code', 'php', None, r'''// чтение
$lang = Yii::$app->request->cookies->getValue('lang', 'ru');

// запись
Yii::$app->response->cookies->add(new yii\web\Cookie([
    'name' => 'lang',
    'value' => 'ru',
    'expire' => time() + 86400 * 365,
    'httpOnly' => true,
    'secure' => true,
    'sameSite' => yii\web\Cookie::SAME_SITE_LAX,
]));

// удаление
Yii::$app->response->cookies->remove('lang');'''),
            ('note', 'tip', 'Куки подписаны',
             'Yii добавляет к значению подпись на основе `cookieValidationKey`. Подделанная кука просто не прочитается. '
             'Поэтому ключ обязателен и должен быть случайным.'),
            ('h', 'Кэш'),
            ('code', 'php', None, r'''$cache = Yii::$app->cache;

// главный приём: посчитать один раз
$top = $cache->getOrSet(['top-posts', $page], function () {
    return Post::find()->popular()->limit(10)->all();
}, 3600, new TagDependency(['tags' => 'posts']));

$cache->set($key, $value, 600);
$cache->get($key);           // false, если промах
$cache->add($key, $value);   // только если ключа ещё нет
$cache->delete($key);
$cache->flush();

$cache->multiSet(['a' => 1, 'b' => 2], 600);
$cache->multiGet(['a', 'b']);

// сброс по тегу, обычно в afterSave модели
TagDependency::invalidate($cache, 'posts');'''),
        ]),
        ('all', 'Хранилища и зависимости', [
            ('h', 'Куда складывать кэш'),
            ('ref', [
                {'n': 'FileCache', 'd': 'Файлы в runtime. Работает везде и без настройки, поэтому стоит по умолчанию. Для одного сервера нормально.', 'o': 'cachePath, dirMode, gcProbability', 'c': "'cache' => ['class' => yii\\caching\\FileCache::class],"},
                {'n': 'ApcCache', 'd': 'Память процесса PHP через APCu. Самый быстрый вариант, но не разделяется между серверами и сбрасывается при перезапуске.', 'o': 'useApcu', 'c': "'cache' => [\n    'class' => yii\\caching\\ApcCache::class,\n    'useApcu' => true,\n],"},
                {'n': 'MemCache', 'd': 'Memcached: общий кэш для нескольких серверов приложения.', 'o': 'servers, useMemcached, username, password', 'c': "'cache' => [\n    'class' => yii\\caching\\MemCache::class,\n    'useMemcached' => true,\n    'servers' => [[\n        'host' => 'cache1', 'port' => 11211, 'weight' => 100,\n    ]],\n],"},
                {'n': 'yii\\redis\\Cache', 'd': 'Redis из расширения yii2-redis: общий кэш, который переживает перезапуск.', 'o': 'redis, keyPrefix', 'c': "'cache' => [\n    'class' => yii\\redis\\Cache::class,\n    'redis' => ['hostname' => 'localhost', 'database' => 1],\n],"},
                {'n': 'DbCache', 'd': 'Таблица в базе. Медленно, но иногда это единственное общее хранилище.', 'o': 'db, cacheTable', 'c': "'cache' => [\n    'class' => yii\\caching\\DbCache::class,\n    'cacheTable' => '{{%cache}}',\n],\n// ./yii migrate --migrationPath=@yii/caching/migrations"},
                {'n': 'ArrayCache', 'd': 'Массив в памяти на время одного запроса. Для тестов и для повторных обращений внутри запроса.', 'o': 'serializer', 'c': "'cache' => ['class' => yii\\caching\\ArrayCache::class],"},
                {'n': 'DummyCache', 'd': 'Заглушка: код с кэшем работает как обычно, но ничего не хранится. Удобно в разработке.', 'o': '', 'c': "'cache' => ['class' => yii\\caching\\DummyCache::class],"},
                {'n': 'WinCache, XCache, ZendDataCache', 'd': 'Исторические расширения PHP. В новых проектах не используются.', 'o': '', 'c': "// оставлены для совместимости"},
            ]),
            ('h', 'Когда считать кэш устаревшим'),
            ('ref', [
                {'n': 'TagDependency', 'd': 'Помечает записи тегами и сбрасывает их пачкой. Самый удобный способ.', 'o': 'tags', 'c': "$cache->set($key, $data, 0, new TagDependency([\n    'tags' => ['posts', 'homepage'],\n]));\n\n// в afterSave модели\nTagDependency::invalidate(Yii::$app->cache, 'posts');"},
                {'n': 'DbDependency', 'd': 'Устаревает, когда меняется результат запроса. Обычно это максимум времени изменения.', 'o': 'sql, params, reusable', 'c': "new DbDependency([\n    'sql' => 'SELECT MAX(updated_at) FROM post',\n])"},
                {'n': 'FileDependency', 'd': 'Смотрит на время изменения файла. Для кэша, зависящего от конфигурации или шаблона.', 'o': 'fileName', 'c': "new FileDependency(['fileName' => '@app/config/prices.php'])"},
                {'n': 'ExpressionDependency', 'd': 'Любое выражение PHP: язык, роль пользователя, версия сборки.', 'o': 'expression, params', 'c': "new ExpressionDependency([\n    'expression' => 'Yii::$app->language',\n])"},
                {'n': 'ChainedDependency', 'd': 'Несколько зависимостей сразу; по умолчанию достаточно одной сработавшей.', 'o': 'dependencies, dependOnAll', 'c': "new ChainedDependency([\n    'dependencies' => [$byTag, $byFile],\n])"},
            ]),
            ('h', 'Где ещё живёт состояние'),
            ('ref', [
                {'n': 'DbSession', 'd': 'Сессии в таблице: обязательны, когда серверов приложения несколько.', 'o': 'sessionTable, db, writeCallback', 'c': "'session' => [\n    'class' => yii\\web\\DbSession::class,\n    'sessionTable' => '{{%session}}',\n],"},
                {'n': 'CacheSession', 'd': 'Сессии в кэше: быстро, но при сбросе кэша всех разлогинит.', 'o': 'cache', 'c': "'session' => [\n    'class' => yii\\web\\CacheSession::class,\n    'cache' => 'redisCache',\n],"},
                {'n': 'Кэш схемы базы', 'd': 'Не про данные, а про структуру таблиц. Одна из самых заметных оптимизаций Active Record.', 'o': 'enableSchemaCache, schemaCacheDuration, schemaCache', 'c': "'db' => [\n    'enableSchemaCache' => !YII_DEBUG,\n    'schemaCacheDuration' => 3600,\n],\n// после миграций: ./yii cache/flush-schema"},
                {'n': 'Кэш фрагмента', 'd': 'Кусок готового HTML прямо в представлении.', 'o': 'duration, dependency, variations, enabled', 'c': "<?php if ($this->beginCache('menu', [\n    'duration' => 600,\n    'variations' => [Yii::$app->language],\n])) { ?>\n    …тяжёлый блок…\n<?php $this->endCache(); } ?>"},
                {'n': 'Кэш страницы', 'd': 'Фильтр, который отдаёт весь ответ из кэша, не заходя в действие.', 'o': 'yii\\filters\\PageCache', 'c': "['class' => yii\\filters\\PageCache::class,\n 'only' => ['index'],\n 'duration' => 60,\n 'variations' => [Yii::$app->language]],"},
                {'n': 'HTTP-кэш', 'd': 'Ответ 304 без тела, если у браузера уже свежая копия.', 'o': 'yii\\filters\\HttpCache: lastModified, etagSeed', 'c': "['class' => yii\\filters\\HttpCache::class,\n 'lastModified' => function () {\n     return Post::find()->max('updated_at');\n }],"},
            ]),
        ]),
        ('own', 'Рецепты', [
            ('h', 'Сброс кэша прямо из модели'),
            ('code', 'php', 'models/Post.php', r'''public function afterSave($insert, $changedAttributes)
{
    parent::afterSave($insert, $changedAttributes);
    TagDependency::invalidate(Yii::$app->cache, ['posts', 'post-' . $this->id]);
}

public function afterDelete()
{
    parent::afterDelete();
    TagDependency::invalidate(Yii::$app->cache, 'posts');
}'''),
            ('h', 'Несколько компонентов кэша под разные задачи'),
            ('code', 'php', 'config/web.php', r''''components' => [
    // общий, между серверами
    'cache' => [
        'class' => yii\redis\Cache::class,
        'keyPrefix' => 'shop',
    ],
    // локальный и очень быстрый, для мелочей внутри одного сервера
    'localCache' => [
        'class' => yii\caching\ApcCache::class,
    ],
],'''),
            ('h', 'Корзина в сессии'),
            ('code', 'php', 'components/Cart.php', r'''class Cart extends Component
{
    const KEY = 'cart';

    public function add($productId, $qty = 1)
    {
        $items = $this->all();
        $items[$productId] = ($items[$productId] ?? 0) + $qty;
        Yii::$app->session->set(self::KEY, $items);
    }

    public function all()
    {
        return Yii::$app->session->get(self::KEY, []);
    }

    public function clear()
    {
        Yii::$app->session->remove(self::KEY);
    }
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Кэшировали false',
             '`get()` возвращает `false` и при промахе, и когда вы сами сохранили `false`. Отличить нельзя. '
             'Оборачивайте такие значения в массив.'),
            ('note', 'trap', 'Один кэш на несколько приложений',
             'Без `keyPrefix` два приложения на одном Redis или memcached перезапишут ключи друг друга. Это выглядит как случайная порча данных.'),
            ('note', 'warn', 'Кэш страницы и персональные данные',
             'Забытый `variations` у `PageCache` приведёт к тому, что гость увидит страницу, собранную для вошедшего пользователя. '
             'Перечисляйте всё, что меняет вывод.'),
            ('note', 'trap', 'Файловые сессии на нескольких серверах',
             'Пользователь попадает на другой сервер и оказывается разлогинен. Лечится `DbSession`, `CacheSession` или закреплением сессии на балансировщике.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Хелперы

topic(
    id='helpers', group='object',
    title='Хелперы',
    cls='yii\\helpers',
    lead='Статические утилиты на каждый день: массивы, HTML, адреса, JSON, строки.',
    badge='13 классов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Каждый хелпер состоит из двух классов: `BaseArrayHelper` с логикой и тонкий `ArrayHelper`, который от него наследует. '
                  'Такое разделение сделано ровно для одного: чтобы вы могли подменить хелпер своим.'),
            ('code', 'php', 'components/ArrayHelper.php', r'''namespace app\helpers;

class ArrayHelper extends \yii\helpers\BaseArrayHelper
{
    public static function toSelect($models, $valueKey = 'id', $textKey = 'name')
    {
        return static::map($models, $valueKey, $textKey);
    }
}

// дальше просто импортируете свой класс вместо стандартного
use app\helpers\ArrayHelper;'''),
            ('note', 'tip', 'Подмена глобально, включая код фреймворка',
             'Если нужно, чтобы ваш вариант использовался и внутри Yii, зарегистрируйте его в карте классов до создания приложения: '
             '`Yii::$classMap[\'yii\\helpers\\Html\'] = \'@app/helpers/Html.php\';`'),
        ]),
        ('all', 'Все 13 хелперов', [
            ('ref', [
                {'n': 'ArrayHelper', 'd': 'Самый нужный. Достаёт значения по пути, строит карты для списков, сортирует, сливает конфигурации.', 'o': 'getValue, setValue, remove, keyExists, getColumn, map, index, merge, multisort, toArray, isAssociative, isIn, isSubset, htmlEncode, filter', 'c': "ArrayHelper::getValue($user, 'address.city', '—');\nArrayHelper::map($countries, 'code', 'name');\nArrayHelper::map($rows, 'id', 'name', 'group');\nArrayHelper::index($users, 'id');\nArrayHelper::getColumn($posts, 'id');\nArrayHelper::merge($base, $override);\nArrayHelper::multisort($data, ['age', 'name'],\n    [SORT_ASC, SORT_DESC]);"},
                {'n': 'Html', 'd': 'Генерация разметки с экранированием. Методы с приставкой active работают по модели и атрибуту.', 'o': 'encode, tag, a, img, ul, submitButton, beginForm, dropDownList, checkboxList, activeTextInput, activeLabel, error, errorSummary, addCssClass, addCssStyle, csrfMetaTags', 'c': "Html::encode($user->name);\nHtml::a('Профиль', ['user/view', 'id' => 42]);\nHtml::img('@web/logo.png', ['alt' => 'Логотип']);\nHtml::dropDownList('city', $selected, $items,\n    ['prompt' => '—']);\nHtml::addCssClass($options, 'is-active');\nHtml::activeTextInput($model, 'username');"},
                {'n': 'Url', 'd': 'Построение адресов по маршрутам, чтобы работали правила urlManager.', 'o': 'to, toRoute, current, home, base, canonical, remember, previous, isRelative', 'c': "Url::to(['post/view', 'id' => 1]);\nUrl::to(['post/view', 'id' => 1], true);   // абсолютный\nUrl::current(['page' => 2]);               // текущий + параметр\nUrl::current(['page' => null]);            // убрать параметр\nUrl::home();  Url::canonical();\nUrl::remember();  Url::previous();"},
                {'n': 'Json', 'd': 'Кодирование с учётом Arrayable и вставка кода JavaScript в настройки виджетов.', 'o': 'encode, decode, htmlEncode, errorSummary', 'c': "Json::encode($data);\nJson::decode($json);           // всегда массив\nJson::htmlEncode($data);       // безопасно внутри HTML\n\nJson::encode([\n    'onSelect' => new JsExpression('function (e) { … }'),\n]);"},
                {'n': 'StringHelper', 'd': 'Работа со строками, безопасная для многобайтовых кодировок.', 'o': 'byteLength, byteSubstr, truncate, truncateWords, startsWith, endsWith, explode, basename, dirname, mb_ucfirst, base64UrlEncode', 'c': "StringHelper::truncate($text, 120, '…');\nStringHelper::truncateWords($text, 20);\nStringHelper::startsWith($url, 'https://');\nStringHelper::explode('a, b, ,c', ',', true, true);\n// ['a', 'b', 'c'] — с обрезкой и без пустых"},
                {'n': 'Inflector', 'd': 'Превращения имён: множественное число, camelCase, адресные части.', 'o': 'pluralize, singularize, camelize, camel2id, id2camel, camel2words, humanize, slug, titleize, tableize, classify, ordinalize', 'c': "Inflector::slug('Привет, мир!');    // privet-mir\nInflector::pluralize('post');        // posts\nInflector::camel2id('PostTag');      // post-tag\nInflector::camel2words('createdAt'); // Created At"},
                {'n': 'FileHelper', 'd': 'Файлы и каталоги: поиск с фильтрами, копирование, определение типа.', 'o': 'findFiles, findDirectories, createDirectory, removeDirectory, copyDirectory, getMimeType, getExtensionsByMimeType, normalizePath, localize', 'c': "FileHelper::findFiles('@app/models', [\n    'only' => ['*.php'],\n    'except' => ['/tests/'],\n]);\nFileHelper::createDirectory('@runtime/export', 0775);\nFileHelper::getMimeType($path);"},
                {'n': 'VarDumper', 'd': 'Читаемый вывод любых структур, в отличие от var_dump справляется с объектами Yii.', 'o': 'dump, dumpAsString, export', 'c': "VarDumper::dump($model, 10, true);\n$text = VarDumper::dumpAsString($config);\n$php = VarDumper::export($array);   // готовый код"},
                {'n': 'Console', 'd': 'Цвета, прогресс и диалоги для консольных команд.', 'o': 'ansiFormat, stdout, prompt, confirm, select, startProgress, updateProgress, endProgress, wrapText', 'c': "$this->stdout(\"Готово\\n\", Console::FG_GREEN);\nConsole::startProgress(0, $total);\nConsole::updateProgress($done, $total);\nConsole::endProgress();"},
                {'n': 'Markdown', 'd': 'Разметка Markdown в HTML, в том числе вариант GitHub.', 'o': 'process, processParagraph', 'c': "echo Markdown::process($text, 'gfm');\necho Markdown::processParagraph($short);"},
                {'n': 'HtmlPurifier', 'd': 'Очистка чужого HTML от опасных конструкций. Медленно, поэтому результат кэшируют.', 'o': 'process($html, $config)', 'c': "echo HtmlPurifier::process($post->body, [\n    'HTML.Allowed' => 'p,b,i,a[href],ul,ol,li',\n]);"},
                {'n': 'FormatConverter', 'd': 'Перевод форматов дат между ICU, PHP и jQuery UI. Нужен, когда даты ходят между сервером и виджетом.', 'o': 'convertDateIcuToPhp, convertDatePhpToIcu, convertDateIcuToJui', 'c': "FormatConverter::convertDateIcuToPhp('dd.MM.yyyy');\n// 'd.m.Y'"},
                {'n': 'IpHelper', 'd': 'Разбор адресов и проверка вхождения в подсеть.', 'o': 'getIpVersion, inRange, expandIPv6, ip2bin', 'c': "IpHelper::inRange('192.168.1.7', '192.168.0.0/16');\nIpHelper::getIpVersion($ip);"},
            ]),
        ]),
        ('own', 'Что стоит помнить', [
            ('h', 'ArrayHelper::merge и особые значения'),
            ('code', 'php', None, r'''use yii\helpers\UnsetArrayValue;
use yii\helpers\ReplaceArrayValue;

$config = ArrayHelper::merge($base, [
    'components' => [
        // убрать ключ совсем
        'log' => new UnsetArrayValue(),
        // заменить массив целиком, а не слить поэлементно
        'urlManager' => new ReplaceArrayValue([
            'rules' => ['<c:\w+>/<a:\w+>' => '<c>/<a>'],
        ]),
    ],
]);'''),
            ('h', 'getValue умеет больше, чем кажется'),
            ('code', 'php', None, r'''ArrayHelper::getValue($user, 'address.street');       // вложенный путь
ArrayHelper::getValue($model, 'author.profile.city'); // и по объектам
ArrayHelper::getValue($arr, ['x', 'y']);              // если в ключе есть точка
ArrayHelper::getValue($user, function ($u) {          // вычисляемое значение
    return $u->first . ' ' . $u->last;
});'''),
            ('h', 'Html::addCssClass не плодит дубликаты'),
            ('code', 'php', None, r'''$options = ['class' => 'btn'];
Html::addCssClass($options, 'btn-primary');   // 'btn btn-primary'
Html::addCssClass($options, 'btn');           // ничего не изменится
Html::removeCssClass($options, 'btn-primary');

Html::addCssStyle($options, ['width' => '120px']);
Html::removeCssStyle($options, 'width');'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Url::to(["index"]) и ведущий слеш',
             'Без слеша маршрут считается относительно текущего контроллера, со слешем — от корня приложения. '
             'В модулях разница особенно заметна.'),
            ('note', 'trap', 'Json::decode всегда отдаёт массив',
             'Второй аргумент по умолчанию `true`. Если нужен объект, передайте `false`. '
             'И помните: при неверном JSON метод бросает исключение, а не возвращает null.'),
            ('note', 'warn', 'HtmlPurifier дорогой',
             'Каждый вызов разбирает и собирает HTML заново. Чистите при сохранении или кэшируйте результат, а не зовите в цикле вывода.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Фильтры

topic(
    id='filters', group='http',
    title='Фильтры',
    cls='behaviors() контроллера',
    lead='Поведения контроллера, которые оборачивают действия: доступ, методы, кэш, формат, CORS.',
    badge='12 встроенных',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Фильтр — это поведение, подписанное на события контроллера. '
                  'Возврат `false` из `beforeAction` отменяет действие, поэтому фильтры и умеют запрещать доступ.'),
            ('svg', '''<svg viewBox="0 0 740 190" role="img" aria-label="Фильтры выполняются вокруг действия: сначала beforeAction по порядку, затем действие, затем afterAction в обратном порядке" class="dg">
<defs><marker id="m-arr7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g class="dg-box dg-muted"><rect x="20" y="30" width="700" height="120" rx="10"/></g>
<g class="dg-box"><rect x="44" y="52" width="150" height="76" rx="8"/><text x="119" y="78">access</text><text x="119" y="96" class="dg-sub">кто вы</text></g>
<g class="dg-box"><rect x="212" y="52" width="150" height="76" rx="8"/><text x="287" y="78">verbs</text><text x="287" y="96" class="dg-sub">каким методом</text></g>
<g class="dg-box dg-live"><rect x="380" y="52" width="160" height="76" rx="8"/><text x="460" y="78">действие</text><text x="460" y="96" class="dg-sub">actionUpdate()</text></g>
<g class="dg-box"><rect x="558" y="52" width="138" height="76" rx="8"/><text x="627" y="78">pageCache</text><text x="627" y="96" class="dg-sub">и обратно</text></g>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr7)" opacity=".55">
<path d="M194 78h12"/><path d="M362 78h12"/><path d="M540 78h12"/>
<path d="M552 112H546"/><path d="M374 112h-6"/><path d="M206 112h-6"/>
</g>
<text x="370" y="172" class="dg-note" text-anchor="middle">beforeAction идёт слева направо, afterAction возвращается справа налево</text>
</svg>''', 'Порядок в behaviors() задаёт очередь: первый фильтр входит первым и выходит последним.'),
            ('code', 'php', 'controllers/PostController.php', r'''public function behaviors()
{
    return [
        'access' => [
            'class' => AccessControl::class,
            'only' => ['create', 'update', 'delete'],
            'rules' => [
                ['allow' => true, 'actions' => ['create'], 'roles' => ['@']],
                ['allow' => true, 'actions' => ['update', 'delete'],
                 'roles' => ['updatePost'],
                 'roleParams' => function () {
                     return ['post' => Post::findOne(Yii::$app->request->get('id'))];
                 }],
            ],
        ],
        'verbs' => [
            'class' => VerbFilter::class,
            'actions' => ['delete' => ['POST'], 'update' => ['POST', 'PUT']],
        ],
    ];
}'''),
        ]),
        ('all', 'Все 12 фильтров', [
            ('ref', [
                {'n': 'AccessControl', 'd': 'Простой контроль доступа по правилам. Проверка идёт сверху вниз до первого совпадения, а если не совпало ничего — доступ запрещён.', 'o': 'only, except, rules, denyCallback; в правиле: allow, actions, controllers, roles, roleParams, ips, verbs, matchCallback', 'c': "'access' => [\n    'class' => AccessControl::class,\n    'rules' => [\n        ['allow' => true, 'actions' => ['login'], 'roles' => ['?']],\n        ['allow' => true, 'roles' => ['@']],\n        ['allow' => true, 'ips' => ['10.0.*'], 'roles' => ['*']],\n    ],\n],"},
                {'n': 'VerbFilter', 'd': 'Разрешает действию только определённые HTTP-методы. Иначе — 405 и заголовок Allow.', 'o': 'actions', 'c': "'verbs' => [\n    'class' => VerbFilter::class,\n    'actions' => [\n        'index' => ['GET'],\n        'delete' => ['POST', 'DELETE'],\n    ],\n],"},
                {'n': 'ContentNegotiator', 'd': 'Выбирает формат ответа и язык по заголовкам Accept. Основа REST-контроллеров.', 'o': 'formats, languages, formatParam, languageParam', 'c': "'contentNegotiator' => [\n    'class' => ContentNegotiator::class,\n    'formats' => [\n        'application/json' => Response::FORMAT_JSON,\n        'application/xml' => Response::FORMAT_XML,\n    ],\n    'languages' => ['ru-RU', 'en-US'],\n],"},
                {'n': 'PageCache', 'd': 'Кэширует ответ целиком. При попадании действие вообще не выполняется.', 'o': 'only, duration, variations, dependency, cacheCookies, cacheHeaders', 'c': "['class' => PageCache::class,\n 'only' => ['index'],\n 'duration' => 60,\n 'variations' => [Yii::$app->language],\n 'dependency' => [\n     'class' => DbDependency::class,\n     'sql' => 'SELECT MAX(updated_at) FROM post',\n ]],"},
                {'n': 'HttpCache', 'd': 'Отвечает 304 без тела, если у клиента свежая копия. Экономит трафик и время генерации.', 'o': 'lastModified, etagSeed, cacheControlHeader, sessionCacheLimiter, weakEtag', 'c': "['class' => HttpCache::class,\n 'only' => ['view'],\n 'lastModified' => function ($action, $params) {\n     return Post::find()->max('updated_at');\n },\n 'cacheControlHeader' => 'public, max-age=300'],"},
                {'n': 'Cors', 'd': 'Заголовки кросс-доменных запросов и ответ на предварительный OPTIONS.', 'o': 'cors: Origin, Request-Method, Request-Headers, Allow-Credentials, Max-Age', 'c': "'corsFilter' => [\n    'class' => Cors::class,\n    'cors' => [\n        'Origin' => ['https://app.example.com'],\n        'Access-Control-Request-Method' => ['GET', 'POST'],\n        'Access-Control-Allow-Credentials' => true,\n        'Access-Control-Max-Age' => 3600,\n    ],\n],"},
                {'n': 'RateLimiter', 'd': 'Ограничение частоты запросов по алгоритму дырявого ведра. Включается сам, если identity реализует RateLimitInterface.', 'o': 'enableRateLimitHeaders, errorMessage', 'c': "// в модели User\npublic function getRateLimit($request, $action)\n{\n    return [100, 600];   // 100 запросов за 600 секунд\n}\npublic function loadAllowance($request, $action) { … }\npublic function saveAllowance($request, $action, $allowance, $ts) { … }"},
                {'n': 'AjaxFilter', 'd': 'Пропускает только AJAX-запросы. Для действий, которые не должны открываться в адресной строке.', 'o': 'errorMessage', 'c': "['class' => AjaxFilter::class,\n 'only' => ['suggest']],"},
                {'n': 'HttpBasicAuth', 'd': 'Логин и пароль в заголовке Authorization. По умолчанию логин трактуется как токен.', 'o': 'auth, realm', 'c': "'authenticator' => [\n    'class' => HttpBasicAuth::class,\n    'auth' => function ($username, $password) {\n        return User::findByLogin($username, $password);\n    },\n],"},
                {'n': 'HttpBearerAuth', 'd': 'Токен в заголовке Authorization: Bearer. Стандартный выбор для API.', 'o': 'realm', 'c': "'authenticator' => ['class' => HttpBearerAuth::class],\n\n// в модели\npublic static function findIdentityByAccessToken($token, $type = null)\n{\n    return static::findOne(['access_token' => $token]);\n}"},
                {'n': 'QueryParamAuth', 'd': 'Токен в параметре адреса. Удобно, но токен попадает в журналы сервера.', 'o': 'tokenParam', 'c': "'authenticator' => [\n    'class' => QueryParamAuth::class,\n    'tokenParam' => 'access-token',\n],"},
                {'n': 'CompositeAuth', 'd': 'Несколько способов аутентификации по очереди: побеждает первый успешный.', 'o': 'authMethods', 'c': "'authenticator' => [\n    'class' => CompositeAuth::class,\n    'authMethods' => [\n        HttpBearerAuth::class,\n        HttpBasicAuth::class,\n        QueryParamAuth::class,\n    ],\n    'except' => ['options'],\n],"},
            ]),
        ]),
        ('own', 'Свой фильтр', [
            ('code', 'php', 'filters/MaintenanceFilter.php', r'''namespace app\filters;

use Yii;
use yii\base\ActionFilter;
use yii\web\ServiceUnavailableHttpException;

class MaintenanceFilter extends ActionFilter
{
    /** @var string[] IP, которым можно даже во время работ */
    public $allowedIps = [];

    public function beforeAction($action)
    {
        if (!Yii::$app->params['maintenance']) {
            return true;
        }
        if (in_array(Yii::$app->request->userIP, $this->allowedIps, true)) {
            return true;
        }
        throw new ServiceUnavailableHttpException('Идут технические работы, вернитесь позже.');
    }

    public function afterAction($action, $result)
    {
        Yii::$app->response->headers->set('X-App-Version', Yii::$app->params['version']);
        return parent::afterAction($action, $result);
    }
}'''),
            ('h', 'Подключение: к контроллеру, модулю или всему приложению'),
            ('code', 'php', None, r'''// к контроллеру
public function behaviors()
{
    return [
        ['class' => MaintenanceFilter::class, 'allowedIps' => ['127.0.0.1']],
    ];
}

// ко всему модулю
class Module extends \yii\base\Module
{
    public function behaviors()
    {
        return [MaintenanceFilter::class];
    }
}

// ко всему приложению — через as в конфигурации
'as maintenance' => [
    'class' => app\filters\MaintenanceFilter::class,
    'allowedIps' => ['127.0.0.1'],
],'''),
            ('note', 'tip', 'only и except есть у любого фильтра',
             'Они достались от `ActionFilter`, поэтому работают и у своих фильтров тоже: '
             '`[\'class\' => MyFilter::class, \'only\' => [\'create\', \'update\']]`.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Правила доступа проверяются до первого совпадения',
             'Правило `[\'allow\' => true, \'roles\' => [\'@\']]` в начале списка перекроет все более точные правила ниже. Ставьте частные случаи выше общих.'),
            ('note', 'trap', 'Не совпало ни одно правило — это запрет',
             'Молчаливого разрешения нет. Если добавили `only`, а действие в него не попало, фильтр просто не применится; '
             'но если попало и не совпало ни одно правило, будет 403.'),
            ('note', 'warn', 'CORS и аутентификация',
             'Предварительный запрос OPTIONS приходит без заголовка авторизации. Добавьте `\'except\' => [\'options\']` аутентификатору, '
             'а фильтр `Cors` поставьте выше него в списке.'),
            ('note', 'trap', 'PageCache кэширует и токен CSRF',
             'Закэшированная страница с формой отдаст всем один и тот же токен, и отправка формы сломается. '
             'Не кэшируйте страницы с формами целиком, кэшируйте фрагменты.'),
        ]),
    ],
)



# --------------------------------------------------------------------------- Пользователь и доступ

topic(
    id='user', group='http',
    title='Пользователь и доступ',
    cls='yii\\web\\User',
    lead='Кто пришёл и что ему можно: компонент user, identity-класс, правила ACF и роли RBAC.',
    badge='31 настройка и правило',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Два разных вопроса и два разных механизма. **Аутентификация** отвечает «кто это» — '
                  'этим занят компонент `Yii::$app->user` и ваш identity-класс. **Авторизация** отвечает '
                  '«что ему можно» — это фильтр `AccessControl` для простых случаев и RBAC, когда прав много. '
                  'Проверка пароля остаётся вашим кодом, всё остальное — сессии, куки, тайм-ауты — берёт на себя фреймворк.'),
            ('svg', '''<svg viewBox="0 0 700 300" role="img" aria-label="Запрос опознаётся по сессии, куке автологина или токену, компонент user поднимает identity-класс, затем правила доступа решают, пускать ли к действию" class="dg">
<defs><marker id="m-us" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-us)" opacity=".55">
<path d="M118 76v26"/><path d="M350 76v26"/><path d="M582 76v26"/>
<path d="M350 162v24"/><path d="M350 246v22"/>
</g>
<g class="dg-box dg-muted"><rect x="14" y="14" width="208" height="62" rx="8"/><text x="118" y="38">сессия</text><text x="118" y="56" class="dg-sub">обычный вход, ID в сессии</text></g>
<g class="dg-box dg-muted"><rect x="246" y="14" width="208" height="62" rx="8"/><text x="350" y="38">кука автологина</text><text x="350" y="56" class="dg-sub">ID и authKey, «запомнить меня»</text></g>
<g class="dg-box dg-muted"><rect x="478" y="14" width="208" height="62" rx="8"/><text x="582" y="38">токен</text><text x="582" y="56" class="dg-sub">REST, сессии нет</text></g>
<g class="dg-box"><rect x="14" y="102" width="672" height="60" rx="8"/><text x="350" y="124">Yii::$app-&gt;user</text><text x="350" y="142" class="dg-sub">findIdentity · validateAuthKey · findIdentityByAccessToken</text></g>
<g class="dg-box dg-live"><rect x="150" y="186" width="400" height="60" rx="8"/><text x="350" y="208">правила доступа</text><text x="350" y="226" class="dg-sub">AccessControl · can() · RBAC</text></g>
<g class="dg-box dg-muted"><rect x="250" y="268" width="200" height="32" rx="8"/><text x="350" y="289">действие</text></g>
</svg>''', 'Три входа, одна точка опознания и одна точка решения. Пароль проверяется до всего этого — в вашем коде.'),
            ('h', 'Настройка компонента'),
            ('code', 'php', 'config/web.php', r''''user' => [
    'identityClass' => app\models\User::class,
    'enableAutoLogin' => true,        // «запомнить меня» через куку
    'loginUrl' => ['site/login'],     // куда отправлять гостей
    'authTimeout' => 3600,            // выход после часа бездействия
    'absoluteAuthTimeout' => 86400,   // выход через сутки в любом случае
    // 'enableSession' => false,      // для REST: только токен, без сессии
],'''),
            ('h', 'Пять методов identity-класса'),
            ('kv', [
                ('findIdentity($id)', 'Найти пользователя по ID. Вызывается при каждом запросе с сессией.'),
                ('findIdentityByAccessToken($token, $type)', 'Найти по токену — для REST. `$type` это класс аутентификатора.'),
                ('getId()', 'Уникальный ID, который кладётся в сессию.'),
                ('getAuthKey()', 'Секрет для куки автологина. Хранится в базе, генерируется при регистрации.'),
                ('validateAuthKey($key)', 'Сверка ключа из куки с тем, что в базе.'),
            ]),
            ('p', 'Identity не обязан быть Active Record: подойдёт любой класс — LDAP, внешний API, массив в конфигурации.'),
            ('note', 'tip', 'Порядок при входе',
             'Сначала ваш код проверяет пароль через `Yii::$app->security->validatePassword()`, и только потом '
             'вызывается `Yii::$app->user->login($identity, $duration)`. Фреймворк пароли не проверяет.'),
        ]),
        ('all', 'Настройки и правила', [
            ('h', 'Компонент user'),
            ('ref', [
                {'n': 'identityClass', 'd': 'Класс, реализующий IdentityInterface. Без него компонент не работает.', 'o': 'обычно модель User', 'c': "'user' => [\n    'identityClass' => app\\models\\User::class,\n],"},
                {'n': 'enableAutoLogin', 'd': 'Разрешает вход по куке. Без него параметр $duration у login() не сработает.', 'o': 'по умолчанию false', 'c': "'enableAutoLogin' => true,\n\n// и при входе:\nYii::$app->user->login($identity, 3600 * 24 * 30);"},
                {'n': 'loginUrl', 'd': 'Куда отправлять гостя, которому нужен вход. null — сразу 403 вместо редиректа.', 'o': 'маршрут массивом', 'c': "'loginUrl' => ['site/login'],"},
                {'n': 'authTimeout', 'd': 'Выход после N секунд бездействия. Отсчёт продлевается каждым запросом.', 'o': 'null — пока жива сессия', 'c': "'authTimeout' => 3600,"},
                {'n': 'absoluteAuthTimeout', 'd': 'Выход через N секунд после входа, сколько бы человек ни работал.', 'o': 'считается от момента входа', 'c': "'absoluteAuthTimeout' => 86400,"},
                {'n': 'enableSession', 'd': 'Выключается для REST: пользователь опознаётся по токену на каждом запросе, состояние не хранится.', 'o': 'при false куки и сессия не используются', 'c': "'user' => [\n    'identityClass' => app\\models\\User::class,\n    'enableSession' => false,\n],"},
                {'n': 'login($identity, $duration)', 'd': 'Вход. При $duration больше нуля и включённом enableAutoLogin ставится кука с ID и authKey.', 'o': 'вызывается после вашей проверки пароля', 'c': "if ($this->validate()) {\n    return Yii::$app->user->login(\n        $this->getUser(),\n        $this->rememberMe ? 3600 * 24 * 30 : 0\n    );\n}"},
                {'n': 'logout($destroySession)', 'd': 'Выход. По умолчанию уничтожает сессию целиком; logout(false) оставляет её.', 'o': 'куку автологина удаляет в обоих случаях', 'c': "Yii::$app->user->logout();\nreturn $this->goHome();"},
                {'n': 'isGuest · id · identity', 'd': 'Текущий пользователь. identity поднимается лениво: findIdentity() вызовется только при обращении.', 'o': 'id и identity равны null у гостя', 'c': "if (Yii::$app->user->isGuest) { /* гость */ }\n\n$id = Yii::$app->user->id;\n$name = Yii::$app->user->identity->username;"},
                {'n': 'loginRequired()', 'd': 'Отправить гостя на loginUrl, запомнив, куда он шёл. Для AJAX-запроса вместо редиректа бросает 403.', 'o': 'то же делает AccessControl', 'c': "if (Yii::$app->user->isGuest) {\n    return Yii::$app->user->loginRequired();\n}"},
                {'n': 'getReturnUrl() · setReturnUrl()', 'd': 'Адрес, куда вернуть после входа. goBack() в контроллере уводит именно туда.', 'o': 'хранится в сессии', 'c': "Yii::$app->user->setReturnUrl(['post/view', 'id' => 7]);\n\n// после успешного входа\nreturn $this->goBack();"},
                {'n': 'switchIdentity()', 'd': 'Сменить пользователя на лету, не проходя вход заново. Основа режима «войти как».', 'o': 'второй аргумент — срок куки', 'c': "Yii::$app->user->switchIdentity($other, 0);"},
                {'n': 'События входа и выхода', 'd': 'beforeLogin можно отменить, выставив $event->isValid = false. В событии есть identity, cookieBased и duration.', 'o': 'beforeLogin, afterLogin, beforeLogout, afterLogout', 'c': "'user' => [\n    'on afterLogin' => function (yii\\web\\UserEvent $e) {\n        $e->identity->updateAttributes(['last_login_at' => time()]);\n    },\n],"},
            ]),
            ('h', 'Правила AccessControl'),
            ('p', 'Правила проверяются сверху вниз до первого совпадения. Совпало `allow` — пропустить, `deny` — запретить. '
                  'Не совпало ни одно — **запретить**: гостя отправят на вход, вошедшего встретит 403.'),
            ('ref', [
                {'n': 'allow', 'd': 'true — разрешающее правило, false — запрещающее.', 'o': 'обязательный ключ', 'c': "['allow' => true, 'roles' => ['@']],"},
                {'n': 'actions', 'd': 'ID действий, к которым правило относится. Пусто — ко всем.', 'o': 'имена без префикса action', 'c': "['allow' => true, 'actions' => ['login', 'signup'], 'roles' => ['?']],"},
                {'n': 'controllers', 'd': 'ID контроллеров. Контроллер из модуля пишется вместе с ним.', 'o': "например 'admin/user'", 'c': "['allow' => false, 'controllers' => ['admin/user'], 'roles' => ['?']],"},
                {'n': 'roles', 'd': 'Знак ? — гость, @ — любой вошедший. Всё остальное считается ролью или разрешением RBAC и проверяется через can().', 'o': 'можно перечислить несколько', 'c': "['allow' => true, 'actions' => ['update'], 'roles' => ['moderator', 'admin']],"},
                {'n': 'roleParams', 'd': 'Параметры для can(). Замыкание удобно тем, что модель грузится только когда правило действительно проверяется.', 'o': 'массив или замыкание', 'c': "[\n    'allow' => true,\n    'actions' => ['update'],\n    'roles' => ['updatePost'],\n    'roleParams' => function ($rule) {\n        return ['post' => Post::findOne(Yii::$app->request->get('id'))];\n    },\n],"},
                {'n': 'ips', 'd': 'IP клиента. В конце допускается звёздочка.', 'o': "например '192.168.*'", 'c': "['allow' => true, 'ips' => ['192.168.*'], 'actions' => ['debug']],"},
                {'n': 'verbs', 'd': 'HTTP-методы, на которые распространяется правило.', 'o': 'GET, POST, PUT, DELETE', 'c': "['allow' => false, 'verbs' => ['DELETE'], 'roles' => ['@']],"},
                {'n': 'matchCallback', 'd': 'Произвольное условие: возвращает true, если правило подходит.', 'o': 'function ($rule, $action)', 'c': "[\n    'allow' => true,\n    'actions' => ['promo'],\n    'matchCallback' => function ($rule, $action) {\n        return date('d-m') === '31-10';\n    },\n],"},
                {'n': 'denyCallback', 'd': 'Что делать при запрете. Задаётся у правила или у всего фильтра.', 'o': 'по умолчанию редирект или 403', 'c': "'denyCallback' => function ($rule, $action) {\n    throw new yii\\web\\ForbiddenHttpException('Вам сюда нельзя');\n},"},
            ]),
            ('h', 'RBAC'),
            ('p', 'Три сущности: **разрешение** — конкретное действие, **роль** — набор разрешений и других ролей, '
                  '**правило** — дополнительная проверка с параметрами. Пользователю назначаются роли, проверка одна: `can()`.'),
            ('ref', [
                {'n': 'authManager', 'd': 'DbManager хранит иерархию в четырёх таблицах, PhpManager — в файлах. Компонент нужен в обеих конфигурациях, и веб, и консольной.', 'o': 'таблицы: auth_item, auth_item_child, auth_assignment, auth_rule', 'c': "'authManager' => [\n    'class' => yii\\rbac\\DbManager::class,\n    'cache' => 'cache',\n],\n\n// ./yii migrate --migrationPath=@yii/rbac/migrations"},
                {'n': 'createPermission() и add()', 'd': 'Создать разрешение — самую мелкую единицу доступа — и положить его в хранилище.', 'o': 'description виден в интерфейсах управления', 'c': "$auth = Yii::$app->authManager;\n\n$createPost = $auth->createPermission('createPost');\n$createPost->description = 'Создание постов';\n$auth->add($createPost);"},
                {'n': 'createRole() и add()', 'd': 'Создать роль. Сама по себе она ничего не даёт, пока к ней не привязаны разрешения.', 'o': 'имя роли уникально в пределах хранилища', 'c': "$author = $auth->createRole('author');\n$auth->add($author);"},
                {'n': 'addChild()', 'd': 'Собрать иерархию: роли — разрешения, ролям — другие роли. Проверка идёт по всей цепочке вниз.', 'o': 'циклы не допускаются', 'c': "$auth->addChild($author, $createPost);\n$auth->addChild($admin, $updatePost);\n$auth->addChild($admin, $author);   // admin получает всё от author"},
                {'n': 'Rule и ruleName', 'd': 'Правило решает по данным: например, автор ли пользователь этого поста. Привязывается к разрешению по имени.', 'o': 'execute($user, $item, $params)', 'c': "class AuthorRule extends yii\\rbac\\Rule\n{\n    public $name = 'isAuthor';\n\n    public function execute($user, $item, $params)\n    {\n        return isset($params['post'])\n            ? $params['post']->createdBy == $user\n            : false;\n    }\n}"},
                {'n': 'assign() · revoke() · revokeAll()', 'd': 'Назначение и снятие ролей. Обычно назначают при регистрации.', 'o': 'второй аргумент — ID пользователя', 'c': "$auth->assign($auth->getRole('author'), $user->id);\n$auth->revoke($role, $userId);\n$auth->revokeAll($userId);"},
                {'n': 'getRolesByUser() и соседи', 'd': 'Чтение назначений: роли пользователя, все его разрешения, все пользователи роли.', 'o': 'getRolesByUser, getPermissionsByUser, getUserIdsByRole', 'c': "$roles = $auth->getRolesByUser($userId);\n$perms = $auth->getPermissionsByUser($userId);\n$ids = $auth->getUserIdsByRole('admin');"},
                {'n': 'can() и checkAccess()', 'd': 'Проверка. can() — для текущего пользователя, checkAccess() — для любого ID.', 'o': 'второй аргумент уходит в правило', 'c': "if (Yii::$app->user->can('updatePost', ['post' => $post])) { }\n\nif ($auth->checkAccess($userId, 'updatePost', ['post' => $post])) { }"},
                {'n': 'defaultRoles', 'd': 'Роли, которые есть у всех без записи в таблице назначений. Обычно сочетаются с правилом, определяющим роль по полю пользователя.', 'o': 'для гостя can() проверяет только их', 'c': "'authManager' => [\n    'class' => yii\\rbac\\DbManager::class,\n    'defaultRoles' => ['guest'],\n],"},
            ]),
        ]),
        ('own', 'Приёмы', [
            ('h', 'Свой identity-класс'),
            ('code', 'php', 'models/User.php', r'''namespace app\models;

use Yii;
use yii\db\ActiveRecord;
use yii\web\IdentityInterface;

class User extends ActiveRecord implements IdentityInterface
{
    public static function findIdentity($id)
    {
        return static::findOne($id);
    }

    public static function findIdentityByAccessToken($token, $type = null)
    {
        return static::findOne(['access_token' => $token]);
    }

    public function getId() { return $this->id; }

    public function getAuthKey() { return $this->auth_key; }

    public function validateAuthKey($authKey)
    {
        return $this->getAuthKey() === $authKey;
    }

    // проверка пароля — ваш код, не фреймворка
    public function validatePassword($password)
    {
        return Yii::$app->security->validatePassword($password, $this->password_hash);
    }

    public function beforeSave($insert)
    {
        if (!parent::beforeSave($insert)) {
            return false;
        }
        if ($this->isNewRecord) {
            $this->auth_key = Yii::$app->security->generateRandomString();
        }
        return true;
    }
}'''),
            ('h', 'Вход и выход'),
            ('code', 'php', 'controllers/SiteController.php', r'''public function actionLogin()
{
    if (!Yii::$app->user->isGuest) {
        return $this->goHome();
    }

    $model = new LoginForm();
    if ($model->load(Yii::$app->request->post()) && $model->login()) {
        return $this->goBack();   // на returnUrl или домой
    }

    return $this->render('login', ['model' => $model]);
}

public function actionLogout()
{
    Yii::$app->user->logout();
    return $this->goHome();
}'''),
            ('h', 'Доступ только для вошедших'),
            ('code', 'php', 'controllers/PostController.php', r'''public function behaviors()
{
    return [
        'access' => [
            'class' => yii\filters\AccessControl::class,
            'only' => ['create', 'update', 'delete'],
            'rules' => [
                ['allow' => true, 'roles' => ['@']],
            ],
        ],
    ];
}'''),
            ('h', 'Своё правило RBAC: автор правит свой пост'),
            ('code', 'php', 'commands/RbacController.php', r'''$rule = new app\rbac\AuthorRule();
$auth->add($rule);

$updateOwnPost = $auth->createPermission('updateOwnPost');
$updateOwnPost->description = 'Редактирование своего поста';
$updateOwnPost->ruleName = $rule->name;
$auth->add($updateOwnPost);

$auth->addChild($updateOwnPost, $updatePost);
$auth->addChild($author, $updateOwnPost);'''),
            ('p', 'Для автора цепочка `author → updateOwnPost (правило) → updatePost`, и правило сверит `createdBy`. '
                  'Для администратора путь короче — `admin → updatePost`, без правила, то есть можно всегда.'),
            ('note', 'tip', 'Проверка в представлении',
             'Тот же `can()` уместен в шаблоне, чтобы не рисовать кнопку, которая всё равно упрётся в 403: '
             '`<?php if (Yii::$app->user->can(\'updatePost\', [\'post\' => $model])): ?>`'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Постоянный authKey',
             '`getAuthKey()` — фактически второй пароль, лежащий в куке. Возвращать оттуда константу или что-то '
             'производное от ID нельзя: подделав куку, войдут кем угодно. Генерируйте `generateRandomString()` '
             'и меняйте ключ при смене пароля и выходе со всех устройств.'),
            ('note', 'trap', 'Ни одно правило ACF не совпало',
             'Это запрет, а не разрешение. Частая ошибка — описать только запрещающие правила и ждать, '
             'что остальное откроется: закроется всё.'),
            ('note', 'trap', 'authManager только в веб-конфигурации',
             'Консольная команда, которая строит иерархию RBAC, запускается с `config/console.php`. '
             'Если компонент описан только в `web.php`, `./yii rbac/init` упадёт.'),
            ('note', 'warn', 'roleParams массивом вместо замыкания',
             'Массив вычисляется всегда, даже когда до этого правила дело не доходит. Замыкание грузит модель '
             'только при реальной проверке — на списках с десятками кнопок разница заметна.'),
            ('note', 'warn', 'can() для гостя',
             'У гостя `user->id` равен null, поэтому `can()` проверит только `defaultRoles` и обычно вернёт false. '
             'Отличать «не вошёл» от «вошёл, но нельзя» нужно через `isGuest`.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Маршруты

topic(
    id='routing', group='http',
    title='Маршруты и URL',
    cls='yii\\web\\UrlManager',
    lead='Как адрес превращается в контроллер с действием и как из маршрута собирается обратно красивый адрес.',
    badge='9 видов правил',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Маршрут — строка вида `модуль/контроллер/действие`. Компонент `urlManager` работает в обе стороны: '
                  '**разбирает** входящий адрес в маршрут с параметрами и **собирает** адрес обратно, когда вы зовёте `Url::to()`. '
                  'Поэтому менять схему адресов можно в одном месте, не трогая шаблоны.'),
            ('svg', '''<svg viewBox="0 0 760 236" role="img" aria-label="urlManager разбирает адрес в маршрут и собирает адрес обратно из маршрута" class="dg">
<defs><marker id="m-arr8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr8)" opacity=".55">
<path d="M242 56h60"/><path d="M458 56h60"/>
<path d="M518 170h-60"/><path d="M302 170h-60"/>
</g>
<g class="dg-box"><rect x="22" y="30" width="220" height="52" rx="8"/><text x="132" y="52">/post/7?src=ad</text><text x="132" y="69" class="dg-sub">адрес из браузера</text></g>
<g class="dg-box dg-live"><rect x="302" y="24" width="156" height="128" rx="10"/><text x="380" y="52">urlManager</text><text x="380" y="70" class="dg-sub">rules</text><text x="380" y="104" class="dg-sub">enablePrettyUrl</text><text x="380" y="122" class="dg-sub">suffix, defaults</text></g>
<g class="dg-box"><rect x="518" y="30" width="220" height="52" rx="8"/><text x="628" y="52">post/view, id=7</text><text x="628" y="69" class="dg-sub">маршрут и параметры</text></g>
<g class="dg-box"><rect x="518" y="144" width="220" height="52" rx="8"/><text x="628" y="166">Url::to([...])</text><text x="628" y="183" class="dg-sub">маршрут в коде</text></g>
<g class="dg-box"><rect x="22" y="144" width="220" height="52" rx="8"/><text x="132" y="166">/post/7</text><text x="132" y="183" class="dg-sub">адрес в ссылке</text></g>
<text x="380" y="216" class="dg-note" text-anchor="middle">одни и те же правила работают в обе стороны</text>
</svg>''', 'Разбор и сборка адресов идут через один набор правил, поэтому ссылки не ломаются при смене схемы.'),
            ('h', 'Включить красивые адреса'),
            ('code', 'php', 'config/web.php', r''''urlManager' => [
    'enablePrettyUrl' => true,      // без ?r=post/view
    'showScriptName' => false,      // без index.php в адресе
    'enableStrictParsing' => false, // true — принимать только описанные адреса
    'rules' => [
        'post/<id:\d+>' => 'post/view',
    ],
],'''),
            ('p', 'Для `showScriptName => false` веб-сервер должен направлять все запросы на `index.php`. '
                  'В nginx это `try_files $uri $uri/ /index.php?$args`, в Apache — правило `mod_rewrite` из шаблона приложения.'),
            ('h', 'Куда ведёт маршрут'),
            ('kv', [
                ('post/view', '`PostController::actionView()`'),
                ('post-tag/view-all', '`PostTagController::actionViewAll()` — имена переводятся из CamelCase в дефисы'),
                ('admin/user/index', '`UserController` внутри модуля `admin`'),
                ('site/index', 'маршрут по умолчанию, задаётся свойством `defaultRoute`'),
                ('пустой маршрут', 'берётся `defaultRoute` приложения, обычно `site/index`'),
            ]),
        ]),
        ('all', 'Все виды правил', [
            ('p', 'Правило — пара «шаблон адреса ⇒ маршрут». Порядок важен: побеждает первое подошедшее, '
                  'поэтому частные случаи пишут выше общих.'),
            ('ref', [
                {'n': 'Простое соответствие', 'd': 'Фиксированный адрес ведёт на фиксированный маршрут. Самый предсказуемый вид.', 'o': 'шаблон ⇒ маршрут', 'c': "'rules' => [\n    '' => 'site/index',\n    'about' => 'site/about',\n    'login' => 'site/login',\n],"},
                {'n': 'Параметры в адресе', 'd': 'Часть адреса становится параметром действия. Имя в угловых скобках совпадает с именем аргумента метода.', 'o': '&lt;имя&gt;', 'c': "'post/<id>' => 'post/view',\n// → actionView($id)\n\n'<controller>/<action>' => '<controller>/<action>',"},
                {'n': 'Ограничение регулярным выражением', 'd': 'Второй частью задаётся, что именно считать параметром. Без него в id попадёт что угодно.', 'o': '&lt;имя:выражение&gt;', 'c': "'post/<id:\\d+>' => 'post/view',\n'post/<slug:[\\w-]+>' => 'post/view-by-slug',\n'<lang:(ru|en)>/<controller:\\w+>' => '<controller>/index',"},
                {'n': 'Значения по умолчанию', 'd': 'Делает параметр необязательным: адрес без него тоже подойдёт.', 'o': 'defaults', 'c': "[\n    'pattern' => 'posts/<page:\\d+>/<tag>',\n    'route' => 'post/index',\n    'defaults' => ['page' => 1, 'tag' => ''],\n],\n// подойдут /posts, /posts/2, /posts/2/news"},
                {'n': 'HTTP-методы', 'd': 'Одно и то же имя адреса ведёт на разные действия в зависимости от метода. Основа REST-маршрутов.', 'o': 'метод перед шаблоном, через запятую', 'c': "'POST users' => 'user/create',\n'PUT,PATCH users/<id:\\d+>' => 'user/update',\n'DELETE users/<id:\\d+>' => 'user/delete',"},
                {'n': 'Суффикс', 'd': 'Добавляет окончание ко всем адресам или к одному правилу. Исторический приём для «статичных» адресов.', 'o': 'suffix у менеджера или у правила', 'c': "'urlManager' => [\n    'suffix' => '.html',\n    'rules' => [\n        ['pattern' => 'feed', 'route' => 'site/feed',\n         'suffix' => '.xml'],\n    ],\n],"},
                {'n': 'Поддомены', 'd': 'Правило с хостом в шаблоне: часть адреса берётся из домена.', 'o': 'абсолютный шаблон с http:// или //', 'c': "'http://<shop:\\w+>.example.com/<action>' => 'shop/<action>',\n// magazin.example.com/cart → shop/cart, shop=magazin"},
                {'n': 'Именованные правила и Url::to', 'd': 'Правилу можно дать имя и строить по нему адрес, не повторяя параметры.', 'o': 'name у правила', 'c': "['pattern' => 'post/<id:\\d+>', 'route' => 'post/view',\n 'name' => 'post-view'],\n\nUrl::to(['post/view', 'id' => 7]);"},
                {'n': 'yii\\rest\\UrlRule', 'd': 'Разворачивается в целый набор правил для контроллера REST: index, view, create, update, delete, options.', 'o': 'controller, prefix, pluralize, only, except, extraPatterns, tokens', 'c': "['class' => yii\\rest\\UrlRule::class,\n 'controller' => ['v1/user', 'v1/post'],\n 'prefix' => 'api',\n 'except' => ['delete'],\n 'extraPatterns' => [\n     'GET search' => 'search',\n ]],"},
            ]),
            ('h', 'Настройки самого менеджера'),
            ('kv', [
                ('enablePrettyUrl', 'человекочитаемые адреса вместо `?r=маршрут`'),
                ('showScriptName', '`false` убирает `index.php` из адреса'),
                ('enableStrictParsing', '`true` — принимать только адреса, описанные правилами; всё остальное 404'),
                ('suffix', 'общее окончание для всех адресов'),
                ('baseUrl, hostInfo', 'база для абсолютных адресов; в консоли задаются вручную'),
                ('cache', 'кэш скомпилированных правил; по умолчанию компонент `cache`'),
                ('normalizer', 'приведение адресов: убрать двойные слеши, решить судьбу завершающего слеша'),
                ('ruleConfig', 'настройки по умолчанию для всех правил'),
            ]),
        ]),
        ('own', 'Своё правило', [
            ('p', 'Когда адрес нельзя описать шаблоном — например, часть пути берётся из базы — пишут класс правила.'),
            ('code', 'php', 'components/CategoryUrlRule.php', r'''namespace app\components;

use yii\web\UrlRuleInterface;
use yii\base\BaseObject;

class CategoryUrlRule extends BaseObject implements UrlRuleInterface
{
    // адрес → маршрут
    public function parseRequest($manager, $request)
    {
        $path = $request->getPathInfo();

        if (preg_match('%^catalog/([\w-]+)$%', $path, $m)) {
            $category = Category::findOne(['slug' => $m[1]]);
            if ($category === null) {
                return false;          // правило не подошло
            }
            return ['catalog/index', ['id' => $category->id]];
        }

        return false;
    }

    // маршрут → адрес
    public function createUrl($manager, $route, $params)
    {
        if ($route === 'catalog/index' && isset($params['id'])) {
            $category = Category::findOne($params['id']);
            if ($category !== null) {
                return 'catalog/' . $category->slug;
            }
        }

        return false;                  // пусть попробуют другие правила
    }
}'''),
            ('code', 'php', 'config/web.php', r''''urlManager' => [
    'enablePrettyUrl' => true,
    'showScriptName' => false,
    'rules' => [
        ['class' => app\components\CategoryUrlRule::class],
        'post/<id:\d+>' => 'post/view',
    ],
],'''),
            ('note', 'tip', 'Кэшируйте обращения к базе',
             'Правило вызывается на каждом запросе, а `createUrl` — ещё и на каждой ссылке в списке. '
             'Держите соответствие «адресная часть ⇒ идентификатор» в кэше, иначе страница со списком категорий даст десятки запросов.'),
            ('h', 'Сборка адресов в коде'),
            ('code', 'php', None, r'''Url::to(['post/view', 'id' => 7]);           // /post/7
Url::to(['post/view', 'id' => 7], true);     // https://host/post/7
Url::to(['/site/index']);                     // от корня приложения
Url::to(['index']);                           // относительно текущего контроллера
Url::current(['page' => 2]);                  // текущий адрес с заменой параметра
Url::current(['page' => null]);               // и с удалением

Html::a('Пост', ['post/view', 'id' => 7]);
$this->redirect(['post/view', 'id' => 7]);'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Порядок правил решает всё',
             'Правило `<controller>/<action>` в начале списка перехватит всё и более точные правила ниже никогда не сработают. '
             'Общие шаблоны всегда последними.'),
            ('note', 'trap', 'Лишние параметры уходят в строку запроса',
             '`Url::to([\'post/view\', \'id\' => 7, \'src\' => \'ad\'])` при правиле `post/<id:\\d+>` даст `/post/7?src=ad`. '
             'Это не ошибка, но неожиданность, если вы ждали чистый адрес.'),
            ('note', 'trap', 'В консоли адреса другие',
             'У консольного приложения нет запроса, поэтому `Url::to([...], true)` соберёт адрес без домена. '
             'Задайте `hostInfo` и `baseUrl` у `urlManager` в консольной конфигурации, иначе ссылки в письмах из cron будут битыми.'),
            ('note', 'warn', 'enableStrictParsing выключен по умолчанию',
             'Поэтому адрес `/post/view?id=7` работает даже при описанном правиле `post/<id:\\d+>`, и одна страница доступна по двум адресам. '
             'Для API и для SEO это стоит включить.'),
        ]),
    ],
)



# --------------------------------------------------------------------------- Представления и ресурсы

topic(
    id='views', group='view',
    title='Представления и ресурсы',
    cls='yii\\web\\View',
    lead='Как собирается страница: шаблон, представление, блоки — и как в неё попадают стили и скрипты.',
    badge='33 метода и настройки',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Представление — обычный PHP-файл с разметкой, в котором `$this` это компонент `View`. '
                  'Контроллер зовёт `render()`, результат подставляется в шаблон вместо `$content` и уходит в ответ. '
                  'Стили и скрипты страница не пишет тегами руками: она **регистрирует** их у того же `View`, '
                  'а шаблон расставляет их в пяти служебных точках.'),
            ('svg', '''<svg viewBox="0 0 700 332" role="img" aria-label="Контроллер рендерит представление, оно подставляется в шаблон вместо content, а зарегистрированные представлением ресурсы и пакеты попадают в шаблон и оттуда на страницу" class="dg">
<defs><marker id="m-vw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-vw)" opacity=".55">
<path d="M164 64v20"/><path d="M164 152v20"/><path d="M164 240v20"/>
<path d="M318 121h62"/><path d="M536 176v33H320"/>
</g>
<g class="dg-box"><rect x="14" y="14" width="300" height="50" rx="8"/><text x="164" y="36">контроллер</text><text x="164" y="53" class="dg-sub">render('view', $params)</text></g>
<g class="dg-box dg-live"><rect x="14" y="90" width="300" height="62" rx="8"/><text x="164" y="112">представление</text><text x="164" y="130" class="dg-sub">разметка, блоки</text><text x="164" y="146" class="dg-sub">registerJs · registerCss</text></g>
<g class="dg-box"><rect x="14" y="178" width="300" height="62" rx="8"/><text x="164" y="200">шаблон</text><text x="164" y="218" class="dg-sub">$content вместо страницы</text><text x="164" y="234" class="dg-sub">head() · beginBody() · endBody()</text></g>
<g class="dg-box dg-muted"><rect x="14" y="266" width="300" height="50" rx="8"/><text x="164" y="288">готовая страница</text><text x="164" y="305" class="dg-sub">теги link и script на своих местах</text></g>
<g class="dg-box"><rect x="386" y="90" width="300" height="86" rx="8"/><text x="536" y="118">зарегистрированные ресурсы</text><text x="536" y="139" class="dg-sub">registerJs · registerCss · registerMetaTag</text><text x="536" y="157" class="dg-sub">AssetBundle: js, css, depends</text></g>
</svg>''', 'Регистрация и вывод разнесены: страница говорит, что ей нужно, шаблон — куда это поставить.'),
            ('h', 'Как рендерить'),
            ('kv', [
                ('$this->render(...)', 'В контроллере: представление плюс шаблон. Обычный случай.'),
                ('$this->renderPartial(...)', 'Без шаблона — фрагменты и вставки.'),
                ('$this->renderAjax(...)', 'Без шаблона, но с зарегистрированными скриптами и стилями — для подгрузки модалок.'),
                ('$this->renderFile(...)', 'По пути или псевдониму. Работает и из письма, и из консоли.'),
            ]),
            ('h', 'Как разрешается имя'),
            ('kv', [
                ('about', 'В папке контекста: `@app/views/site/about.php` для `SiteController`.'),
                ('_item', 'Рядом с текущим файлом — если вызвано из представления.'),
                ('/site/about', 'От папки представлений текущего модуля или приложения.'),
                ('//site/about', 'Всегда `@app/views/site/about.php`, минуя модуль.'),
                ('@app/views/site/about', 'Псевдоним как есть. Расширение `.php` можно не писать.'),
            ]),
            ('h', 'Минимальный шаблон'),
            ('code', 'php', 'views/layouts/main.php', r'''<?php
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
    <?= $content ?>
<?php $this->endBody() ?>
</body>
</html>
<?php $this->endPage() ?>'''),
            ('note', 'trap', 'Пять вызовов обязательны',
             '`beginPage` и `endPage` оборачивают страницу, `head()` — место для мета-тегов и стилей, '
             '`beginBody` и `endBody` — для скриптов в начале и конце тела. Уберёте любой — '
             'зарегистрированные ресурсы просто не появятся, и никакой ошибки при этом не будет.'),
        ]),
        ('all', 'Методы и пакеты', [
            ('h', 'Сборка страницы'),
            ('ref', [
                {'n': 'render()', 'd': 'Представление плюс шаблон. Массив во втором аргументе превращается в переменные.', 'o': 'внутри представления ищет файл рядом', 'c': "return $this->render('report', [\n    'model' => $model,\n    'rows' => $rows,\n]);"},
                {'n': 'renderPartial()', 'd': 'Без шаблона. Для фрагментов, которые встраиваются в другую страницу.', 'o': 'зарегистрированные скрипты не выводит', 'c': "return $this->renderPartial('_row', ['item' => $item]);"},
                {'n': 'renderAjax()', 'd': 'Без шаблона, но со скриптами и стилями. Нужен, когда фрагмент содержит виджеты и подгружается по AJAX.', 'o': 'разница с renderPartial только в этом', 'c': "return $this->renderAjax('_form', ['model' => $model]);"},
                {'n': 'renderFile()', 'd': 'Рендер по пути или псевдониму, без правил поиска. Отсюда рендерят письма и консольный вывод.', 'o': 'доступен и как Yii::$app->view->renderFile()', 'c': "$body = Yii::$app->view->renderFile(\n    '@app/mail/welcome.php',\n    ['user' => $user]\n);"},
                {'n': 'layout', 'd': 'Шаблон контроллера. false отключает его совсем. Если null — берётся первый заданный по цепочке модулей вверх.', 'o': 'псевдоним, /абсолютный или относительный путь', 'c': "class PostController extends Controller\n{\n    public $layout = 'post';\n}\n\n// для одного действия\n$this->layout = false;"},
                {'n': 'beginBlock() и endBlock()', 'd': 'Блок записывается в представлении, а выводится в шаблоне — так страница управляет частями общей разметки.', 'o': 'читается как $this->blocks[имя]', 'c': "// в представлении\n<?php $this->beginBlock('sidebar'); ?>\n    <h3>Похожие статьи</h3>\n<?php $this->endBlock(); ?>\n\n// в шаблоне\n<?= $this->blocks['sidebar'] ?? '' ?>"},
                {'n': 'beginContent() и endContent()', 'd': 'Вложенные шаблоны: один шаблон оборачивается другим.', 'o': 'аргумент — путь к внешнему шаблону', 'c': "<?php $this->beginContent('@app/views/layouts/main.php'); ?>\n<div class=\"row\">\n    <div class=\"col-8\"><?= $content ?></div>\n</div>\n<?php $this->endContent(); ?>"},
                {'n': 'title', 'd': 'Заголовок страницы. Ставится в представлении, выводится в шаблоне.', 'o': 'не экранируется сам — только через Html::encode', 'c': "$this->title = 'Вход';\n\n// в шаблоне\n<title><?= Html::encode($this->title) ?></title>"},
                {'n': 'params', 'd': 'Общие данные между представлением и шаблоном. Классический пример — хлебные крошки.', 'o': 'обычный массив', 'c': "// в представлении\n$this->params['breadcrumbs'][] = 'О нас';\n\n// в шаблоне\nBreadcrumbs::widget([\n    'links' => $this->params['breadcrumbs'] ?? [],\n]);"},
                {'n': 'context', 'd': 'Объект, который запустил рендер: контроллер или виджет. В Yii 1 им был сам $this.', 'o': 'может быть null при renderFile', 'c': "ID контроллера: <?= $this->context->id ?>"},
                {'n': 'Служебные точки шаблона', 'd': 'Пять вызовов, без которых ресурсы не попадут на страницу.', 'o': 'beginPage, head, beginBody, endBody, endPage', 'c': "<?php $this->beginPage() ?>\n<head><?php $this->head() ?></head>\n<body>\n<?php $this->beginBody() ?>\n    <?= $content ?>\n<?php $this->endBody() ?>\n</body>\n<?php $this->endPage() ?>"},
                {'n': 'События View', 'd': 'Точки вокруг рендера. В afterRender вывод можно подменить через $event->output.', 'o': 'beforeRender, afterRender, beginPage, endPage, beginBody, endBody', 'c': "Yii::$app->view->on(View::EVENT_END_BODY, function () {\n    echo '<!-- rendered ' . date('c') . ' -->';\n});"},
                {'n': 'theme и pathMap', 'd': 'Тема подменяет файлы представлений по префиксу пути, не трогая код. Несколько значений дают наследование тем: берётся первый существующий файл.', 'o': 'basePath, baseUrl, pathMap', 'c': "'view' => [\n    'theme' => [\n        'basePath' => '@app/themes/basic',\n        'baseUrl' => '@web/themes/basic',\n        'pathMap' => [\n            '@app/views' => [\n                '@app/themes/christmas',\n                '@app/themes/basic',\n            ],\n        ],\n    ],\n],"},
                {'n': 'renderers', 'd': 'Twig и Smarty подключаются по расширению файла. Файлы .php при этом продолжают работать.', 'o': 'расширения yii2-twig и yii2-smarty', 'c': "'view' => [\n    'renderers' => [\n        'twig' => [\n            'class' => yii\\twig\\ViewRenderer::class,\n            'cachePath' => '@runtime/Twig/cache',\n        ],\n    ],\n],"},
            ]),
            ('h', 'Регистрация ресурсов'),
            ('ref', [
                {'n': 'registerCss()', 'd': 'Кусок стилей прямо в страницу. Третий аргумент — ключ, он защищает от дублей.', 'o': 'попадает в head', 'c': "$this->registerCss('.badge { display: none }', [], 'hide-badge');"},
                {'n': 'registerCssFile()', 'd': 'Отдельный файл стилей. Через depends можно задать порядок относительно пакетов.', 'o': "options: media, condition", 'c': "$this->registerCssFile('@web/css/print.css', ['media' => 'print']);"},
                {'n': 'registerJs()', 'd': 'Код на странице. Позиция решает, куда он попадёт и когда выполнится.', 'o': 'POS_HEAD, POS_BEGIN, POS_END, POS_READY, POS_LOAD', 'c': "$this->registerJs(\n    \"$('#btn').on('click', function () { });\",\n    yii\\web\\View::POS_READY,\n    'btn-handler'\n);"},
                {'n': 'registerJsFile()', 'd': 'Отдельный файл скрипта. depends важен: без него порядок относительно jQuery не гарантирован.', 'o': "options: position, depends, async, defer", 'c': "$this->registerJsFile('@web/js/main.js', [\n    'depends' => [yii\\web\\JqueryAsset::class],\n]);"},
                {'n': 'registerMetaTag()', 'd': 'Мета-тег. Ключ вторым аргументом позволяет представлению перебить значение из шаблона.', 'o': 'без ключа теги накапливаются', 'c': "$this->registerMetaTag([\n    'name' => 'description',\n    'content' => 'Каталог механизмов Yii 2',\n], 'description');"},
                {'n': 'registerLinkTag()', 'd': 'Тег link: RSS, канонический адрес, иконки.', 'o': 'аргументы — атрибуты тега', 'c': "$this->registerLinkTag([\n    'rel' => 'alternate',\n    'type' => 'application/rss+xml',\n    'href' => '/rss',\n]);"},
                {'n': 'Html::csrfMetaTags()', 'd': 'Мета-теги с CSRF-токеном. Без них yii.js не сможет отправлять POST-запросы.', 'o': 'ставится в head шаблона', 'c': "<?= Html::csrfMetaTags() ?>"},
            ]),
            ('h', 'Пакеты ресурсов'),
            ('ref', [
                {'n': 'AssetBundle::register()', 'd': 'Основной способ подключать стили и скрипты. Пакет знает свои файлы и зависимости и сам расставляет теги в нужном порядке.', 'o': 'в шаблоне — $this, в виджете — $this->view', 'c': "use app\\assets\\AppAsset;\n\nAppAsset::register($this);"},
                {'n': 'basePath и baseUrl', 'd': 'Файлы уже лежат в веб-корне, публиковать нечего. Так описывают ресурсы самого приложения.', 'o': 'обычно @webroot и @web', 'c': "public $basePath = '@webroot';\npublic $baseUrl = '@web';\npublic $css = ['css/site.css'];\npublic $js = ['js/app.js'];"},
                {'n': 'sourcePath', 'd': 'Папка с исходниками вне веб-корня: расширения, пакеты из Bower и NPM. При регистрации содержимое публикуется в @webroot/assets.', 'o': 'вместо basePath и baseUrl', 'c': "public $sourcePath = '@npm/chart.js/dist';\npublic $js = ['chart.umd.js'];"},
                {'n': 'js и css', 'd': 'Списки файлов. Порядок сохраняется. Полный URL означает внешний ресурс с CDN.', 'o': 'пути относительно basePath или sourcePath', 'c': "public $css = ['css/site.css'];\npublic $js = [\n    'js/app.js',\n    '//cdn.example.com/lib.min.js',\n];"},
                {'n': 'depends', 'd': 'Пакеты, которые должны подключиться раньше. Зависимости транзитивны — перечислять всю цепочку не нужно.', 'o': 'главный способ управлять порядком', 'c': "public $depends = [\n    yii\\web\\YiiAsset::class,          // jQuery и yii.js\n    yii\\bootstrap5\\BootstrapAsset::class,\n];"},
                {'n': 'jsOptions и cssOptions', 'd': 'Параметры для всех файлов пакета: позиция, медиа-запрос, условный комментарий.', 'o': 'уходят в registerJsFile и registerCssFile', 'c': "public $jsOptions = ['position' => yii\\web\\View::POS_HEAD];\npublic $cssOptions = ['media' => 'print'];"},
                {'n': 'publishOptions', 'd': 'Что именно публиковать из sourcePath. Полезно, когда в пакете лежит лишнее.', 'o': 'only, except, forceCopy, beforeCopy', 'c': "public $publishOptions = [\n    'only' => ['css/*', 'fonts/*'],\n];"},
                {'n': 'assetManager.bundles', 'd': 'Перенастроить чужой пакет, не трогая его класс: подменить файлы, увести на CDN или отключить целиком через false.', 'o': 'ключ — имя класса пакета', 'c': "'assetManager' => [\n    'bundles' => [\n        yii\\web\\JqueryAsset::class => [\n            'sourcePath' => null,\n            'js' => ['//code.jquery.com/jquery-3.7.1.min.js'],\n        ],\n        yii\\bootstrap5\\BootstrapPluginAsset::class => false,\n    ],\n],"},
                {'n': 'assetMap', 'd': 'Заменить один файл сразу во всех пакетах, где он встречается.', 'o': 'ключ — имя файла', 'c': "'assetMap' => [\n    'jquery.js' => '//code.jquery.com/jquery-3.7.1.min.js',\n],"},
                {'n': 'linkAssets и appendTimestamp', 'd': 'Публиковать симлинками вместо копирования и добавлять к адресам метку времени, чтобы браузер не держал старый файл.', 'o': 'linkAssets не годится там, где симлинки запрещены', 'c': "'assetManager' => [\n    'linkAssets' => true,\n    'appendTimestamp' => true,\n],"},
                {'n': 'converter', 'd': 'В списках js и css можно перечислять .less, .scss, .ts — AssetConverter вызовет установленный компилятор.', 'o': 'команды настраиваются', 'c': "'assetManager' => [\n    'converter' => [\n        'commands' => [\n            'scss' => ['css', 'sass {from} {to}'],\n        ],\n    ],\n],"},
                {'n': 'yii asset', 'd': 'Объединение и сжатие для боевого сервера: команда склеивает файлы и генерирует конфигурацию пакетов.', 'o': 'yii asset/template создаёт заготовку', 'c': "yii asset/template assets.php\nyii asset assets.php config/assets-prod.php"},
            ]),
        ]),
        ('own', 'Приёмы', [
            ('h', 'Свой пакет ресурсов'),
            ('code', 'php', 'assets/AppAsset.php', r'''namespace app\assets;

use yii\web\AssetBundle;

class AppAsset extends AssetBundle
{
    public $basePath = '@webroot';
    public $baseUrl = '@web';
    public $css = ['css/site.css'];
    public $js = ['js/app.js'];
    public $depends = [
        yii\web\YiiAsset::class,
        yii\bootstrap5\BootstrapAsset::class,
    ];
}'''),
            ('h', 'Свой шаблон для одного контроллера'),
            ('code', 'php', None, r'''class PostController extends Controller
{
    public $layout = 'post';       // @app/views/layouts/post.php

    public function actionPreview($id)
    {
        $this->layout = false;     // это действие — без шаблона вовсе
        return $this->render('preview', ['model' => $this->findModel($id)]);
    }
}'''),
            ('h', 'Боковая панель из страницы'),
            ('code', 'php', 'views/post/view.php', r'''<?php $this->beginBlock('sidebar'); ?>
    <h3>Похожие статьи</h3>
    <?= ListView::widget(['dataProvider' => $related]) ?>
<?php $this->endBlock(); ?>'''),
            ('code', 'php', 'views/layouts/column2.php', r'''<?php $this->beginContent('@app/views/layouts/main.php'); ?>
<div class="row">
    <div class="col-8"><?= $content ?></div>
    <div class="col-4">
        <?= $this->blocks['sidebar'] ?? 'Боковая панель по умолчанию' ?>
    </div>
</div>
<?php $this->endContent(); ?>'''),
            ('h', 'Десяток статичных страниц одним действием'),
            ('code', 'php', None, r'''public function actions()
{
    // site/page?view=about → views/site/pages/about.php
    return ['page' => ['class' => yii\web\ViewAction::class]];
}'''),
            ('note', 'tip', 'Что делать в представлении, а что нет',
             'Только разметка и простой вывод. Запросы к базе, обращения к `$_GET` и изменение моделей — не здесь. '
             'Читать свойства модели можно, менять — нет. Крупные файлы дробите на `_item.php` и `_form.php`, '
             'а форматирование выносите в хелперы и `formatter`.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Вывод без Html::encode',
             'Всё, что пришло от пользователя, экранируется: `<?= Html::encode($user->name) ?>`. '
             'Для HTML, который человек прислал сам, — `HtmlPurifier::process()`, но он медленный, '
             'результат стоит кэшировать.'),
            ('note', 'trap', 'В Yii 1 $this был контроллером',
             'В Yii 2 `$this` в представлении — это объект `View`. Контроллер доступен как `$this->context`. '
             'Код, перенесённый из Yii 1 дословно, тихо обращается не к тому объекту.'),
            ('note', 'trap', 'renderPartial там, где нужен renderAjax',
             'Оба не применяют шаблон, но `renderPartial` не выводит зарегистрированные скрипты и стили. '
             'Виджет, подгруженный им в модалку, окажется без своего JS и просто не заработает.'),
            ('note', 'trap', '@webroot/assets как sourcePath',
             'Эта папка принадлежит менеджеру ресурсов и может быть очищена целиком. '
             'Исходники держите отдельно.'),
            ('note', 'warn', 'Правка свойств пакета после register()',
             'Изменения в `init()` или после регистрации перекроют настройки из `assetManager->bundles` '
               'и сломают объединение ресурсов. Настраивайте пакет снаружи, через конфигурацию.'),
            ('note', 'warn', 'Скрипт без depends',
             '`registerJsFile()` без `depends` не гарантирует, что jQuery уже подключён — файл может уехать выше него. '
             'Порядок задаётся зависимостями, а не порядком вызовов.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Виджеты

topic(
    id='widgets', group='view',
    title='Виджеты',
    cls='yii\\base\\Widget',
    lead='Переиспользуемые куски представления со своей логикой: формы, таблицы, меню, навигация.',
    badge='14 встроенных',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Виджет — компонент, который умеет отрисовать себя. Два способа вызова: '
                  '**однократный** через `widget()` и **парный** через `begin()` и `end()`, когда виджет оборачивает разметку.'),
            ('svg', '''<svg viewBox="0 0 740 210" role="img" aria-label="Два способа вызвать виджет: однократный widget и парный begin с end" class="dg">
<g class="dg-box"><rect x="24" y="26" width="320" height="158" rx="10"/><text x="184" y="52">widget()</text><text x="184" y="70" class="dg-sub">отрисовал и вернул строку</text></g>
<g class="dg-chip"><rect x="48" y="90" width="272" height="30" rx="6"/><text x="184" y="110">init() → run()</text></g>
<g class="dg-chip"><rect x="48" y="130" width="272" height="30" rx="6"/><text x="184" y="150">GridView, Menu, Breadcrumbs</text></g>
<g class="dg-box dg-live"><rect x="396" y="26" width="320" height="158" rx="10"/><text x="556" y="52">begin() … end()</text><text x="556" y="70" class="dg-sub">обернул чужую разметку</text></g>
<g class="dg-chip"><rect x="420" y="90" width="272" height="30" rx="6"/><text x="556" y="110">init() → ваш HTML → run()</text></g>
<g class="dg-chip dg-live"><rect x="420" y="130" width="272" height="30" rx="6"/><text x="556" y="150">ActiveForm, Pjax, Modal</text></g>
</svg>''', 'Разница только в том, где находится ваша разметка: снаружи виджета или внутри него.'),
            ('h', 'Однократный вызов'),
            ('code', 'php', 'views/post/index.php', r'''<?= GridView::widget([
    'dataProvider' => $dataProvider,
    'filterModel' => $searchModel,
    'columns' => [
        ['class' => yii\grid\SerialColumn::class],
        'title',
        'created_at:datetime',
        ['class' => yii\grid\ActionColumn::class],
    ],
]) ?>'''),
            ('h', 'Парный вызов'),
            ('code', 'php', 'views/post/_form.php', r'''<?php $form = ActiveForm::begin([
    'id' => 'post-form',
    'options' => ['enctype' => 'multipart/form-data'],
]) ?>

    <?= $form->field($model, 'title')->textInput(['maxlength' => true]) ?>
    <?= $form->field($model, 'body')->textarea(['rows' => 8]) ?>
    <?= Html::submitButton('Сохранить', ['class' => 'btn btn-primary']) ?>

<?php ActiveForm::end() ?>'''),
            ('note', 'trap', 'Забытый end()',
             'Парный виджет без `end()` не отрисуется вовсе: содержимое останется в буфере вывода и молча пропадёт. '
             'Если из шаблона исчез целый блок, ищите незакрытый виджет.'),
            ('h', 'Настройки по умолчанию для всех экземпляров'),
            ('code', 'php', 'config/web.php', r''''container' => [
    'definitions' => [
        yii\widgets\LinkPager::class => ['maxButtonCount' => 5],
        yii\grid\GridView::class => [
            'tableOptions' => ['class' => 'table table-sm table-striped'],
        ],
    ],
],'''),
        ]),
        ('all', 'Все 14 встроенных', [
            ('ref', [
                {'n': 'ActiveForm', 'd': 'Форма по модели: имена полей, клиентская проверка по rules(), вывод ошибок, токен CSRF.', 'o': 'id, action, method, options, fieldConfig, enableClientValidation, enableAjaxValidation, validateOnBlur, validationUrl', 'c': "$form = ActiveForm::begin([\n    'id' => 'login-form',\n    'enableAjaxValidation' => true,\n    'fieldConfig' => [\n        'template' => \"{label}\\n{input}\\n{error}\",\n    ],\n]);\nActiveForm::end();"},
                {'n': 'ActiveField', 'd': 'Одно поле формы. Возвращается из $form->field() и настраивается цепочкой.', 'o': 'textInput, passwordInput, textarea, dropDownList, checkbox, radioList, checkboxList, fileInput, hiddenInput, widget, label, hint, error', 'c': "$form->field($model, 'email')->input('email');\n$form->field($model, 'city_id')->dropDownList($items,\n    ['prompt' => '—']);\n$form->field($model, 'date')\n    ->widget(DatePicker::class, ['dateFormat' => 'yyyy-MM-dd']);\n$form->field($model, 'agree')->checkbox()->hint('Обязательно');"},
                {'n': 'GridView', 'd': 'Таблица с сортировкой, фильтрами и постраничной навигацией. Главный виджет админок.', 'o': 'dataProvider, filterModel, columns, layout, rowOptions, tableOptions, summary, emptyText, pager', 'c': "GridView::widget([\n    'dataProvider' => $dp,\n    'filterModel' => $search,\n    'columns' => ['id', 'title', 'price:currency'],\n    'rowOptions' => function ($model) {\n        return ['class' => $model->is_new ? 'table-warning' : ''];\n    },\n]);"},
                {'n': 'Колонки GridView', 'd': 'Пять готовых типов колонок. DataColumn стоит по умолчанию, остальные указывают классом.', 'o': 'DataColumn, ActionColumn, CheckboxColumn, SerialColumn, RadioButtonColumn', 'c': "['class' => SerialColumn::class],\n['attribute' => 'price', 'format' => ['currency', 'RUB'],\n 'contentOptions' => ['class' => 'text-end']],\n['class' => ActionColumn::class,\n 'template' => '{view} {update}',\n 'visibleButtons' => [\n     'update' => fn ($m) => $m->canEdit(),\n ]],\n['class' => CheckboxColumn::class],"},
                {'n': 'ListView', 'd': 'Список произвольной вёрстки: каждый элемент рисуется отдельным шаблоном.', 'o': 'dataProvider, itemView, itemOptions, viewParams, layout, summary, emptyText', 'c': "ListView::widget([\n    'dataProvider' => $dp,\n    'itemView' => '_card',      // views/post/_card.php\n    'viewParams' => ['short' => true],\n    'layout' => \"{summary}\\n{items}\\n{pager}\",\n]);"},
                {'n': 'DetailView', 'd': 'Карточка одной записи: строки «подпись — значение» с форматированием.', 'o': 'model, attributes, template, options', 'c': "DetailView::widget([\n    'model' => $model,\n    'attributes' => [\n        'title',\n        'author.name',\n        'created_at:datetime',\n        ['label' => 'Статус', 'format' => 'raw',\n         'value' => $model->statusBadge()],\n    ],\n]);"},
                {'n': 'Menu', 'd': 'Вложенное меню со списками. Сам помечает активный пункт по текущему маршруту.', 'o': 'items, activateItems, activateParents, activeCssClass, itemOptions, encodeLabels, submenuTemplate', 'c': "Menu::widget([\n    'items' => [\n        ['label' => 'Главная', 'url' => ['site/index']],\n        ['label' => 'Посты', 'url' => ['post/index'], 'items' => [\n            ['label' => 'Черновики', 'url' => ['post/drafts']],\n        ]],\n        ['label' => 'Выход', 'url' => ['site/logout'],\n         'visible' => !Yii::$app->user->isGuest],\n    ],\n]);"},
                {'n': 'Breadcrumbs', 'd': 'Хлебные крошки. Берёт цепочку из $this->params, которую страницы наполняют сами.', 'o': 'links, homeLink, itemTemplate, activeItemTemplate', 'c': "// в представлении страницы\n$this->params['breadcrumbs'][] = ['label' => 'Посты',\n    'url' => ['index']];\n$this->params['breadcrumbs'][] = $model->title;\n\n// в layout\nBreadcrumbs::widget([\n    'links' => $this->params['breadcrumbs'] ?? [],\n]);"},
                {'n': 'LinkPager', 'd': 'Постраничная навигация по объекту Pagination. Обычно вызывается внутри GridView и ListView.', 'o': 'pagination, maxButtonCount, firstPageLabel, lastPageLabel, prevPageLabel, nextPageLabel, hideOnSinglePage, linkOptions', 'c': "LinkPager::widget([\n    'pagination' => $dp->pagination,\n    'maxButtonCount' => 5,\n    'hideOnSinglePage' => true,\n    'linkContainerOptions' => ['class' => 'page-item'],\n    'linkOptions' => ['class' => 'page-link'],\n]);"},
                {'n': 'LinkSorter', 'd': 'Ссылки сортировки отдельно от таблицы: нужен в ListView, где заголовков колонок нет.', 'o': 'sort, attributes, options', 'c': "LinkSorter::widget([\n    'sort' => $dp->sort,\n    'attributes' => ['title', 'created_at'],\n]);"},
                {'n': 'Pjax', 'd': 'Обновляет свой кусок страницы через AJAX и подменяет адрес, без перезагрузки.', 'o': 'id, options, linkSelector, formSelector, submitEvent, enablePushState, timeout, scrollTo', 'c': "<?php Pjax::begin(['id' => 'post-grid',\n                   'timeout' => 5000]) ?>\n<?= GridView::widget([...]) ?>\n<?php Pjax::end() ?>\n\n// обновить вручную из JS\n$.pjax.reload({container: '#post-grid'});"},
                {'n': 'MaskedInput', 'd': 'Поле ввода по маске: телефоны, даты, номера документов.', 'o': 'mask, clientOptions, definitions', 'c': "$form->field($model, 'phone')->widget(MaskedInput::class, [\n    'mask' => '+7 (999) 999-99-99',\n]);"},
                {'n': 'Captcha', 'd': 'Картинка с кодом и поле ввода. Работает в паре с CaptchaAction и валидатором captcha.', 'o': 'captchaAction, imageOptions, template', 'c': "// контроллер\npublic function actions()\n{\n    return ['captcha' => [\n        'class' => yii\\captcha\\CaptchaAction::class,\n    ]];\n}\n\n// представление\n$form->field($model, 'verifyCode')->widget(Captcha::class);"},
                {'n': 'Обёртки представления', 'd': 'Три служебных парных виджета: кэш фрагмента, удаление лишних пробелов и обёртка содержимого другим шаблоном.', 'o': 'FragmentCache (через beginCache), Spaceless, ContentDecorator (через beginContent), Block (beginBlock)', 'c': "<?php if ($this->beginCache('menu',\n        ['duration' => 600])) { ?>\n    …тяжёлый блок…\n<?php $this->endCache(); } ?>\n\n<?php $this->beginContent('@app/views/layouts/box.php') ?>\n    содержимое в рамке\n<?php $this->endContent() ?>\n\n<?php $this->beginBlock('sidebar') ?>…<?php $this->endBlock() ?>\n<?= $this->blocks['sidebar'] ?? '' ?>"},
            ]),
            ('note', 'tip', 'Виджеты оформления живут в расширениях',
             'Модальные окна, вкладки, выпадающие меню и кнопки пришли не из ядра, а из `yii2-bootstrap5` (или `yii2-bootstrap4`). '
             'Устроены они точно так же и вызываются теми же двумя способами.'),
        ]),
        ('own', 'Свой виджет', [
            ('h', 'Однократный: отрисовал и вернул'),
            ('code', 'php', 'components/StatBadge.php', r'''namespace app\components;

use yii\base\Widget;
use yii\helpers\Html;

class StatBadge extends Widget
{
    public $label;
    public $value;
    public $tone = 'neutral';

    public function init()
    {
        parent::init();
        if ($this->label === null) {
            throw new \yii\base\InvalidConfigException('StatBadge: нужен label.');
        }
    }

    public function run()
    {
        // вариант попроще — собрать разметку здесь
        return Html::tag('span',
            Html::tag('b', Html::encode($this->value)) . ' ' . Html::encode($this->label),
            ['class' => 'stat stat-' . $this->tone]
        );

        // вариант с шаблоном: views/statBadge.php рядом с классом
        // return $this->render('statBadge', ['label' => $this->label]);
    }
}

// использование
echo StatBadge::widget(['label' => 'заказов', 'value' => 42, 'tone' => 'ok']);'''),
            ('h', 'Парный: оборачивает чужую разметку'),
            ('code', 'php', 'components/Panel.php', r'''class Panel extends Widget
{
    public $title;

    public function init()
    {
        parent::init();
        ob_start();                       // начали перехват вывода
        echo Html::beginTag('section', ['class' => 'panel']);
        echo Html::tag('h3', Html::encode($this->title), ['class' => 'panel-title']);
        echo Html::beginTag('div', ['class' => 'panel-body']);
    }

    public function run()
    {
        $content = ob_get_clean();        // забрали всё, что вывели между begin и end
        return $content
            . Html::endTag('div')
            . Html::endTag('section');
    }
}'''),
            ('code', 'php', None, r'''<?php Panel::begin(['title' => 'Последние заказы']) ?>
    <?= GridView::widget(['dataProvider' => $dp]) ?>
<?php Panel::end() ?>'''),
            ('h', 'Свои ресурсы и скрипты'),
            ('code', 'php', None, r'''public function run()
{
    $view = $this->getView();
    ChartAsset::register($view);          // свой пакет ресурсов

    $id = $this->options['id'] ?? $this->getId();
    $options = Json::htmlEncode($this->clientOptions);
    $view->registerJs("initChart('#$id', $options);");

    return Html::tag('div', '', ['id' => $id, 'class' => 'chart']);
}'''),
            ('note', 'tip', 'Кэширование вывода виджета',
             'Если виджет дорогой, не пишите кэш внутрь `run()`. Прикрепите `CacheableWidgetBehavior`: '
             'он закэширует результат целиком и учтёт вариации по языку и пользователю.'),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Виджет без end() съедает разметку',
             'Парный виджет открывает буфер вывода в `init()`. Нет `end()` — буфер не закроется, и часть страницы исчезнет без ошибки.'),
            ('note', 'trap', 'Одинаковые id при повторном вызове',
             'Два `ActiveForm` или два `Pjax` на странице без явных `id` получат автоматические имена, но их клиентский код может конфликтовать. '
             'Задавайте `id` вручную, если виджет вызывается больше одного раза.'),
            ('note', 'warn', 'GridView с сырым HTML',
             'Колонки по умолчанию экранируют значения. Формат `raw` это отключает, поэтому в него можно отдавать только доверенное содержимое, '
             'иначе получите внедрение скрипта из данных пользователя.'),
            ('note', 'trap', 'Ссылки внутри Pjax перехватываются',
             'Все ссылки внутри блока начинают работать через AJAX. Для выхода наружу помечайте ссылку атрибутом `data-pjax="0"`.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Миграции

topic(
    id='migrations', group='db',
    title='Миграции',
    cls='yii\\db\\Migration',
    lead='Структура базы в коде и под контролем версий: применяется, откатывается, повторяется на любой машине.',
    badge='24 метода схемы',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Миграция — класс с двумя методами: «применить» и «откатить». Применённые миграции фреймворк запоминает '
                  'в служебной таблице `migration`, поэтому повторный запуск ничего не сломает.'),
            ('svg', '''<svg viewBox="0 0 760 210" role="img" aria-label="Команда migrate сравнивает файлы миграций с таблицей migration и применяет только новые" class="dg">
<defs><marker id="m-arr9" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#m-arr9)" opacity=".55">
<path d="M212 62h56"/><path d="M212 146h56"/><path d="M456 104h56"/>
</g>
<g class="dg-box"><rect x="22" y="36" width="190" height="52" rx="8"/><text x="117" y="58">файлы миграций</text><text x="117" y="75" class="dg-sub">m250101_… .php</text></g>
<g class="dg-box"><rect x="22" y="120" width="190" height="52" rx="8"/><text x="117" y="142">таблица migration</text><text x="117" y="159" class="dg-sub">что уже применено</text></g>
<g class="dg-box dg-live"><rect x="268" y="66" width="188" height="76" rx="10"/><text x="362" y="96">./yii migrate</text><text x="362" y="114" class="dg-sub">разница между ними</text></g>
<g class="dg-box dg-ok"><rect x="512" y="78" width="226" height="52" rx="8"/><text x="625" y="100">применить только новые</text><text x="625" y="117" class="dg-sub">safeUp() по очереди</text></g>
</svg>''', 'Команда не «накатывает всё заново», а вычисляет разницу. Поэтому её безопасно запускать на каждом развёртывании.'),
            ('h', 'Создать и применить'),
            ('code', 'bash', None, r'''./yii migrate/create create_post_table
# → migrations/m250101_120000_create_post_table.php

./yii migrate                    # применить все новые
./yii migrate --interactive=0    # без вопросов, для развёртывания
./yii migrate/down               # откатить последнюю
./yii migrate/history            # что уже применено
./yii migrate/new                # что ещё не применено'''),
            ('h', 'Как выглядит файл'),
            ('code', 'php', 'migrations/m250101_120000_create_post_table.php', r'''use yii\db\Migration;

class m250101_120000_create_post_table extends Migration
{
    public function safeUp()
    {
        $this->createTable('{{%post}}', [
            'id' => $this->primaryKey(),
            'title' => $this->string()->notNull(),
            'body' => $this->text(),
            'author_id' => $this->integer()->notNull(),
            'status' => $this->smallInteger()->notNull()->defaultValue(0),
            'created_at' => $this->integer()->notNull(),
        ]);

        $this->createIndex('idx-post-status', '{{%post}}', 'status');
        $this->addForeignKey('fk-post-author', '{{%post}}', 'author_id',
            '{{%user}}', 'id', 'CASCADE');
    }

    public function safeDown()
    {
        $this->dropTable('{{%post}}');     // индексы и ключи уйдут вместе с таблицей
    }
}'''),
            ('note', 'tip', 'safeUp вместо up',
             'Методы с приставкой safe выполняются внутри транзакции: упало на середине — откатится целиком. '
             'Берите их по умолчанию. Обычные `up()` и `down()` нужны там, где транзакционный DDL не поддерживается или мешает.'),
        ]),
        ('all', 'Методы и типы', [
            ('h', 'Что умеет Migration'),
            ('ref', [
                {'n': 'createTable', 'd': 'Создаёт таблицу. Третьим аргументом можно передать настройки СУБД.', 'o': '$table, $columns, $options', 'c': "$this->createTable('{{%post}}', [\n    'id' => $this->primaryKey(),\n    'title' => $this->string(255)->notNull(),\n], $this->db->driverName === 'mysql'\n    ? 'ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'\n    : null);"},
                {'n': 'dropTable, renameTable, truncateTable', 'd': 'Удалить, переименовать, очистить таблицу.', 'o': '$table, $newName', 'c': "$this->dropTable('{{%post}}');\n$this->renameTable('{{%post}}', '{{%article}}');\n$this->truncateTable('{{%log}}');"},
                {'n': 'addColumn, dropColumn', 'd': 'Добавить и убрать столбец.', 'o': '$table, $column, $type', 'c': "$this->addColumn('{{%post}}', 'views',\n    $this->integer()->notNull()->defaultValue(0));\n$this->dropColumn('{{%post}}', 'views');"},
                {'n': 'alterColumn, renameColumn', 'd': 'Изменить тип столбца или его имя.', 'o': '$table, $column, $type | $newName', 'c': "$this->alterColumn('{{%post}}', 'title',\n    $this->string(500)->notNull());\n$this->renameColumn('{{%post}}', 'text', 'body');"},
                {'n': 'createIndex, dropIndex', 'd': 'Индекс по одному или нескольким столбцам, обычный или уникальный.', 'o': '$name, $table, $columns, $unique', 'c': "$this->createIndex('idx-post-status', '{{%post}}', 'status');\n$this->createIndex('idx-post-slug-lang', '{{%post}}',\n    ['slug', 'lang'], true);   // уникальный\n$this->dropIndex('idx-post-status', '{{%post}}');"},
                {'n': 'addPrimaryKey, dropPrimaryKey', 'd': 'Первичный ключ, в том числе составной, отдельным шагом.', 'o': '$name, $table, $columns', 'c': "$this->addPrimaryKey('pk-post-tag', '{{%post_tag}}',\n    ['post_id', 'tag_id']);"},
                {'n': 'addForeignKey, dropForeignKey', 'd': 'Внешний ключ с правилами каскада.', 'o': '$name, $table, $columns, $refTable, $refColumns, $delete, $update', 'c': "$this->addForeignKey('fk-post-author',\n    '{{%post}}', 'author_id',\n    '{{%user}}', 'id',\n    'CASCADE',    // при удалении пользователя\n    'CASCADE');   // при смене id"},
                {'n': 'addCommentOnColumn, addCommentOnTable', 'd': 'Комментарии к таблице и столбцам. Заметно помогают, когда схему читает другой человек.', 'o': 'и парные dropCommentFrom…', 'c': "$this->addCommentOnColumn('{{%post}}', 'status',\n    '0 черновик, 1 опубликован, 2 в архиве');\n$this->addCommentOnTable('{{%post}}', 'Записи блога');"},
                {'n': 'insert, batchInsert, upsert', 'd': 'Наполнение справочников прямо в миграции. Так окружения получаются одинаковыми.', 'o': '$table, $columns, $rows', 'c': "$this->insert('{{%role}}', ['name' => 'admin']);\n$this->batchInsert('{{%role}}', ['code', 'name'], [\n    ['editor', 'Редактор'],\n    ['viewer', 'Читатель'],\n]);"},
                {'n': 'update, delete', 'd': 'Правка существующих данных при изменении схемы.', 'o': '$table, $columns, $condition', 'c': "$this->update('{{%post}}', ['status' => 1],\n    ['status' => null]);\n$this->delete('{{%log}}', ['<', 'created_at', $ts]);"},
                {'n': 'execute', 'd': 'Произвольный SQL, когда нужного метода нет: представления, триггеры, специфика СУБД.', 'o': '$sql, $params', 'c': "$this->execute('CREATE VIEW {{%active_post}} AS\n    SELECT * FROM {{%post}} WHERE status = 1');"},
                {'n': 'createView, dropView', 'd': 'Представления отдельными методами, с 2.0.14.', 'o': '$viewName, $subQuery', 'c': "$this->createView('{{%active_post}}',\n    (new Query())->from('{{%post}}')\n        ->where(['status' => 1]));"},
            ]),
            ('h', 'Типы столбцов, одинаковые для всех СУБД'),
            ('ref', [
                {'n': 'primaryKey, bigPrimaryKey', 'd': 'Автоинкрементный первичный ключ.', 'o': '', 'c': "'id' => $this->primaryKey(),\n'id' => $this->bigPrimaryKey(),"},
                {'n': 'string, text, char', 'd': 'Текстовые типы. У string по умолчанию 255 символов.', 'o': '$length', 'c': "'title' => $this->string()->notNull(),\n'slug' => $this->string(160)->unique(),\n'body' => $this->text(),\n'code' => $this->char(6),"},
                {'n': 'integer, bigInteger, smallInteger, tinyInteger', 'd': 'Целые числа разной ширины.', 'o': '$precision', 'c': "'views' => $this->integer()->defaultValue(0),\n'status' => $this->smallInteger()->notNull(),"},
                {'n': 'decimal, float, double, money', 'd': 'Дробные числа. Для денег берут decimal, а не float.', 'o': '$precision, $scale', 'c': "'price' => $this->decimal(12, 2)->notNull(),\n'rate' => $this->float(),"},
                {'n': 'boolean', 'd': 'Логическое значение; в MySQL разворачивается в TINYINT(1).', 'o': '', 'c': "'is_active' => $this->boolean()->notNull()\n    ->defaultValue(true),"},
                {'n': 'date, time, dateTime, timestamp', 'd': 'Дата и время средствами СУБД. Часто вместо них берут integer с меткой времени.', 'o': '$precision', 'c': "'published_at' => $this->dateTime(),\n'created_at' => $this->timestamp()\n    ->defaultExpression('CURRENT_TIMESTAMP'),"},
                {'n': 'binary, json', 'd': 'Двоичные данные и JSON; json поддержан с 2.0.14 там, где его знает СУБД.', 'o': '', 'c': "'payload' => $this->json(),\n'file' => $this->binary(),"},
                {'n': 'Модификаторы', 'd': 'Цепочка уточнений после типа. after и first работают только в MySQL.', 'o': 'notNull, null, unique, defaultValue, defaultExpression, comment, after, first, unsigned, check', 'c': "'email' => $this->string()->notNull()->unique()\n    ->comment('Логин пользователя'),\n'position' => $this->integer()->notNull()\n    ->defaultValue(0)->after('id'),"},
            ]),
            ('h', 'Команды'),
            ('kv', [
                ('migrate', 'применить все новые'),
                ('migrate 3', 'применить только три следующие'),
                ('migrate/to 250101_120000', 'дойти до указанной миграции в любую сторону'),
                ('migrate/down, migrate/down 3', 'откатить последнюю или несколько'),
                ('migrate/redo', 'откатить и применить заново — удобно при отладке'),
                ('migrate/history, migrate/new', 'что применено и что осталось'),
                ('migrate/mark', 'пометить применённой, не выполняя; для приведения окружений в порядок'),
                ('migrate/fresh', '⚠ удалить все таблицы и применить всё заново, только для разработки'),
                ('--migrationPath, --migrationNamespaces', 'откуда брать миграции; так применяют миграции расширений'),
                ('--db=db2', 'применить к другому соединению'),
            ]),
        ]),
        ('own', 'Приёмы', [
            ('h', 'Генерация по имени файла'),
            ('p', 'Команда понимает несколько шаблонов имён и заполняет тело миграции сама.'),
            ('code', 'bash', None, r'''# создание таблицы с полями и внешним ключом
./yii migrate/create create_post_table \
    --fields="title:string:notNull,body:text,author_id:integer:notNull:foreignKey(user)"

# добавление и удаление столбца
./yii migrate/create add_position_column_to_post_table --fields="position:integer"
./yii migrate/create drop_position_column_from_post_table --fields="position:integer"

# связующая таблица для связи многие-ко-многим
./yii migrate/create create_junction_table_for_post_and_tag_tables'''),
            ('h', 'Миграция данных, а не схемы'),
            ('code', 'php', None, r'''public function safeUp()
{
    $this->addColumn('{{%user}}', 'display_name', $this->string());

    // заполняем новое поле из старых, порциями — таблица может быть большой
    foreach (User::find()->batch(500) as $users) {
        foreach ($users as $user) {
            $this->update('{{%user}}',
                ['display_name' => trim($user->first_name . ' ' . $user->last_name)],
                ['id' => $user->id]
            );
        }
    }
}

public function safeDown()
{
    $this->dropColumn('{{%user}}', 'display_name');
}'''),
            ('h', 'Несколько источников миграций'),
            ('code', 'php', 'config/console.php', r''''controllerMap' => [
    'migrate' => [
        'class' => yii\console\controllers\MigrateController::class,
        'migrationPath' => null,              // выключаем старый механизм
        'migrationNamespaces' => [
            'app\migrations',
            'app\modules\shop\migrations',
        ],
    ],
],'''),
            ('code', 'bash', None, r'''# миграции расширений применяются так же
./yii migrate --migrationPath=@yii/rbac/migrations
./yii migrate --migrationPath=@yii/caching/migrations'''),
            ('h', 'Когда откат невозможен'),
            ('code', 'php', None, r'''public function safeDown()
{
    echo "Миграция удаляет данные и не может быть отменена.\n";
    return false;   // migrate/down остановится с сообщением
}'''),
        ]),
        ('traps', 'Грабли', [
            ('note', 'trap', 'Правка уже применённой миграции',
             'У коллег и на сервере она числится выполненной, поэтому исправленный файл там никогда не запустится, '
             'и схемы разъедутся. Изменения вносят новой миграцией.'),
            ('note', 'trap', 'Использование моделей внутри миграции',
             'Класс модели со временем меняется, а миграция должна работать и через год. '
             'Обращение к `Post::find()` в старой миграции однажды упадёт на несуществующем поле. '
             'Безопаснее писать запросы явно через методы миграции.'),
            ('note', 'warn', 'MySQL и транзакционный DDL',
             'MySQL фиксирует изменения схемы неявно, поэтому `safeUp()` там не откатит уже созданную таблицу. '
             'Это не повод отказываться от safe-методов, но рассчитывать на полный откат нельзя.'),
            ('note', 'trap', 'Забытый сброс кэша схемы',
             'После миграции Active Record может ещё какое-то время видеть старую структуру таблицы. '
             'Добавьте в развёртывание `./yii cache/flush-schema` сразу после `./yii migrate`.'),
        ]),
    ],
)


# порядок узлов задаётся явно — по ходу запроса; номера считаются из него
ORDER = [
    'http', 'routing', 'filters', 'user',
    'model', 'rules', 'scenarios',
    'ar', 'query', 'migrations',
    'views', 'widgets', 'state',
    'components', 'di', 'behaviors', 'events', 'helpers',
]

_known = {t['id'] for t in TOPICS}
assert _known == set(ORDER), 'ORDER и TOPICS разошлись: %s' % (_known ^ set(ORDER))
TOPICS.sort(key=lambda t: ORDER.index(t['id']))

# группы в ORDER должны идти подряд и в том же порядке, что и в GROUPS,
# иначе сквозная нумерация разойдётся с порядком карточек на странице
_gseq = [t['group'] for t in TOPICS]
_gidx = [g for g, _, _ in GROUPS].index
assert _gseq == sorted(_gseq, key=_gidx), 'группы в ORDER идут вразнобой: %s' % _gseq

# номера считаются здесь, а не проставляются руками у каждой темы
for _i, _t in enumerate(TOPICS):
    _t['num'] = '%02d' % (_i + 1)

NUM = {t['id']: t['num'] for t in TOPICS}
