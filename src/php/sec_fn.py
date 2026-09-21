# -*- coding: utf-8 -*-
"""Функции: объявления и аргументы, замыкания, генераторы, файберы."""

from model import topic

# --------------------------------------------------------------------------- Функции

topic(
    id='functions', group='fn',
    title='Функции и аргументы',
    cls='function',
    lead='Объявление, типы, значения по умолчанию и четыре способа передать аргумент — '
         'включая именованные, которые убирают из вызова ряды из true, null и false.',
    badge='7 приёмов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Объявление функции — это имя, список параметров и, по желанию, объявленные типы. '
                  'Всё, что не передано и не имеет значения по умолчанию, — ошибка вызова: '
                  'с PHP 8 `ArgumentCountError`, а не предупреждение.'),
            ('code', 'php', None, r'''declare(strict_types=1);

function paginate(
    array $rows,                 // обязательный
    int $page = 1,               // со значением по умолчанию
    int $perPage = 20,
    ?string $sort = null,        // ? обязателен: неявный nullable устарел в 8.4
): array {
    $offset = ($page - 1) * $perPage;
    return array_slice($rows, $offset, $perPage);
}

paginate($rows);                          // 2-й и далее — по умолчанию
paginate($rows, perPage: 50);             // именованный: пропустили $page
paginate($rows, sort: 'id', page: 2);     // порядок именованных не важен'''),
            ('h', 'Четыре способа передать аргументы'),
            ('kv', [
                ('позиционно', 'по порядку; после именованного аргумента позиционных быть не может'),
                ('именованно — с 8.0', '`perPage: 50`; имя параметра становится частью публичного контракта'),
                ('списком — `...$args`', 'в объявлении собирает остаток, в вызове раскладывает массив'),
                ('по ссылке — `&$x`', 'функция меняет переменную вызывающего; в новом коде почти не нужен'),
            ]),
            ('note', 'trap', 'Имя параметра теперь тоже контракт',
             'Как только кто-то вызвал вашу функцию с именованным аргументом, переименование параметра — '
             'ломающее изменение. В библиотеках это отдельная причина не переименовывать параметры '
             'в минорных версиях.'),
            ('h', 'Возврат'),
            ('code', 'php', None, r'''class Repository
{
    public function find(int $id): ?User { }   // объект или null
    public function total(): int { }           // ровно int
    public function save(): void { }           // ничего: return; можно, а return null; — нет
    public function fail(string $m): never { } // не вернётся: бросит или завершит
    public function copy(): static { }         // объект того класса, у которого вызвали
}

// несколько значений — массивом или объектом; список разбирается на месте
[$ok, $error] = validate($input);'''),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'Именованные аргументы', 'd': 'Аргумент по имени параметра. Убирает из вызова цепочки `null, null, true` и делает читаемым вызов с флагами.', 'o': 'после них позиционных быть не может', 'v': '8.0', 'c': "json_encode($data, flags: JSON_PRETTY_PRINT);\nsetcookie('t', $v, httponly: true, samesite: 'Lax');"},
                {'n': 'Переменное число аргументов', 'd': 'Собирает остаток в массив; с объявленным типом проверяет каждый элемент. В вызове тот же `...` раскладывает массив по параметрам.', 'o': 'только последний параметр', 'c': "function log(string $fmt, string|int ...$args): void\n{\n    error_log(sprintf($fmt, ...$args));\n}"},
                {'n': 'Значения по умолчанию', 'd': 'Константное выражение, а с 8.1 — ещё и `new`. Объект создаётся при каждом вызове без аргумента, а не один раз.', 'o': 'new в умолчаниях — с 8.1', 'v': '8.1', 'c': "function send(Message $m, Logger $log = new NullLogger()): void {}"},
                {'n': 'Передача по ссылке', 'd': 'Функция получает саму переменную. Работает только с переменными: результат выражения передать по ссылке нельзя.', 'o': 'сортировки и preg_match работают так', 'c': "function addRow(array &$rows, array $row): void\n{\n    $rows[] = $row;\n}"},
                {'n': 'Объявленный тип возврата', 'd': 'Проверяется на каждом `return`. В строгом режиме приведения не будет: вернёте `\'5\'` из функции с `: int` — получите `TypeError` в самой функции.', 'o': 'никогда не мешает, всегда помогает', 'c': "function total(array $items): int\n{\n    return array_sum($items);\n}"},
                {'n': 'never', 'd': 'Функция не возвращает управление. Анализаторы понимают, что после вызова код недостижим, и перестают требовать `return` в ветке.', 'o': 'наследник может сузить до never', 'v': '8.1', 'c': "function redirect(string $url): never\n{\n    header('Location: ' . $url);\n    exit;\n}"},
                {'n': 'static-переменные', 'd': 'Живут между вызовами функции. С 8.3 инициализатор — любое выражение, а не только константа. С 8.1 у наследников общая переменная с родителем.', 'o': 'в методах — общие для класса', 'v': '8.3', 'c': "function counter(): int\n{\n    static $n = 0;\n    return ++$n;\n}"},
                {'n': 'Первоклассный вызов — f(...)', 'd': 'Превращает любую функцию или метод в `Closure`, не теряя объявленные типы. Заменяет строки-имена функций, которые не проверяются на этапе компиляции.', 'o': 'вместо Closure::fromCallable', 'v': '8.1', 'c': "$trim = trim(...);\n$send = $mailer->send(...);\n$fromStatic = User::byId(...);"},
                {'n': '#[\\Deprecated]', 'd': 'Помечает функцию, метод или константу устаревшими: при вызове PHP сам выдаёт `E_USER_DEPRECATED`, а IDE зачёркивает имя.', 'o': 'message, since', 'v': '8.4', 'c': "#[\\Deprecated(message: 'берите Clock::now()', since: '2.3')]\nfunction now(): DateTimeImmutable {}"},
                {'n': '#[\\NoDiscard]', 'd': 'Помечает функцию, у которой результат обязан использоваться: игнор возврата даёт предупреждение. Явный `(void)` перед вызовом его гасит.', 'o': 'для чистых функций и with-методов', 'v': '8.5', 'c': "class Order\n{\n    #[\\NoDiscard]\n    public function withStatus(string $s): static {}\n}\n\n// $order->withStatus('paid');  →  Warning: результат потерян"},
                {'n': 'Вложенные и условные функции', 'd': 'Функция, объявленная внутри другой или внутри `if`, появляется в глобальном пространстве в момент выполнения объявления. В нормальном коде этого не делают.', 'o': 'function_exists() для проверки', 'c': "if (!function_exists('str_contains')) {\n    function str_contains($h, $n): bool { }\n}"},
                {'n': 'Ссылка на функцию строкой', 'd': 'Имя функции строкой всё ещё работает, но частичные формы вроде `\'self::method\'` устарели в 8.2. Первоклассный вызов лучше во всём.', 'o': 'is_callable() для проверки', 'v': '8.2', 'c': "array_map('strtoupper', $rows);   // работает\narray_map('self::norm', $rows);   // устарело"},
                {'n': 'func_get_args()', 'd': 'Все переданные аргументы массивом, включая те, что не объявлены. Наследие времён без `...$args`; с именованными аргументами работает неочевидно.', 'o': 'предпочитайте ...$args', 'c': "function legacy() {\n    $args = func_get_args();\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Флаги в вызове читаются только с именами'),
            ('code', 'php', None, r'''// что делают эти true и null — по вызову не понять
$pdf = render($html, true, null, false, 'A4');

// то же самое, но читается без документации
$pdf = render($html, landscape: true, format: 'A4');'''),
            ('h', 'Когда параметров стало слишком много'),
            ('code', 'php', 'src/Report/Params.php', r'''// шесть параметров, половина необязательных — признак того, что это объект
final class ReportParams
{
    public function __construct(
        public readonly DateTimeImmutable $from,
        public readonly DateTimeImmutable $to,
        public readonly string $currency = 'RUB',
        public readonly bool $withTax = true,
    ) {}
}

function report(ReportParams $params): Report { /* ... */ }

report(new ReportParams(from: $from, to: $to, withTax: false));'''),
            ('note', 'tip', 'Ранний выход вместо лестницы условий',
             'Проверки в начале функции с немедленным `return` или `throw` держат основной путь '
               'на нулевом уровне вложенности. Сравните: три вложенных `if` против трёх охранных условий — '
               'вторые читаются сверху вниз и не заканчиваются частоколом закрывающих скобок.'),
            ('code', 'php', None, r'''function publish(Post $post, User $user): void
{
    if (!$user->can('publish')) {
        throw new AccessDenied();
    }
    if ($post->isPublished()) {
        return;                       // уже сделано — не ошибка
    }

    $post->publish();                 // основной путь: без вложенности
}'''),
        ]),
    ],
)


# --------------------------------------------------------------------------- Замыкания

topic(
    id='closures', group='fn',
    title='Замыкания',
    cls='Closure',
    lead='Функция как значение: объект класса Closure, который можно передать, сохранить '
         'и привязать к другому объекту.',
    badge='5 форм',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Замыкание — это **объект** класса `Closure`. Оно помнит область видимости, в которой создано: '
                  'обычная форма берёт переменные списком `use`, стрелочная — сама, по значению, '
                  'и только те, что реально упомянуты в теле.'),
            ('code', 'php', None, r'''$rate = 0.2;

// обычное: что захватить — пишем явно
$withVat = function (int $sum) use ($rate): int {
    return (int) round($sum * (1 + $rate));
};

// стрелочное: захватывает само, по значению, тело — одно выражение
$withVat = fn(int $sum): int => (int) round($sum * (1 + $rate));

// по ссылке: изменения видны снаружи
$total = 0;
$add = function (int $n) use (&$total): void { $total += $n; };
$add(5);   // $total === 5'''),
            ('h', 'Замыкание и $this'),
            ('code', 'php', None, r'''class Cart
{
    private array $items = [];

    public function totals(): array
    {
        // замыкание внутри метода видит $this автоматически
        return array_map(fn(Item $i) => $i->price * $i->qty, $this->items);
    }
}

// static-замыкание отказывается от $this: его нельзя привязать к объекту
$pure = static fn(int $a, int $b): int => $a + $b;'''),
            ('note', 'trap', 'Стрелочная функция захватывает значение, а не переменную',
             '`$fn = fn() => $i;` внутри цикла запомнит текущее значение `$i` — и это обычно то, что нужно. '
             'Но если переменная меняется позже, замыкание об этом не узнает: '
             'для связи по ссылке нужна обычная форма с `use (&$i)`.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'function () use ()', 'd': 'Полная форма: тело из нескольких инструкций, захват списком. Захват по значению копирует переменную в момент создания замыкания.', 'o': 'use (&$x) — по ссылке', 'c': "$log = function (string $line) use ($file): void {\n    file_put_contents($file, $line, FILE_APPEND);\n};"},
                {'n': 'fn() =>', 'd': 'Стрелочная функция: ровно одно выражение, захват автоматический и по значению. Идеальна для колбэков сортировки и преобразования.', 'o': 'вложенные fn тоже видят внешние переменные', 'c': "usort($rows, fn($a, $b) => $a->at <=> $b->at);"},
                {'n': 'static fn / static function', 'd': 'Замыкание без `$this`. Полезно там, где замыкание хранится долго: без привязки оно не удержит объект от сборки мусора.', 'o': 'привязать к объекту нельзя', 'c': "$compare = static fn(int $a, int $b): int => $a <=> $b;"},
                {'n': 'Первоклассный вызов f(...)', 'd': 'Превращает функцию, метод или статический метод в `Closure` с сохранением типов. Проверяется компилятором — опечатка в имени видна сразу.', 'o': 'работает с $obj->m(...), C::m(...)', 'v': '8.1', 'c': "$fns = [strlen(...), $this->format(...), Money::fromInt(...)];"},
                {'n': 'Closure::fromCallable()', 'd': 'То же самое до 8.1 и для случаев, когда callable приходит переменной. Первоклассный вызов читается лучше и проверяется раньше.', 'o': 'принимает любой callable', 'c': "$fn = Closure::fromCallable($maybeCallable);"},
                {'n': 'bindTo() / Closure::bind()', 'd': 'Копия замыкания, привязанная к другому объекту и области видимости. С областью видимости класса замыкание получает доступ к его приватным свойствам.', 'o': 'вторым аргументом — scope', 'c': "$peek = function () { return $this->secret; };\n$peek->bindTo($obj, $obj::class)();"},
                {'n': 'call()', 'd': 'Вызвать замыкание так, будто оно метод этого объекта: привязка и вызов одной операцией.', 'o': 'bindTo + вызов', 'c': "$sum = function () { return $this->a + $this->b; };\n$sum->call($point);"},
                {'n': '__invoke()', 'd': 'Объект, который вызывается как функция. В отличие от замыкания у него есть имя класса, конструктор и тесты — так пишут обработчики и политики.', 'o': 'объект проходит как callable', 'c': "final class Slugify\n{\n    public function __invoke(string $s): string\n    {\n        return mb_strtolower(trim($s));\n    }\n}\n\narray_map(new Slugify(), $titles);"},
                {'n': 'Формы callable', 'd': 'Строка с именем функции, массив `[$obj, \'method\']`, массив `[Class::class, \'method\']`, объект с `__invoke`, замыкание.', 'o': 'частичные строковые формы устарели в 8.2', 'c': "$c1 = 'strlen';\n$c2 = [$service, 'handle'];\n$c3 = [Service::class, 'staticHandle'];\n$c4 = new Slugify();"},
                {'n': 'Closure::getCurrent()', 'd': 'Ссылка на само выполняющееся замыкание. Даёт рекурсию без внешней переменной и без имени.', 'o': 'внутри замыкания', 'v': '8.5', 'c': "$fact = static fn(int $n): int =>\n    $n <= 1 ? 1 : $n * Closure::getCurrent()($n - 1);"},
                {'n': 'Замыкания в константных выражениях', 'd': 'Замыкание и первоклассный вызов теперь можно писать в значениях по умолчанию, инициализаторах и аргументах атрибутов.', 'o': 'только static-замыкания', 'v': '8.5', 'c': "class Route\n{\n    public function __construct(\n        public Closure $guard = static fn() => true,\n    ) {}\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Колбэк с состоянием вместо глобальной переменной'),
            ('code', 'php', None, r'''function counter(int $start = 0): Closure
{
    $n = $start;
    // захват по ссылке делает переменную состоянием замыкания
    return function () use (&$n): int {
        return $n++;
    };
}

$next = counter();
$next();   // 0
$next();   // 1'''),
            ('h', 'Мемоизация дорогого вызова'),
            ('code', 'php', 'src/Support/memoize.php', r'''function memoize(callable $fn): Closure
{
    $cache = [];
    return function (...$args) use ($fn, &$cache) {
        $key = serialize($args);
        return $cache[$key] ??= $fn(...$args);
    };
}

$rates = memoize($api->rate(...));
$rates('USD');   // запрос
$rates('USD');   // из кэша'''),
            ('note', 'warn', 'Замыкание нельзя сериализовать',
             '`serialize()` на объекте, у которого в свойстве лежит `Closure`, бросит исключение. '
             'Это всплывает там, где объекты кладут в кэш или в очередь: '
             'вместо замыкания в таких местах держат имя класса-обработчика или `__invoke`-объект.'),
            ('h', 'Приватное — наружу, когда очень надо'),
            ('code', 'php', None, r'''// в тестах иногда нужно заглянуть внутрь объекта без geттера
$read = function (string $prop) { return $this->$prop; };
$value = Closure::bind($read, $object, $object::class)('secret');'''),
        ]),
    ],
)


# --------------------------------------------------------------------------- Генераторы

topic(
    id='generators', group='fn',
    title='Генераторы',
    cls='Generator',
    lead='Функция, которая отдаёт значения по одному и останавливается между ними. '
         'Миллион строк проходит через память по одной, а не целиком.',
    badge='yield',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Одно `yield` в теле превращает функцию в **генератор**: при вызове тело не выполняется, '
                  'а возвращается объект `Generator`. Тело двигается только тогда, когда у генератора '
                  'просят следующее значение, и замирает ровно на `yield` — со всеми локальными переменными.'),
            ('svg', '''<svg viewBox="0 0 760 196" role="img" aria-label="Массив держит все строки в памяти, генератор отдаёт их по одной" class="dg">
<defs><marker id="p-g1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#p-g1)" opacity=".55">
<path d="M212 46h52"/><path d="M212 146h52"/><path d="M470 146h52"/>
</g>
<g class="dg-box"><rect x="16" y="22" width="196" height="48" rx="8"/><text x="114" y="42">file()</text><text x="114" y="59" class="dg-sub">1 000 000 строк</text></g>
<g class="dg-box dg-bad"><rect x="264" y="22" width="240" height="48" rx="8"/><text x="384" y="42">массив целиком в памяти</text><text x="384" y="59" class="dg-sub">сотни мегабайт</text></g>
<g class="dg-box"><rect x="16" y="122" width="196" height="48" rx="8"/><text x="114" y="142">yield в цикле</text><text x="114" y="159" class="dg-sub">1 000 000 строк</text></g>
<g class="dg-box"><rect x="264" y="122" width="206" height="48" rx="8"/><text x="367" y="142">одна строка</text><text x="367" y="159" class="dg-sub">остальное ждёт</text></g>
<g class="dg-box dg-ok"><rect x="522" y="122" width="222" height="48" rx="8"/><text x="633" y="142">обработали — забыли</text><text x="633" y="159" class="dg-sub">память не растёт</text></g>
</svg>''', 'Генератор не ускоряет обработку — он снимает потолок по памяти.'),
            ('code', 'php', None, r'''function rows(string $path): Generator
{
    $fh = fopen($path, 'r');
    try {
        while (($row = fgetcsv($fh)) !== false) {
            yield $row;                 // здесь функция замирает до следующего шага
        }
    } finally {
        fclose($fh);                    // finally отработает и при выходе из foreach через break
    }
}

foreach (rows('orders.csv') as $i => $row) {
    // $i — ключ: по умолчанию счётчик с нуля
}'''),
            ('h', 'Ключи, возврат и двусторонняя связь'),
            ('code', 'php', None, r'''function pairs(): Generator
{
    yield 'id' => 1;          // свой ключ
    $answer = yield 'q' => 2; // yield как выражение: получает то, что передали в send()
    return 'итог';            // доступно после обхода
}

$gen = pairs();
$gen->current();     // 2 — нет, сначала первое значение
$gen->send('ответ'); // продолжает с места yield, возвращает следующее значение
$gen->getReturn();   // 'итог' — только когда генератор дошёл до конца'''),
            ('note', 'trap', 'Генератор нельзя перемотать и пройти дважды',
             '`foreach` по одному генератору второй раз бросит `Exception: Cannot rewind a generator '
             'that was already run`. Если результат нужен дважды — либо вызывайте функцию-генератор заново, '
             'либо соберите её в массив через `iterator_to_array()`, приняв расход памяти сознательно.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'yield $value', 'd': 'Отдать значение и замереть. Ключ по умолчанию — счётчик с нуля, как в списке.', 'o': 'yield без значения отдаёт null', 'c': "function ids(): Generator\n{\n    foreach ($this->rows as $row) {\n        yield $row['id'];\n    }\n}"},
                {'n': 'yield $key => $value', 'd': 'Отдать пару. Обычно так возвращают словарь, который лень собирать целиком.', 'o': 'ключи могут повторяться', 'c': "yield $user->email => $user;"},
                {'n': 'yield from', 'd': 'Передать наружу всё, что отдаёт другой массив или генератор, — включая его ключи. Делает из генераторов цепочки и рекурсию.', 'o': 'возврат вложенного доступен как значение выражения', 'c': "function tree(array $nodes): Generator\n{\n    foreach ($nodes as $node) {\n        yield $node;\n        yield from tree($node->children);\n    }\n}"},
                {'n': '$x = yield', 'd': '`yield` — выражение: его значением становится то, что передали в `send()`. Так генератор превращается в сопрограмму, которой можно отвечать.', 'o': 'скобки обязательны в сложных выражениях', 'c': "function collector(): Generator\n{\n    $sum = 0;\n    while (true) {\n        $sum += yield $sum;\n    }\n}"},
                {'n': 'current() / key() / next()', 'd': 'Ручной обход вместо `foreach`. Первый вызов `current()` запускает тело до первого `yield`.', 'o': 'valid() — дошли ли до конца', 'c': "$gen = rows($path);\nwhile ($gen->valid()) {\n    process($gen->current());\n    $gen->next();\n}"},
                {'n': 'send()', 'd': 'Передать значение в точку `yield` и получить следующее. Обратите внимание: `send()` **тоже двигает** генератор.', 'o': 'до первого send нужен current()', 'c': "$c = collector();\n$c->current();\n$c->send(10);   // 10\n$c->send(5);    // 15"},
                {'n': 'getReturn()', 'd': 'Значение из `return` генератора. Доступно только после того, как генератор завершился, иначе — `Exception`.', 'o': 'проверяйте valid() === false', 'c': "foreach ($gen as $row) { }\n$stats = $gen->getReturn();"},
                {'n': 'throw()', 'd': 'Бросить исключение в точке, где генератор остановлен. Так отменяют долгую работу изнутри цикла-потребителя.', 'o': 'генератор может его поймать', 'c': "$gen->throw(new StopWork());"},
                {'n': 'iterator_to_array()', 'd': 'Собрать генератор в массив. Второй аргумент `false` отключает сохранение ключей — без него повторяющиеся ключи затрут друг друга.', 'o': 'второй аргумент почти всегда false', 'c': "iterator_to_array($gen, false);"},
                {'n': 'Бесконечные генераторы', 'd': 'Генератор не обязан заканчиваться: потребитель сам решает, когда остановиться, через `break` или `LimitIterator`.', 'o': 'break закрывает генератор', 'c': "function naturals(): Generator\n{\n    for ($i = 1; ; $i++) {\n        yield $i;\n    }\n}"},
                {'n': 'Generator как Iterator', 'd': '`Generator` реализует `Iterator`, поэтому подходит везде, где ждут `iterable` или `Traversable`: в `foreach`, в `iterator_apply()`, в SPL-итераторах.', 'o': 'но не Countable и не ArrayAccess', 'c': "function process(iterable $rows): void\n{\n    foreach ($rows as $row) { }\n}\n\nprocess(rows($path));   // и генератор, и массив"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Конвейер из генераторов'),
            ('code', 'php', 'src/Import/pipeline.php', r'''function read(string $path): Generator
{
    $fh = fopen($path, 'r');
    try {
        while (($row = fgetcsv($fh)) !== false) {
            yield $row;
        }
    } finally {
        fclose($fh);
    }
}

function onlyPaid(iterable $rows): Generator
{
    foreach ($rows as $row) {
        if ($row[3] === 'paid') {
            yield $row;
        }
    }
}

function batch(iterable $rows, int $size): Generator
{
    $chunk = [];
    foreach ($rows as $row) {
        $chunk[] = $row;
        if (count($chunk) === $size) {
            yield $chunk;
            $chunk = [];
        }
    }
    if ($chunk !== []) {
        yield $chunk;             // хвост
    }
}

// файл любого размера проходит через постоянную память
foreach (batch(onlyPaid(read('orders.csv')), 500) as $chunk) {
    $db->insertMany($chunk);
}'''),
            ('note', 'trap', 'yield from не перенумеровывает ключи',
             'Вложенный генератор отдаёт **свои** ключи — и они спокойно совпадут с ключами внешнего. '
             'В `foreach` это незаметно, а вот `iterator_to_array($gen)` молча потеряет элементы с одинаковыми '
             'ключами: из четырёх значений останется два. Лечится вторым аргументом `false`.'),
            ('note', 'tip', 'Возвращайте iterable, а принимайте тоже iterable',
             'Функция, объявленная с `iterable`, одинаково принимает массив и генератор — '
             'и вызывающий код решает, что ему важнее: простота или память. '
               'Это позволяет перевести обработку на генераторы позже, не переписывая сигнатуры.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Файберы

topic(
    id='fibers', group='fn',
    title='Файберы',
    cls='Fiber',
    lead='Кусок кода, который можно остановить на любой глубине вызовов и продолжить позже. '
         'Фундамент асинхронных библиотек, а не инструмент прикладного кода.',
    badge='8.1',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Файбер — это **отдельный стек вызовов**, которым управляют руками. '
                  'Запустили, внутри дошли до `Fiber::suspend()` — выполнение вернулось туда, откуда запускали, '
                  'вместе с переданным значением. Потом `resume()` — и файбер продолжил с той же строки.'),
            ('p', 'Отличие от генератора одно, но решающее: генератор умеет останавливаться только '
                  '**в своём теле**, а файбер — на любой глубине вложенных вызовов. '
                  'Поэтому на файберах строят асинхронные библиотеки: код внутри выглядит обычным, '
                  'синхронным, а ждёт он неблокирующе.'),
            ('code', 'php', None, r'''$fiber = new Fiber(function (string $task): string {
    $answer = Fiber::suspend($task . ': жду ответа');   // отдали управление наружу
    return $answer . ': готово';                        // продолжили после resume()
});

$question = $fiber->start('запрос');   // 'запрос: жду ответа'
$fiber->resume('ответ');               // вернёт null: файбер дошёл до конца
$fiber->getReturn();                   // 'ответ: готово'
$fiber->isTerminated();                // true'''),
            ('note', 'warn', 'Файбер — это не параллелизм',
             'В один момент времени работает ровно один файбер: PHP по-прежнему однопоточен. '
             'Файберы переключаются только там, где кто-то явно вызвал `suspend()`, — '
             'это кооперативная многозадачность, а не потоки и не процессы.'),
            ('note', 'trap', 'Fiber::suspend() вне файбера — ошибка',
             'Вызов снаружи бросает `FiberError: Cannot suspend outside of a fiber`. '
             'Поэтому библиотеки вроде Amp и ReactPHP прячут файберы внутри своего планировщика: '
             'прикладной код зовёт их `await`, а не `Fiber::suspend()` напрямую.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'new Fiber(callable $callback)', 'd': 'Создаёт файбер, но не запускает его. В колбэк уйдут аргументы `start()`.', 'o': 'создание ничего не выполняет', 'v': '8.1', 'c': "$fiber = new Fiber(function (int $id) {\n    // тело выполнится только после start()\n});"},
                {'n': 'start(...$args)', 'd': 'Запускает тело и работает до первого `suspend()` или до конца. Возвращает то, что передали в `suspend()`, либо `null`.', 'o': 'повторный start — FiberError', 'v': '8.1', 'c': "$value = $fiber->start($id);"},
                {'n': 'Fiber::suspend($value)', 'd': 'Останавливает текущий файбер и отдаёт значение наружу. Вызывается из любой функции, до которой дошло выполнение внутри файбера.', 'o': 'статический метод', 'v': '8.1', 'c': "function readAsync($stream): string\n{\n    return Fiber::suspend(['read', $stream]);\n}"},
                {'n': 'resume($value)', 'd': 'Продолжает остановленный файбер; переданное значение станет результатом `Fiber::suspend()` внутри.', 'o': 'вернёт следующее значение suspend', 'v': '8.1', 'c': "$next = $fiber->resume($dataFromSocket);"},
                {'n': 'throw(Throwable $e)', 'd': 'Продолжает файбер броском исключения в точке остановки. Так планировщик сообщает об ошибке операции, которой файбер ждал.', 'o': 'исключение можно поймать внутри', 'v': '8.1', 'c': "$fiber->throw(new TimeoutException());"},
                {'n': 'getReturn()', 'd': 'Значение, которое вернул колбэк. До завершения — `FiberError`.', 'o': 'проверяйте isTerminated()', 'v': '8.1', 'c': "if ($fiber->isTerminated()) {\n    $result = $fiber->getReturn();\n}"},
                {'n': 'isStarted() / isSuspended() / isRunning() / isTerminated()', 'd': 'Четыре состояния файбера. Планировщик выбирает по ним, кого продолжить на этом круге.', 'o': 'взаимоисключающие', 'v': '8.1', 'c': "foreach ($fibers as $f) {\n    if ($f->isSuspended()) {\n        $f->resume();\n    }\n}"},
                {'n': 'Fiber::getCurrent()', 'd': 'Файбер, внутри которого выполняется код, или `null`. Нужен библиотекам, чтобы понять, можно ли приостанавливаться.', 'o': 'статический метод', 'v': '8.1', 'c': "if (Fiber::getCurrent() === null) {\n    throw new LogicException('только внутри файбера');\n}"},
                {'n': 'FiberError', 'd': 'Ошибки управления: двойной запуск, `resume()` незапущенного, `suspend()` снаружи, `getReturn()` до конца.', 'o': 'наследник Error', 'v': '8.1', 'c': "try {\n    Fiber::suspend();\n} catch (FiberError $e) {\n    // Cannot suspend outside of a fiber\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Планировщик в двадцать строк'),
            ('code', 'php', 'src/Async/scheduler.php', r'''/** Крутит файберы по очереди, пока все не закончатся. */
function run(callable ...$tasks): array
{
    $fibers = array_map(static fn(callable $t) => new Fiber($t), $tasks);
    $results = [];

    foreach ($fibers as $i => $fiber) {
        $fiber->start();
    }
    while ($fibers !== []) {
        foreach ($fibers as $i => $fiber) {
            if ($fiber->isTerminated()) {
                $results[$i] = $fiber->getReturn();
                unset($fibers[$i]);
                continue;
            }
            $fiber->resume();       // здесь настоящая библиотека ждала бы готовности сокета
        }
    }
    ksort($results);
    return $results;
}

run(
    function () { Fiber::suspend(); return 'первая'; },
    function () { Fiber::suspend(); return 'вторая'; },
);'''),
            ('note', 'tip', 'В прикладном коде файберы почти не пишут руками',
             'Их место — внутри Amp, ReactPHP, Swoole и очередей задач. '
             'Оттуда они выглядят как обычные вызовы: `$response = $client->request($url)` не блокирует процесс, '
             'потому что под капотом стоит `Fiber::suspend()`. Знать про файберы полезно, '
             'чтобы понимать, почему такой код вообще работает.'),
            ('note', 'warn', 'Общее состояние остаётся общим',
             'Файберы делят память процесса: статические свойства, контейнер, открытые соединения. '
             'Переключение происходит только на `suspend()`, так что гонок в привычном смысле нет, '
             'но состояние, оставленное посреди операции, увидят все остальные файберы.'),
        ]),
    ],
)
