# -*- coding: utf-8 -*-
"""Объекты: классы, свойства, интерфейсы, трейты, перечисления, магия."""

from model import topic

# --------------------------------------------------------------------------- Классы

topic(
    id='classes', group='oop',
    title='Классы и объекты',
    cls='class',
    lead='Объявление, конструктор в одну строку, наследование и позднее статическое связывание — '
         'всё, из чего собирают объекты в PHP 8.',
    badge='10 модификаторов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Класс описывает свойства и методы, объект — их экземпляр. '
                  'С PHP 8.0 конструктор умеет **объявлять свойства прямо в параметрах**: '
                  'одна строка вместо трёх — объявления, параметра и присваивания.'),
            ('code', 'php', 'src/Order.php', r'''declare(strict_types=1);

final class Order                       // final: наследовать нельзя
{
    public const string STATUS_NEW = 'new';   // типизированная константа — с 8.3

    private array $items = [];

    public function __construct(
        public readonly int $id,              // продвижение: свойство + параметр сразу
        private Clock $clock = new SystemClock(),   // new в умолчании — с 8.1
    ) {}

    public static function draft(int $id): self   // именованный конструктор
    {
        return new self($id);
    }

    public function add(Item $item): static       // static: наследник вернёт себя
    {
        $this->items[] = $item;
        return $this;
    }
}

$order = Order::draft(7)->add($item);
$order::class;          // 'Order' — с 8.0 работает и на объекте
$order instanceof Order;'''),
            ('h', 'Наследование и позднее связывание'),
            ('code', 'php', None, r'''abstract class Model
{
    public static function create(): static   // static — «класс, у которого вызвали»
    {
        return new static();                  // позднее статическое связывание
    }

    public static function table(): string
    {
        return static::TABLE;                 // возьмёт константу наследника
    }

    abstract public function rules(): array;  // наследник обязан реализовать
}

final class User extends Model
{
    public const TABLE = 'users';

    public function rules(): array
    {
        return [];
    }
}

User::create();   // User, а не Model — из-за static вместо self'''),
            ('note', 'trap', 'self и static — не синонимы',
             '`self` — это класс, в котором написана строка, `static` — класс, у которого вызвали метод. '
               'Фабрика с `new self()` в базовом классе всегда вернёт базовый класс, '
               'сколько бы наследников ни было. Это ломается тихо: тесты на базовом классе проходят.'),
            ('h', 'Объект без имени'),
            ('code', 'php', None, r'''$logger = new class implements LoggerInterface {
    public function log(string $line): void
    {
        error_log($line);
    }
};

// анонимный класс с аргументами конструктора и родителем
$stub = new class($clock) extends BaseRepo {
    public function find(int $id): ?User { return null; }
};'''),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'Продвижение свойств конструктора', 'd': 'Модификатор видимости у параметра конструктора объявляет свойство и присваивает его. Работает вместе с `readonly` и объявленными типами.', 'o': 'нельзя для callable и var', 'v': '8.0', 'c': "public function __construct(\n    private readonly Mailer $mailer,\n    private int $retries = 3,\n) {}"},
                {'n': 'final', 'd': 'Класс нельзя наследовать, метод — переопределить. С 8.1 можно и константу класса. Разумный умолчальный выбор: наследование открывают осознанно.', 'o': 'final const — с 8.1', 'v': '8.1', 'c': "final class Money\n{\n    final public const string CODE = 'RUB';\n}"},
                {'n': 'abstract', 'd': 'Класс нельзя создать, метод обязан быть реализован в наследнике. Абстрактный метод — это интерфейс, встроенный в класс.', 'o': 'абстрактный класс может иметь код', 'c': "abstract class Command\n{\n    abstract public function run(): int;\n}"},
                {'n': 'readonly class', 'd': 'Все свойства класса становятся `readonly`, а динамические свойства запрещены. Короткая запись для value-объектов.', 'o': 'все свойства должны быть типизированы', 'v': '8.2', 'c': "readonly class Point\n{\n    public function __construct(\n        public int $x,\n        public int $y,\n    ) {}\n}"},
                {'n': 'static-свойства и методы', 'd': 'Принадлежат классу, а не объекту. Статическое свойство — это глобальная переменная с именем класса: в тестах она переживает тест.', 'o': 'обращение через self:: или static::', 'c': "final class Registry\n{\n    private static array $items = [];\n\n    public static function put(string $k, mixed $v): void\n    {\n        self::$items[$k] = $v;\n    }\n}"},
                {'n': 'Константы класса', 'd': 'Неизменяемые значения, доступные без объекта. С 8.3 им можно объявить тип, с 8.1 — сделать `final`, с 8.3 — обращаться динамически.', 'o': 'видимость тоже задаётся', 'v': '8.3', 'c': "class Http\n{\n    public const int OK = 200;\n    private const array CODES = [200, 404];\n}\n\n$name = 'OK';\nHttp::{$name};   // 8.3"},
                {'n': 'new в инициализаторах', 'd': 'Объект как значение по умолчанию параметра, аргумент атрибута или инициализатор статической переменной. Создаётся при каждом вызове, а не один раз на объявление.', 'o': 'нельзя в свойствах и константах', 'v': '8.1', 'c': "function send(Message $m, Logger $l = new NullLogger()) {}"},
                {'n': 'Позднее статическое связывание', 'd': '`static::` и `new static()` смотрят на класс вызова, а не объявления. На этом стоят фабрики, текучие интерфейсы и Active Record.', 'o': 'static как тип возврата — с 8.0', 'c': "public static function make(): static\n{\n    return new static();\n}"},
                {'n': '$object::class', 'd': 'Имя класса объекта без `get_class()`. Работает на любом выражении-объекте, в том числе `$this::class`.', 'o': 'на строке — ошибка компиляции', 'v': '8.0', 'c': "match ($e::class) {\n    NotFound::class => 404,\n    default => 500,\n};"},
                {'n': 'Анонимные классы', 'd': 'Класс на месте: заглушка в тесте, разовая реализация интерфейса, обёртка. С 8.3 может быть `readonly`.', 'o': 'каждый вызов — новый класс', 'v': '8.3', 'c': "$clock = new readonly class implements Clock {\n    public function now(): DateTimeImmutable\n    {\n        return new DateTimeImmutable('2024-01-01');\n    }\n};"},
                {'n': '#[\\Override]', 'd': 'Проверка на этапе компиляции: метод действительно переопределяет родительский. Опечатка в имени или переименование в базовом классе сразу становится ошибкой.', 'o': 'с 8.5 — и на свойствах', 'v': '8.3', 'c': "final class JsonController extends Controller\n{\n    #[\\Override]\n    public function handle(Request $r): Response {}\n}"},
                {'n': '__destruct()', 'd': 'Вызывается, когда на объект не осталось ссылок или при завершении скрипта. Порядок при завершении не гарантирован — закрывать ресурсы лучше явно.', 'o': 'исключение в деструкторе фатально', 'c': "public function __destruct()\n{\n    $this->connection?->close();\n}"},
                {'n': 'Ленивые объекты', 'd': 'Объект, который создаётся по-настоящему только при первом обращении к свойству или методу. Раньше это делали прокси-классами в DI-контейнерах.', 'o': 'newLazyGhost, newLazyProxy', 'v': '8.4', 'c': "$r = new ReflectionClass(Heavy::class);\n$obj = $r->newLazyGhost(function (Heavy $o): void {\n    $o->__construct($deps);   // вызовется при первом обращении\n});"},
                {'n': 'Сравнение и копирование объектов', 'd': '`==` сравнивает класс и свойства, `===` — тождество. `clone` копирует поверхностно: вложенные объекты остаются общими, это чинят в `__clone()`.', 'o': 'spl_object_id — идентификатор экземпляра', 'c': "$a == $b;    // тот же класс и равные свойства\n$a === $b;   // тот же объект\n\npublic function __clone(): void\n{\n    $this->createdAt = clone $this->createdAt;\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Именованные конструкторы вместо флагов'),
            ('code', 'php', None, r'''final class Money
{
    private function __construct(
        public readonly int $amount,       // в копейках: float для денег не годится
        public readonly string $currency,
    ) {}

    public static function fromRubles(float $rub): self
    {
        return new self((int) round($rub * 100), 'RUB');
    }

    public static function zero(string $currency = 'RUB'): self
    {
        return new self(0, $currency);
    }
}

Money::fromRubles(199.90);'''),
            ('note', 'tip', 'Закрытый конструктор + статические фабрики',
             'Приватный `__construct()` заставляет создавать объект через методы с именами: '
             '`Money::fromRubles()`, `Money::zero()`. Каждый путь создания виден в списке методов, '
             'а не прячется в наборе необязательных аргументов.'),
            ('h', 'Неизменяемый объект с with-методами'),
            ('code', 'php', None, r'''final readonly class Query
{
    public function __construct(
        public string $table,
        public int $limit = 20,
        public array $where = [],
    ) {}

    public function withLimit(int $limit): self
    {
        return new self($this->table, $limit, $this->where);
    }
}

$q = new Query('users')->withLimit(100);   // цепочка без скобок — с 8.4'''),
            ('note', 'warn', 'Наследование — не способ переиспользовать код',
             'Если у наследника «почти то же самое, только другой способ сохранения», '
             'это композиция: передайте объект, который умеет сохранять. '
             'Наследование оправдано там, где наследник **действительно является** родителем '
             'и его можно подставить в любой код, ожидающий базовый тип.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Свойства

topic(
    id='props', group='oop',
    title='Свойства',
    cls='readonly · hooks',
    lead='Типизированные, неизменяемые, с раздельной видимостью на чтение и запись '
         'и с перехватом чтения и записи — свойство в PHP 8.4 умеет почти всё, что раньше делали геттеры.',
    badge='8.4: хуки',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'У свойства есть тип, видимость и — с 8.4 — **хуки**: код, который выполняется '
                  'при чтении и записи. Снаружи это по-прежнему обычное свойство: '
                  '`$user->email = $v` вместо `$user->setEmail($v)`, но с проверкой внутри.'),
            ('code', 'php', 'src/User.php', r'''declare(strict_types=1);

class User
{
    // вычисляемое свойство: хранилища нет, есть только чтение
    public string $fullName {
        get => trim($this->first . ' ' . $this->last);
    }

    // обычное свойство с проверкой на записи
    public string $email {
        set (string $value) {
            $value = mb_strtolower(trim($value));
            if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
                throw new InvalidArgumentException('не похоже на адрес почты');
            }
            $this->email = $value;     // запись в само свойство, рекурсии нет
        }
    }

    // читают все, пишет только класс — с 8.4
    public private(set) int $version = 1;

    public function __construct(
        public string $first,
        public string $last,
        string $email,
    ) {
        $this->email = $email;         // сеттер отработает и здесь
    }
}

$u = new User('Иван', 'Петров', '  IVAN@Example.COM ');
$u->fullName;   // 'Иван Петров'
$u->email;      // 'ivan@example.com'
$u->version = 5; // Error: Cannot modify private(set) property User::$version'''),
            ('h', 'Три состояния типизированного свойства'),
            ('kv', [
                ('не инициализировано', 'тип есть, значения нет; чтение — `Error: must not be accessed before initialization`'),
                ('со значением', 'обычная работа; тип проверяется при каждой записи'),
                ('readonly — после записи', 'первая запись из класса разрешена, вторая — `Error`, даже из самого класса'),
            ]),
            ('note', 'trap', 'readonly — не «константа объекта»',
             'Ограничение только на **переприсваивание свойства**. Если в `readonly`-свойстве лежит массив, '
             'его нельзя изменить целиком, но объект внутри свойства менять можно сколько угодно: '
             '`$this->logger->push(...)` работает. Неизменяемость вглубь язык не обеспечивает.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'Тип свойства', 'd': 'Проверяется при каждой записи. Свойство с типом и без значения по умолчанию не инициализировано — это не `null`.', 'o': 'кроме callable', 'c': "class Post\n{\n    public string $title;      // не инициализировано\n    public ?User $author = null;\n    public array $tags = [];\n}"},
                {'n': 'readonly', 'd': 'Записать можно один раз и только из области видимости класса. Идеальная пара к продвижению свойств конструктора.', 'o': 'требует объявленного типа', 'v': '8.1', 'c': "public function __construct(\n    public readonly DateTimeImmutable $at,\n) {}"},
                {'n': 'readonly class', 'd': 'Помечает `readonly` все свойства сразу и запрещает динамические. Компактная запись неизменяемого объекта.', 'o': 'наследник тоже должен быть readonly', 'v': '8.2', 'c': "final readonly class Uuid\n{\n    public function __construct(public string $value) {}\n}"},
                {'n': 'Переприсваивание readonly в __clone()', 'd': 'Внутри `__clone()` неизменяемые свойства можно записать заново — иначе «копию с изменением» нельзя было сделать вовсе.', 'o': 'только внутри __clone', 'v': '8.3', 'c': "public function __clone(): void\n{\n    $this->id = Uuid::new();   // можно только здесь\n}"},
                {'n': 'clone с изменением', 'd': 'Копия объекта с новыми значениями свойств, включая `readonly`. Делает «with-методы» тривиальными: не нужно перечислять все поля конструктора.', 'o': 'clone стал функцией', 'v': '8.5', 'c': "public function withStatus(string $s): static\n{\n    return clone($this, ['status' => $s]);\n}"},
                {'n': 'Хук get', 'd': 'Код, который выполняется при чтении. Если хук не обращается к самому свойству, оно становится **виртуальным**: памяти не занимает, считается каждый раз.', 'o': 'get => выражение — короткая форма', 'v': '8.4', 'c': "public int $age {\n    get => $this->born->diff(new DateTimeImmutable())->y;\n}"},
                {'n': 'Хук set', 'd': 'Код, который выполняется при записи. Может нормализовать значение и бросить исключение; тип параметра хука может быть шире типа свойства.', 'o': 'set (Type $value) { … }', 'v': '8.4', 'c': "public string $slug {\n    set (string|Stringable $v) {\n        $this->slug = mb_strtolower((string) $v);\n    }\n}"},
                {'n': 'Асимметричная видимость', 'd': 'Разные права на чтение и запись: читают все, пишет класс или наследник. Убирает пары «публичный геттер + приватное свойство».', 'o': 'private(set), protected(set)', 'v': '8.4', 'c': "public private(set) string $status = 'new';\nprotected protected(set) int $tries = 0;"},
                {'n': 'Свойства в интерфейсах', 'd': 'Интерфейс может потребовать свойство с чтением и записью — реализовать его можно как обычным свойством, так и хуками.', 'o': 'запись через { get; set; }', 'v': '8.4', 'c': "interface HasTitle\n{\n    public string $title { get; }\n}"},
                {'n': 'static-свойства', 'd': 'Одно значение на класс. С 8.5 у них тоже бывает асимметричная видимость. В наследнике статическое свойство общее с родителем, если не объявлено заново.', 'o': 'не участвуют в клонировании', 'v': '8.5', 'c': "public private(set) static int $count = 0;"},
                {'n': 'Динамические свойства', 'd': 'Запись в необъявленное свойство устарела в 8.2: опечатка в имени больше не создаёт молча новое поле. Классу, которому это нужно, ставят атрибут.', 'o': '#[\\AllowDynamicProperties]', 'v': '8.2', 'c': "#[\\AllowDynamicProperties]\nclass Bag {}\n\n$std = new stdClass();\n$std->anything = 1;   // stdClass можно всегда"},
                {'n': 'final у продвинутых свойств', 'd': 'Продвинутое свойство конструктора теперь может быть `final`: наследник не переопределит его хуки и видимость.', 'o': 'final public readonly', 'v': '8.5', 'c': "public function __construct(\n    final public readonly string $id,\n) {}"},
                {'n': 'Значения по умолчанию', 'd': 'Только константное выражение: массив, скаляр, константа, enum-кейс. Объект в умолчании свойства запрещён — его создают в конструкторе.', 'o': 'new — только в параметрах', 'c': "public array $headers = ['Accept' => 'application/json'];\npublic Status $status = Status::New;"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Хуки вместо пары геттер-сеттер'),
            ('code', 'php', None, r'''// было: два метода и приватное поле
class Temperature
{
    private float $celsius = 0.0;

    public function getFahrenheit(): float { return $this->celsius * 9 / 5 + 32; }
    public function setFahrenheit(float $f): void { $this->celsius = ($f - 32) * 5 / 9; }
}

// стало: одно свойство, которого физически нет
class Temperature
{
    public float $celsius = 0.0;

    public float $fahrenheit {
        get => $this->celsius * 9 / 5 + 32;
        set (float $f) { $this->celsius = ($f - 32) * 5 / 9; }
    }
}'''),
            ('note', 'tip', 'Хуки — способ не ломать публичный интерфейс',
             'Свойство, которое уже используют как `$obj->title`, можно превратить в вычисляемое '
             'или добавить к нему проверку, не меняя ни одной строки в вызывающем коде. '
             'До 8.4 ради такой возможности заранее прятали всё за геттеры — теперь это не нужно.'),
            ('note', 'trap', 'Хук set пишет в само свойство, а не в другое',
             'Внутри `set` присваивание `$this->email = $value` не вызывает хук заново — '
             'оно пишет в хранилище свойства. А вот обращение к **другому** свойству с хуком '
             'сработает как обычно, со всеми его проверками.'),
            ('h', 'Неизменяемость без километра конструктора'),
            ('code', 'php', None, r'''final readonly class Filter
{
    public function __construct(
        public ?string $query = null,
        public ?int $categoryId = null,
        public int $page = 1,
    ) {}

    // до 8.5: перечисляем все поля
    public function withPage(int $page): self
    {
        return new self($this->query, $this->categoryId, $page);
    }
}'''),
        ]),
    ],
)


# --------------------------------------------------------------------------- Интерфейсы

topic(
    id='interfaces', group='oop',
    title='Интерфейсы',
    cls='interface',
    lead='Договор без реализации: что объект умеет, не говоря ни слова о том, как. '
         'Половина возможностей языка — от foreach до json_encode — держится на встроенных интерфейсах.',
    badge='14 встроенных',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Интерфейс перечисляет публичные методы, константы и — с 8.4 — свойства, '
                  'которые обязан иметь класс. Класс реализует сколько угодно интерфейсов, '
                  'и каждый из них становится его **типом**: по интерфейсу пишут объявления параметров, '
                  'а значит, подменить реализацию можно не трогая вызывающий код.'),
            ('code', 'php', 'src/Clock.php', r'''declare(strict_types=1);

interface Clock
{
    public function now(): DateTimeImmutable;
}

final class SystemClock implements Clock
{
    public function now(): DateTimeImmutable
    {
        return new DateTimeImmutable();
    }
}

final class FrozenClock implements Clock
{
    public function __construct(private readonly DateTimeImmutable $at) {}

    public function now(): DateTimeImmutable
    {
        return $this->at;
    }
}

// код зависит от интерфейса — и поэтому тестируется без ожидания реального времени
final class Subscription
{
    public function __construct(private readonly Clock $clock) {}

    public function isExpired(DateTimeImmutable $until): bool
    {
        return $this->clock->now() > $until;
    }
}'''),
            ('h', 'Сужать можно, расширять нельзя'),
            ('code', 'php', None, r'''interface Repository
{
    public function find(int $id): ?Model;
}

final class UserRepository implements Repository
{
    // возврат сузили: ?User вместо ?Model — так можно (ковариантность)
    public function find(int $id): ?User
    {
        return null;
    }
}

// а вот потребовать от аргумента больше, чем интерфейс, нельзя:
// параметр можно только расширить (контравариантность)'''),
            ('note', 'tip', 'Интерфейс описывает роль, а не класс',
             'Хороший интерфейс называется по тому, что объект умеет: `Clock`, `Mailer`, `PasswordHasher`. '
             'Интерфейс `UserServiceInterface` с двадцатью методами, у которого одна реализация, — '
             'это не абстракция, а второй файл с тем же содержимым.'),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Встроенные интерфейсы, на которые опирается сам язык: реализуете — и объект начинает '
                  'работать в `foreach`, `count()`, `json_encode()` и квадратных скобках.'),
            ('ref', [
                {'n': 'Traversable', 'd': 'Корень всего, что проходится в `foreach`. Напрямую не реализуется — только через `Iterator` или `IteratorAggregate`.', 'o': 'iterable = array|Traversable', 'c': "function each(iterable $items): void\n{\n    foreach ($items as $item) { }\n}"},
                {'n': 'IteratorAggregate', 'd': 'Самый простой способ сделать объект обходимым: один метод, который отдаёт генератор или другой итератор.', 'o': 'getIterator(): Traversable', 'c': "final class Collection implements IteratorAggregate\n{\n    public function __construct(private array $items) {}\n\n    public function getIterator(): Generator\n    {\n        yield from $this->items;\n    }\n}"},
                {'n': 'Iterator', 'd': 'Полный ручной обход: пять методов состояния. Нужен редко — обычно хватает `IteratorAggregate` с генератором.', 'o': 'current, key, next, rewind, valid', 'c': "class Cursor implements Iterator\n{\n    public function current(): mixed { }\n    public function key(): mixed { }\n    public function next(): void { }\n    public function rewind(): void { }\n    public function valid(): bool { }\n}"},
                {'n': 'ArrayAccess', 'd': 'Квадратные скобки у объекта. Удобно для конфигов и контейнеров, но прячет тип: что вернёт `$c[\'x\']`, знает только документация.', 'o': 'offsetGet, offsetSet, offsetExists, offsetUnset', 'c': "final class Config implements ArrayAccess\n{\n    public function offsetGet(mixed $k): mixed\n    {\n        return $this->data[$k] ?? null;\n    }\n}"},
                {'n': 'Countable', 'd': 'Заставляет `count($obj)` работать. Без него `count()` на объекте с 8.0 — `TypeError`.', 'o': 'count(): int', 'c': "public function count(): int\n{\n    return count($this->items);\n}"},
                {'n': 'Stringable', 'd': 'Появился в 8.0 и реализуется **автоматически** любым классом с `__toString()`. Годится как объявление типа: `string|Stringable`.', 'o': '__toString(): string', 'v': '8.0', 'c': "function write(string|Stringable $line): void\n{\n    echo $line;\n}"},
                {'n': 'JsonSerializable', 'd': 'Что именно уедет в `json_encode()`. Без него сериализуются публичные свойства — обычно не то, что нужно наружу.', 'o': 'jsonSerialize(): mixed', 'c': "public function jsonSerialize(): array\n{\n    return ['id' => $this->id, 'at' => $this->at->format(DATE_ATOM)];\n}"},
                {'n': 'Throwable', 'd': 'Общий интерфейс `Error` и `Exception`. Свой класс исключения реализовать `Throwable` напрямую не может — только наследовать `Exception`.', 'o': 'getMessage, getCode, getPrevious, getTrace', 'c': "try {\n    run();\n} catch (Throwable $e) {\n    $log->error($e->getMessage(), ['e' => $e]);\n}"},
                {'n': 'UnitEnum / BackedEnum', 'd': 'Интерфейсы, которые перечисления получают сами. Ими объявляют параметры функций, работающих с любым enum.', 'o': 'cases(); from(), tryFrom()', 'v': '8.1', 'c': "function labels(string $enum): array\n{\n    return array_column($enum::cases(), 'name');\n}"},
                {'n': 'Константы интерфейса', 'd': 'Интерфейс может объявлять константы. С 8.1 класс-реализация вправе их переопределить — если это нежелательно, константу помечают `final`.', 'o': 'final public const', 'v': '8.1', 'c': "interface HasCode\n{\n    final public const string PREFIX = 'ord_';\n}"},
                {'n': 'Свойства в интерфейсе', 'd': 'Интерфейс требует свойство, доступное на чтение и/или запись. Класс закрывает требование обычным свойством или хуками.', 'o': '{ get; } / { get; set; }', 'v': '8.4', 'c': "interface HasSlug\n{\n    public string $slug { get; }\n}"},
                {'n': 'Наследование интерфейсов', 'd': 'Интерфейс может расширять сразу несколько других. Так собирают крупный контракт из мелких, не заставляя всех реализовывать всё.', 'o': 'extends A, B', 'c': "interface ReadWriteStream extends ReadableStream, WritableStream {}"},
                {'n': 'DateTimeInterface', 'd': 'Общий тип `DateTime` и `DateTimeImmutable`. В объявлениях параметров берут его, чтобы принимать оба; для возврата лучше конкретный `DateTimeImmutable`.', 'o': 'свой класс реализовать не может', 'c': "function isPast(DateTimeInterface $at): bool\n{\n    return $at < new DateTimeImmutable();\n}"},
                {'n': 'Serializable', 'd': 'Старый интерфейс сериализации, устарел в 8.1. Замена — магические `__serialize()` и `__unserialize()`, которые работают с массивом.', 'o': 'вместо него __serialize/__unserialize', 'v': '8.1', 'c': "public function __serialize(): array\n{\n    return ['id' => $this->id];\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Коллекция, которая ведёт себя как массив'),
            ('code', 'php', 'src/Collection.php', r'''final class Items implements IteratorAggregate, Countable, JsonSerializable
{
    /** @param list<Item> $items */
    public function __construct(private readonly array $items = []) {}

    public function getIterator(): Generator
    {
        yield from $this->items;
    }

    public function count(): int
    {
        return count($this->items);
    }

    public function jsonSerialize(): array
    {
        return array_values($this->items);
    }

    public function filter(callable $fn): self
    {
        return new self(array_values(array_filter($this->items, $fn)));
    }
}

$paid = new Items($rows)->filter(fn(Item $i) => $i->isPaid());
count($paid);
foreach ($paid as $item) { }
json_encode($paid);'''),
            ('note', 'warn', 'ArrayAccess ломает подсказки типов',
             'Для `$container[\'db\']` ни IDE, ни анализатор не знают тип результата — там `mixed`. '
             'Поэтому современные контейнеры и конфиги дают типизированные методы '
             '(`getString()`, `get(Db::class)`), а скобки оставляют для совместимости.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Трейты

topic(
    id='traits', group='oop',
    title='Трейты',
    cls='trait',
    lead='Кусок класса, который можно вставить в несколько классов. Не наследование и не интерфейс: '
         'код копируется в класс на этапе компиляции.',
    badge='6 правил',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Трейт **вкладывается** в класс так, будто его методы и свойства написаны прямо там. '
                  'Отсюда все свойства трейтов: они видят `$this`, участвуют в разрешении конфликтов '
                  'и не создают отдельного типа — по трейту нельзя объявить параметр.'),
            ('code', 'php', None, r'''trait Timestamps
{
    public ?DateTimeImmutable $createdAt = null;

    public const string FORMAT = 'Y-m-d H:i';   // константы в трейтах — с 8.2

    abstract public function clock(): Clock;    // требование к классу-хозяину

    public function touch(): void
    {
        $this->createdAt ??= $this->clock()->now();
    }
}

final class Post
{
    use Timestamps;

    public function __construct(private readonly Clock $clock) {}

    public function clock(): Clock
    {
        return $this->clock;
    }
}

Post::FORMAT;                  // константа пришла из трейта
$post instanceof Timestamps;   // ошибка: трейт — не тип'''),
            ('h', 'Конфликты имён'),
            ('code', 'php', None, r'''trait Json { public function render(): string { return '{}'; } }
trait Xml  { public function render(): string { return '<x/>'; } }

final class Report
{
    use Json, Xml {
        Json::render insteadof Xml;      // чей метод победит
        Xml::render as renderXml;        // второй доступен под другим именем
        renderXml as protected;          // заодно можно сменить видимость
    }
}'''),
            ('note', 'trap', 'Статическое свойство трейта — своё у каждого класса',
             'Трейт со `static $count` даст **отдельный счётчик** каждому использующему классу: '
             'это копия, а не общее хранилище. Ровно та же история со статическими переменными внутри '
             'методов трейта — общего состояния между классами не будет.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'use в классе', 'd': 'Вставляет трейт. Методы трейта проигрывают методам самого класса и выигрывают у унаследованных от родителя.', 'o': 'несколько трейтов через запятую', 'c': "final class User\n{\n    use Timestamps, SoftDelete;\n}"},
                {'n': 'insteadof', 'd': 'Разрешение конфликта: чей метод остаётся при одинаковых именах. Без него два трейта с одним методом — фатальная ошибка.', 'o': 'обязательно при конфликте', 'c': "use A, B {\n    A::run insteadof B;\n}"},
                {'n': 'as — псевдоним и видимость', 'd': 'Даёт методу второе имя и/или меняет его видимость в классе. Так прячут метод трейта или открывают доступ к обоим конфликтующим.', 'o': 'as protected, as private', 'c': "use Logger {\n    log as private writeLog;\n}"},
                {'n': 'abstract в трейте', 'd': 'Требование к классу-хозяину: «реализуй это, иначе не соберёшься». Способ передать трейту зависимость, не заводя конструктор.', 'o': 'проверяется при компиляции класса', 'c': "trait NeedsDb\n{\n    abstract protected function db(): PDO;\n}"},
                {'n': 'Свойства трейта', 'd': 'Копируются в класс. Одноимённое свойство в классе допустимо, только если полностью совпадает — тип, видимость и значение по умолчанию.', 'o': 'иначе фатальная ошибка', 'c': "trait HasId\n{\n    public readonly int $id;\n}"},
                {'n': 'Константы трейта', 'd': 'До 8.2 в трейтах их не было вовсе. Класс не может объявить одноимённую константу с другим значением.', 'o': 'доступны как константы класса', 'v': '8.2', 'c': "trait Limits\n{\n    public const int MAX = 100;\n}"},
                {'n': 'static-свойства и методы', 'd': 'Работают, но копия достаётся каждому классу отдельно. Для общего состояния нужен настоящий общий объект, а не трейт.', 'o': 'одно свойство — один класс', 'c': "trait Counter\n{\n    public static int $count = 0;\n}"},
                {'n': 'final у метода из трейта', 'd': 'Метод, пришедший из трейта, можно объявить финальным прямо в месте подключения — наследник его не переопределит.', 'o': 'as final', 'v': '8.3', 'c': "use Timestamps {\n    touch as final;\n}"},
                {'n': 'Трейт внутри трейта', 'd': 'Трейт может подключать другие трейты — получается композиция, которая разворачивается в классе-хозяине.', 'o': 'конфликты разрешаются там же', 'c': "trait Full\n{\n    use Timestamps, SoftDelete;\n}"},
                {'n': 'Конструктор в трейте', 'd': 'Технически возможен, но почти всегда ошибка: класс получает конструктор, о котором не знает, а два трейта с конструкторами конфликтуют.', 'o': 'лучше abstract-метод', 'c': "trait NeedsDeps\n{\n    // вместо конструктора — требование к классу-хозяину\n    abstract protected function deps(): Deps;\n}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Хороший трейт — мелкий и без состояния'),
            ('code', 'php', None, r'''// трейт на одну механику: сравнение value-объектов
trait ComparesByValue
{
    public function equals(self $other): bool
    {
        return $this == $other;   // == сравнит класс и свойства
    }
}

// трейт на «умеет превращаться в массив»
trait ArrayableFromPublic
{
    public function toArray(): array
    {
        return get_object_vars($this);
    }
}'''),
            ('note', 'warn', 'Трейт с десятью методами и своим состоянием — это класс',
             'Если трейт завёл свойства, конструирует объекты и обращается к базе, '
             'из него получится обычная зависимость: объект, который передают в конструктор. '
             'Такую зависимость видно в сигнатуре, её можно подменить в тесте — с трейтом не выйдет ни того, ни другого.'),
            ('note', 'tip', 'Трейт не заменяет интерфейс',
             'По трейту нельзя объявить тип, поэтому пара «интерфейс + трейт с реализацией по умолчанию» — '
             'обычная связка: интерфейс объявляет контракт и годится в объявлениях типов, '
             'трейт избавляет реализации от копипасты.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Перечисления

topic(
    id='enums', group='oop',
    title='Перечисления',
    cls='enum',
    lead='Тип с заранее известным набором значений. Заменяет строковые константы там, '
         'где «статус» может быть только одним из четырёх.',
    badge='8.1',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Перечисление объявляет **все свои значения сразу**, и других быть не может. '
                  'Каждый вариант — объект-одиночка, поэтому сравнивать их можно через `===`, '
                  'а объявление типа `Status $status` гарантирует, что внутрь не попадёт опечатка.'),
            ('code', 'php', 'src/Order/Status.php', r'''declare(strict_types=1);

enum Status: string           // привязанное: у каждого варианта есть скалярное значение
{
    case New = 'new';
    case Paid = 'paid';
    case Shipped = 'shipped';
    case Cancelled = 'cancelled';

    public function label(): string        // у перечислений бывают методы
    {
        return match ($this) {
            self::New => 'новый',
            self::Paid => 'оплачен',
            self::Shipped => 'отправлен',
            self::Cancelled => 'отменён',
        };
    }

    public function isFinal(): bool
    {
        return in_array($this, [self::Shipped, self::Cancelled], true);
    }

    public static function default(): self
    {
        return self::New;
    }
}

Status::Paid->value;            // 'paid'  — то, что уходит в базу
Status::Paid->name;             // 'Paid'  — имя варианта
Status::from('paid');           // Status::Paid, иначе ValueError
Status::tryFrom('nope');        // null вместо исключения
Status::cases();                // все варианты списком'''),
            ('h', 'Два вида перечислений'),
            ('kv', [
                ('чистое — `enum Status`', 'варианты без значений; хранить в базе напрямую нельзя, зато ничего лишнего'),
                ('привязанное — `enum Status: string`', 'у каждого варианта есть `value` типа `int` или `string`: его и пишут в базу и JSON'),
                ('`->name`', 'имя варианта, есть у обоих видов; менять его — ломающее изменение, как и имя класса'),
                ('`->value`', 'только у привязанного; это и есть контракт с внешним миром'),
            ]),
            ('note', 'trap', 'В перечислении не бывает состояния',
             'Свойства объявлять нельзя: варианты — одиночки, и любое «состояние» стало бы глобальным. '
             'Если варианту нужны данные, их возвращает метод через `match ($this)` '
             'или они лежат в константе-таблице.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'enum без типа — чистое', 'd': 'Набор именованных вариантов без значений. Подходит, когда наружу перечисление не уезжает: режимы, направления сортировки.', 'o': 'реализует UnitEnum', 'v': '8.1', 'c': "enum Direction\n{\n    case Asc;\n    case Desc;\n}"},
                {'n': 'enum: string | int — привязанное', 'd': 'Каждому варианту задано уникальное скалярное значение. Только `int` или `string`, значения должны различаться.', 'o': 'реализует BackedEnum', 'v': '8.1', 'c': "enum Level: int\n{\n    case Debug = 100;\n    case Error = 400;\n}"},
                {'n': 'cases()', 'd': 'Все варианты в порядке объявления. Основа для выпадающих списков, валидации и генерации миграций.', 'o': 'статический метод', 'v': '8.1', 'c': "$options = array_column(\n    array_map(fn(Status $s) => ['v' => $s->value, 'l' => $s->label()], Status::cases()),\n    'l', 'v',\n);"},
                {'n': 'from() / tryFrom()', 'd': 'Вариант по значению. `from()` бросает `ValueError` на неизвестном, `tryFrom()` возвращает `null` — второй нужен для данных извне.', 'o': 'только у привязанных', 'v': '8.1', 'c': "$status = Status::tryFrom($request['status']) ?? Status::New;"},
                {'n': 'Методы и статические методы', 'd': 'Перечисление — почти класс: методы, статические методы, константы. Нельзя только свойства и конструктор.', 'o': '$this внутри — текущий вариант', 'v': '8.1', 'c': "public function color(): string\n{\n    return match ($this) {\n        self::Error => 'red',\n        default => 'gray',\n    };\n}"},
                {'n': 'Интерфейсы', 'd': 'Перечисление может реализовать интерфейс — и тогда его варианты подходят везде, где объявлен этот тип.', 'o': 'вместе с константами интерфейса', 'v': '8.1', 'c': "interface HasLabel { public function label(): string; }\n\nenum Status: string implements HasLabel { /* ... */ }"},
                {'n': 'Константы перечисления', 'd': 'Внутри enum можно объявить константы, в том числе ссылающиеся на его варианты, — удобный способ задать значение по умолчанию.', 'o': 'self::Case в константах', 'v': '8.1', 'c': "enum Status: string\n{\n    case New = 'new';\n    const DEFAULT = self::New;\n}"},
                {'n': 'Перечисление как тип', 'd': 'Годится в параметрах, свойствах, возвратах. Именно это убирает проверки «а вдруг там не тот статус» из тела метода.', 'o': 'Status|null тоже работает', 'v': '8.1', 'c': "public function changeStatus(Status $to): void {}"},
                {'n': 'Свойства варианта в константных выражениях', 'd': 'С 8.2 `Status::New->value` можно писать там, где требуется константное выражение: в значениях по умолчанию и аргументах атрибутов.', 'o': 'только name и value', 'v': '8.2', 'c': "function find(string $s = Status::New->value) {}"},
                {'n': 'В JSON и базе', 'd': 'Привязанное перечисление сериализуется в своё значение, если реализует `JsonSerializable`, — иначе `json_encode()` отдаст объект. ORM обычно умеют приводить сами.', 'o': 'BackedEnum кодируется как value', 'v': '8.1', 'c': "json_encode(['status' => Status::Paid]);   // {\"status\":\"paid\"}"},
                {'n': 'Чего у перечислений нет', 'd': 'Ни свойств, ни конструктора, ни наследования, ни `new`. Варианты — одиночки: `Status::New === Status::New` всегда истинно.', 'o': 'instanceof работает', 'c': "$a = Status::New;\n$b = Status::from('new');\nvar_dump($a === $b);   // true"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Перечисление вместо набора констант'),
            ('code', 'php', None, r'''// было: значение — любая строка, опечатка всплывёт в продакшене
final class Order
{
    public const STATUS_NEW = 'new';
    public const STATUS_PAID = 'paid';

    public string $status = self::STATUS_NEW;
}

$order->status = 'payed';   // тишина

// стало: тип не пустит ничего постороннего
final class Order
{
    public Status $status = Status::New;
}

$order->status = 'payed';   // TypeError сразу'''),
            ('h', 'Переходы состояний внутри перечисления'),
            ('code', 'php', None, r'''enum Status: string
{
    case New = 'new';
    case Paid = 'paid';
    case Shipped = 'shipped';
    case Cancelled = 'cancelled';

    /** @return list<self> */
    public function allowedNext(): array
    {
        return match ($this) {
            self::New => [self::Paid, self::Cancelled],
            self::Paid => [self::Shipped, self::Cancelled],
            self::Shipped, self::Cancelled => [],
        };
    }

    public function canMoveTo(self $next): bool
    {
        return in_array($next, $this->allowedNext(), true);
    }
}'''),
            ('note', 'tip', 'match по перечислению не нуждается в default',
             'Если ветки покрывают все варианты, `default` не нужен — и это плюс: '
             'добавив новый вариант, вы получите `UnhandledMatchError` в первом же тесте, '
             'а не тихо уедете в ветку по умолчанию. С `default` новая карта состояний молча сломается.'),
            ('note', 'warn', 'Значение привязанного перечисления — часть контракта',
             '`value` уезжает в базу, в JSON и в чужие системы. Менять его нельзя так же, как нельзя менять '
             'название колонки: понадобится миграция данных. Имя варианта (`name`) — контракт для кода.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Магические методы

topic(
    id='magic', group='oop',
    title='Магические методы',
    cls='__get() · __call()',
    lead='Методы с двумя подчёркиваниями, которые PHP вызывает сам: при обращении к несуществующему '
         'свойству, при печати объекта, при клонировании и сериализации.',
    badge='15 методов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Магический метод — это **запасной путь**. PHP зовёт его, только когда обычный не сработал: '
                  '`__get()` — если свойства нет или оно недоступно, `__call()` — если метода нет. '
                  'Отсюда две особенности: магия не мешает обычным свойствам и методам, '
                  'и она невидима для IDE, анализаторов и автодополнения.'),
            ('code', 'php', None, r'''final class Bag
{
    private array $data = [];

    public function __get(string $name): mixed
    {
        return $this->data[$name] ?? null;
    }

    public function __set(string $name, mixed $value): void
    {
        $this->data[$name] = $value;
    }

    public function __isset(string $name): bool
    {
        return isset($this->data[$name]);   // без него isset($bag->x) всегда false
    }

    public function __unset(string $name): void
    {
        unset($this->data[$name]);
    }
}

$bag = new Bag();
$bag->title = 'Привет';   // __set
isset($bag->title);       // __isset — иначе false, даже когда значение есть
$bag->title;              // __get'''),
            ('note', 'trap', '__get() без __isset() ломает isset() и ??',
             '`isset($obj->prop)` и `$obj->prop ?? \'default\'` не зовут `__get()` — они зовут `__isset()`. '
             'Класс, где объявлен только `__get()`, будет уверенно отвечать, что свойства нет, '
             'и `??` всегда подставит значение по умолчанию.'),
            ('h', 'Цена магии'),
            ('kv', [
                ('IDE и анализаторы', 'не знают, какие свойства есть; спасает только `@property` в PHPDoc'),
                ('скорость', 'вызов метода вместо чтения поля; на горячем пути это заметно'),
                ('ошибки', 'опечатка в имени не ошибка, а новое «свойство» со значением `null`'),
                ('рефакторинг', 'переименование поля не находится поиском по коду'),
            ]),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': '__construct() / __destruct()', 'd': 'Создание и уничтожение. Деструктор вызывается, когда исчезла последняя ссылка, или при завершении скрипта — порядок в конце не гарантирован.', 'o': 'исключение в __destruct фатально', 'c': "public function __destruct()\n{\n    $this->flush();\n}"},
                {'n': '__get() / __set()', 'd': 'Чтение и запись недоступного свойства. С 8.4 то же самое чаще решается хуками — они видны анализаторам и работают с типами.', 'o': 'вызываются только для отсутствующих', 'c': "public function __get(string $n): mixed\n{\n    return $this->attributes[$n] ?? null;\n}"},
                {'n': '__isset() / __unset()', 'd': 'Обслуживают `isset()`, `empty()`, `??` и `unset()` для магических свойств. Без `__isset()` первые три врут.', 'o': 'идут в паре с __get', 'c': "public function __isset(string $n): bool\n{\n    return array_key_exists($n, $this->attributes);\n}"},
                {'n': '__call() / __callStatic()', 'd': 'Вызов несуществующего метода объекта и класса. На них стоят прокси, фасады и «текучие» построители запросов.', 'o': 'аргументы приходят массивом', 'c': "public function __call(string $m, array $args): mixed\n{\n    return $this->inner->$m(...$args);\n}"},
                {'n': '__invoke()', 'd': 'Объект вызывается как функция и проходит везде, где ждут `callable`. Так пишут обработчики с одной публичной операцией.', 'o': 'is_callable($obj) === true', 'c': "public function __invoke(Request $r): Response\n{\n    return new Response('ok');\n}"},
                {'n': '__toString()', 'd': 'Объект в строковом контексте. С 8.0 класс с этим методом автоматически реализует `Stringable`, и `string|Stringable` работает без лишних слов.', 'o': 'бросать исключение можно с 7.4', 'v': '8.0', 'c': "public function __toString(): string\n{\n    return $this->amount . ' ' . $this->currency;\n}"},
                {'n': '__clone()', 'd': 'Вызывается у копии сразу после поверхностного копирования. Место, где глубоко копируют вложенные объекты; с 8.3 здесь можно переприсвоить `readonly`.', 'o': 'копия уже создана', 'v': '8.3', 'c': "public function __clone(): void\n{\n    $this->items = array_map(fn($i) => clone $i, $this->items);\n}"},
                {'n': '__serialize() / __unserialize()', 'd': 'Что именно сохранять и как восстанавливать. Работают с массивом и заменяют собой и `Serializable`, и старую пару `__sleep()/__wakeup()`.', 'o': 'вместо интерфейса Serializable', 'v': '8.1', 'c': "public function __serialize(): array\n{\n    return ['id' => $this->id];\n}\n\npublic function __unserialize(array $data): void\n{\n    $this->id = $data['id'];\n}"},
                {'n': '__sleep() / __wakeup()', 'd': 'Древняя пара для сериализации. В 8.5 объявлена мягко устаревшей: новый код пишет `__serialize()`/`__unserialize()`.', 'o': 'оставляйте только ради PHP 7', 'v': '8.5', 'c': "public function __sleep(): array\n{\n    return ['id'];   // какие свойства сохранить\n}"},
                {'n': '__debugInfo()', 'd': 'Что показывать в `var_dump()`. Удобно, чтобы прятать пароли и не вываливать полгигабайта связанных объектов. Возврат `null` устарел в 8.5 — отдавайте пустой массив.', 'o': 'только для var_dump', 'v': '8.5', 'c': "public function __debugInfo(): array\n{\n    return ['user' => $this->user, 'token' => '***'];\n}"},
                {'n': '__set_state()', 'd': 'Вызывается при `var_export()`. Нужен, если экспортированный код должны уметь выполнять обратно — например, в кэше конфигурации.', 'o': 'статический метод', 'c': "public static function __set_state(array $a): static\n{\n    return new static($a['id']);\n}"},
                {'n': '@property в PHPDoc', 'd': 'Не язык, а соглашение: описывает магические свойства для IDE и анализаторов. Без него магический класс для инструментов — чёрный ящик.', 'o': '@method — то же для __call', 'c': "/**\n * @property-read int $id\n * @method self where(string $column, mixed $value)\n */\nfinal class Query {}"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Прокси с логированием на __call()'),
            ('code', 'php', 'src/Support/LoggingProxy.php', r'''final class LoggingProxy
{
    public function __construct(
        private readonly object $inner,
        private readonly Logger $log,
    ) {}

    public function __call(string $method, array $args): mixed
    {
        $started = hrtime(true);
        try {
            return $this->inner->$method(...$args);
        } finally {
            $this->log->debug(sprintf(
                '%s::%s — %.1f мс',
                $this->inner::class,
                $method,
                (hrtime(true) - $started) / 1e6,
            ));
        }
    }
}'''),
            ('note', 'tip', 'С 8.4 половина поводов для __get() исчезла',
             'Вычисляемое свойство, проверка при записи, «только чтение снаружи» — всё это теперь делают хуки '
             'и асимметричная видимость. В отличие от магии они объявлены явно, типизированы '
             'и видны анализатору. Магию оставляют там, где набор свойств действительно неизвестен заранее: '
             'в обёртках над данными и в прокси.'),
            ('note', 'warn', 'Магия и производительность',
             '`__get()` — это полноценный вызов метода вместо чтения поля, а `__call()` ещё и собирает массив '
               'аргументов. На единичных обращениях разницы нет, но в цикле на сто тысяч итераций '
               'она становится главным пунктом профиля.'),
        ]),
    ],
)
