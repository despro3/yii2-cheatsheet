---
id: concepts
title: Ключевые концепции
icon: 💡
summary: Компоненты, свойства через геттеры, события, поведения, конфигурации, алиасы, автозагрузка, Service Locator, DI.
---

# Ключевые концепции Yii

Это «ядро» фреймворка: если понять эти восемь вещей, остальное читается интуитивно.

## Component и BaseObject

```
yii\base\BaseObject   → свойства (геттеры/сеттеры), init(), конфигурация через массив
yii\base\Component    → BaseObject + события + поведения
```

```php
class MyClass extends \yii\base\BaseObject
{
    public $prop1;

    public function __construct($param1, $config = [])   // $config — всегда последний
    {
        // инициализация ДО применения конфигурации
        parent::__construct($config);                    // родитель — в конце
    }

    public function init()
    {
        parent::init();                                  // родитель — в начале
        // проверки и нормализация ПОСЛЕ конфигурации
    }
}
```

Жизненный цикл: конструктор → применение `$config` → `init()` → работа.

> Совет: если события и поведения не нужны — наследуйтесь от `BaseObject`: он дешевле по
> памяти и времени, но свойства через геттеры/сеттеры поддерживает.

## Свойства через геттеры и сеттеры

```php
class Foo extends \yii\base\BaseObject
{
    private $_label;

    public function getLabel()          { return $this->_label; }
    public function setLabel($value)    { $this->_label = trim($value); }
}

$foo->label = '  abc  ';   // вызовет setLabel()
echo $foo->label;          // вызовет getLabel()
```

- только геттер → свойство только для чтения (запись даёт `InvalidCallException`);
- имена **регистронезависимы** (`$obj->label` == `$obj->Label`);
- реальное поле класса приоритетнее магического свойства;
- `property_exists()` не видит такие свойства — используйте `canGetProperty()` /
  `canSetProperty()`;
- статические геттеры/сеттеры не работают.

## События

```php
class Mailer extends \yii\base\Component
{
    const EVENT_MESSAGE_SENT = 'messageSent';

    public function send($message)
    {
        // ...
        $event = new MessageEvent(['message' => $message]);
        $this->trigger(self::EVENT_MESSAGE_SENT, $event);
    }
}
```

```php
// Подписка: строка-функция, [$obj,'method'], ['Class','method'], анонимка
$mailer->on(Mailer::EVENT_MESSAGE_SENT, function ($event) {
    echo $event->name, $event->sender, $event->data;
});
$mailer->on(Mailer::EVENT_MESSAGE_SENT, 'handler', $data, $append = false);  // в начало очереди

$mailer->off(Mailer::EVENT_MESSAGE_SENT, $handler);   // отписать один
$mailer->off(Mailer::EVENT_MESSAGE_SENT);             // отписать все
```

В обработчике `$event->handled = true` прерывает вызов остальных обработчиков.

**Уровни подписки:**

```php
// в конфигурации
'components' => ['db' => ['on afterOpen' => function ($e) { /* ... */ }]],

// на уровне класса — для всех экземпляров и наследников
Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, fn ($e) => /* ... */);
Event::trigger(Foo::class, Foo::EVENT_HELLO);       // $event->sender === null
Event::off(Foo::class, Foo::EVENT_HELLO);

// на уровне интерфейса
Event::on('app\interfaces\DanceEventInterface', DanceEventInterface::EVENT_DANCE, $h);

// глобальные события — через синглтон приложения
Yii::$app->on('backend.mail.sent', $handler);
Yii::$app->trigger('backend.mail.sent', new Event(['sender' => $this]));
```

Сначала вызываются обработчики уровня экземпляра, потом — уровня класса.

## Поведения (behaviors)

Поведение «примешивает» свойства и методы к компоненту и может слушать его события —
без изменения иерархии наследования.

```php
namespace app\components;

use yii\base\Behavior;
use yii\db\ActiveRecord;

class MyBehavior extends Behavior
{
    public $prop1;

    public function events()
    {
        return [ActiveRecord::EVENT_BEFORE_VALIDATE => 'beforeValidate'];
    }

    public function beforeValidate($event)
    {
        $this->owner;        // компонент, к которому прикреплено поведение
    }

    public function foo() { /* станет методом компонента */ }
}
```

```php
// статически
public function behaviors()
{
    return [
        MyBehavior::class,                                   // анонимное
        'myBehavior' => ['class' => MyBehavior::class, 'prop1' => 'v'],  // именованное
    ];
}

// динамически
$component->attachBehavior('myBehavior', new MyBehavior());
$component->detachBehavior('myBehavior');
$component->getBehavior('myBehavior');
$component->getBehaviors();

// через конфигурацию
['as myBehavior' => ['class' => MyBehavior::class, 'prop1' => 'v']]
```

При конфликте имён выигрывает поведение, прикреплённое **раньше**.

### Встроенные поведения

```php
use yii\behaviors\TimestampBehavior;
use yii\behaviors\BlameableBehavior;
use yii\behaviors\SluggableBehavior;

public function behaviors()
{
    return [
        [
            'class' => TimestampBehavior::class,
            'attributes' => [
                ActiveRecord::EVENT_BEFORE_INSERT => ['created_at', 'updated_at'],
                ActiveRecord::EVENT_BEFORE_UPDATE => ['updated_at'],
            ],
            // 'value' => new \yii\db\Expression('NOW()'),   // для типа datetime
        ],
        ['class' => BlameableBehavior::class, 'createdByAttribute' => 'author_id'],
        ['class' => SluggableBehavior::class, 'attribute' => 'title', 'ensureUnique' => true],
    ];
}

$user->touch('login_time');    // TimestampBehavior: обновить поле и сохранить
```

Ещё есть `AttributeBehavior`, `AttributeTypecastBehavior`, `OptimisticLockBehavior`,
`CacheableWidgetBehavior`.

**Поведения vs трейты:** поведения поддерживают наследование, настройку, динамическое
подключение и подписку на события; трейты быстрее и лучше видны IDE.

## Конфигурации

```php
[
    'class' => 'app\components\SearchEngine',   // что создавать
    'apiKey' => 'xxx',                          // свойства
    'on search' => function ($event) { },       // обработчики событий
    'as indexer' => ['class' => IndexerBehavior::class],   // поведения
]
```

```php
$object = Yii::createObject($config);     // создать по конфигу
Yii::configure($object, $config);         // применить к существующему (без ключа class)
```

Значения по умолчанию для всех будущих объектов класса:

```php
Yii::$container->set('yii\widgets\LinkPager', ['maxButtonCount' => 5]);
// или декларативно, в конфиге приложения (с 2.0.11):
'container' => [
    'definitions' => ['yii\widgets\LinkPager' => ['maxButtonCount' => 5]],
    'singletons' => [/* ... */],
],
```

Конфигурацию разбивают на файлы: `web.php` подключает `db.php`, `params.php`,
`components.php` через `require`, а окружение различают константами:

```php
if (YII_ENV_DEV) { $config['bootstrap'][] = 'debug'; }
```

## Псевдонимы путей (алиасы)

```php
Yii::setAlias('@images', '@webroot/images');
Yii::setAlias('@cdn', 'https://cdn.example.com');
echo Yii::getAlias('@images/logo.png');    // /var/www/web/images/logo.png
```

| Алиас | Значение |
|---|---|
| `@yii` | папка фреймворка |
| `@app` | `basePath` приложения |
| `@runtime` | `@app/runtime` |
| `@vendor` | `@app/vendor` |
| `@webroot` | папка входного скрипта (`web/`) |
| `@web` | базовый URL приложения |
| `@bower`, `@npm` | клиентские пакеты в `vendor` |
| `@yii/imagine` и пр. | автоматически для каждого расширения |

Производные алиасы получаются добавлением пути: `@app/models`. Более специфичный корневой
алиас выигрывает: при `@foo` и `@foo/bar` путь `@foo/bar/file.php` разрешится через `@foo/bar`.

## Автозагрузка классов

Автозагрузчик Yii совместим с PSR-4: класс `foo\bar\MyClass` ищется по алиасу
`@foo/bar/MyClass.php`. Для `app\...` алиас `@app` уже определён — свои классы в
`basic`-шаблоне работают «из коробки».

```php
Yii::$classMap['foo\bar\MyClass'] = '@app/legacy/MyClass.php';  // карта классов, самый быстрый путь
```

Порядок в входном скрипте важен: сначала `vendor/autoload.php` (Composer), затем `Yii.php`.

## Service Locator

`Yii::$app` (и каждый модуль) — это `yii\di\ServiceLocator`: реестр «ID → компонент»
с ленивым созданием и кешированием экземпляра.

```php
$locator->set('cache', 'yii\caching\ApcCache');
$locator->set('db', ['class' => 'yii\db\Connection', 'dsn' => '...']);
$locator->set('search', fn () => new app\components\SolrService());
$locator->set('pageCache', new FileCache());

$locator->get('cache');   // == $locator->cache
$locator->has('cache');
```

Массив `components` в конфиге приложения — это и есть `setComponents()`.

## Контейнер внедрения зависимостей (DI)

`Yii::$container` умеет разрешать зависимости по типам в конструкторе — рекурсивно.

```php
// Регистрация
Yii::$container->set('yii\mail\MailerInterface', 'yii\symfonymailer\Mailer');  // интерфейс → класс
Yii::$container->set('db', ['class' => 'yii\db\Connection', 'dsn' => '...']);  // алиас + конфиг
Yii::$container->set('Foo', fn ($c, $params, $config) => new Foo(new Bar()));  // фабрика
Yii::$container->setSingleton('app\storage\FileStorage', [['class' => FileStorage::class], ['/var/tmp']]);

// Получение
$obj = Yii::$container->get('app\components\SearchEngine', [$apiKey], ['type' => 1]);
Yii::$container->invoke([$obj, 'doSomething'], ['param1' => 42]);  // внедрение в метод
```

Виды внедрения: через конструктор (по типам параметров), через метод (`invoke()`),
через сеттер/свойство (конфигурация), через PHP-callback.

Зависимости в контроллере разрешаются автоматически:

```php
class HotelController extends \yii\web\Controller
{
    public function __construct($id, $module, BookingInterface $booking, $config = [])
    {
        $this->booking = $booking;
        parent::__construct($id, $module, $config);
    }
}
// нужно лишь сказать контейнеру, какая реализация используется:
Yii::$container->set(BookingInterface::class, BookingService::class);
```

`Instance::of('alias')` в параметрах ссылается на другую зарегистрированную зависимость.
`set()` создаёт объект каждый раз, `setSingleton()` — один раз.

> Совет: регистрируйте зависимости как можно раньше — в конфигурации приложения или в
> bootstrap-классе расширения. `Yii::createObject()` внутри использует контейнер, поэтому
> переопределение классов ядра работает глобально.
