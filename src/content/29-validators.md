---
id: validators
title: Встроенные валидаторы
part: input
summary: Справочник валидаторов ядра — required, string, integer/number, email, url, ip, date, compare, in, match, boolean, default, filter, trim, each, exist, unique, file, image, captcha, safe — с ключевыми опциями и типичными примерами.
sources: tutorial-core-validators
---

:::lead
Каждый валидатор — класс в `yii\validators`, но в `rules()` его зовут коротким именем. Ниже — все встроенные, сгруппированные по назначению, с опциями, которые реально нужны. Общие для всех: `message`, `on`, `except`, `skipOnEmpty`, `skipOnError`, `when`, `whenClient`, `enableClientValidation`.
:::

## Обязательность и умолчания

:::kv
`required` — не пусто. `requiredValue` (ожидать конкретное значение), `strict` (сравнивать строго). Единственный валидатор, который не пропускает пустые значения
`default` — подставить `value` (значение или замыкание), если атрибут пуст. Не проверяет, а заполняет
`safe` — «ничего не проверять, но считать атрибут безопасным» для массового присваивания
:::

```php
[['username', 'password'], 'required'],
['accept', 'required', 'requiredValue' => 1, 'message' => 'Примите условия'],
['age', 'default', 'value' => null],
['country', 'default', 'value' => 'USA'],
['from', 'default', 'value' => function ($model) { return date('Y-m-d'); }],
['notes', 'safe'],
```

## Строки и форматы

:::kv
`string` — строка длиной `min`..`max` или ровно `length`; `encoding` (по умолчанию `charset` приложения)
`email` — адрес; `allowName` (разрешить `Иван <ivan@site.ru>`), `checkDNS` (проверить MX-запись), `enableIDN`
`url` — URL; `validSchemes` (`['http', 'https']`), `defaultScheme` (дописать, если схемы нет), `enableIDN`
`ip` — IPv4/IPv6; `ipv4`, `ipv6`, `subnet` (`true` — обязательно с маской, `null` — можно с маской), `normalize`, `ranges` (белый/чёрный список: `['10.0.1.0/24', '!10.0.0.0/8', 'any']`), `negation` (разрешить `!`)
`match` — регулярное выражение `pattern`; `not` — инвертировать
`trim` — обрезать пробелы (фильтр); `chars` — какие символы
`filter` — применить callback `filter` (строка, замыкание, `[класс, метод]`); `skipOnArray` — не применять к массивам
:::

```php
['username', 'string', 'length' => [4, 24]],
['email', 'email', 'checkDNS' => true],
['website', 'url', 'defaultScheme' => 'https'],
['ip', 'ip', 'ipv6' => false, 'ranges' => ['10.0.0.0/8', '!any']],
['username', 'match', 'pattern' => '/^[a-z]\w*$/i'],
['username', 'match', 'pattern' => '/^admin$/', 'not' => true, 'message' => 'Имя занято'],
[['title', 'body'], 'trim'],
['username', 'filter', 'filter' => 'strtolower'],
['phone', 'filter', 'filter' => function ($value) { return preg_replace('/\D/', '', $value); }],
```

`ip` при `subnet => null` и `normalize => true` приведёт `192.168.1.1` к `192.168.1.1/32`; при `expandIPv6` — развернёт сокращённую запись.

## Числа и логика

:::kv
`integer` — целое; `min`, `max`, `tooSmall`, `tooBig`
`number` (`double`) — любое число; те же `min`/`max`; `integerPattern`, `numberPattern`
`boolean` — `trueValue`/`falseValue` (по умолчанию `1`/`0`), `strict`. Не преобразует значение
`compare` — сравнить с другим атрибутом `compareAttribute` или значением `compareValue`; `operator` (`==`, `===`, `!=`, `!==`, `>`, `>=`, `<`, `<=`); `type` (`string`, `number`, `datetime` с 2.0.35?) — тип сравнения
`in` — значение из `range`; `strict`, `not`, `allowArray` (проверить каждый элемент массива)
:::

```php
['age', 'integer', 'min' => 18],
['price', 'number', 'min' => 0, 'max' => 1e6],
['salary', 'double'],
['remember_me', 'boolean'],
['is_active', 'boolean', 'trueValue' => true, 'falseValue' => false, 'strict' => true],
['password_repeat', 'compare', 'compareAttribute' => 'password'],
['age', 'compare', 'compareValue' => 30, 'operator' => '>=', 'type' => 'number'],
['level', 'in', 'range' => [1, 2, 3]],
['tags', 'in', 'range' => ['php', 'yii'], 'allowArray' => true],
```

> [!GOTCHA]
> `compare` по умолчанию сравнивает **строки**: `'10' < '9'`. Для чисел и дат задавайте `'type' => 'number'`.

## Даты

:::kv
`date` — дата в формате `format` (ICU: `yyyy-MM-dd`, или `php:Y-m-d`); `timestampAttribute` — куда записать UNIX-время; `timestampAttributeFormat` — или в каком формате записать; `min`/`max` (+`tooSmall`/`tooBig`); `timeZone`, `locale`
`datetime`, `time` — тот же валидатор с `type => 'datetime'` / `'time'` (с 2.0.8)
:::

```php
[['from_date', 'to_date'], 'date'],
['birthday', 'date', 'format' => 'php:d.m.Y', 'timestampAttribute' => 'birthday_ts'],
['created', 'datetime', 'format' => 'php:Y-m-d H:i:s', 'timestampAttribute' => 'created', 'timestampAttributeFormat' => 'php:Y-m-d H:i:s'],
['start', 'date', 'min' => date('Y-m-d'), 'tooSmall' => 'Дата уже прошла'],
```

Без `format` берётся `dateFormat` компонента `formatter`. С `timestampAttribute` проверенное значение преобразуется в UNIX-timestamp и **записывается в атрибут** (можно в тот же самый) — удобно для сохранения в INT.

## Массивы и вложенность

:::kv
`each` — применить `rule` к каждому элементу массива; `allowMessageFromRule` (сообщение от вложенного правила), `stopOnFirstError`
:::

```php
['categoryIDs', 'each', 'rule' => ['integer']],
['emails', 'each', 'rule' => ['email'], 'allowMessageFromRule' => false, 'message' => 'Один из адресов неверен'],
```

Проверяет только один уровень; для сложных структур — свой валидатор. Не работает с `unique`/`exist` через `targetAttribute`.

## Проверки по базе данных

:::kv
`exist` — значение существует в таблице: `targetClass` (по умолчанию — класс модели), `targetAttribute` (столбец или карта `['a1' => 'b1']`), `filter` (доп. условие), `allowArray`, `targetRelation` (по связи AR, 2.0.14)
`unique` — значение уникально в таблице; те же опции, `comboNotUnique` (сообщение для составного ключа). Для AR исключает саму запись при обновлении
:::

```php
['a1', 'exist'],                                                  // столбец a1 в таблице модели
['category_id', 'exist', 'targetClass' => Category::class, 'targetAttribute' => 'id'],
['a1', 'exist', 'targetAttribute' => ['a1', 'a2']],               // пара (a1, a2) существует
['a1', 'exist', 'targetAttribute' => ['a2' => 'a1']],             // a1 существует в столбце… см. документацию: [значение атрибута => столбец]
['a1', 'exist', 'filter' => ['status' => 1]],
['user_id', 'exist', 'targetRelation' => 'user'],

['username', 'unique'],
['email', 'unique', 'targetClass' => User::class, 'filter' => ['status' => User::STATUS_ACTIVE]],
[['slug', 'lang'], 'unique', 'targetAttribute' => ['slug', 'lang']],   // комбинация уникальна
```

Оба не имеют клиентской реализации — используйте [AJAX-валидацию](validation#ajax-validaciya).

## Файлы и изображения

:::kv
`file` — `UploadedFile`: `extensions`, `mimeTypes` (`image/*`, `text/plain`), `minSize`, `maxSize`, `maxFiles` (0 — без ограничения), `checkExtensionByMimeType` (сверять расширение с реальным MIME, по умолчанию `true`), `wrongExtension`, `tooBig`, `tooMany`…
`image` — `file` + проверка изображения: `minWidth`, `maxWidth`, `minHeight`, `maxHeight`, `notImage`, `underWidth`, `overWidth`…
:::

```php
['file', 'file', 'extensions' => ['pdf', 'docx'], 'maxSize' => 5 * 1024 * 1024, 'skipOnEmpty' => false],
['avatar', 'image', 'extensions' => 'png, jpg', 'minWidth' => 100, 'maxWidth' => 1000, 'minHeight' => 100],
['docs', 'file', 'maxFiles' => 10],
```

Помните про `upload_max_filesize`/`post_max_size` в php.ini и `enctype="multipart/form-data"` — подробнее в разделе [Формы](forms#zagruzka-faylov).

## CAPTCHA

:::kv
`captcha` — сверяет ввод с виджетом `yii\captcha\Captcha`; `captchaAction` (по умолчанию `site/captcha`), `caseSensitive`
:::

```php
// модель
['verifyCode', 'captcha'],
// контроллер: действие captcha в actions()
'captcha' => ['class' => 'yii\captcha\CaptchaAction', 'fixedVerifyCode' => YII_ENV_TEST ? 'testme' : null],
// форма
<?= $form->field($model, 'verifyCode')->widget(Captcha::class) ?>
```

Требует расширения GD или ImageMagick с поддержкой FreeType.

## Шпаргалка по ключевым опциям

| Валидатор | Самое важное |
|---|---|
| `required` | `requiredValue`, `strict` |
| `string` | `min`, `max`, `length` |
| `integer`, `number` | `min`, `max` |
| `email`, `url` | `checkDNS` / `defaultScheme`, `enableIDN` |
| `compare` | `compareAttribute`, `operator`, `type` |
| `in` | `range`, `not`, `allowArray` |
| `date` | `format`, `timestampAttribute`, `min`, `max` |
| `each` | `rule` |
| `exist`, `unique` | `targetClass`, `targetAttribute`, `filter` |
| `file`, `image` | `extensions`, `maxSize`, `maxFiles`, `minWidth`… |
| `match` | `pattern`, `not` |
| `filter`, `trim`, `default` | `filter` / `chars` / `value` — меняют значение |

:::quiz Проверь себя
Q: Какой единственный валидатор проверяет пустые значения по умолчанию?
A: `required`; остальные пропускают пустые атрибуты, пока не указан `'skipOnEmpty' => false`.
Q: Что делает `timestampAttribute` у валидатора `date`?
A: Записывает в указанный атрибут UNIX-время (или строку в `timestampAttributeFormat`), полученное из проверенной даты.
Q: Почему `['end', 'compare', 'compareAttribute' => 'start', 'operator' => '>']` может считать 10 меньше 9?
A: Сравнение по умолчанию строковое; задайте `'type' => 'number'` (или сравнивайте даты как timestamp).
Q: Как проверить, что каждый элемент массива — целое число?
A: `['ids', 'each', 'rule' => ['integer']]`.
Q: Как разрешить массовое присваивание атрибуту без проверки?
A: Правилом `['attr', 'safe']`.
:::
