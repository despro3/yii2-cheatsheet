# -*- coding: utf-8 -*-
"""Путь кода: запуск и настройка, автозагрузка, ошибки и исключения."""

from model import topic

# --------------------------------------------------------------------------- Запуск

topic(
    id='runtime', group='exec',
    title='Запуск и настройка',
    cls='php.ini · OPcache',
    lead='Каждый запрос начинается с чистого листа: PHP поднимается, компилирует файлы в опкоды, '
         'выполняет их и всё забывает. Кэш опкодов и настройки решают, сколько это стоит.',
    badge='SAPI · ini · OPcache',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Главная особенность модели PHP — **shared nothing**: ни один запрос не видит память '
                  'предыдущего. Глобальные переменные, статические свойства, открытые соединения — '
                  'всё создаётся заново и уничтожается в конце. Отсюда простота отладки '
                  'и отсюда же цена: код компилируется на каждом запросе, если его не закэшировать.'),
            ('steps', [
                'PHP стартует в выбранном **SAPI** — `php-fpm` для веба, `cli` для консоли, встроенный сервер для разработки.',
                'Читается `php.ini`, подключаются расширения, применяются настройки пула.',
                'Входной файл разбирается и **компилируется в опкоды** — низкоуровневые инструкции Zend VM.',
                '**OPcache** кладёт опкоды в общую память: со второго запроса шаг компиляции пропускается.',
                'Опкоды выполняются; классы подтягиваются автозагрузчиком по мере первого обращения.',
                'Вывод уходит клиенту, память освобождается, всё состояние процесса сбрасывается.',
            ]),
            ('note', 'tip', 'JIT нужен не всем',
             'JIT компилирует горячие опкоды в машинный код и заметно ускоряет **вычисления**: '
             'обработку изображений, математику, разбор данных. Типичное веб-приложение упирается '
             'не в процессор, а в базу и сеть, поэтому там выигрыш от JIT обычно в пределах шума, '
             'а от OPcache — кратный.'),
            ('code', 'bash', None, r'''php -v                    # версия и включённые SAPI-расширения
php -m                    # список загруженных расширений
php --ini                 # какие ini-файлы реально прочитаны
php -i | grep opcache     # что с кэшем опкодов
php -l file.php           # проверить синтаксис, ничего не выполняя
php -r 'echo PHP_INT_MAX;' # выполнить строку
php -a                    # интерактивная оболочка
php -S localhost:8000 -t public   # встроенный сервер: только для разработки'''),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Настройки, которые приходится трогать чаще всего, и способы узнать, '
                  'что происходит с окружением.'),
            ('ref', [
                {'n': 'opcache.enable / validate_timestamps', 'd': 'Кэш опкодов. На проде проверку времени файлов отключают: PHP перестаёт опрашивать диск на каждом запросе, а деплой сбрасывает кэш перезапуском.', 'o': 'memory_consumption, max_accelerated_files', 'lang': 'ini', 'c': "opcache.enable=1\nopcache.validate_timestamps=0\nopcache.memory_consumption=256\nopcache.max_accelerated_files=20000"},
                {'n': 'opcache.jit / jit_buffer_size', 'd': 'JIT работает только вместе с OPcache. Режим `tracing` — разумный выбор; без буфера JIT выключен, сколько бы ни стоял режим.', 'o': 'tracing | function | off', 'v': '8.0', 'lang': 'ini', 'c': "opcache.jit=tracing\nopcache.jit_buffer_size=64M"},
                {'n': 'opcache.preload', 'd': 'Файл, который загружается один раз при старте и держит классы в памяти между запросами. Даёт заметный выигрыш фреймворкам и требует перезапуска при каждом изменении кода.', 'o': 'preload_user для FPM', 'lang': 'ini', 'c': "opcache.preload=/app/preload.php\nopcache.preload_user=www-data"},
                {'n': 'memory_limit', 'd': 'Потолок памяти на один процесс. `-1` снимает ограничение — так делают только в консольных задачах, и то осознанно.', 'o': 'в CLI по умолчанию -1', 'lang': 'ini', 'c': "memory_limit=256M\n\n// на месте:\nini_set('memory_limit', '1G');"},
                {'n': 'max_execution_time', 'd': 'Ограничение времени на запрос; в CLI не действует. Ожидание внешних вызовов в него не входит — там свои таймауты сокетов.', 'o': 'set_time_limit() сбрасывает счётчик', 'lang': 'ini', 'c': "max_execution_time=30"},
                {'n': 'error_reporting / display_errors', 'd': 'Что считать ошибкой и показывать ли её в ответе. На проде — всё в лог и ничего на экран: текст ошибки PHP выдаёт пути и версии.', 'o': 'log_errors, error_log', 'lang': 'ini', 'c': "error_reporting=E_ALL\ndisplay_errors=Off\nlog_errors=On\nerror_log=/var/log/php/error.log"},
                {'n': 'date.timezone', 'd': 'Часовой пояс по умолчанию для всех функций дат. Не задан — PHP возьмёт UTC и предупредит; в приложении пояс обычно фиксируют явно.', 'o': 'date_default_timezone_set()', 'lang': 'ini', 'c': "date.timezone=Europe/Moscow"},
                {'n': 'upload_max_filesize / post_max_size', 'd': 'Два разных лимита, и второй должен быть больше первого: в POST уезжает и файл, и остальные поля. Превышение `post_max_size` даёт пустые `$_POST` и `$_FILES`.', 'o': 'max_file_uploads', 'lang': 'ini', 'c': "upload_max_filesize=20M\npost_max_size=25M"},
                {'n': 'default_charset / mbstring.*', 'd': 'Кодировка по умолчанию для вывода и функций `mb_*`. Менять UTF-8 нет причин, а вот проверить, что она действительно стоит, стоит.', 'o': 'mbstring.internal_encoding устарела', 'lang': 'ini', 'c': "default_charset=\"UTF-8\""},
                {'n': 'zend.assertions', 'd': 'Компилировать ли `assert()`. На проде `-1` — проверки исчезают ещё на этапе компиляции и не стоят ничего.', 'o': '1 — включены, 0 — компилируются, но не выполняются', 'lang': 'ini', 'c': "; разработка\nzend.assertions=1\n; прод\nzend.assertions=-1"},
                {'n': 'realpath_cache_size', 'd': 'Кэш преобразования путей. На проекте с тысячами файлов и включённым OPcache увеличение кэша убирает лишние обращения к диску.', 'o': 'realpath_cache_ttl', 'lang': 'ini', 'c': "realpath_cache_size=4096K\nrealpath_cache_ttl=600"},
                {'n': 'ini_set() / ini_get()', 'd': 'Чтение и изменение настройки на лету. Часть директив (`opcache.*`, `memory_limit` в некоторых сборках) менять из кода нельзя — они применяются при старте.', 'o': 'ini_get_all() — всё разом', 'c': "ini_set('display_errors', '0');\n$limit = ini_get('memory_limit');"},
                {'n': 'getenv() / $_ENV / $_SERVER', 'd': 'Переменные окружения — основной способ передать настройки в контейнер. `getenv()` читает и те, что заданы после старта.', 'o': 'putenv() — только внутри процесса', 'c': "$dsn = getenv('DATABASE_URL') ?: throw new RuntimeException('нет DATABASE_URL');"},
                {'n': 'Константы окружения', 'd': 'Встроенные константы, по которым код узнаёт, где он выполняется.', 'o': 'PHP_VERSION_ID для сравнений', 'c': "PHP_VERSION;        // '8.4.3'\nPHP_VERSION_ID;     // 80403\nPHP_OS_FAMILY;      // 'Linux'\nPHP_SAPI;           // 'cli' | 'fpm-fcgi'\nPHP_EOL; PHP_INT_MAX; PHP_FLOAT_EPSILON;"},
                {'n': 'SAPI: fpm, cli, встроенный сервер', 'd': 'FPM держит пул процессов и обслуживает веб; CLI выполняет скрипт и выходит; `php -S` — однопроцессный сервер строго для разработки.', 'o': 'php_sapi_name(), PHP_SAPI', 'c': "if (PHP_SAPI === 'cli') {\n    // консольная ветка: нет заголовков и таймаута\n}"},
                {'n': 'register_shutdown_function()', 'd': 'Код, который выполнится даже после фатальной ошибки. Последний шанс записать в лог, что именно убило процесс.', 'o': 'error_get_last() внутри', 'c': "register_shutdown_function(static function (): void {\n    $e = error_get_last();\n    if ($e !== null && $e['type'] === E_ERROR) {\n        error_log('фатальная: ' . $e['message']);\n    }\n});"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Разные настройки для разработки и прода'),
            ('code', 'ini', 'php.ini — прод', r'''display_errors = Off
log_errors = On
error_reporting = E_ALL
zend.assertions = -1

opcache.enable = 1
opcache.validate_timestamps = 0     ; сброс кэша — перезапуском FPM при деплое
opcache.memory_consumption = 256
opcache.max_accelerated_files = 20000
opcache.interned_strings_buffer = 16'''),
            ('code', 'ini', 'php.ini — разработка', r'''display_errors = On
error_reporting = E_ALL
zend.assertions = 1

opcache.enable = 1
opcache.validate_timestamps = 1
opcache.revalidate_freq = 0         ; изменения видны сразу'''),
            ('note', 'trap', 'Забытый opcache.validate_timestamps=0 после деплоя',
             'С отключённой проверкой времени PHP **не заметит**, что файлы изменились: '
             'сайт продолжит работать на старом коде, пока не перезапустят FPM или не позовут '
             '`opcache_reset()`. Если деплой раскладывает файлы в тот же каталог — это классические '
             '«полчаса странного поведения» после выката.'),
            ('h', 'Проверить, что окружение действительно такое, как думаете'),
            ('code', 'php', 'bin/env-check.php', r'''declare(strict_types=1);

$checks = [
    'версия' => version_compare(PHP_VERSION, '8.3', '>='),
    'opcache' => function_exists('opcache_get_status')
        && (opcache_get_status(false)['opcache_enabled'] ?? false),
    'кодировка' => ini_get('default_charset') === 'UTF-8',
    'ошибки не на экран' => ini_get('display_errors') === '' || !filter_var(
        ini_get('display_errors'), FILTER_VALIDATE_BOOL
    ),
    'расширения' => !array_diff(['mbstring', 'pdo_mysql', 'intl'], get_loaded_extensions()),
];

foreach ($checks as $name => $ok) {
    printf("%-22s %s\n", $name, $ok ? 'ок' : 'ПРОВЕРЬТЕ');
}'''),
        ]),
    ],
)


# --------------------------------------------------------------------------- Автозагрузка

topic(
    id='autoload', group='exec',
    title='Пространства имён и автозагрузка',
    cls='namespace · use',
    lead='Имя класса — это путь к файлу, по которому его найдут в момент первого обращения. '
         'Вся схема держится на одном соглашении и одной функции.',
    badge='PSR-4',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Пространство имён — это **префикс к именам**, не более: он не создаёт области видимости '
                  'для переменных и не влияет на выполнение. Зато по полному имени класса автозагрузчик '
                  'вычисляет путь к файлу — и подключает его ровно тогда, когда класс впервые понадобился.'),
            ('svg', '''<svg viewBox="0 0 760 178" role="img" aria-label="Обращение к классу: PHP не находит его, зовёт автозагрузчик, тот подключает файл по PSR-4" class="dg">
<defs><marker id="p-a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5 0 10z" fill="currentColor"/></marker></defs>
<g stroke="currentColor" stroke-width="1.5" fill="none" marker-end="url(#p-a1)" opacity=".55">
<path d="M186 48h40"/><path d="M406 48h40"/><path d="M596 72v58H448"/>
</g>
<g class="dg-box"><rect x="16" y="24" width="170" height="48" rx="8"/><text x="101" y="44">new App\\Mail\\Sender</text><text x="101" y="61" class="dg-sub">класс ещё не загружен</text></g>
<g class="dg-box"><rect x="226" y="24" width="180" height="48" rx="8"/><text x="316" y="44">автозагрузчик</text><text x="316" y="61" class="dg-sub">spl_autoload_register</text></g>
<g class="dg-box"><rect x="446" y="24" width="300" height="48" rx="8"/><text x="596" y="44">src/Mail/Sender.php</text><text x="596" y="61" class="dg-sub">префикс App\\ → каталог src/</text></g>
<g class="dg-box dg-ok"><rect x="240" y="106" width="200" height="48" rx="8"/><text x="340" y="126">класс объявлен</text><text x="340" y="143" class="dg-sub">дальше — как обычно</text></g>
</svg>''', 'Не нашёлся файл или имя класса внутри не совпало с ожидаемым — будет «Class not found».'),
            ('code', 'php', 'src/Mail/Sender.php', r'''<?php

declare(strict_types=1);

namespace App\Mail;                    // одна на файл — и первой инструкцией после declare

use App\Config\Settings;               // импорт класса
use App\Mail\Transport\{Smtp, Sendmail};   // групповой импорт
use App\Support\Str as StrHelper;      // псевдоним
use function App\Support\slugify;      // импорт функции
use const App\Support\VERSION;         // импорт константы

final class Sender
{
    public function send(): void
    {
        $t = new Smtp();               // короткое имя — из-за use
        $x = new \DateTimeImmutable(); // обратный слеш: глобальное пространство
        strlen('...');                 // встроенные функции ищутся и в глобальном тоже
    }
}'''),
            ('note', 'trap', 'Внутри пространства имён \\ обязателен для классов',
             'В файле с `namespace App;` запись `new DateTime()` означает `App\\DateTime` — '
             'и падает с «Class not found». Для **функций** правило мягче: если функции нет '
               'в текущем пространстве, PHP посмотрит в глобальном. Для классов такого запасного пути нет.'),
        ]),
        ('all', 'Что есть в языке', [
            ('ref', [
                {'n': 'namespace', 'd': 'Объявляется первой инструкцией файла (после `declare`). Фигурная форма с несколькими пространствами в одном файле существует, но в нормальном коде не встречается.', 'o': 'один файл — одно пространство', 'c': "<?php\n\ndeclare(strict_types=1);\n\nnamespace App\\Domain\\Order;"},
                {'n': 'use', 'd': 'Импорт имени в текущий файл. Работает только на уровне файла: строка `\'App\\Mail\\Sender\'` в переменной никакими `use` не сокращается.', 'o': 'use A\\B as C', 'c': "use App\\Mail\\Sender;\nuse App\\Mail\\Sender as MailSender;"},
                {'n': 'use function / use const', 'd': 'Отдельные импорты для функций и констант — у них свои пространства имён, и обычный `use` их не затрагивает.', 'o': 'групповая форма тоже работает', 'c': "use function App\\Support\\{slugify, excerpt};\nuse const App\\Support\\DEFAULT_LOCALE;"},
                {'n': 'Групповой use', 'd': 'Несколько импортов из общего префикса одной строкой. Читается хорошо, пока префикс действительно общий.', 'o': 'вложенность не поддерживается', 'c': "use App\\Http\\{Request, Response, Router};"},
                {'n': '::class', 'd': 'Полное имя класса строкой, разрешённое с учётом `use`. Опечатка становится видна IDE и анализатору — в отличие от строкового литерала.', 'o': 'на объекте — с 8.0', 'v': '8.0', 'c': "$container->get(Mailer::class);\n$e::class;"},
                {'n': 'spl_autoload_register()', 'd': 'Регистрирует функцию, которую PHP зовёт при первом обращении к неизвестному классу. Их может быть несколько: PHP пробует по очереди, пока класс не появится.', 'o': 'бросать исключение из загрузчика не нужно', 'c': "spl_autoload_register(static function (string $class): void {\n    $prefix = 'App\\\\';\n    if (!str_starts_with($class, $prefix)) {\n        return;\n    }\n    $rel = substr($class, strlen($prefix));\n    $file = __DIR__ . '/src/' . str_replace('\\\\', '/', $rel) . '.php';\n    if (is_file($file)) {\n        require $file;\n    }\n});"},
                {'n': 'PSR-4', 'd': 'Соглашение «префикс пространства имён → базовый каталог»: остаток имени становится путём, класс — файлом с тем же именем. Именно его реализует автозагрузчик Composer.', 'o': 'регистр важен', 'lang': 'json', 'c': "{\n  \"autoload\": {\n    \"psr-4\": { \"App\\\\\": \"src/\" }\n  }\n}"},
                {'n': 'classmap и files', 'd': 'Два других способа Composer: `classmap` сканирует каталоги и строит таблицу «класс → файл», `files` просто подключает файлы на старте — так подключают файлы с функциями.', 'o': 'функции автозагрузкой не ищутся', 'lang': 'json', 'c': "\"autoload\": {\n  \"classmap\": [\"database/migrations\"],\n  \"files\": [\"src/Support/helpers.php\"]\n}"},
                {'n': 'class_exists() / interface_exists()', 'd': 'Проверка наличия класса. Второй аргумент управляет запуском автозагрузки — `false` спрашивает только про уже загруженные.', 'o': 'enum_exists() — с 8.1', 'c': "if (class_exists($handler)) {\n    $instance = new $handler();\n}"},
                {'n': 'get_declared_classes()', 'd': 'Все классы, которые уже загружены в этом процессе. Полезно в диагностике и в сборщиках preload-файлов.', 'o': 'растёт по мере автозагрузки', 'c': "count(get_declared_classes());"},
                {'n': '__NAMESPACE__ и namespace\\', 'd': 'Текущее пространство строкой и явная ссылка на него. Нужны редко — в динамическом разрешении имён.', 'o': 'namespace\\Foo::bar()', 'c': "$class = __NAMESPACE__ . '\\\\' . $name;"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Что делать с «Class not found»'),
            ('steps', [
                'Проверьте **регистр**: на macOS файл `sender.php` найдётся, на боевом Linux — нет.',
                'Сверьте имя пространства внутри файла с путём: `App\\Mail\\Sender` → `src/Mail/Sender.php` при префиксе `App\\` → `src/`.',
                'Убедитесь, что каталог вообще указан в `autoload` composer.json, а не только в `autoload-dev`.',
                'После добавления новой секции автозагрузки выполните `composer dump-autoload`.',
                'Если класс из пакета — проверьте, что пакет в `require`, а не только в `require-dev`.',
            ]),
            ('h', 'Оптимизация автозагрузки на проде'),
            ('code', 'bash', None, r'''composer install --no-dev --optimize-autoloader   # таблица «класс → файл» вместо поиска
composer dump-autoload --classmap-authoritative   # неизвестный класс даже не ищем на диске'''),
            ('note', 'tip', 'Имя класса — это адрес файла',
             'Единственная причина, по которой автозагрузка вообще работает, — соглашение. '
             'Как только в файле оказываются два класса, или имя файла не совпадает с именем класса, '
               'или пространство имён не соответствует каталогу, автозагрузчик перестаёт находить код. '
               'Отсюда правило «один класс — один файл», не связанное ни с какой эстетикой.'),
        ]),
    ],
)


# --------------------------------------------------------------------------- Ошибки

topic(
    id='errors', group='exec',
    title='Ошибки и исключения',
    cls='Throwable',
    lead='В PHP 8 почти всё, что раньше было предупреждением, стало исключением. '
         'Ловить их принято точечно, а не одним catch на весь файл.',
    badge='20 классов',
    tabs=[
        ('how', 'Как устроено', [
            ('p', 'Всё, что можно бросить, реализует `Throwable`. Дальше развилка: '
                  '`Error` — это **ошибки самого языка** (не тот тип, деление на ноль, нет метода), '
                  '`Exception` — ошибки приложения. Ловить `Error` обычно не нужно: '
                  'он означает, что код написан неверно.'),
            ('svg', '''<svg viewBox="0 0 760 250" role="img" aria-label="Иерархия Throwable: слева Error с TypeError, ValueError и ArithmeticError, справа Exception с RuntimeException, LogicException и ErrorException" class="dg">
<g stroke="currentColor" stroke-width="1.4" fill="none" opacity=".45">
<path d="M380 44v14H104v14"/><path d="M380 58H476v14"/>
<path d="M104 106v92"/><path d="M104 130h24"/><path d="M104 164h24"/><path d="M104 198h24"/>
<path d="M476 106v92"/><path d="M476 130h24"/><path d="M476 164h24"/><path d="M476 198h24"/>
</g>
<g class="dg-box"><rect x="300" y="12" width="160" height="32" rx="7"/><text x="380" y="33">Throwable</text></g>
<g class="dg-box dg-bad"><rect x="24" y="72" width="160" height="34" rx="7"/><text x="104" y="94">Error</text></g>
<g class="dg-box"><rect x="396" y="72" width="160" height="34" rx="7"/><text x="476" y="94">Exception</text></g>
<g class="dg-sub" text-anchor="start">
<text x="136" y="134">TypeError · ArgumentCountError</text>
<text x="136" y="168">ValueError · UnhandledMatchError</text>
<text x="136" y="202">ArithmeticError · DivisionByZeroError</text>
<text x="508" y="134">RuntimeException</text>
<text x="508" y="168">LogicException</text>
<text x="508" y="202">ErrorException · JsonException</text>
</g>
<text x="24" y="236" class="dg-note" text-anchor="start">ошибка в коде — чинить, а не ловить</text>
<text x="396" y="236" class="dg-note" text-anchor="start">ошибка в ситуации — обрабатывать</text>
</svg>''', 'Свой класс исключения наследуют от `Exception` или его потомков: реализовать `Throwable` напрямую язык не разрешает.'),
            ('code', 'php', None, r'''try {
    $order = $repo->find($id) ?? throw new NotFound("заказ $id");  // throw — выражение с 8.0
    $order->pay($amount);
} catch (NotFound | AccessDenied $e) {      // несколько типов одним блоком
    return $this->error(404, $e->getMessage());
} catch (PaymentFailed) {                   // без переменной, если она не нужна (8.0)
    return $this->error(402, 'платёж отклонён');
} catch (Throwable $e) {
    $this->log->error($e->getMessage(), ['exception' => $e]);
    throw $e;                               // не проглатываем: пробрасываем выше
} finally {
    $this->lock->release();                 // выполнится в любом случае
}'''),
            ('h', 'Предупреждения PHP — это не исключения'),
            ('p', 'Обращение к несуществующему ключу, `include` пропавшего файла, деление на ноль '
                  'через `%` — часть из этого по-прежнему диагностика движка, а не `Throwable`. '
                  'Чтобы такие места тоже попадали в `catch`, их превращают в исключения обработчиком.'),
            ('code', 'php', 'src/bootstrap.php', r'''set_error_handler(static function (int $no, string $msg, string $file, int $line): bool {
    if (!(error_reporting() & $no)) {
        return false;          // уровень подавлен настройкой — пусть PHP разбирается сам
    }
    throw new ErrorException($msg, 0, $no, $file, $line);
});

set_exception_handler(static function (Throwable $e): void {
    error_log((string) $e);
    http_response_code(500);
    echo 'Что-то пошло не так';
});'''),
            ('note', 'trap', 'catch (Throwable) на каждом шаге прячет ошибки',
             'Перехват всего подряд превращает `TypeError` и опечатку в имени метода в «ошибку сервиса»: '
             'приложение продолжает работать со сломанными данными. Ловите то, что умеете обработать, '
             'а общий `catch` оставьте одному месту — на границе, где формируется ответ.'),
        ]),
        ('all', 'Что есть в языке', [
            ('p', 'Слева — классы и конструкции. Из встроенных классов исключений в приложении обычно '
                  'бросают четыре-пять; остальные полезно узнавать в чужих трассировках.'),
            ('ref', [
                {'n': 'Throwable', 'd': 'Общий интерфейс. Годится для объявления типов; свой класс должен наследовать `Exception` или `Error`, а не реализовывать интерфейс напрямую.', 'o': 'getMessage, getCode, getFile, getLine, getPrevious, getTrace', 'c': "function report(Throwable $e): void\n{\n    error_log($e::class . ': ' . $e->getMessage());\n}"},
                {'n': 'Error', 'd': 'Ошибки движка: вызов метода у `null`, обращение к неинициализированному свойству, доступ к приватному. Почти всегда означает, что код нужно исправить.', 'o': 'не наследник Exception', 'c': "try {\n    $null->method();\n} catch (Error $e) {\n    // Call to a member function method() on null\n}"},
                {'n': 'TypeError / ArgumentCountError', 'd': 'Значение не того типа и нехватка аргументов. В строгом режиме — основной способ узнать об ошибке сразу, а не тремя слоями ниже.', 'o': 'ArgumentCountError наследует TypeError', 'v': '8.0', 'c': "function f(int $n) {}\nf('abc');   // TypeError\nf();        // ArgumentCountError"},
                {'n': 'ValueError', 'd': 'Тип верный, а значение недопустимое: отрицательная длина, пустой разделитель, неизвестный флаг. До 8.0 такие функции возвращали `false`.', 'o': 'массово появился в 8.0', 'v': '8.0', 'c': "array_chunk($rows, 0);        // ValueError\nStatus::from('нет такого');    // ValueError"},
                {'n': 'ArithmeticError / DivisionByZeroError', 'd': 'Переполнение при сдвиге и деление на ноль. С 8.0 на ноль делят с исключением и операторы `%`, `intdiv()`, и сам `/`.', 'o': 'DivisionByZeroError наследует ArithmeticError', 'v': '8.0', 'c': "try {\n    $x = 1 % 0;\n} catch (DivisionByZeroError $e) {\n    $x = null;\n}"},
                {'n': 'UnhandledMatchError', 'd': 'В `match` не нашлось ветки и нет `default`. Хороший сигнал: где-то появился новый вариант перечисления, а карта решений не обновлена.', 'o': 'наследник Error', 'v': '8.0', 'c': "match ($status) {\n    'new' => 1,\n};   // UnhandledMatchError на любом другом значении"},
                {'n': 'RuntimeException', 'd': 'Ошибка, которую нельзя было предвидеть при чтении кода: не ответил сервис, кончилось место, не прочитался файл. База для большинства своих исключений.', 'o': 'потомки: OutOfBounds, Range, Overflow, Underflow, UnexpectedValue', 'c': "throw new RuntimeException('платёжный шлюз не ответил');"},
                {'n': 'LogicException', 'd': 'Ошибка в самой программе: неверный аргумент, вызов метода в неподходящем состоянии. По идее, должна отлавливаться тестами, а не обрабатываться в проде.', 'o': 'потомки: InvalidArgument, Domain, Length, OutOfRange, BadFunctionCall', 'c': "throw new InvalidArgumentException('ожидался положительный лимит');"},
                {'n': 'ErrorException', 'd': 'Обёртка над диагностикой движка. Её бросает `set_error_handler()`, когда предупреждения превращают в исключения.', 'o': 'хранит severity', 'c': "throw new ErrorException($msg, 0, $severity, $file, $line);"},
                {'n': 'JsonException', 'd': 'Ошибка разбора или кодирования JSON — если запрошен флаг. Без него `json_decode()` молча вернёт `null`.', 'o': 'JSON_THROW_ON_ERROR', 'c': "json_decode($raw, true, 512, JSON_THROW_ON_ERROR);"},
                {'n': 'throw как выражение', 'd': 'С 8.0 `throw` можно писать там, где ожидается значение: в `??`, в тернарнике, в стрелочной функции.', 'o': 'удобно вместе с ??', 'v': '8.0', 'c': "$user = $repo->find($id) ?? throw new NotFound();\n$fn = fn() => throw new LogicException();"},
                {'n': 'catch без переменной', 'd': 'Если объект исключения не нужен, переменную можно не писать. Мелочь, но убирает неиспользуемые `$e`, на которые ругается анализатор.', 'o': 'catch (Type)', 'v': '8.0', 'c': "try {\n    $cache->clear();\n} catch (CacheMiss) {\n    // и так всё понятно\n}"},
                {'n': 'Цепочка исключений', 'd': 'Третий аргумент конструктора — предыдущее исключение. Позволяет заменить техническую ошибку доменной, не потеряв исходную трассировку.', 'o': 'getPrevious()', 'c': "try {\n    $pdo->exec($sql);\n} catch (PDOException $e) {\n    throw new StorageUnavailable('база недоступна', previous: $e);\n}"},
                {'n': 'finally', 'd': 'Выполняется всегда: после `return`, после `throw`, после `break`. Место для освобождения ресурсов. `return` внутри `finally` перекрывает исключение — так делать не стоит.', 'o': 'работает и без catch', 'c': "try {\n    return $this->run();\n} finally {\n    $this->lock->release();\n}"},
                {'n': 'set_error_handler() / get_error_handler()', 'd': 'Свой обработчик диагностики движка. С 8.5 текущий обработчик можно получить обратно — раньше его приходилось запоминать самому.', 'o': 'restore_error_handler()', 'v': '8.5', 'c': "$previous = get_error_handler();"},
                {'n': 'set_exception_handler()', 'd': 'Последний рубеж: сюда попадают исключения, которые никто не поймал. После него скрипт завершается.', 'o': 'get_exception_handler() — с 8.5', 'v': '8.5', 'c': "set_exception_handler(static function (Throwable $e): void {\n    http_response_code(500);\n});"},
                {'n': '#[\\SensitiveParameter]', 'd': 'Скрывает значение аргумента в трассировке. Без него пароль или токен уедет в лог при первом же исключении внутри метода.', 'o': 'ставится на параметр', 'v': '8.2', 'c': "function login(string $user, #[\\SensitiveParameter] string $password): void {}"},
                {'n': 'Трассировка у фатальных ошибок', 'd': 'Превышение времени выполнения и лимита памяти теперь тоже пишут трассировку — раньше в логе была одна строка без единой подсказки, где это случилось.', 'o': 'fatal_error_backtraces=1 по умолчанию', 'v': '8.5', 'c': "; php.ini\nfatal_error_backtraces=1", 'lang': 'ini'},
                {'n': 'error_reporting / @', 'd': 'Какие уровни диагностики учитывать. Оператор `@` с PHP 8 больше не гасит фатальные ошибки — раньше это делало отладку особенно интересной.', 'o': 'E_ALL всегда, фильтрация — при выводе', 'v': '8.0', 'c': "error_reporting(E_ALL);\nini_set('display_errors', '0');"},
            ]),
        ]),
        ('own', 'Свои приёмы', [
            ('h', 'Своя иерархия исключений'),
            ('code', 'php', 'src/Exception/', r'''// одно базовое на приложение — по нему ловят «всё наше»
interface AppException extends Throwable {}

// на домен — от LogicException или RuntimeException, по смыслу
class OrderException extends RuntimeException implements AppException {}

final class OrderNotFound extends OrderException
{
    public static function byId(int $id): self
    {
        return new self("заказ $id не найден");
    }
}

final class OrderAlreadyPaid extends OrderException {}

// на границе HTTP ловим свои и переводим в коды ответа
try {
    $this->handler->run($request);
} catch (OrderNotFound $e) {
    return new Response(404, $e->getMessage());
} catch (AppException $e) {
    return new Response(409, $e->getMessage());
}'''),
            ('note', 'tip', 'Исключение с именованным конструктором читается как предложение',
             '`throw OrderNotFound::byId($id)` говорит и что случилось, и с чем. '
             'Заодно формулировка сообщения лежит в одном месте — и её можно поменять, '
             'не бегая по всему проекту.'),
            ('h', 'Ресурсы освобождает finally, а не последняя строка'),
            ('code', 'php', None, r'''$fh = fopen($path, 'r');
try {
    foreach (readRows($fh) as $row) {
        if ($row['broken']) {
            return null;         // ранний выход — файл всё равно закроется
        }
    }
} finally {
    fclose($fh);
}'''),
            ('note', 'warn', 'Сообщение исключения видит не только разработчик',
             'Текст `getMessage()` часто оказывается в ответе API или на экране пользователя. '
             'Пути к файлам, SQL-запросы и содержимое переменных туда попадать не должны: '
             'детали — в лог через контекст, пользователю — что случилось и что делать.'),
        ]),
    ],
)
