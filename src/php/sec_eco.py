# -*- coding: utf-8 -*-
"""Вокруг языка: атрибуты и рефлексия, Composer, PSR, инструменты, версии."""

from model import topic

# --------------------------------------------------------------------------- Атрибуты

topic(
    id='attributes', group='eco',
    title='Атрибуты и рефлексия',
    cls='#[Attribute]',
    lead='Метаданные, которые пишутся в коде и читаются программой. '
         'То, ради чего раньше разбирали PHPDoc-комментарии регулярными выражениями.',
    badge='8.0',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Атрибут — это **объявление, которое компилятор сохраняет рядом с элементом кода**, '
                  'но сам не выполняет. Прочитать его можно только рефлексией, '
                  'и только там он превращается в объект своего класса.'),
            ('code', 'php', 'src/Routing/Route.php', r'''declare(strict_types=1);

#[Attribute(Attribute::TARGET_METHOD | Attribute::IS_REPEATABLE)]
final class Route
{
    public function __construct(
        public readonly string $path,
        public readonly string $method = 'GET',
    ) {}
}

final class OrderController
{
    #[Route('/orders', method: 'GET')]
    #[Route('/orders/list')]                 // повторяемый — можно несколько
    public function index(): Response { /* ... */ }
}

// читаем: без этого шага атрибут не делает ничего
$rc = new ReflectionClass(OrderController::class);
foreach ($rc->getMethods() as $method) {
    foreach ($method->getAttributes(Route::class) as $attr) {
        $route = $attr->newInstance();       // вот здесь создаётся объект Route
        $router->add($route->method, $route->path, [$rc->getName(), $method->getName()]);
    }
}'''),
            ('note', 'tip', 'Атрибут сам по себе ничего не делает',
             'Ни валидация, ни маршрут, ни кэш не появятся оттого, что вы написали `#[Route]`. '
             'Работает код, который **читает** атрибуты рефлексией. Именно поэтому фреймворки '
             'кэшируют результат чтения: рефлексия на каждом запросе — заметная трата.'),
            ('h', 'Куда можно ставить'),
            ('kv', [
                ('TARGET_CLASS', 'классы, интерфейсы, трейты, перечисления'),
                ('TARGET_METHOD / TARGET_FUNCTION', 'методы и функции'),
                ('TARGET_PROPERTY / TARGET_PARAMETER', 'свойства и параметры — на них держится валидация и внедрение зависимостей'),
                ('TARGET_CLASS_CONSTANT', 'константы класса; с 8.5 — и обычные константы'),
                ('TARGET_ALL | IS_REPEATABLE', 'везде; и разрешить несколько одинаковых на одном элементе'),
            ]),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Сначала атрибуты, встроенные в сам PHP, затем рефлексия — то, чем их читают.'),
            ('ref', [
                {'n': '#[Attribute]', 'd': 'Помечает класс как атрибут и задаёт, куда его разрешено ставить. Без него класс использовать как атрибут нельзя.', 'o': 'TARGET_*, IS_REPEATABLE', 'v': '8.0', 'c': "#[Attribute(Attribute::TARGET_PROPERTY)]\nfinal class Column {}"},
                {'n': '#[\\Override]', 'd': 'Проверка при компиляции: метод действительно переопределяет родительский или реализует метод интерфейса. С 8.5 применим и к свойствам.', 'o': 'ловит опечатки и переименования', 'v': '8.3', 'c': "#[\\Override]\npublic function handle(): void {}"},
                {'n': '#[\\Deprecated]', 'd': 'Помечает функцию, метод или константу устаревшими: вызов даёт `E_USER_DEPRECATED`, а IDE зачёркивает имя.', 'o': 'message, since', 'v': '8.4', 'c': "#[\\Deprecated(message: 'используйте send()', since: '3.1')]\npublic function post(): void {}"},
                {'n': '#[\\SensitiveParameter]', 'd': 'Прячет значение аргумента в трассировке исключения. Обязателен для паролей, токенов и ключей.', 'o': 'ставится на параметр', 'v': '8.2', 'c': "function connect(string $dsn, #[\\SensitiveParameter] string $password) {}"},
                {'n': '#[\\AllowDynamicProperties]', 'd': 'Разрешает классу динамические свойства, которые в 8.2 объявлены устаревшими. Нужен для старого кода, который присваивает что попало.', 'o': 'только на класс', 'v': '8.2', 'c': "#[\\AllowDynamicProperties]\nclass LegacyBag {}"},
                {'n': '#[\\ReturnTypeWillChange]', 'd': 'Подавляет предупреждение о несовпадении типа возврата с внутренним интерфейсом — временная мера на период миграции.', 'o': 'для ArrayAccess, Iterator и подобных', 'v': '8.1', 'c': "#[\\ReturnTypeWillChange]\npublic function offsetGet($offset) {}"},
                {'n': '#[\\NoDiscard]', 'd': 'Результат вызова обязан использоваться, иначе предупреждение. Явный `(void)` перед вызовом говорит «я знаю, что делаю».', 'o': '(void) подавляет', 'v': '8.5', 'c': "#[\\NoDiscard]\nfunction withHeader(string $h): static {}"},
                {'n': '#[\\DelayedTargetValidation]', 'd': 'Откладывает проверку «атрибут стоит не там» с компиляции до чтения рефлексией. Нужен библиотекам, поддерживающим несколько версий PHP.', 'o': 'ошибка всплывёт в newInstance()', 'v': '8.5', 'c': "#[\\DelayedTargetValidation]\n#[SomeAttr]\nclass X {}"},
                {'n': 'ReflectionClass', 'd': 'Точка входа в рефлексию: методы, свойства, константы, интерфейсы, атрибуты, создание объекта без конструктора.', 'o': 'getAttributes, newInstanceArgs', 'c': "$rc = new ReflectionClass($class);\n$rc->getShortName();\n$rc->implementsInterface(Handler::class);\n$rc->newInstanceWithoutConstructor();"},
                {'n': 'getAttributes()', 'd': 'Возвращает `ReflectionAttribute`, а не сам объект: имя и аргументы можно прочитать, не создавая экземпляр, — это дешевле и не зависит от загрузки класса.', 'o': 'фильтр по имени и INSTANCEOF', 'c': "foreach ($rp->getAttributes(Column::class, ReflectionAttribute::IS_INSTANCEOF) as $a) {\n    $a->getName();\n    $a->getArguments();\n    $a->newInstance();\n}"},
                {'n': 'ReflectionMethod / ReflectionProperty', 'd': 'Вызов и чтение в обход видимости. С 8.1 `setAccessible()` больше не нужен — приватное доступно сразу.', 'o': 'getValue, setValue, invoke', 'v': '8.1', 'c': "$rp = new ReflectionProperty($obj, 'secret');\n$rp->getValue($obj);   // setAccessible() не требуется"},
                {'n': 'ReflectionNamedType / ReflectionUnionType', 'd': 'Разбор объявленных типов: имя, допускается ли `null`, встроенный ли тип. На этом стоит автоматическое внедрение зависимостей.', 'o': 'getType() у параметра', 'c': "$type = $param->getType();\nif ($type instanceof ReflectionNamedType && !$type->isBuiltin()) {\n    $dep = $container->get($type->getName());\n}"},
                {'n': 'ReflectionEnum', 'd': 'Рефлексия перечислений: варианты, их значения и атрибуты на них. Так строят списки для интерфейса с подписями из атрибутов.', 'o': 'getCases(), getBackingType()', 'v': '8.1', 'c': "$re = new ReflectionEnum(Status::class);\n$re->getBackingType();"},
                {'n': 'ReflectionFunction / ReflectionClosure', 'd': 'Параметры, типы и атрибуты функции или замыкания. Используется в контейнерах для вызова колбэка с автоподстановкой аргументов.', 'o': 'getParameters(), invokeArgs()', 'c': "$rf = new ReflectionFunction($callable);\n$args = array_map($resolve(...), $rf->getParameters());\n$rf->invokeArgs($args);"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Свой атрибут проверки — и то, что его читает'),
            ('code', 'php', 'src/Validation/', r'''#[Attribute(Attribute::TARGET_PROPERTY)]
final class NotBlank
{
    public function __construct(public readonly string $message = 'не может быть пустым') {}
}

final class Form
{
    #[NotBlank]
    public string $title = '';

    #[NotBlank(message: 'укажите текст')]
    public string $body = '';
}

final class Validator
{
    /** @return array<string, string> ошибки по именам свойств */
    public function validate(object $object): array
    {
        $errors = [];
        foreach (new ReflectionClass($object)->getProperties() as $property) {
            foreach ($property->getAttributes(NotBlank::class) as $attribute) {
                $value = $property->getValue($object);
                if (trim((string) $value) === '') {
                    $errors[$property->getName()] = $attribute->newInstance()->message;
                }
            }
        }
        return $errors;
    }
}'''),
            ('note', 'warn', 'Рефлексия дорога — кэшируйте результат',
             'Разбор атрибутов у сотни классов на каждом запросе съедает больше, чем сама работа. '
             'Правило простое: рефлексия выполняется один раз, результат складывается в массив '
               'или файл (`var_export()` + `require`), а в рантайме читается уже он.'),
            ('note', 'tip', 'Атрибуты не заменяют конфигурацию',
             'Маршруты и правила валидации рядом с кодом читаются лучше. '
             'А вот настройки окружения, подключения и списки сервисов в атрибуты не помещаются: '
             'их меняют без правки кода. Обычно проект использует и то, и другое, '
             'и это нормально.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Composer

topic(
    id='composer', group='eco',
    title='Composer',
    cls='composer.json',
    lead='Менеджер зависимостей, который заодно раздаёт автозагрузку. '
         'Два файла: чего мы хотим и что в итоге установилось.',
    badge='зависимости',
    tabs=[
        ('how', 'Как устроено', [
            ('p', '`composer.json` описывает **пожелания**: какие пакеты нужны и в каких пределах версий. '
                  '`composer.lock` фиксирует **результат**: конкретные версии с контрольными суммами. '
                  'На сервере выполняется `composer install`, который ставит ровно то, что в lock-файле, '
                  'и поэтому у всех одинаковый набор.'),
            ('code', 'json', 'composer.json', r'''{
  "name": "acme/shop",
  "type": "project",
  "require": {
    "php": "^8.3",
    "psr/log": "^3.0",
    "ext-mbstring": "*"
  },
  "require-dev": {
    "phpunit/phpunit": "^11.0",
    "phpstan/phpstan": "^2.0"
  },
  "autoload": {
    "psr-4": { "App\\": "src/" },
    "files": ["src/Support/helpers.php"]
  },
  "autoload-dev": {
    "psr-4": { "App\\Tests\\": "tests/" }
  },
  "scripts": {
    "test": "phpunit",
    "stan": "phpstan analyse --memory-limit=512M",
    "check": ["@stan", "@test"]
  },
  "config": {
    "sort-packages": true,
    "platform": { "php": "8.3.0" }
  }
}'''),
            ('h', 'Ограничения версий'),
            ('kv', [
                ('^3.2', 'от 3.2 до 4.0 — разрешает минорные и патчи. Обычный выбор для библиотек'),
                ('~3.2', 'от 3.2 до 3.3 — только патчи. Строже, чем `^`'),
                ('~3.2.1', 'от 3.2.1 до 3.3 — тоже только патчи, но с точкой отсчёта'),
                ('3.*', 'любая версия ветки 3'),
                ('>=3.2 <4.0', 'явный диапазон; пишут, когда нужны нестандартные границы'),
                ('dev-main', 'ветка вместо версии — только для своих пакетов и временных правок'),
            ]),
            ('note', 'trap', 'composer.lock нужно коммитить',
             'Без него `composer install` на сервере и в CI поставит **другие** версии, '
             'чем у вас на машине: диапазон `^3.0` со временем начинает означать другое. '
             'Правило: `composer.lock` в репозитории, `vendor/` — нет.'),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Команды, которые нужны каждый день, и поля файла, которые действительно настраивают.'),
            ('ref', [
                {'n': 'composer install', 'd': 'Ставит ровно то, что записано в `composer.lock`. Это команда для сервера, CI и коллеги, который только клонировал репозиторий.', 'o': '--no-dev --optimize-autoloader на проде', 'c': "composer install --no-dev --optimize-autoloader --no-interaction", 'lang': 'bash'},
                {'n': 'composer update', 'd': 'Пересчитывает зависимости по ограничениям и переписывает lock-файл. Команда разработчика, а не деплоя. Можно обновить один пакет.', 'o': '--with-dependencies', 'c': "composer update psr/log --with-dependencies\ncomposer update --dry-run", 'lang': 'bash'},
                {'n': 'composer require / remove', 'd': 'Добавить или убрать пакет, обновив оба файла. Без указания версии Composer подберёт актуальную и запишет ограничение сам.', 'o': '--dev для инструментов', 'c': "composer require symfony/console\ncomposer require --dev phpstan/phpstan", 'lang': 'bash'},
                {'n': 'composer dump-autoload', 'd': 'Перестроить карту автозагрузки после изменений в секции `autoload`. На проде — с оптимизацией.', 'o': '-o, --classmap-authoritative', 'c': "composer dump-autoload -o", 'lang': 'bash'},
                {'n': 'composer outdated / show', 'd': 'Что устарело и что вообще установлено. `outdated --direct` показывает только ваши зависимости, без транзитивных.', 'o': '--direct, --major-only', 'c': "composer outdated --direct\ncomposer show --tree", 'lang': 'bash'},
                {'n': 'composer audit', 'd': 'Проверка установленных версий по базе известных уязвимостей. Место этой команды — в CI, рядом с тестами.', 'o': '--locked проверяет lock-файл', 'c': "composer audit --locked", 'lang': 'bash'},
                {'n': 'composer why / why-not', 'd': 'Кто тянет этот пакет и что мешает поставить нужную версию. Первое, что запускают, когда обновление «не идёт».', 'o': 'depends / prohibits', 'c': "composer why psr/container\ncomposer why-not php 8.4", 'lang': 'bash'},
                {'n': 'require: php и ext-*', 'd': 'Версия PHP и расширения — такие же зависимости, как пакеты. Composer откажется ставить то, что не запустится на целевой версии.', 'o': 'ext-json, ext-pdo, ext-intl', 'c': "\"require\": {\n  \"php\": \"^8.3\",\n  \"ext-intl\": \"*\"\n}", 'lang': 'json'},
                {'n': 'config.platform', 'd': 'Говорит Composer, какая версия PHP на сервере, даже если локально другая. Без этого можно собрать зависимости, которые на проде не поставятся.', 'o': 'платформа фиксируется в lock', 'c': "\"config\": {\n  \"platform\": { \"php\": \"8.3.0\" }\n}", 'lang': 'json'},
                {'n': 'scripts', 'd': 'Команды проекта под короткими именами — общая точка входа для разработчика и CI. Ссылка `@name` вызывает другой скрипт.', 'o': 'события post-install-cmd и другие', 'c': "\"scripts\": {\n  \"check\": [\"@stan\", \"@test\"]\n}", 'lang': 'json'},
                {'n': 'autoload: psr-4, files, classmap', 'd': 'Три способа найти код. `psr-4` — основной, `files` подключается всегда (для функций), `classmap` сканирует каталоги без соглашений об именах.', 'o': 'autoload-dev — только для тестов', 'c': "\"autoload\": {\n  \"psr-4\": { \"App\\\\\": \"src/\" },\n  \"files\": [\"src/helpers.php\"]\n}", 'lang': 'json'},
                {'n': 'replace / conflict / provide', 'd': 'Поля для сложных случаев: пакет заменяет другой, несовместим с ним или предоставляет реализацию интерфейса (например, PSR-логгера).', 'o': 'чаще нужны авторам пакетов', 'c': "\"provide\": { \"psr/log-implementation\": \"3.0\" }", 'lang': 'json'},
                {'n': 'repositories', 'd': 'Откуда брать пакеты кроме Packagist: приватный Git, локальный путь, собственный Satis. Путь удобен для разработки пакета рядом с проектом.', 'o': 'type: vcs | path | composer', 'c': "\"repositories\": [\n  { \"type\": \"path\", \"url\": \"../my-package\" }\n]", 'lang': 'json'},
                {'n': 'Вендорные бинарники', 'd': 'Пакеты кладут исполняемые файлы в `vendor/bin`. Их запускают оттуда или через `composer exec`, чтобы версия совпадала с зафиксированной в проекте.', 'o': 'bin-dir настраивается', 'c': "vendor/bin/phpunit\ncomposer exec -- phpstan analyse", 'lang': 'bash'},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Одна команда на проверку всего'),
            ('code', 'json', 'composer.json', r'''{
  "scripts": {
    "lint": "parallel-lint src tests",
    "cs": "php-cs-fixer fix --dry-run --diff",
    "stan": "phpstan analyse",
    "test": "phpunit",
    "check": ["@lint", "@cs", "@stan", "@test"]
  }
}'''),
            ('code', 'bash', None, r'''composer check          # то же самое запускает и CI, и разработчик
composer install --no-dev --optimize-autoloader   # сборка для прода'''),
            ('note', 'tip', 'Обновляйтесь малыми шагами',
             '`composer update` всего сразу превращает обновление в отдельный проект с непонятным '
             'сроком. Раз в пару недель `composer outdated --direct`, затем обновление одного-двух '
             'пакетов с прогоном тестов — и версия зависимостей никогда не становится проблемой.'),
            ('note', 'warn', 'Пакет — это чужой код в вашем процессе',
             'Он выполняется с теми же правами, читает ту же память и попадает в ваш деплой. '
             'Перед установкой стоит посмотреть на число поддерживающих, дату последнего релиза '
             'и объём: зависимость ради одной функции на двадцать строк почти никогда не окупается.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- PSR

topic(
    id='psr', group='eco',
    title='PSR — общие интерфейсы',
    cls='psr/log · psr/http',
    lead='Договорённости PHP-FIG: как оформлять код и какими интерфейсами обмениваться, '
         'чтобы библиотеки разных авторов подходили друг к другу.',
    badge='12 стандартов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'PSR — это рекомендации группы PHP-FIG. Часть из них про **оформление кода**, '
                  'часть — готовые **пакеты с интерфейсами**: `psr/log`, `psr/container`, '
                  '`psr/http-message`. Второе важнее первого: библиотека, которая принимает '
                  '`LoggerInterface`, работает с любым логгером, а не только с тем, о котором знал автор.'),
            ('code', 'php', None, r'''use Psr\Log\LoggerInterface;
use Psr\Log\NullLogger;

final class PaymentService
{
    public function __construct(
        private readonly LoggerInterface $log = new NullLogger(),
    ) {}

    public function pay(Order $order): void
    {
        $this->log->info('оплата начата', ['order' => $order->id]);
    }
}

// в проекте сюда попадёт Monolog, в тесте — свой заглушечный логгер:
// классу всё равно, он знает только интерфейс'''),
            ('note', 'tip', 'Интерфейс из пакета — это не зависимость от фреймворка',
             '`psr/log` — три файла без единой строки реализации. Пакет, который принимает '
             '`LoggerInterface`, не тянет за собой Monolog и вообще ничего не навязывает. '
             'Именно поэтому такие интерфейсы стали общим языком экосистемы.'),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Принятые стандарты, которые встречаются в реальных проектах. '
                  'Номера идут по времени принятия, поэтому соседние номера редко связаны по смыслу.'),
            ('ref', [
                {'n': 'PSR-1 и PSR-12 — стиль кода', 'd': 'Базовые правила и подробный стиль оформления: отступы, переносы, порядок модификаторов. Проверяются и исправляются автоматически.', 'o': 'php-cs-fixer, PHP_CodeSniffer', 'c': "vendor/bin/php-cs-fixer fix --rules=@PSR12", 'lang': 'bash'},
                {'n': 'PSR-4 — автозагрузка', 'd': 'Правило «пространство имён = каталог, класс = файл». То, что делает автозагрузчик Composer и без чего проект не собрать.', 'o': 'см. узел «автозагрузка»', 'c': "\"autoload\": { \"psr-4\": { \"App\\\\\": \"src/\" } }", 'lang': 'json'},
                {'n': 'PSR-3 — логирование', 'd': '`LoggerInterface` с восемью уровнями и контекстом. Самый распространённый PSR: его принимают почти все библиотеки.', 'o': 'пакет psr/log', 'c': "$log->error('платёж отклонён', ['order' => $id, 'code' => $code]);"},
                {'n': 'PSR-11 — контейнер', 'd': 'Два метода: `get()` и `has()`. Позволяет библиотеке принять любой DI-контейнер, не зная, какой именно.', 'o': 'пакет psr/container', 'c': "interface ContainerInterface\n{\n    public function get(string $id): mixed;\n    public function has(string $id): bool;\n}"},
                {'n': 'PSR-7 — HTTP-сообщения', 'd': 'Неизменяемые объекты запроса и ответа: каждый `withHeader()` возвращает копию. На них построены Slim, Mezzio и большинство middleware.', 'o': 'пакет psr/http-message', 'c': "$response = $response\n    ->withStatus(201)\n    ->withHeader('Content-Type', 'application/json');"},
                {'n': 'PSR-15 — обработчики и middleware', 'd': 'Запрос проходит цепочку посредников и доходит до обработчика. Аутентификация, CORS и логирование становятся отдельными классами.', 'o': 'MiddlewareInterface, RequestHandlerInterface', 'c': "public function process(\n    ServerRequestInterface $request,\n    RequestHandlerInterface $handler,\n): ResponseInterface {\n    return $handler->handle($request)->withHeader('X-Time', (string) time());\n}"},
                {'n': 'PSR-17 — фабрики HTTP-объектов', 'd': 'Как создать запрос, ответ или поток, не завися от конкретной реализации PSR-7.', 'o': 'ResponseFactoryInterface', 'c': "$response = $this->responseFactory->createResponse(204);"},
                {'n': 'PSR-18 — HTTP-клиент', 'd': 'Один метод `sendRequest()`. Библиотека-обёртка над чужим API может не тянуть Guzzle, а принять любой клиент.', 'o': 'пакет psr/http-client', 'c': "$response = $this->client->sendRequest($request);"},
                {'n': 'PSR-6 и PSR-16 — кэш', 'd': 'Два интерфейса: подробный с объектами-элементами (PSR-6) и простой «ключ-значение» (PSR-16). В прикладном коде обычно берут второй.', 'o': 'psr/cache, psr/simple-cache', 'c': "$value = $cache->get('rates') ?? $this->fetchAndStore();\n$cache->set('rates', $value, ttl: 3600);"},
                {'n': 'PSR-14 — диспетчер событий', 'd': 'Общий интерфейс шины событий: объект-событие уходит слушателям. Позволяет пакетам объявлять события, не привязываясь к фреймворку.', 'o': 'EventDispatcherInterface', 'c': "$dispatcher->dispatch(new OrderPaid($order));"},
                {'n': 'PSR-20 — часы', 'd': 'Интерфейс `ClockInterface` с одним методом `now()`. Делает тестируемым любой код, который зависит от текущего времени.', 'o': 'пакет psr/clock', 'c': "public function __construct(private readonly ClockInterface $clock) {}\n\n$now = $this->clock->now();"},
                {'n': 'PSR-13 — ссылки', 'd': 'Описание гипермедиа-ссылок для API. Встречается редко, но входит в список принятых.', 'o': 'psr/link', 'c': "$link->getHref();"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Зависимость от интерфейса, а не от библиотеки'),
            ('code', 'php', None, r'''// было: класс намертво связан с конкретным логгером и клиентом
final class Notifier
{
    public function send(string $to): void
    {
        (new Monolog\Logger('app'))->info('шлём ' . $to);
        (new GuzzleHttp\Client())->post('https://api.example.com/send');
    }
}

// стало: подменяется в тесте, не тянет лишнего в composer.json
final class Notifier
{
    public function __construct(
        private readonly ClientInterface $http,          // PSR-18
        private readonly RequestFactoryInterface $requests, // PSR-17
        private readonly LoggerInterface $log = new NullLogger(), // PSR-3
    ) {}
}'''),
            ('note', 'warn', 'PSR — не всегда лучший выбор',
             'PSR-7 с его неизменяемыми объектами многословен, PSR-6 сложнее, чем нужно половине проектов. '
             'Смысл стандартов — в **совместимости**: они нужны там, где код должен подойти чужому '
               'приложению. Во внутреннем сервисе свой маленький интерфейс часто честнее.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Инструменты

topic(
    id='tools', group='eco',
    title='Инструменты',
    cls='phpstan · phpunit',
    lead='Пять инструментов, которые ловят ошибки до продакшена: статический анализ, тесты, '
         'единый стиль, автоматический рефакторинг и отладчик.',
    badge='7 штук',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'PHP не компилируется заранее, поэтому «синтаксически верно» не значит «работает». '
                  'Разницу закрывают инструменты: **статический анализатор** читает код и находит то, '
                  'что упадёт при выполнении, **тесты** проверяют поведение, '
                  '**форматтер** убирает споры о стиле из обсуждений.'),
            ('code', 'bash', None, r'''composer require --dev phpstan/phpstan phpunit/phpunit friendsofphp/php-cs-fixer rector/rector

vendor/bin/phpstan analyse src --level=8   # уровень 0 — мягкий, 9 (max) — строгий
vendor/bin/phpunit
vendor/bin/php-cs-fixer fix
vendor/bin/rector process src --dry-run'''),
            ('h', 'Что во что упирается'),
            ('kv', [
                ('php -l', 'только синтаксис; бесплатно и мгновенно — годится как самый первый шаг в CI'),
                ('PHPStan / Psalm', 'типы, недостижимый код, обращения к несуществующим методам — без запуска'),
                ('PHPUnit', 'поведение: что код действительно делает с этими данными'),
                ('php-cs-fixer', 'оформление; спорить о скобках больше не нужно'),
                ('Rector', 'массовые правки: миграция на новую версию PHP, замена устаревшего'),
                ('Xdebug', 'пошаговая отладка и покрытие тестами; на проде — выключен'),
            ]),
            ('note', 'tip', 'Статический анализ начинают не с максимума',
             'Поставьте уровень, на котором ошибок немного, зафиксируйте текущие проблемы в baseline '
             '(`phpstan analyse --generate-baseline`) и поднимайте планку по одному уровню. '
               'Так анализатор начинает приносить пользу с первого дня, а не «когда-нибудь потом».'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'PHPStan', 'd': 'Статический анализатор с уровнями строгости от 0 до 10. Понимает PHPDoc-обобщения (`list<User>`, `array<string, int>`), которых в самом языке нет.', 'o': 'baseline, расширения для фреймворков', 'c': "parameters:\n    level: 8\n    paths: [src, tests]\n    treatPhpDocTypesAsCertain: false", 'lang': 'yaml'},
                {'n': 'Psalm', 'd': 'Второй крупный анализатор. Похож на PHPStan, сильнее в выводе типов и умеет автоматически исправлять часть находок.', 'o': 'psalm --alter --issues=MissingReturnType', 'c': "vendor/bin/psalm --show-info=true", 'lang': 'bash'},
                {'n': 'PHPUnit', 'd': 'Стандарт тестирования. Атрибуты вместо аннотаций — с 10-й версии; покрытие требует Xdebug или PCOV.', 'o': 'phpunit.xml, dataProvider', 'c': "#[Test]\n#[DataProvider('cases')]\npublic function it_sums(int $a, int $b, int $sum): void\n{\n    self::assertSame($sum, add($a, $b));\n}"},
                {'n': 'php-cs-fixer / PHP_CodeSniffer', 'd': 'Единый стиль: первый исправляет, второй проверяет. Настраивается набором правил — обычно берут `@PSR12` и добавляют своё.', 'o': '.php-cs-fixer.dist.php', 'c': "vendor/bin/php-cs-fixer fix --dry-run --diff", 'lang': 'bash'},
                {'n': 'Rector', 'd': 'Автоматический рефакторинг по правилам: перевод кода на новую версию PHP, замена устаревших вызовов, добавление типов. Незаменим при обновлении больших проектов.', 'o': 'наборы LevelSetList, SetList', 'c': "return RectorConfig::configure()\n    ->withPaths([__DIR__ . '/src'])\n    ->withPhpSets(php84: true)\n    ->withTypeCoverageLevel(5);"},
                {'n': 'Xdebug', 'd': 'Пошаговая отладка, трассировка и покрытие. Замедляет выполнение в разы, поэтому включается только на рабочей машине.', 'o': 'xdebug.mode=debug,coverage', 'c': "xdebug.mode=debug\nxdebug.client_host=host.docker.internal\nxdebug.start_with_request=yes", 'lang': 'ini'},
                {'n': 'composer audit', 'd': 'Проверка зависимостей на известные уязвимости прямо из Composer, без отдельного сервиса.', 'o': 'ставьте в CI', 'c': "composer audit --locked", 'lang': 'bash'},
                {'n': 'PHPBench / Blackfire', 'd': 'Замер производительности: первый — микротесты в репозитории, второй — профилирование реального запроса с разбором, где именно потрачено время.', 'o': 'профилировать до оптимизации', 'c': "vendor/bin/phpbench run --report=aggregate", 'lang': 'bash'},
                {'n': 'Deptrac / PHPArkitect', 'd': 'Проверка архитектурных правил: какой слой какому может звонить. Не даёт домену начать зависеть от контроллеров.', 'o': 'правила описываются в конфиге', 'c': "vendor/bin/deptrac analyse", 'lang': 'bash'},
                {'n': 'Infection', 'd': 'Мутационное тестирование: портит код и смотрит, заметят ли это тесты. Отвечает на вопрос «покрытие 90%, но проверяет ли оно хоть что-нибудь».', 'o': 'MSI — индекс качества тестов', 'c': "vendor/bin/infection --min-msi=70", 'lang': 'bash'},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Минимальный набор в CI'),
            ('code', 'yaml', '.github/workflows/ci.yml', r'''name: CI
on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.4'
          coverage: none
      - run: composer install --no-interaction --prefer-dist
      - run: composer audit --locked
      - run: vendor/bin/php-cs-fixer fix --dry-run --diff
      - run: vendor/bin/phpstan analyse --no-progress
      - run: vendor/bin/phpunit'''),
            ('note', 'tip', 'Локально то же самое, что в CI',
             'Если проверки запускаются одной командой (`composer check`), никто не узнаёт '
             'о нарушении стиля из красной сборки через десять минут. '
               'Полезно и в git-хуке перед коммитом — но только быстрые проверки, иначе его отключат.'),
            ('note', 'warn', 'Инструменты не заменяют ревью',
             'Анализатор не скажет, что метод называется неверно, абстракция протекает, '
             'а вместо трёх классов хватило бы функции. Он снимает механическую часть — '
             'и именно поэтому на ревью остаётся время для содержательной.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Версии

# Данные для демонстрации «что даёт версия»: build_php.py кладёт их в страницу,
# php.js рисует по ним переключатель. Даты выпуска — по php.net.
VERSIONS = [
    {
        'v': '8.0', 'date': 'ноябрь 2020', 'state': 'не поддерживается с ноября 2023',
        'lead': 'Самый крупный выпуск восьмёрки: именованные аргументы, match, атрибуты, '
                'конструктор в одну строку и другие правила сравнения.',
        'added': [
            ('Именованные аргументы', 'вызов по именам параметров вместо позиций'),
            ('Атрибуты #[...]', 'метаданные в коде вместо разбора PHPDoc'),
            ('Продвижение свойств конструктора', 'свойство объявляется прямо в параметре'),
            ('match', 'выражение со строгим сравнением и обязательным результатом'),
            ('Оператор ?->', 'nullsafe-цепочка вместо лестницы проверок на null'),
            ('Объединения типов', 'int|string прямо в объявлении'),
            ('static как тип возврата', 'фабрики и текучие интерфейсы наконец типизируются'),
            ('throw как выражение', 'throw в ??, в тернарнике и в стрелочной функции'),
            ('catch без переменной', 'catch (CacheMiss) — если объект не нужен'),
            ('str_contains, str_starts_with, str_ends_with', 'вместо strpos() !== false'),
            ('get_debug_type()', 'название типа ровно такое, как в объявлении'),
            ('WeakMap', 'кэш по объекту, который не мешает сборке мусора'),
            ('JIT', 'компиляция горячего кода в машинный; заметна на вычислениях'),
            ('Stringable, ValueError, UnhandledMatchError', 'новые интерфейсы и классы ошибок'),
        ],
        'gone': [
            ('Число и строка сравниваются иначе', '0 == "abc" стало false — самое заметное изменение выпуска'),
            ('Предупреждения стали ошибками', 'многие внутренние функции теперь бросают TypeError и ValueError'),
            ('@ не глушит фатальные ошибки', 'подавление перестало прятать падения'),
            ('Убраны create_function() и each()', 'а также синтаксис $str{0}'),
        ],
    },
    {
        'v': '8.1', 'date': 'ноябрь 2021', 'state': 'не поддерживается с января 2026',
        'lead': 'Выпуск неизменяемости и перечислений: readonly, enum, файберы и первоклассный '
                'синтаксис вызова.',
        'added': [
            ('Перечисления', 'enum с методами, интерфейсами и привязанными значениями'),
            ('readonly-свойства', 'записываются один раз — основа value-объектов'),
            ('Файберы', 'остановка и продолжение кода на любой глубине вызовов'),
            ('never', 'тип возврата для функций, которые не возвращаются'),
            ('Первоклассный вызов f(...)', 'замыкание из любой функции с сохранением типов'),
            ('new в инициализаторах', 'объект как значение по умолчанию параметра'),
            ('Пересечения типов', 'Countable&ArrayAccess'),
            ('final для констант класса', 'наследник не подменит значение'),
            ('Распаковка со строковыми ключами', '[...$defaults, ...$options]'),
            ('array_is_list()', 'список это или словарь — важно перед json_encode()'),
            ('fsync() и fdatasync()', 'сброс записи на диск по-настоящему'),
        ],
        'gone': [
            ('Интерфейс Serializable', 'устарел в пользу __serialize() и __unserialize()'),
            ('Неявная потеря точности float → int', 'теперь предупреждение'),
            ('null в параметры встроенных функций', 'передача null туда, где ожидается скаляр, устарела'),
            ('strftime(), FILTER_SANITIZE_STRING', 'и ещё несколько функций объявлены устаревшими'),
        ],
    },
    {
        'v': '8.2', 'date': 'декабрь 2022', 'state': 'исправления безопасности до конца 2026 года',
        'lead': 'Небольшой выпуск про типы и аккуратность: readonly-классы, самостоятельные '
                'true/false/null и конец динамическим свойствам.',
        'added': [
            ('readonly-классы', 'все свойства неизменяемы одним словом'),
            ('Типы true, false и null', 'теперь самостоятельные, а не только внутри объединения'),
            ('DNF-типы', '(A&B)|null — пересечения внутри объединения'),
            ('Константы в трейтах', 'раньше их там не было вовсе'),
            ('#[\\SensitiveParameter]', 'пароль не попадёт в трассировку'),
            ('Свойства перечислений в константных выражениях', 'Status::New->value как значение по умолчанию'),
        ],
        'gone': [
            ('Динамические свойства', 'устарели; классу нужен #[\\AllowDynamicProperties]'),
            ('Интерполяция ${var}', 'устарела, остаётся "$var" и "{$expr}"'),
            ('utf8_encode() и utf8_decode()', 'устарели: названия вводили в заблуждение'),
            ('Частичные callable-строки', '"self::method" и подобное устарели'),
        ],
    },
    {
        'v': '8.3', 'date': 'ноябрь 2023', 'state': 'исправления безопасности до конца 2027 года',
        'lead': 'Выпуск про мелкие, но заметные удобства: типизированные константы, #[\\Override] '
                'и проверка JSON без разбора.',
        'added': [
            ('Типизированные константы класса', 'const string ENV = "prod"'),
            ('#[\\Override]', 'проверка, что метод действительно что-то переопределяет'),
            ('Динамическое обращение к константам', 'C::{$name}'),
            ('Переприсваивание readonly в __clone()', 'копия с изменением стала возможной'),
            ('json_validate()', 'проверка без построения структуры'),
            ('str_increment(), str_decrement()', 'безопасная замена $s++ для строк'),
            ('mb_str_pad()', 'выравнивание, которое не ломается на кириллице'),
            ('Любые выражения в static-переменных', 'инициализатор больше не обязан быть константой'),
            ('Свои исключения дат', 'DateMalformedStringException вместо разбора текста ошибки'),
        ],
        'gone': [
            ('++ и -- на нечисловых строках', 'поведение объявлено устаревшим'),
            ('get_class() без аргументов', 'устарело — пишите $this::class'),
            ('assert_options()', 'устарела вместе с семейством констант ASSERT_*'),
        ],
    },
    {
        'v': '8.4', 'date': 'ноябрь 2024', 'state': 'активная поддержка до конца 2026 года',
        'lead': 'Выпуск про свойства: хуки, раздельная видимость на чтение и запись, '
                'ленивые объекты и новые функции массивов.',
        'added': [
            ('Хуки свойств', 'get и set прямо у свойства — вместо пары геттер-сеттер'),
            ('Асимметричная видимость', 'public private(set): читают все, пишет класс'),
            ('Ленивые объекты', 'создаются при первом обращении; раньше это делали прокси'),
            ('#[\\Deprecated]', 'пометка устаревшего кода, видимая IDE и движку'),
            ('new Foo()->method()', 'цепочка после new без скобок вокруг выражения'),
            ('array_find(), array_any(), array_all()', 'поиск и проверки без ручных циклов'),
            ('DateTime::createFromTimestamp()', 'с поддержкой дробных секунд'),
            ('mb_trim() и родственники', 'многобайтовые версии обрезки строк'),
            ('Dom\\HTMLDocument', 'разбор HTML5 по стандарту вместо старого DOMDocument'),
        ],
        'gone': [
            ('Неявно nullable параметры', 'function f(int $x = null) устарело — пишите ?int'),
            ('E_STRICT', 'константа устарела, уровень больше не используется'),
            ('trigger_error(E_USER_ERROR)', 'устарел: бросайте исключение'),
        ],
    },
    {
        'v': '8.5', 'date': 'ноябрь 2025', 'state': 'активная поддержка',
        'lead': 'Выпуск про читаемость вызовов: конвейер |>, clone с изменением свойств '
                'и обязательное использование результата.',
        'added': [
            ('Оператор конвейера |>', 'цепочка вызовов читается слева направо'),
            ('clone с изменением свойств', 'clone($obj, [...]) — копия с новыми значениями, включая readonly'),
            ('#[\\NoDiscard] и приведение (void)', 'предупреждение, если результат вызова потерян'),
            ('Замыкания в константных выражениях', 'static fn() как значение по умолчанию'),
            ('Closure::getCurrent()', 'рекурсия без внешней переменной'),
            ('array_first() и array_last()', 'без reset() и end(), не трогая указатель массива'),
            ('Асимметричная видимость у static-свойств', 'private(set) теперь и для статических'),
            ('final у продвинутых свойств конструктора', 'наследник их не переопределит'),
            ('Трассировка у фатальных ошибок', 'превышение памяти и времени больше не безымянно'),
            ('get_error_handler() и get_exception_handler()', 'текущий обработчик можно прочитать'),
            ('Расширение URI', 'разбор адресов по RFC 3986 и WHATWG без регулярных выражений'),
            ('Атрибуты на константах', '#[\\Deprecated] работает и для обычных констант'),
        ],
        'gone': [
            ('__sleep() и __wakeup()', 'мягко устарели: пишите __serialize()/__unserialize()'),
            ('Обратные кавычки `cmd`', 'устарели как синоним shell_exec()'),
            ('Приведения (boolean), (integer), (double)', 'устарели — только (bool), (int), (float)'),
            ('Инкремент нечисловых строк', 'устарел окончательно: есть str_increment()'),
            ('null как ключ массива', 'использование null в качестве смещения устарело'),
        ],
    },
]

topic(
    id='versions', group='eco',
    title='Версии 8.0–8.5',
    cls='PHP_VERSION',
    lead='Что появилось в каждом выпуске восьмёрки, что из старого перестало работать '
         'и как переезжать, не устраивая проект на полгода.',
    badge='что нового',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Выпуски PHP выходят **раз в год, в конце ноября**. Каждая версия получает два года '
                  'активной поддержки и ещё два — только исправления безопасности. '
                  'Отсюда практическое правило: отставание больше двух версий означает, '
                  'что дыры в вашем PHP уже никто не чинит.'),
            ('demo', 'version-lab'),
            ('note', 'trap', 'Устаревшее — это не «сломается завтра»',
             '`E_DEPRECATED` ничего не ломает сегодня, но обещает ошибку в следующей крупной версии. '
             'Проект, где в логе тысячи deprecated-сообщений, обновляется рывком и с болью; '
             'проект, где их ноль, переезжает за вечер.'),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Все заметные возможности восьмёрки в одном списке — с версией, '
                  'начиная с которой их можно писать. Фильтр понимает и номер версии: '
                  'наберите «8.3», чтобы увидеть только её.'),
            ('ref', [
                {'n': 'Именованные аргументы', 'd': 'Передача по имени параметра, а не по позиции.', 'o': 'см. узел «функции»', 'v': '8.0', 'c': "setcookie('token', $v, httponly: true, samesite: 'Lax');"},
                {'n': 'Атрибуты', 'd': 'Машиночитаемые метаданные вместо аннотаций в комментариях.', 'o': 'см. узел «атрибуты»', 'v': '8.0', 'c': "#[Route('/orders', method: 'POST')]"},
                {'n': 'Продвижение свойств конструктора', 'd': 'Объявление свойства прямо в параметре конструктора.', 'o': 'см. узел «классы»', 'v': '8.0', 'c': "public function __construct(private readonly Clock $clock) {}"},
                {'n': 'match', 'd': 'Выражение со строгим сравнением, без провала между ветками.', 'o': 'см. узел «операторы»', 'v': '8.0', 'c': "$code = match ($status) { 'new' => 201, default => 400 };"},
                {'n': 'Оператор ?->', 'd': 'Вся цепочка даёт null, если слева оказался null.', 'o': 'см. узел «операторы»', 'v': '8.0', 'c': "$city = $order?->customer?->address?->city;"},
                {'n': 'Объединения типов', 'd': 'int|string в объявлении параметра, свойства или возврата.', 'o': 'см. узел «типы»', 'v': '8.0', 'c': "function size(int|string $v): int {}"},
                {'n': 'Сравнение чисел и строк', 'd': 'Число сравнивается с нечисловой строкой как строка: `0 == "abc"` теперь false.', 'o': 'главное ломающее изменение 8.0', 'v': '8.0', 'c': "var_dump(0 == 'abc');   // false"},
                {'n': 'Перечисления', 'd': 'Тип с фиксированным набором значений, методами и интерфейсами.', 'o': 'см. узел «перечисления»', 'v': '8.1', 'c': "enum Status: string { case New = 'new'; }"},
                {'n': 'readonly-свойства', 'd': 'Запись один раз из области видимости класса.', 'o': 'см. узел «свойства»', 'v': '8.1', 'c': "public readonly DateTimeImmutable $at;"},
                {'n': 'Файберы', 'd': 'Остановка и продолжение выполнения на любой глубине стека.', 'o': 'см. узел «файберы»', 'v': '8.1', 'c': "$value = Fiber::suspend($request);"},
                {'n': 'Первоклассный вызов', 'd': 'Замыкание из функции или метода: `strlen(...)`.', 'o': 'см. узел «замыкания»', 'v': '8.1', 'c': "$fn = $mailer->send(...);"},
                {'n': 'never', 'd': 'Функция не возвращает управление: бросает или завершает процесс.', 'o': 'см. узел «типы»', 'v': '8.1', 'c': "function fail(): never { throw new RuntimeException(); }"},
                {'n': 'Пересечения типов', 'd': 'Объект, реализующий сразу несколько интерфейсов.', 'o': 'см. узел «типы»', 'v': '8.1', 'c': "function f(Countable&ArrayAccess $bag) {}"},
                {'n': 'readonly-классы', 'd': 'Все свойства класса неизменяемы, динамические запрещены.', 'o': 'см. узел «свойства»', 'v': '8.2', 'c': "readonly class Point { public function __construct(public int $x) {} }"},
                {'n': 'Типы true, false, null', 'd': 'Самостоятельные типы, а не только части объединения.', 'o': 'см. узел «типы»', 'v': '8.2', 'c': "function open(string $p): resource|false {}"},
                {'n': 'DNF-типы', 'd': 'Пересечения в скобках внутри объединения.', 'o': 'см. узел «типы»', 'v': '8.2', 'c': "function r((Stringable&Countable)|string $v) {}"},
                {'n': 'Конец динамическим свойствам', 'd': 'Запись в необъявленное свойство устарела: нужен атрибут #[\\AllowDynamicProperties].', 'o': 'опечатка больше не создаёт поле', 'v': '8.2', 'c': "#[\\AllowDynamicProperties]\nclass Legacy {}"},
                {'n': 'Типизированные константы класса', 'd': 'У константы появился объявленный тип.', 'o': 'см. узел «классы»', 'v': '8.3', 'c': "const string ENV = 'prod';"},
                {'n': '#[\\Override]', 'd': 'Компилятор проверяет, что метод действительно переопределяет родительский.', 'o': 'см. узел «атрибуты»', 'v': '8.3', 'c': "#[\\Override]\npublic function handle(): void {}"},
                {'n': 'json_validate()', 'd': 'Проверка JSON без построения структуры в памяти.', 'o': 'см. узел «JSON»', 'v': '8.3', 'c': "json_validate($body);"},
                {'n': 'Хуки свойств', 'd': 'Код на чтение и запись прямо у свойства; бывают виртуальные свойства.', 'o': 'см. узел «свойства»', 'v': '8.4', 'c': "public string $full { get => $this->a . ' ' . $this->b; }"},
                {'n': 'Асимметричная видимость', 'd': 'Читают все, пишет класс или наследник.', 'o': 'см. узел «свойства»', 'v': '8.4', 'c': "public private(set) int $version = 1;"},
                {'n': 'Ленивые объекты', 'd': 'Объект создаётся при первом обращении — из коробки, без прокси-классов.', 'o': 'см. узел «классы»', 'v': '8.4', 'c': "$obj = new ReflectionClass(Heavy::class)->newLazyGhost($init);"},
                {'n': 'array_find(), array_any(), array_all()', 'd': 'Поиск первого подходящего и проверки «есть хоть один» и «все».', 'o': 'см. узел «массивы»', 'v': '8.4', 'c': "array_any($orders, fn($o) => $o->isOverdue());"},
                {'n': 'new Foo()->method()', 'd': 'Обращение к новому объекту без скобок вокруг выражения.', 'o': 'см. узел «классы»', 'v': '8.4', 'c': "$id = new Uuid()->toString();"},
                {'n': 'Оператор конвейера |>', 'd': 'Значение слева уходит первым аргументом в вызываемое справа.', 'o': 'см. узел «операторы»', 'v': '8.5', 'c': "$slug = $title |> trim(...) |> mb_strtolower(...);"},
                {'n': 'clone с изменением', 'd': 'Копия объекта с новыми значениями свойств, в том числе readonly.', 'o': 'см. узел «свойства»', 'v': '8.5', 'c': "return clone($this, ['status' => $new]);"},
                {'n': '#[\\NoDiscard]', 'd': 'Предупреждение, если результат вызова не использован; (void) его гасит.', 'o': 'см. узел «атрибуты»', 'v': '8.5', 'c': "#[\\NoDiscard]\nfunction withHeader(string $h): static {}"},
                {'n': 'array_first() и array_last()', 'd': 'Первое и последнее значение без reset() и end().', 'o': 'см. узел «массивы»', 'v': '8.5', 'c': "$first = array_first($rows);"},
                {'n': 'Расширение URI', 'd': 'Разбор и нормализация адресов по RFC 3986 и стандарту WHATWG.', 'o': 'Uri\\Rfc3986\\Uri, Uri\\WhatWg\\Url', 'v': '8.5', 'c': "$uri = new Uri\\Rfc3986\\Uri('https://example.com/a?b=1');\n$uri->getHost();"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Как переезжать на новую версию'),
            ('steps', [
                'Поднимите `"php": "^8.4"` в `composer.json` и выполните `composer update` — часть пакетов обновится сама.',
                'Прогоните тесты на новой версии с `error_reporting(E_ALL)` и включённым логированием: устаревшее проявится сразу.',
                'Соберите deprecated-сообщения из логов — это и есть список работ.',
                'Пропустите Rector с набором для целевой версии (`withPhpSets`) и просмотрите изменения глазами.',
                'Поднимите уровень PHPStan: на новой версии он видит больше.',
                'Выкатывайте на часть трафика, если есть такая возможность: часть несовместимостей вылезает только на реальных данных.',
            ]),
            ('h', 'Проверка версии в коде'),
            ('code', 'php', None, r'''// сравнение строк версий работает, но PHP_VERSION_ID быстрее и надёжнее
if (PHP_VERSION_ID < 80300) {
    fwrite(STDERR, "нужен PHP 8.3 или новее, а тут " . PHP_VERSION . "\n");
    exit(1);
}

// возможность лучше проверять по её наличию, а не по номеру версии
if (function_exists('json_validate')) {
    $ok = json_validate($raw);
} else {
    json_decode($raw);
    $ok = json_last_error() === JSON_ERROR_NONE;
}'''),
            ('note', 'tip', 'Минимальную версию задаёт composer.json, а не сервер',
             'Строка `"php": "^8.3"` в `require` не даст установить проект туда, где стоит 8.1, '
             'и заставит Composer подбирать совместимые версии пакетов. '
             'А `config.platform` фиксирует версию, под которую собираются зависимости, '
             'даже если локально у вас новее.'),
            ('note', 'warn', 'Новый синтаксис нельзя закрыть полифилом',
             'Функцию можно дописать самому, а `|>`, хуки свойств и `readonly` — нет: '
             'файл с ними не разберётся на старой версии вовсе, даже если эта ветка кода никогда '
             'не выполняется. Поэтому в библиотеках, поддерживающих несколько версий, '
             'новый синтаксис появляется только со сменой мажорной версии пакета.'),
        ]),
    ],
)
