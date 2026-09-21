# -*- coding: utf-8 -*-
"""Стандартная библиотека: дата и время, JSON, регулярные выражения, файлы, SPL."""

from model import topic

# --------------------------------------------------------------------------- Дата и время

topic(
    id='datetime', group='lib',
    title='Дата и время',
    cls='DateTimeImmutable',
    lead='Один класс на всё: разбор, форматирование, арифметика и часовые пояса. '
         'Берите неизменяемую версию — изменяемая портит объекты, которые вы кому-то передали.',
    badge='DateTimeImmutable',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'В PHP два почти одинаковых класса. `DateTime` меняет **сам себя**: '
                  '`$d->modify(\'+1 day\')` сдвигает объект, который вы, возможно, уже куда-то передали. '
                  '`DateTimeImmutable` возвращает новый объект и ничего не портит — '
                  'в новом коде используют только его.'),
            ('code', 'php', None, r'''$at = new DateTimeImmutable('2024-03-31 12:00', new DateTimeZone('Europe/Moscow'));

$at->format(DATE_ATOM);                    // '2024-03-31T12:00:00+03:00'
$at->setTimezone(new DateTimeZone('UTC')); // тот же момент в другом поясе: 09:00
$at->getTimestamp();                       // секунды с 1970 года

$tomorrow = $at->modify('+1 day');         // новый объект
$at->format('d.m');                        // 31.03 — исходный не изменился

$start = new DateTimeImmutable('2024-01-01');
$end   = new DateTimeImmutable('2024-03-01');
$diff  = $start->diff($end);               // DateInterval
$diff->days;                               // 60 — всего дней
$diff->m;                                  // 2  — «месяцев и дней», а не месяцев всего

$start < $end;                             // объекты дат сравниваются напрямую'''),
            ('h', 'Разбор строки'),
            ('code', 'php', None, r'''new DateTimeImmutable('2024-03-31');            // ISO — понимается всегда
new DateTimeImmutable('now');
new DateTimeImmutable('first day of next month');
new DateTimeImmutable('@1700000000');           // из метки времени, пояс UTC

DateTimeImmutable::createFromFormat('d.m.Y', '31.03.2024');   // свой формат
DateTimeImmutable::createFromFormat('!d.m.Y', '31.03.2024');  // ! обнуляет время
DateTimeImmutable::createFromTimestamp(1700000000.5);         // с 8.4, дробные секунды

// разбор может не удаться — проверять обязательно
$d = DateTimeImmutable::createFromFormat('!d.m.Y', $input);
if ($d === false) {
    throw new InvalidArgumentException('ожидался формат дд.мм.гггг');
}'''),
            ('note', 'trap', 'createFromFormat без «!» подставляет текущее время',
             'Разбирая `\'31.03.2024\'` по формату `\'d.m.Y\'`, PHP возьмёт **сегодняшние** часы, минуты '
             'и секунды. Две такие даты никогда не окажутся равны, а сравнение «начало дня» '
             'будет работать через раз. Восклицательный знак в начале формата обнуляет всё, '
             'что в нём не указано.'),
            ('note', 'trap', '«+1 month» от 31 января — это 2 марта',
             'PHP прибавляет месяц к номеру месяца, а потом нормализует несуществующую дату: '
             '31 февраля превращается во 2 марта. Если нужен «последний день следующего месяца», '
             'так и пишут: `modify(\'last day of next month\')`.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'new DateTimeImmutable($time, $tz)', 'd': 'Разбирает строку в человеческом формате: ISO, `now`, `+3 days`, `next monday`, `first day of next month`.', 'o': 'без пояса — date.timezone', 'c': "new DateTimeImmutable('first day of next month midnight');"},
                {'n': 'createFromFormat()', 'd': 'Разбор строго по формату. Возвращает `false` при несовпадении, поэтому результат всегда проверяют. `!` в начале обнуляет неуказанные поля.', 'o': 'getLastErrors() — что именно не так', 'c': "$d = DateTimeImmutable::createFromFormat('!Y-m-d', $raw);\nif ($d === false) { /* ... */ }"},
                {'n': 'createFromTimestamp()', 'd': 'Из метки времени, в том числе дробной. До 8.4 писали `new DateTimeImmutable(\'@\' . $ts)` — и теряли микросекунды.', 'o': 'результат в UTC', 'v': '8.4', 'c': "DateTimeImmutable::createFromTimestamp($ts);"},
                {'n': 'format()', 'd': 'Строка по шаблону. Для машин берут готовые константы форматов, для людей — свой шаблон.', 'o': 'DATE_ATOM, DATE_RFC3339, DATE_COOKIE', 'c': "$d->format('d.m.Y H:i');   // 31.03.2024 12:00\n$d->format(DATE_ATOM);      // 2024-03-31T12:00:00+03:00\n$d->format('u');            // микросекунды"},
                {'n': 'modify()', 'd': 'Относительный сдвиг строкой. Понимает `+2 weeks`, `last day of this month`, `monday next week`.', 'o': 'возвращает новый объект', 'c': "$d->modify('-1 day')->modify('midnight');"},
                {'n': 'add() / sub()', 'd': 'Сдвиг на `DateInterval`. В отличие от `modify()` интервал можно собрать программно и передать дальше.', 'o': 'DateInterval принимает ISO 8601', 'c': "$d->add(new DateInterval('P1M'));    // +1 месяц\n$d->sub(new DateInterval('PT30M'));  // -30 минут"},
                {'n': 'diff()', 'd': 'Разница двух дат как `DateInterval`. Поле `days` — всего дней, `y/m/d` — «лет, месяцев и дней», их нельзя складывать между собой.', 'o': 'invert — знак разницы', 'c': "$age = $born->diff(new DateTimeImmutable())->y;"},
                {'n': 'setTime() / setDate() / setTimezone()', 'd': 'Точечная замена части даты. `setTimezone()` меняет представление, но не сам момент времени.', 'o': 'все возвращают новый объект', 'c': "$dayStart = $d->setTime(0, 0);\n$utc = $d->setTimezone(new DateTimeZone('UTC'));"},
                {'n': 'DateTimeZone', 'd': 'Часовой пояс по названию из базы IANA. Смещение `+03:00` тоже работает, но не знает про переход на летнее время.', 'o': 'listIdentifiers()', 'c': "new DateTimeZone('Europe/Moscow');\n(new DateTimeZone('Europe/Berlin'))->getOffset($d);"},
                {'n': 'DateInterval', 'd': 'Длительность: `P1Y2M3DT4H5M6S`. Аккуратно: «месяц» — не фиксированное число дней, результат зависит от даты, к которой прибавляют.', 'o': 'createFromDateString()', 'c': "new DateInterval('P30D');\nDateInterval::createFromDateString('2 weeks');"},
                {'n': 'DatePeriod', 'd': 'Последовательность дат с шагом — для отчётов по дням и календарей. По умолчанию конец не включается.', 'o': 'INCLUDE_END_DATE — с 8.2', 'c': "foreach (new DatePeriod($from, new DateInterval('P1D'), $to) as $day) {\n    $rows[$day->format('Y-m-d')] = 0;\n}"},
                {'n': 'DateTimeInterface', 'd': 'Общий тип `DateTime` и `DateTimeImmutable`. Принимайте его в параметрах, возвращайте конкретный неизменяемый класс.', 'o': 'свой класс реализовать не может', 'c': "function isPast(DateTimeInterface $at): bool\n{\n    return $at < new DateTimeImmutable();\n}"},
                {'n': 'time() / date() / strtotime()', 'd': 'Процедурная тройка из PHP 4. Работает, но теряет пояс, не проверяет ошибки и не даёт типов: `strtotime(\'вчера\')` вернёт `false`, и об этом никто не узнает.', 'o': 'для нового кода не нужны', 'c': "date('Y-m-d', time());   // то же самое делает format()"},
                {'n': 'hrtime() / microtime()', 'd': 'Замер длительности. `hrtime(true)` даёт наносекунды монотонных часов — их не сдвинет синхронизация времени посреди замера.', 'o': 'для дат не годятся', 'c': "$t = hrtime(true);\n// ...\n$ms = (hrtime(true) - $t) / 1e6;"},
                {'n': 'checkdate() / cal_days_in_month()', 'd': 'Проверка существования даты и число дней в месяце — без создания объектов.', 'o': 'checkdate(месяц, день, год)', 'c': "checkdate(2, 30, 2024);   // false"},
                {'n': 'IntlDateFormatter', 'd': 'Локализованный вывод из расширения `intl`: названия месяцев и дней на нужном языке, местные форматы.', 'o': 'format() PHP не переводит', 'c': "$f = new IntlDateFormatter('ru_RU', IntlDateFormatter::LONG, IntlDateFormatter::NONE);\n$f->format($d);   // '31 марта 2024 г.'"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Часы как зависимость'),
            ('code', 'php', 'src/Clock.php', r'''interface Clock                                  // так же выглядит PSR-20
{
    public function now(): DateTimeImmutable;
}

final class SystemClock implements Clock
{
    public function __construct(private readonly DateTimeZone $tz = new DateTimeZone('UTC')) {}

    public function now(): DateTimeImmutable
    {
        return new DateTimeImmutable('now', $this->tz);
    }
}

final class FrozenClock implements Clock
{
    public function __construct(private DateTimeImmutable $at) {}

    public function now(): DateTimeImmutable
    {
        return $this->at;
    }
}

// в тесте «через 30 дней подписка истекла» больше не нужно ждать 30 дней'''),
            ('note', 'tip', 'Хранить в UTC, показывать в поясе пользователя',
             'В базе — момент времени в UTC, в интерфейсе — `setTimezone()` на пояс пользователя. '
             'Это избавляет от целого класса ошибок: переход на летнее время, переезд сервера, '
             'пользователи из разных стран и «час, который случился дважды».'),
            ('h', 'Диапазон дат без дыр'),
            ('code', 'php', None, r'''$from = new DateTimeImmutable('2024-01-01');
$to   = new DateTimeImmutable('2024-01-08');

$byDay = [];
foreach (new DatePeriod($from, new DateInterval('P1D'), $to) as $day) {
    $byDay[$day->format('Y-m-d')] = 0;      // заготовка с нулями
}

foreach ($rowsFromDb as $row) {
    $byDay[$row['day']] = (int) $row['count'];   // дни без данных останутся нулями
}'''),
            ('note', 'warn', 'Сравнивать даты строками можно только в ISO',
             '`\'2024-03-31\' < \'2024-04-01\'` работает, потому что порядок символов совпадает с порядком дат. '
             'Стоит формату стать `d.m.Y` — и сравнение начинает врать. Сравнивайте объекты: '
             'у `DateTimeImmutable` операторы `<`, `>`, `==` делают ровно то, что нужно.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- JSON

topic(
    id='json', group='lib',
    title='JSON и сериализация',
    cls='json_encode()',
    lead='Две функции с десятком флагов и одна привычка: всегда включать исключения, '
         'иначе ошибка разбора выглядит как «пришёл null».',
    badge='16 флагов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', '`json_encode()` превращает значение в строку, `json_decode()` — обратно. '
                  'Без флага `JSON_THROW_ON_ERROR` обе при ошибке возвращают `false` или `null` '
                  'и оставляют код ошибки в глобальном состоянии — это главный источник '
                  'молчаливых потерь данных.'),
            ('code', 'php', None, r'''$json = json_encode($data, JSON_THROW_ON_ERROR
    | JSON_UNESCAPED_UNICODE      // «привет», а не при...
    | JSON_UNESCAPED_SLASHES      // http://a/b вместо http:\/\/a\/b
    | JSON_PRETTY_PRINT);         // с отступами: для логов и файлов

$data = json_decode($json, associative: true, flags: JSON_THROW_ON_ERROR);

// без ассоциативного режима объекты становятся stdClass
$obj = json_decode('{"a":1}');        // $obj->a
$arr = json_decode('{"a":1}', true);  // $arr['a']

json_validate($json);                 // с 8.3: проверить, не разбирая'''),
            ('h', 'Что уедет в JSON от объекта'),
            ('code', 'php', None, r'''final class Order implements JsonSerializable
{
    public function __construct(
        public readonly int $id,
        private readonly string $secret,
        public readonly DateTimeImmutable $at,
    ) {}

    public function jsonSerialize(): array
    {
        return [
            'id' => $this->id,
            'at' => $this->at->format(DATE_ATOM),   // иначе выедет структура DateTime
        ];
    }
}

json_encode(new Order(1, 'токен', new DateTimeImmutable()));
// {"id":1,"at":"2024-03-31T12:00:00+03:00"} — приватное поле не попало'''),
            ('note', 'trap', 'Пустой массив в JSON — это [], а не {}',
             'PHP не различает список и словарь, а JSON различает. Массив `[]` закодируется как `[]`, '
             'массив с дырами в ключах — как объект. Если API обещает объект, приводите явно: '
             '`(object) $map` или `JSON_FORCE_OBJECT`; если массив — закрывайте цепочку `array_values()`.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'JSON_THROW_ON_ERROR', 'd': 'Бросать `JsonException` вместо возврата `false`/`null`. Ставьте всегда: без него ошибка разбора неотличима от значения `null` в данных.', 'o': 'работает у обеих функций', 'c': "json_decode($raw, true, flags: JSON_THROW_ON_ERROR);"},
                {'n': 'JSON_UNESCAPED_UNICODE', 'd': 'Не превращать кириллицу в `\\uXXXX`. Размер ответа меньше, логи читаются глазами.', 'o': 'с INVALID_UTF8_SUBSTITUTE — безопаснее', 'c': "json_encode($data, JSON_UNESCAPED_UNICODE);"},
                {'n': 'JSON_UNESCAPED_SLASHES', 'd': 'Не экранировать слеши. Экранирование нужно было для вставки JSON в HTML — в обычном API оно просто мусор.', 'o': 'в HTML безопаснее HEX_TAG', 'c': "json_encode($url, JSON_UNESCAPED_SLASHES);"},
                {'n': 'JSON_PRETTY_PRINT', 'd': 'Отступы по четыре пробела. Для файлов конфигурации и логов — да, для ответа API — лишние байты.', 'o': 'отступ не настраивается', 'c': "file_put_contents($f, json_encode($cfg, JSON_PRETTY_PRINT));"},
                {'n': 'JSON_PRESERVE_ZERO_FRACTION', 'd': 'Сохранять `.0` у дробных чисел: `1.0` не превратится в `1`. Важно для API, где тип поля обязан быть стабильным.', 'o': 'иначе float 1.0 → 1', 'c': "json_encode(['sum' => 1.0], JSON_PRESERVE_ZERO_FRACTION);   // {\"sum\":1.0}"},
                {'n': 'JSON_FORCE_OBJECT', 'd': 'Кодировать любой массив как объект. Грубый инструмент: применяется ко всей структуре сразу, а не к одному полю.', 'o': 'точнее — приведение (object)', 'c': "json_encode([], JSON_FORCE_OBJECT);   // {}"},
                {'n': 'JSON_HEX_TAG | HEX_AMP | HEX_APOS | HEX_QUOT', 'd': 'Экранирование символов, опасных при вставке JSON прямо в HTML-страницу. Нужны, когда JSON печатают внутрь `<script>`.', 'o': 'вместе с THROW_ON_ERROR', 'c': "echo '<script>const d = '\n    . json_encode($d, JSON_HEX_TAG | JSON_HEX_AMP)\n    . ';</script>';"},
                {'n': 'JSON_INVALID_UTF8_SUBSTITUTE', 'd': 'Заменять битые байты символом замены вместо провала кодирования. Спасает логирование данных из внешних источников.', 'o': 'INVALID_UTF8_IGNORE — выбросить', 'c': "json_encode($raw, JSON_INVALID_UTF8_SUBSTITUTE);"},
                {'n': 'JSON_BIGINT_AS_STRING', 'd': 'Большие целые из чужого JSON приходят строкой, а не теряют точность во `float`. Актуально для идентификаторов из внешних API.', 'o': 'флаг декодирования', 'c': "json_decode($raw, true, 512, JSON_BIGINT_AS_STRING);"},
                {'n': 'json_validate()', 'd': 'Проверка синтаксиса без построения структуры: заметно дешевле по памяти на больших телах запросов.', 'o': 'те же ошибки, что у decode', 'v': '8.3', 'c': "if (!json_validate($body)) {\n    return new Response(400, 'невалидный JSON');\n}"},
                {'n': 'Глубина вложенности', 'd': 'Третий аргумент `json_decode()` и второй-третий `json_encode()`. Превышение — ошибка, и это защита от бесконечной рекурсии в данных.', 'o': 'по умолчанию 512', 'c': "json_decode($raw, true, 8, JSON_THROW_ON_ERROR);"},
                {'n': 'JsonSerializable', 'd': 'Класс сам решает, во что превращаться. Без него кодируются публичные свойства — обычно не то, что нужно наружу.', 'o': 'jsonSerialize(): mixed', 'c': "public function jsonSerialize(): array\n{\n    return ['id' => $this->id];\n}"},
                {'n': 'serialize() / unserialize()', 'd': 'Родной формат PHP: сохраняет типы и классы. Никогда не применяйте `unserialize()` к данным извне — это выполнение чужого кода через магические методы.', 'o': "allowed_classes => false", 'c': "unserialize($raw, ['allowed_classes' => false]);"},
                {'n': '__serialize() / __unserialize()', 'd': 'Что именно сохранять и как восстанавливать объект. Заменяют старый интерфейс `Serializable` и пару `__sleep()/__wakeup()`.', 'o': 'работают с массивом', 'v': '8.1', 'c': "public function __serialize(): array\n{\n    return ['id' => $this->id];\n}"},
                {'n': 'var_export() / var_dump() / print_r()', 'd': 'Три способа посмотреть на значение. `var_export()` даёт **валидный PHP** — его удобно писать в кэш конфигурации, который потом просто `require`.', 'o': 'второй аргумент — вернуть строкой', 'c': "file_put_contents(\n    'cache/config.php',\n    '<?php return ' . var_export($config, true) . ';',\n);"},
                {'n': 'json_last_error() / json_last_error_msg()', 'd': 'Код и текст последней ошибки — нужны только там, где по какой-то причине нельзя включить исключения.', 'o': 'состояние глобальное', 'c': "if (json_last_error() !== JSON_ERROR_NONE) {\n    throw new RuntimeException(json_last_error_msg());\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Одна обёртка на весь проект'),
            ('code', 'php', 'src/Support/Json.php', r'''declare(strict_types=1);

final class Json
{
    private const int FLAGS = JSON_THROW_ON_ERROR
        | JSON_UNESCAPED_UNICODE
        | JSON_UNESCAPED_SLASHES
        | JSON_PRESERVE_ZERO_FRACTION;

    public static function encode(mixed $value, bool $pretty = false): string
    {
        return json_encode($value, self::FLAGS | ($pretty ? JSON_PRETTY_PRINT : 0));
    }

    /** @return array<string, mixed> */
    public static function decode(string $json): array
    {
        $data = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        if (!is_array($data)) {
            throw new JsonException('ожидался объект или массив');
        }
        return $data;
    }
}'''),
            ('note', 'tip', 'Флаги задаются один раз, а не в каждом вызове',
             'Набор флагов — это решение уровня проекта: кодировка, экранирование, точность чисел. '
             'Когда он повторяется в тридцати местах, рано или поздно где-то забудут '
             '`JSON_THROW_ON_ERROR` — и получат `null` вместо данных без единого сообщения.'),
            ('note', 'warn', 'unserialize() на данных пользователя — дыра',
             'Разбор сериализованной строки создаёт объекты и вызывает их магические методы — '
             'этого достаточно для запуска чужого кода в вашем процессе. '
             'Для данных извне только JSON. Если формат PHP всё же нужен, '
             'обязателен второй аргумент `[\'allowed_classes\' => false]`.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Регулярные выражения

topic(
    id='regex', group='lib',
    title='Регулярные выражения',
    cls='preg_match()',
    lead='Движок PCRE, десять функций и один модификатор, без которого кириллица ломается. '
         'Плюс понимание, где регулярное выражение — не тот инструмент.',
    badge='10 функций',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Шаблон — это строка, внутри которой сам шаблон обёрнут **разделителями**, '
                  'а после закрывающего разделителя идут модификаторы. '
                  'Для текста на кириллице модификатор `u` обязателен: без него движок работает с байтами, '
                  'и `.` съедает половину буквы.'),
            ('code', 'php', None, r'''//  /       шаблон        /  модификаторы
$re = '/^(?<year>\d{4})-(\d{2})$/u';

if (preg_match($re, '2024-03', $m)) {
    $m[0];        // '2024-03'  — всё совпадение
    $m[1];        // '2024'     — первая группа
    $m['year'];   // '2024'     — она же по имени
    $m[2];        // '03'
}

preg_match_all('/\d+/u', 'a1 b22 c333', $all);   // $all[0] === ['1', '22', '333']
preg_replace('/\s+/u', ' ', $text);              // схлопнуть пробелы
preg_split('/[\s,]+/u', $line);                  // разбить по пробелам и запятым
preg_quote($userInput, '/');                     // экранировать пользовательский ввод'''),
            ('h', 'Модификаторы, которые действительно нужны'),
            ('kv', [
                ('u', 'UTF-8: шаблон и строка — символы, а не байты. Для текста обязателен'),
                ('i', 'без учёта регистра; с `u` работает и для кириллицы'),
                ('m', '`^` и `$` совпадают с началом и концом **каждой строки**, а не всего текста'),
                ('s', '`.` начинает совпадать и с переводом строки'),
                ('x', 'пробелы и переводы строк в шаблоне игнорируются — можно писать с отступами и комментариями'),
            ]),
            ('note', 'trap', 'Без модификатора u кириллица — это байты',
             '`preg_match(\'/^.{3}$/\', \'абв\')` не совпадёт: в строке шесть байтов. '
             'А `\\w` без `u` не считает кириллицу буквой. Добавили `u` — и строка обязана быть '
             'корректным UTF-8, иначе функция вернёт `false`, а `preg_last_error_msg()` скажет почему.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'preg_match()', 'd': 'Одно совпадение. Возвращает `1`, `0` или `false` — последнее означает ошибку шаблона, и проверять надо строго.', 'o': 'PREG_OFFSET_CAPTURE, PREG_UNMATCHED_AS_NULL', 'c': "if (preg_match('/^\\d+$/', $s) === 1) { }"},
                {'n': 'preg_match_all()', 'd': 'Все совпадения. Порядок результата задаётся флагом: по шаблонам (по умолчанию) или по наборам — второе почти всегда удобнее.', 'o': 'PREG_SET_ORDER | PREG_PATTERN_ORDER', 'c': "preg_match_all('/(\\w+)=(\\d+)/u', $s, $m, PREG_SET_ORDER);\nforeach ($m as [$all, $key, $value]) { }"},
                {'n': 'preg_replace()', 'd': 'Замена с обратными ссылками `$1`, `${1}`, `\\1`. Принимает массивы шаблонов и замен — тогда они применяются по очереди.', 'o': 'limit и count по ссылке', 'c': "preg_replace('/(\\d{4})-(\\d{2})/u', '$2.$1', $s);"},
                {'n': 'preg_replace_callback()', 'd': 'Замена результатом функции. Нужна везде, где замена зависит от совпадения: подстановка переводов, форматирование чисел, подсветка.', 'o': '_array — свой колбэк на шаблон', 'c': "preg_replace_callback('/\\{(\\w+)\\}/u',\n    fn(array $m): string => $vars[$m[1]] ?? $m[0],\n    $template);"},
                {'n': 'preg_split()', 'd': 'Разбиение по шаблону. Флаг `PREG_SPLIT_NO_EMPTY` убирает пустые куски, `DELIM_CAPTURE` оставляет разделители.', 'o': 'предел частей — третий аргумент', 'c': "preg_split('/\\R/u', $text);   // по любым переводам строки\npreg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);   // на символы"},
                {'n': 'preg_grep()', 'd': 'Фильтр массива по шаблону, с сохранением ключей. Короче, чем `array_filter()` с `preg_match()` внутри.', 'o': 'PREG_GREP_INVERT — наоборот', 'c': "$php = preg_grep('/\\.php$/', $files);"},
                {'n': 'preg_quote()', 'd': 'Экранирует спецсимволы, чтобы строку можно было вставить в шаблон. Второй аргумент — разделитель, его тоже нужно экранировать.', 'o': 'обязателен для пользовательского ввода', 'c': "$re = '/' . preg_quote($needle, '/') . '/iu';"},
                {'n': 'Именованные группы', 'd': '`(?<name>…)` делает результат самодокументируемым: `$m[\'year\']` вместо `$m[3]`, и порядок групп можно менять без правки кода.', 'o': 'доступны и по номеру', 'c': "preg_match('/(?<h>\\d{2}):(?<m>\\d{2})/', $s, $t);\n$t['h'];"},
                {'n': 'PREG_UNMATCHED_AS_NULL', 'd': 'Несовпавшие группы приходят как `null`, а не пустая строка. Позволяет отличить «группа не совпала» от «совпала с пустотой».', 'o': 'флаг preg_match', 'c': "preg_match($re, $s, $m, PREG_UNMATCHED_AS_NULL);\n$m['suffix'] ?? 'нет';"},
                {'n': 'Незахватывающие группы', 'd': '`(?:…)` группирует, но не попадает в результат — меньше мусора в `$matches` и быстрее работа движка.', 'o': 'для альтернатив внутри шаблона', 'c': "'/^(?:https?|ftp):\\/\\//'"},
                {'n': 'Опережающие и ретроспективные проверки', 'd': '`(?=…)`, `(?!…)`, `(?<=…)`, `(?<!…)` — условия, которые не съедают текст. На них строят «пароль, где есть цифра и буква».', 'o': 'ретроспектива требует фиксированной длины', 'c': "'/^(?=.*\\d)(?=.*[A-Za-z]).{8,}$/u'"},
                {'n': 'preg_last_error_msg()', 'd': 'Почему функция вернула `false`: битый UTF-8, превышен лимит возвратов, слишком глубокая рекурсия.', 'o': 'preg_last_error() — код', 'c': "if (preg_match($re, $s) === false) {\n    throw new RuntimeException(preg_last_error_msg());\n}"},
                {'n': 'pcre.backtrack_limit', 'd': 'Предел работы движка. При его превышении функция возвращает `false` — на больших строках это выглядит как «регулярка иногда не работает».', 'o': 'pcre.jit, pcre.recursion_limit', 'c': "pcre.backtrack_limit=1000000", 'lang': 'ini'},
                {'n': 'filter_var()', 'd': 'Не регулярное выражение, но чаще всего именно его и нужно: проверка почты, URL, IP, целого числа — готовая и без шаблонов.', 'o': 'FILTER_VALIDATE_EMAIL, URL, INT, IP, BOOL', 'c': "filter_var($email, FILTER_VALIDATE_EMAIL) !== false;\nfilter_var($n, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Длинный шаблон читается только с модификатором x'),
            ('code', 'php', None, r'''$re = '/
    ^
    (?<protocol>https?)  ://          # схема
    (?<host>[^\/:\s]+)                # хост
    (?: : (?<port>\d+) )?             # необязательный порт
    (?<path>\/[^\s?]*)?               # путь
    $
/xu';

preg_match($re, 'https://example.com:8443/api/v1', $m);
$m['host'];   // 'example.com'
$m['port'];   // '8443' '''),
            ('note', 'warn', 'Катастрофический возврат',
             'Шаблоны вида `(\\w+\\s?)+$` на длинной строке без совпадения заставляют движок перебирать '
             'экспоненциальное число вариантов: запрос висит, процессор занят. '
             'Лечится конкретикой вместо вложенных квантификаторов и ограничением длины входа '
             '**до** проверки шаблоном.'),
            ('note', 'tip', 'Проверять HTML регулярным выражением не нужно',
             'Для HTML есть `DOMDocument` и `Dom\\HTMLDocument` (8.4), для CSV — `fgetcsv()`, '
             'для почты и URL — `filter_var()`, для JSON — `json_decode()`. '
             'Регулярное выражение хорошо там, где формат **простой и строгий**: '
             'номер телефона, код купона, строка лога.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Файлы и потоки

topic(
    id='files', group='lib',
    title='Файлы и потоки',
    cls='fopen() · php://',
    lead='Файл, сетевое соединение, память и стандартный ввод — для PHP это один и тот же поток, '
         'который открывают одной функцией.',
    badge='обёртки php://',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Всё, что читается и пишется, в PHP — **поток**. Путь при открытии может быть обычным файлом, '
                  'адресом `https://`, псевдофайлом `php://memory` или чем-то, что зарегистрировала '
                  'библиотека. Поэтому функции работы с файлами одинаково читают и локальный CSV, '
                  'и тело HTTP-запроса.'),
            ('code', 'php', None, r'''// целиком — когда файл заведомо небольшой
$text = file_get_contents($path);
file_put_contents($path, $text, LOCK_EX);
file_put_contents($log, $line . PHP_EOL, FILE_APPEND | LOCK_EX);

// по частям — когда размер неизвестен
$fh = fopen($path, 'rb');
try {
    while (($line = fgets($fh)) !== false) {
        // ...
    }
} finally {
    fclose($fh);
}

// псевдопотоки
$body = file_get_contents('php://input');     // сырое тело запроса
$buffer = fopen('php://temp', 'r+');          // память, с переездом на диск после 2 МБ
$stdout = fopen('php://stdout', 'w');'''),
            ('h', 'Режимы открытия'),
            ('kv', [
                ("'r' / 'r+'", 'чтение / чтение и запись; файл должен существовать, указатель в начале'),
                ("'w' / 'w+'", 'запись; файл создаётся или **обрезается до нуля**'),
                ("'a' / 'a+'", 'дозапись в конец; существующее содержимое остаётся'),
                ("'x' / 'x+'", 'создать и писать; если файл уже есть — ошибка. Так делают файлы-замки'),
                ("'c' / 'c+'", 'открыть или создать без обрезания; подходит для `flock()` перед записью'),
                ("'b'", 'двоичный режим: добавляйте всегда, иначе Windows подменяет переводы строк'),
            ]),
            ('note', 'trap', "Режим 'w' стирает файл в момент открытия",
             'Не при записи, а именно при `fopen()`. Если дальше код упадёт с исключением, '
             'на диске останется пустой файл вместо прежних данных. '
             'Для безопасной перезаписи пишут во временный файл и затем переименовывают.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'file_get_contents() / file_put_contents()', 'd': 'Весь файл одной строкой. Второе умеет дозапись и блокировку и возвращает число записанных байтов или `false`.', 'o': 'FILE_APPEND, LOCK_EX', 'c': "$n = file_put_contents($path, $data, LOCK_EX);\nif ($n === false) {\n    throw new RuntimeException(\"не записалось: $path\");\n}"},
                {'n': 'fopen() / fgets() / fread() / fwrite() / fclose()', 'd': 'Поштучная работа с потоком. `fgets()` читает строку, `fread()` — заданное число байтов, `feof()` сообщает о конце.', 'o': 'режимы r, w, a, x, c + b', 'c': "$fh = fopen('php://stdin', 'rb');\nwhile (!feof($fh)) {\n    $chunk = fread($fh, 8192);\n}"},
                {'n': 'fgetcsv() / fputcsv()', 'd': 'CSV построчно, с учётом кавычек и экранирования. Читать CSV через `explode(\',\')` нельзя: запятая внутри кавычек ломает разбор.', 'o': 'разделитель и ограничитель настраиваются', 'c': "while (($row = fgetcsv($fh, 0, ';')) !== false) {\n    [$id, $name] = $row;\n}"},
                {'n': 'file() / readfile()', 'd': 'Файл в массив строк и файл сразу в вывод. Первое держит в памяти всё — для больших файлов не годится.', 'o': 'FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES', 'c': "$lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);"},
                {'n': 'Обёртки php://', 'd': 'Псевдофайлы: `input` — тело запроса, `output` — вывод, `memory` и `temp` — буферы, `filter` — конвейер преобразований.', 'o': 'php://temp переезжает на диск', 'c': "$json = json_decode(file_get_contents('php://input'), true);\n$csv = fopen('php://temp', 'r+');"},
                {'n': 'stream_context_create()', 'd': 'Настройки для потока: заголовки и метод HTTP, таймаут, проверка сертификата. Позволяет сделать POST без curl.', 'o': 'таймаут и redirects', 'c': "$ctx = stream_context_create(['http' => [\n    'method' => 'POST',\n    'header' => \"Content-Type: application/json\\r\\n\",\n    'content' => $json,\n    'timeout' => 5,\n]]);\nfile_get_contents($url, false, $ctx);"},
                {'n': 'flock()', 'd': 'Блокировка файла между процессами. Совместная (`LOCK_SH`) и исключительная (`LOCK_EX`); `LOCK_NB` не ждёт освобождения.', 'o': 'не работает на некоторых сетевых ФС', 'c': "$fh = fopen($path, 'c');\nif (flock($fh, LOCK_EX | LOCK_NB)) {\n    // мы единственные, кто пишет\n}"},
                {'n': 'rename() / copy() / unlink()', 'd': 'Переименование в пределах файловой системы атомарно — на этом строят безопасную перезапись. `unlink()` удаляет файл, `rmdir()` — пустой каталог.', 'o': 'проверяйте результат', 'c': "$tmp = $path . '.tmp';\nfile_put_contents($tmp, $data);\nrename($tmp, $path);   // читатели видят либо старое, либо новое"},
                {'n': 'mkdir() / is_dir() / scandir() / glob()', 'd': 'Каталоги: создать (с `true` — рекурсивно), проверить, перечислить. `glob()` понимает шаблоны с `*` и `{a,b}`.', 'o': 'права третьим аргументом', 'c': "mkdir($dir, 0775, true);\nforeach (glob($dir . '/*.{php,phtml}', GLOB_BRACE) as $file) { }"},
                {'n': 'pathinfo() / basename() / dirname() / realpath()', 'd': 'Разбор пути. `realpath()` разворачивает `..` и симлинки и возвращает `false`, если путь не существует, — на этом проверяют выход за пределы каталога.', 'o': 'PATHINFO_EXTENSION', 'c': "$ext = pathinfo($name, PATHINFO_EXTENSION);\n$real = realpath($base . '/' . $user);\nif ($real === false || !str_starts_with($real, $base)) {\n    throw new RuntimeException('путь вне каталога');\n}"},
                {'n': 'tempnam() / tmpfile() / sys_get_temp_dir()', 'd': 'Временные файлы. `tmpfile()` удаляется сам при закрытии — удобно для промежуточных выгрузок.', 'o': 'каталог из окружения', 'c': "$tmp = tempnam(sys_get_temp_dir(), 'report_');"},
                {'n': 'finfo / mime_content_type()', 'd': 'Определение типа по содержимому, а не по расширению. Единственный осмысленный способ проверить загруженный файл.', 'o': 'расширению доверять нельзя', 'c': "$mime = (new finfo(FILEINFO_MIME_TYPE))->file($uploaded);\nif (!in_array($mime, ['image/png', 'image/jpeg'], true)) {\n    throw new RuntimeException('только png и jpeg');\n}"},
                {'n': 'fsync() / fdatasync()', 'd': 'Сбросить записанное на диск по-настоящему. До 8.1 из PHP это было недоступно, и «записали» означало только «отдали операционной системе».', 'o': 'после fwrite и перед fclose', 'v': '8.1', 'c': "fwrite($fh, $data);\nfsync($fh);"},
                {'n': 'SplFileObject / SplFileInfo', 'd': 'Объектная работа с файлом: итератор по строкам, `fgetcsv()` как метод, информация о файле без ручного `stat()`.', 'o': 'READ_CSV, SKIP_EMPTY', 'c': "$f = new SplFileObject($path);\n$f->setFlags(SplFileObject::READ_CSV);\nforeach ($f as $row) { }"},
                {'n': 'is_readable() / file_exists() / filesize()', 'd': 'Проверки перед работой. Между проверкой и открытием файл может исчезнуть — поэтому результат `fopen()` всё равно проверяют.', 'o': 'clearstatcache() сбрасывает кэш', 'c': "if (!is_readable($path)) {\n    throw new RuntimeException(\"нет доступа: $path\");\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Атомарная перезапись'),
            ('code', 'php', 'src/Support/write_atomic.php', r'''function writeAtomic(string $path, string $data): void
{
    $tmp = $path . '.' . bin2hex(random_bytes(4)) . '.tmp';

    $fh = fopen($tmp, 'wb');
    if ($fh === false) {
        throw new RuntimeException("не открылся временный файл: $tmp");
    }
    try {
        if (fwrite($fh, $data) === false) {
            throw new RuntimeException("не записалось: $tmp");
        }
        fsync($fh);                 // данные действительно на диске
    } finally {
        fclose($fh);
    }

    if (!rename($tmp, $path)) {     // переименование в пределах ФС атомарно
        unlink($tmp);
        throw new RuntimeException("не переименовался: $tmp");
    }
}'''),
            ('note', 'tip', 'Загруженные файлы проверяют по содержимому',
             '`$_FILES[\'f\'][\'type\']` приходит от браузера и подделывается тривиально, '
             'расширение — тем более. Реальный тип даёт `finfo`, а сам файл берут '
             'через `move_uploaded_file()` — она проверяет, что файл действительно загружен, '
             'а не подсунут путём.'),
            ('h', 'Построчная обработка большого файла'),
            ('code', 'php', None, r'''$in = new SplFileObject('orders.csv');
$in->setFlags(SplFileObject::READ_CSV | SplFileObject::SKIP_EMPTY | SplFileObject::DROP_NEW_LINE);

$out = new SplFileObject('report.csv', 'w');
foreach ($in as $row) {
    if ($row === [null] || $row === false) {
        continue;                  // хвостовая пустая строка
    }
    $out->fputcsv([$row[0], (int) $row[2] * 2]);
}'''),
        ]),
    ],
)


# --------------------------------------------------------------------------- SPL

topic(
    id='spl', group='lib',
    title='SPL: структуры и итераторы',
    cls='SplObjectStorage',
    lead='Набор готовых классов на случаи, где массив уже мешает: очередь, стек, куча, '
         'множество объектов и обход дерева каталогов.',
    badge='20 классов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Массив PHP умеет почти всё — и поэтому не говорит о намерении. '
                  '`SplQueue` в коде заявляет «это очередь», `SplObjectStorage` — «множество объектов», '
                  '`WeakMap` — «данные, которые исчезнут вместе с объектом». '
                  'Плюс часть структур экономит память там, где массив её не жалеет.'),
            ('code', 'php', None, r'''// множество объектов: ключ — сам объект, а не строка
$seen = new SplObjectStorage();
$seen->attach($user);
$seen->contains($user);        // true
$seen[$user] = ['at' => time()];   // к объекту можно привязать данные
count($seen);

// слабая карта: запись исчезает, когда объект больше никому не нужен
$cache = new WeakMap();
$cache[$entity] = $heavyComputation;   // утечки памяти не будет

// очередь и стек с понятным названием
$queue = new SplQueue();
$queue->enqueue($job);
$job = $queue->dequeue();

// массив фиксированной длины: меньше памяти на больших объёмах
$points = new SplFixedArray(1_000_000);'''),
            ('note', 'tip', 'WeakMap — правильный кэш «по объекту»',
             'Обычный массив с ключом `spl_object_id($obj)` держит запись вечно, даже когда объект '
             'давно не нужен, — и в долгоживущем процессе это утечка. '
             '`WeakMap` (с 8.0) удаляет запись автоматически, как только исчезла последняя ссылка на ключ.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'ArrayObject / ArrayIterator', 'd': 'Массив, завёрнутый в объект: передаётся по ссылке на объект, реализует `ArrayAccess`, `Countable` и `IteratorAggregate`.', 'o': 'ARRAY_AS_PROPS', 'c': "$config = new ArrayObject(['db' => 'mysql'], ArrayObject::ARRAY_AS_PROPS);\n$config['db'];\n$config->db;"},
                {'n': 'SplStack / SplQueue', 'd': 'Стек и очередь поверх двусвязного списка. Разница с массивом не в скорости, а в том, что набор операций ограничен смыслом структуры.', 'o': 'push/pop, enqueue/dequeue', 'c': "$stack = new SplStack();\n$stack->push($node);\n$top = $stack->pop();"},
                {'n': 'SplDoublyLinkedList', 'd': 'Двусвязный список: вставка и удаление с обоих концов без перенумерации. Основа `SplStack` и `SplQueue`.', 'o': 'IT_MODE_LIFO | IT_MODE_FIFO', 'c': "$list = new SplDoublyLinkedList();\n$list->push(1);\n$list->unshift(0);"},
                {'n': 'SplFixedArray', 'd': 'Массив заданной длины с целыми ключами. Экономит память на миллионах элементов, потому что не хранит хэш-таблицу.', 'o': 'setSize(), toArray()', 'c': "$a = new SplFixedArray(10);\n$a[0] = 'x';\n$a->setSize(20);"},
                {'n': 'SplObjectStorage', 'd': 'Множество объектов с возможностью привязать к каждому данные. Заменяет попытки использовать объект как ключ массива, что в PHP запрещено.', 'o': 'attach, detach, contains', 'c': "$handled = new SplObjectStorage();\nforeach ($events as $e) {\n    if ($handled->contains($e)) {\n        continue;\n    }\n    $handled->attach($e);\n}"},
                {'n': 'WeakMap / WeakReference', 'd': 'Ссылки, которые не мешают сборке мусора. `WeakMap` — карта «объект → данные», `WeakReference` — одна ссылка, которая может «опустеть».', 'o': 'get() вернёт null', 'v': '8.0', 'c': "$ref = WeakReference::create($obj);\n$maybe = $ref->get();   // null, если объект уже собран"},
                {'n': 'SplPriorityQueue / SplHeap', 'd': 'Очередь с приоритетами и куча со своим порядком. `SplMinHeap` и `SplMaxHeap` — готовые варианты для чисел.', 'o': 'compare() задаёт порядок', 'c': "$q = new SplPriorityQueue();\n$q->insert($task, priority: 10);\n$next = $q->extract();"},
                {'n': 'RecursiveDirectoryIterator + RecursiveIteratorIterator', 'd': 'Обход дерева каталогов без рекурсии в вашем коде. Пара стандартная: первый даёт узлы, второй разворачивает вложенность.', 'o': 'SKIP_DOTS обязателен', 'c': "$it = new RecursiveIteratorIterator(\n    new RecursiveDirectoryIterator($dir, FilesystemIterator::SKIP_DOTS)\n);\nforeach ($it as $file) {\n    if ($file->getExtension() === 'php') { }\n}"},
                {'n': 'CallbackFilterIterator', 'd': 'Фильтр поверх любого итератора — ленивый аналог `array_filter()`, который не собирает промежуточный массив.', 'o': 'RecursiveCallbackFilterIterator — для деревьев', 'c': "$php = new CallbackFilterIterator(\n    $it,\n    fn(SplFileInfo $f): bool => $f->getExtension() === 'php',\n);"},
                {'n': 'LimitIterator / InfiniteIterator', 'd': 'Взять N элементов начиная с K и зациклить обход. Первое — способ «отрезать» кусок у генератора, не собирая его целиком.', 'o': 'работают с любым Traversable', 'c': "foreach (new LimitIterator($rows, 0, 100) as $row) { }"},
                {'n': 'IteratorIterator / MultipleIterator / AppendIterator', 'd': 'Обернуть `Traversable` в полноценный `Iterator`, пройти несколько итераторов параллельно, склеить их подряд.', 'o': 'MultipleIterator::MIT_NEED_ALL', 'c': "$both = new MultipleIterator(MultipleIterator::MIT_NEED_ALL);\n$both->attachIterator($names);\n$both->attachIterator($emails);"},
                {'n': 'iterator_to_array() / iterator_count() / iterator_apply()', 'd': 'Функции-помощники для всего, что обходится. Помните про второй аргумент `false` — иначе одинаковые ключи затрут значения.', 'o': 'работают и с генераторами', 'c': "$rows = iterator_to_array($gen, false);"},
                {'n': 'SplSubject / SplObserver', 'd': 'Классический «наблюдатель» из стандартной библиотеки. Встречается в старом коде; современные проекты берут шину событий или PSR-14.', 'o': 'attach, detach, notify', 'c': "final class Order implements SplSubject\n{\n    public function notify(): void { }\n}"},
                {'n': 'SplTempFileObject', 'd': 'Файл в памяти с переездом на диск после порога. Удобен для сборки выгрузок, которые не обязательно материализовать.', 'o': 'размер порога — в конструкторе', 'c': "$csv = new SplTempFileObject(4 * 1024 * 1024);\n$csv->fputcsv(['id', 'sum']);"},
                {'n': 'Исключения SPL', 'd': 'Готовая иерархия для прикладных ошибок: `LogicException` и `RuntimeException` с потомками. Свои классы наследуют от них, а не от `Exception` напрямую.', 'o': 'см. узел «ошибки»', 'c': "throw new OutOfRangeException('страница за пределами диапазона');"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Обход проекта без рекурсии'),
            ('code', 'php', 'bin/find-todo.php', r'''$dir = new RecursiveDirectoryIterator(__DIR__ . '/../src', FilesystemIterator::SKIP_DOTS);
$files = new RecursiveIteratorIterator($dir);
$php = new CallbackFilterIterator(
    $files,
    static fn(SplFileInfo $f): bool => $f->isFile() && $f->getExtension() === 'php',
);

foreach ($php as $file) {
    foreach (new SplFileObject($file->getPathname()) as $n => $line) {
        if (is_string($line) && str_contains($line, 'TODO')) {
            printf("%s:%d %s\n", $file->getPathname(), $n + 1, trim($line));
        }
    }
}'''),
            ('note', 'warn', 'SPL-структуры не бесплатны',
             'Каждый элемент `SplDoublyLinkedList` — объект со своими накладными расходами, '
             'и на небольших объёмах обычный массив и быстрее, и экономнее. '
             'Берите SPL ради смысла («это очередь», «это множество объектов») '
             'или ради конкретной возможности, которой у массива нет.'),
        ]),
    ],
)
