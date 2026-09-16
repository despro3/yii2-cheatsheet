---
id: formatting
title: Форматирование данных
part: output
summary: Компонент formatter — asDate/asDatetime/asRelativeTime, asInteger/asDecimal/asCurrency/asPercent, asSize/asShortSize, asBoolean/asEmail/asUrl/asHtml/asNtext; форматы ICU и php:, локаль и часовые пояса, nullDisplay; где форматы применяются автоматически (GridView, DetailView).
sources: output-formatting
---

:::lead
`Yii::$app->formatter` превращает «сырые» значения в человеческий вид с учётом локали: даты, числа, деньги, размеры файлов, логические флаги. Те же имена форматов используют `GridView` и `DetailView` в колонках (`'created_at:datetime'`), так что один компонент отвечает за весь вывод.
:::

## Как вызывать

```php
$formatter = Yii::$app->formatter;

echo $formatter->asDate('2014-01-01', 'long');        // January 1, 2014
echo $formatter->asPercent(0.125, 2);                 // 12.50%
echo $formatter->asEmail('cebe@example.com');         // <a href="mailto:…">…</a>
echo $formatter->asBoolean(true);                     // Yes
echo $formatter->asDate(null);                        // (not set)

// универсально — по имени формата
echo $formatter->format('2014-01-01', 'date');
echo $formatter->format(0.125, ['percent', 2]);        // формат с аргументами
```

`null` в любом методе выводится как `nullDisplay` (по умолчанию `(not set)`, локализуется).

## Настройка

```php title="config/web.php"
'components' => [
    'formatter' => [
        'dateFormat' => 'dd.MM.yyyy',
        'datetimeFormat' => 'dd.MM.yyyy HH:mm',
        'timeFormat' => 'HH:mm',
        'decimalSeparator' => ',',
        'thousandSeparator' => ' ',
        'currencyCode' => 'RUB',
        'locale' => 'ru-RU',           // по умолчанию — Yii::$app->language
        'timeZone' => 'Europe/Moscow', // по умолчанию — Yii::$app->timeZone
        'defaultTimeZone' => 'UTC',    // в каком поясе хранятся входные значения (2.0.1)
        'nullDisplay' => '—',
    ],
],
```

Для другого языка на лету — создать свой экземпляр: `new Formatter(['locale' => 'en-US'])`, или переключить `Yii::$app->language` до обращения к компоненту.

## Даты и время

:::kv
`asDate($value, $format)` — дата
`asTime($value, $format)` — время
`asDatetime($value, $format)` — дата и время
`asTimestamp($value)` — UNIX-время
`asRelativeTime($value, $ref)` — «5 minutes ago», «in 2 days»
`asDuration($value)` — интервал: «1 day, 2 hours»
:::

Входное значение — UNIX-timestamp, строка (всё, что понимает `strtotime()`: `'2014-01-01'`, `'now'`, `'+1 day'`), `DateTime`/`DateTimeInterface`, а с 2.0.1 — и строка вида `2014-01-01 00:00:00`.

### Форматы

```php
$formatter->asDate($v, 'short');            // 1/1/14      — short, medium (по умолчанию), long, full
$formatter->asDate($v, 'yyyy-MM-dd');       // синтаксис ICU
$formatter->asDate($v, 'php:Y-m-d');        // синтаксис PHP date()
$formatter->asDatetime($v, 'php:d.m.Y H:i');
```

| ICU | PHP | Пример |
|---|---|---|
| `yyyy` | `Y` | 2014 |
| `MM` / `MMM` / `MMMM` | `m` / `M` / `F` | 01 / Jan / January |
| `dd` | `d` | 05 |
| `EEE` / `EEEE` | `D` / `l` | Mon / Monday |
| `HH` / `hh a` | `H` / `h A` | 14 / 02 PM |
| `mm`, `ss` | `i`, `s` | 05, 09 |

### Часовые пояса

Значения без явного пояса считаются заданными в `defaultTimeZone` (по умолчанию UTC) и переводятся в `timeZone` при выводе. Храните время в UTC — тогда достаточно выставить `timeZone` под пользователя. У `DateTime` со своим поясом преобразование учитывает его.

```php
$formatter->timeZone = 'Europe/Berlin';
echo $formatter->asDatetime('2014-01-01 00:00:00');   // 1 января 2014, 01:00
```

Только даты (`asDate`) с 2.0.14 не сдвигаются часовым поясом, чтобы 1 января не превратилось в 31 декабря.

## Числа

:::kv
`asInteger($value)` — целое с разделителем тысяч
`asDecimal($value, $decimals, $options, $textOptions)` — дробное; `decimals` — знаков после запятой
`asPercent($value, $decimals)` — проценты (0.125 → 12.5%)
`asScientific($value)` — 1.25E+3
`asCurrency($value, $currency)` — деньги: «1 234,56 ₽»
`asSpellout($value)` — числа прописью (требует intl)
`asOrdinal($value)` — порядковое: 1st, 2nd
`asShortSize($value, $decimals)` — 12.4 KB, `asSize()` — 12.4 kibibytes; `sizeFormatBase` (1024 или 1000)
`asLength($value)`, `asShortLength()`, `asWeight()`, `asShortWeight()` — длина и вес в системе `systemOfUnits` (2.0.13)
:::

```php
$formatter->asInteger(1234567);          // 1,234,567
$formatter->asDecimal(1234.5678, 2);     // 1,234.57
$formatter->asCurrency(1234.5, 'EUR');   // €1,234.50
$formatter->asShortSize(1024 * 1024);    // 1 MB (sizeFormatBase = 1024)
$formatter->numberFormatterOptions = [NumberFormatter::MIN_FRACTION_DIGITS => 0, NumberFormatter::MAX_FRACTION_DIGITS => 2];
$formatter->numberFormatterSymbols = [NumberFormatter::CURRENCY_SYMBOL => '€'];
```

Настройки `NumberFormatter` (`numberFormatterOptions`, `numberFormatterTextOptions`, `numberFormatterSymbols`) применяются ко всем числовым форматам; те же ключи можно передать аргументами `$options`/`$textOptions` в конкретный вызов.

## Прочее

:::kv
`asRaw($value)` — как есть (только `nullDisplay`)
`asText($value)` — с HTML-экранированием
`asNtext($value)` — экранирование + переводы строк → `<br>`
`asParagraphs($value)` — абзацы → `<p>`
`asHtml($value, $config)` — HTML, очищенный через HtmlPurifier
`asEmail($value, $options)` — ссылка `mailto:`
`asUrl($value, $options)` — ссылка `<a>`
`asImage($value, $options)` — `<img>`
`asBoolean($value)` — `booleanFormat` (`['Нет', 'Да']`)
:::

## Где применяется автоматически

```php
// GridView и DetailView понимают формат в описании колонки
'columns' => [
    'created_at:datetime',
    'price:currency',
    ['attribute' => 'size', 'format' => ['shortSize', 1]],
    ['attribute' => 'is_active', 'format' => 'boolean'],
    'email:email',
    'description:ntext',
],
```

По умолчанию колонки выводятся форматом `text` (экранирование). Чтобы вывести HTML — формат `raw` или `html`.

> [!WARNING] Расширение intl
> Локализация чисел, дат и `asSpellout`/`asOrdinal` требуют PHP-расширения `intl`. Без него форматтер работает в упрощённом режиме (US-формат, без локализованных названий месяцев) и не переведёт `nullDisplay`/`booleanFormat`. Ставьте intl в production и dev одинаковых версий — иначе вывод будет отличаться.

:::quiz Проверь себя
Q: Как вывести дату в формате `31.12.2024` через форматтер?
A: `$formatter->asDate($v, 'php:d.m.Y')` или ICU `'dd.MM.yyyy'`, либо задать `dateFormat` в конфигурации компонента.
Q: Что вернёт `asDate(null)`?
A: Значение `nullDisplay` — по умолчанию `(not set)`.
Q: Как задать формат колонки в GridView?
A: Суффиксом после атрибута: `'created_at:datetime'`, `'price:currency'`, или ключом `format` в конфигурации колонки.
Q: Почему `asDatetime('2014-01-01 00:00:00')` показал час ночи?
A: Значение считается заданным в `defaultTimeZone` (UTC) и переводится в `timeZone` форматтера — например, Europe/Berlin (+1).
Q: Что произойдёт без расширения intl?
A: Форматирование работает, но без локализации: английские названия, US-разделители, нет `asSpellout()`/`asOrdinal()`.
:::
