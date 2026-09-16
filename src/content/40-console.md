---
id: console
title: Консольные приложения
part: tools
summary: Входной скрипт yii и config/console.php, консольные контроллеры и действия с аргументами, опции через options()/optionAliases(), диалог с пользователем (prompt/confirm/select), цветной вывод, коды выхода ExitCode, встроенные команды help/migrate/cache/asset/serve/fixture/message.
sources: tutorial-console
---

:::lead
Консольное приложение — тот же Yii с той же конфигурацией моделей и компонентов, только вместо HTTP-запроса — аргументы командной строки. Cron-задачи, миграции, импорт, очереди — всё это контроллеры в `commands/`, запускаемые через `./yii`.
:::

## Запуск

```bash
./yii <route> [--option1=value1 ...] [arg1 arg2 ...]
./yii help                       # список команд
./yii help migrate               # справка по команде и её действиям
./yii migrate/create create_post --interactive=0
./yii hello world                # HelloController::actionIndex('world')
```

Маршрут `controller/action`; без действия — `defaultAction` (по умолчанию `index`). Входной скрипт `yii` (в корне) создаёт `yii\console\Application` с `config/console.php`:

```php title="config/console.php"
return [
    'id' => 'basic-console',
    'basePath' => dirname(__DIR__),
    'bootstrap' => ['log'],
    'controllerNamespace' => 'app\commands',       // где искать контроллеры
    'components' => [
        'cache' => ['class' => 'yii\caching\FileCache'],
        'log' => [...],
        'db' => require __DIR__ . '/db.php',
    ],
    'controllerMap' => [
        'fixture' => ['class' => 'yii\console\controllers\FixtureController', 'namespace' => 'tests\unit\fixtures'],
    ],
    'params' => require __DIR__ . '/params.php',
];
```

Общее с web-конфигурацией выносите в отдельный файл и подключайте в обоих. `YII_DEBUG`/`YII_ENV` задаются во входном скрипте; в консоли `YII_DEBUG` по умолчанию `true`, чтобы видеть стек ошибок.

## Контроллер

```php title="commands/HelloController.php"
namespace app\commands;

use yii\console\Controller;
use yii\console\ExitCode;
use yii\helpers\Console;

/**
 * Демонстрационная команда (эта строка попадёт в ./yii help).
 */
class HelloController extends Controller
{
    /** @var bool сохранять ли результат — опция --save */
    public $save = false;
    /** @var string опция --format */
    public $format = 'json';

    public function options($actionID)
    {
        return ['save', 'format'];             // какие свойства доступны как опции (для всех действий)
    }

    public function optionAliases()
    {
        return ['s' => 'save', 'f' => 'format'];   // ./yii hello -s -f=xml
    }

    /**
     * Здоровается (описание действия для help).
     * @param string $name кому
     * @param int $times сколько раз
     */
    public function actionIndex($name = 'world', $times = 1)
    {
        for ($i = 0; $i < $times; $i++) {
            $this->stdout("Hello, $name!\n", Console::FG_GREEN);
        }
        return ExitCode::OK;
    }

    public function actionImport(array $ids)      // ./yii hello/import 1,2,3 → [1, 2, 3]
    {
        // ...
        return ExitCode::OK;
    }
}
```

:::kv
Аргументы — параметры метода по порядку; необязательные — со значениями по умолчанию; `array $x` — из строки через запятую
Опции — публичные свойства, перечисленные в `options()`; `--name=value`, `--flag` (bool), `-a` через `optionAliases()`; для массивов — `--ids=1 --ids=2`
Общие опции — `--interactive=0`, `--color`, `--help` есть у всех команд
Код выхода — `return ExitCode::OK` (0), `ExitCode::UNSPECIFIED_ERROR` (1), `DATAERR`, `USAGE`… — так cron и CI поймут результат
Справка — из PHPDoc класса, действия и `@param`; `./yii help hello`
:::

## Диалог и вывод

```php
$name = $this->prompt('Ваше имя:', ['required' => true, 'default' => 'anon']);
if ($this->confirm('Продолжить?')) { … }                        // yes/no; при --interactive=0 — всегда да
$choice = $this->select('Формат:', ['json' => 'JSON', 'xml' => 'XML']);

$this->stdout("Готово\n", Console::FG_GREEN, Console::BOLD);
$this->stderr("Ошибка\n", Console::FG_RED);
echo $this->ansiFormat('внимание', Console::FG_YELLOW);
Console::startProgress(0, $total);  Console::updateProgress($done, $total);  Console::endProgress();
// цвета включаются, если терминал их поддерживает (--color)
$this->isColorEnabled();
```

Не используйте `exit()` — верните код; не используйте `echo` для ошибок — `stderr`.

## Встроенные команды

| Команда | Назначение |
|---|---|
| `help` | справка по всем командам |
| `migrate` | [миграции](migrations): `create`, `up`, `down`, `redo`, `fresh`, `history`, `new`, `mark` |
| `cache` | `flush`, `flush-all`, `flush-schema` |
| `asset` | сборка и сжатие ассетов (`asset/template`, `asset config.php bundles.php`) |
| `fixture` | загрузка тестовых данных (`fixture/load`, `fixture/unload`) |
| `message` | извлечение строк для [перевода](i18n) (`message/config`, `message`) |
| `serve` | встроенный сервер разработки: `./yii serve --port=8080` |
| `hello` | пример из шаблона |

Команды расширений (например, `queue`) добавляются в `controllerMap` или через bootstrap.

## Особенности консольного окружения

- Нет `request` в web-смысле: `Yii::$app->request` — `yii\console\Request` с `params`; нет `session`, `user` (компоненты web).
- `Url::to()` без `hostInfo` не построит абсолютный URL — задайте `'urlManager' => ['hostInfo' => 'https://example.com', 'baseUrl' => '/']` в консольной конфигурации (нужно для писем из cron).
- Псевдоним `@web`/`@webroot` не определены — задайте вручную, если нужны.
- Ошибки идут в `stderr` и в `log`; `errorHandler` — `yii\console\ErrorHandler`.
- Длинные задачи: следите за памятью (`batch()` в запросах, `gc_collect_cycles()`), логи с `flushInterval`.

## Cron

```bash
*/5 * * * * cd /var/www/app && ./yii cleanup/temp --interactive=0 >> runtime/logs/cron.log 2>&1
```

Запускайте от пользователя приложения, чтобы файлы в `runtime/` создавались с правильными правами.

:::quiz Проверь себя
Q: Как передать команде опцию `--dry-run`?
A: Объявить публичное свойство `$dryRun`, вернуть `'dryRun'` из `options()`; вызывать `./yii cmd --dryRun=1` (или `--dry-run` — оба варианта работают с 2.0.x).
Q: Как получить массив из аргумента командной строки?
A: Объявить параметр действия `array $ids` и передать `1,2,3`.
Q: Что вернуть из действия, чтобы cron заметил ошибку?
A: Ненулевой код: `ExitCode::UNSPECIFIED_ERROR` или другой из `yii\console\ExitCode`.
Q: Почему в консольной команде `Url::to([...], true)` даёт неверный URL?
A: В консоли нет HTTP-запроса; задайте `hostInfo` и `baseUrl` у `urlManager` в консольной конфигурации.
Q: Как отключить подтверждения для запуска из CI?
A: Опция `--interactive=0`.
:::
