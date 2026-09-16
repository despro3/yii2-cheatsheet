---
id: console
title: Консоль, i18n, почта
icon: 🛠️
summary: Консольные команды, переводы и множественные формы, отправка писем.
sources: tutorial-console, tutorial-i18n, tutorial-mailing
---

# Консоль, интернационализация, почта

## Консольные приложения

```bash
yii <маршрут> [--опция1=значение1 ... аргумент1 аргумент2]
yii                       # список всех команд
yii help migrate          # справка по команде
yii <маршрут> --appconfig=path/to/config.php    # другой конфиг
```

Встроенные команды:

| Команда | Назначение |
|---|---|
| `yii serve` | встроенный веб-сервер PHP (`--docroot=./web --port=8080`) |
| `yii migrate/*` | миграции БД |
| `yii cache/*` | очистка кешей |
| `yii asset/*` | объединение и минификация ресурсов |
| `yii message/*` | извлечение строк для перевода |
| `yii fixture/*` | загрузка и выгрузка фикстур |
| `yii help` | справка |
| `yii gii/*` | генераторы Gii (с расширением) |

### Своя команда

```php
namespace app\commands;

use yii\console\Controller;
use yii\console\ExitCode;
use yii\helpers\Console;

/**
 * Управление рассылкой писем.
 */
class MailController extends Controller
{
    public $message;
    public $limit = 100;

    public function options($actionID)          // какие свойства доступны как --опции
    {
        return ['message', 'limit'];
    }

    public function optionAliases()             // короткие псевдонимы: -m
    {
        return ['m' => 'message'];
    }

    /**
     * Отправляет письма пачкой.
     * @param string $category категория рассылки
     */
    public function actionSend($category, $order = 'name')
    {
        $this->stdout("Отправка...\n", Console::BOLD);
        $name = $this->ansiFormat($category, Console::FG_YELLOW);

        if (!$this->confirm("Отправить рассылку $name?")) {
            return ExitCode::OK;
        }
        if ($somethingWrong) {
            $this->stderr("Ошибка\n", Console::FG_RED);
            return ExitCode::UNSPECIFIED_ERROR;   // 1
        }
        return ExitCode::OK;                      // 0
    }

    public function actionBatch(array $ids) { /* yii mail/batch 1,2,3 */ }
}
```

```bash
yii mail/send news -m=Привет --limit=50
```

- Класс команды — наследник `yii\console\Controller`, действия — `actionXxx`.
- Аргументы действия заполняются позиционно, опции — через `--name=value`.
- Тип `array` в параметре → значение разбивается по запятым.
- Код возврата: `0` — успех, иначе ошибка (`ExitCode::OK`, `ExitCode::UNSPECIFIED_ERROR`, …).
- Команды из модулей: задайте `controllerNamespace` для консоли в `init()` модуля,
  вызов — `yii <module>/<command>/<action>`.
- Есть автодополнение для Bash и ZSH (скрипты в `contrib/completion` репозитория Yii).

Полезные методы контроллера: `stdout()`, `stderr()`, `ansiFormat()`, `prompt()`,
`confirm()`, `select()`, `table()` (в консольном хелпере).

## Интернационализация

```php
'language' => 'ru-RU',           // язык вывода
'sourceLanguage' => 'en-US',     // язык строк в коде
```

```php
Yii::$app->language = 'ru-RU';   // можно менять в рантайме (до вывода)
echo Yii::t('app', 'Hello, {username}!', ['username' => $name]);
```

```php
'components' => [
    'i18n' => [
        'translations' => [
            'app*' => [
                'class' => 'yii\i18n\PhpMessageSource',   // либо GettextMessageSource / DbMessageSource
                'basePath' => '@app/messages',
                'sourceLanguage' => 'en-US',
                'fileMap' => ['app' => 'app.php', 'app/error' => 'error.php'],
                'on missingTranslation' => ['app\components\TranslationEventHandler', 'handleMissingTranslation'],
            ],
            'yii' => [                                    // переопределение сообщений фреймворка
                'class' => 'yii\i18n\PhpMessageSource',
                'basePath' => '@app/messages',
            ],
            '*' => ['class' => 'yii\i18n\PhpMessageSource'],   // fallback для всех категорий
        ],
    ],
],
```

Файлы переводов: `@app/messages/ru-RU/app.php` (fallback — `@app/messages/ru/app.php`),
массив `'исходная строка' => 'перевод'`.

### Форматирование в сообщениях (нужен `intl`)

```php
Yii::t('app', 'Баланс: {0, number, currency}', $sum);
Yii::t('app', 'Сегодня {0, date, long}', time());
Yii::t('app', 'Время {0, time, short}', time());
Yii::t('app', '{n, spellout}', ['n' => 42]);          // сорок два
Yii::t('app', 'Вы {n, ordinal} посетитель', ['n' => 42]);
Yii::t('app', 'Прошло {n, duration}', ['n' => 47]);
```

**Множественные формы** — то, за что стоит любить `intl`:

```php
echo Yii::t('app',
    'На диване {n, plural, =0{нет кошек} =1{лежит одна кошка} one{лежит # кошка} few{лежит # кошки} many{лежит # кошек} other{лежит # кошки}}!',
    ['n' => $count]
);
```

`=0`/`=1` — точные значения; `one` (21, 31…), `few` (2–4, 22–24…), `many` (0, 5–20…),
`other` — остальное; `#` подставляет число. Если один указатель используется и как
`plural`, и как число — второй раз он должен быть `{count, number}`, иначе
`U_ARGUMENT_TYPE_MISMATCH`.

**Выбор по ключу:**

```php
Yii::t('app', '{name} — {gender, select, женщина{ей} мужчина{ему} other{ему}} нравится Yii!',
    ['name' => 'Василий', 'gender' => 'мужчина']);
```

### Извлечение строк и переводы представлений

```bash
yii message/config-template config/i18n.php    # создать конфиг
yii message config/i18n.php                    # извлечь строки в файлы переводов
```

Локализованные представления: `views/site/ru-RU/index.php` подхватится автоматически
вместо `views/site/index.php`. То же работает для модулей и виджетов — они обычно
регистрируют свои переводы в `init()` и дают статический метод `Module::t()`.

> Важно: без расширения `intl` работают только базовые возможности; форматирование зависит
> от версии ICU, поэтому на всех окружениях держите одинаковые версии `intl`/ICU.

## Отправка почты

```php
'components' => [
    'mailer' => [
        'class' => 'yii\symfonymailer\Mailer',   // в старых проектах: yii\swiftmailer\Mailer
        'viewPath' => '@app/mail',
        'useFileTransport' => YII_ENV_DEV,       // письма в @runtime/mail вместо отправки
        'transport' => [
            'scheme' => 'smtps',
            'host' => 'smtp.example.com',
            'username' => 'user',
            'password' => 'secret',
            'port' => 465,
        ],
    ],
],
```

```php
Yii::$app->mailer->compose()
    ->setFrom('from@example.com')
    ->setTo('to@example.com')
    ->setSubject('Тема')
    ->setTextBody('Текст')
    ->setHtmlBody('<b>HTML</b>')
    ->send();
```

Через представления (файлы в `@app/mail`):

```php
Yii::$app->mailer->compose('greetings', ['user' => $user])       // одно представление
Yii::$app->mailer->compose(['html' => 'contact-html', 'text' => 'contact-text'], $params)
    ->setFrom(...)->setTo(...)->setSubject(...)->send();
```

Layout писем задаётся через `htmlLayout` / `textLayout` компонента mailer.

```php
$message->attach('/path/to/file.pdf');
$message->attachContent($csv, ['fileName' => 'report.csv', 'contentType' => 'text/csv']);

// картинка внутри письма (в представлении)
<img src="<?= $message->embed($imageFileName) ?>">

Yii::$app->mailer->sendMultiple($messages);      // пачкой, одним соединением
```

> Совет: на разработке включайте `useFileTransport` — письма складываются в
> `@runtime/mail` и их можно открыть текстовым редактором, ничего никуда не уходит.
