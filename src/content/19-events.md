---
id: events
title: События
part: concepts
summary: Как подписаться на событие, вызвать своё, передать данные, остановить цепочку обработчиков; события уровня класса, интерфейса и глобальные.
sources: concept-events
---

:::lead
Событие — точка, в которой компонент говорит «случилось вот это», а любой код может отреагировать. Компонент вызывает `trigger()`, подписчики регистрируются через `on()`. Так фреймворк даёт встраиваться в свою работу, не требуя наследования.
:::

## Подписка

```php
$foo->on(Foo::EVENT_HELLO, 'function_name');                 // глобальная функция
$foo->on(Foo::EVENT_HELLO, [$object, 'methodName']);         // метод объекта
$foo->on(Foo::EVENT_HELLO, ['app\components\Bar', 'method']); // статический метод
$foo->on(Foo::EVENT_HELLO, function ($event) {               // замыкание
    echo $event->name;       // имя события
    echo $event->sender;     // кто вызвал trigger()
    echo $event->data;       // данные, переданные при подписке
});

// данные для обработчика — третий аргумент
$foo->on(Foo::EVENT_HELLO, function ($event) { echo $event->data; }, 'abc');

// в начало очереди, а не в конец
$foo->on(Foo::EVENT_HELLO, $handler, null, false);
```

Через конфигурацию — ключ `'on имяСобытия'`:

```php
'components' => [
    'db' => [
        'class' => 'yii\db\Connection',
        'on afterOpen' => function ($event) {
            $event->sender->createCommand("SET time_zone = '+00:00'")->execute();
        },
    ],
],
```

### Порядок и остановка

Обработчики вызываются в порядке подписки. Чтобы остановить остальные:

```php
$foo->on(Foo::EVENT_HELLO, function ($event) {
    $event->handled = true;   // следующие обработчики не вызовутся
});
```

Многие события фреймворка отменяют операцию через `$event->isValid = false` (`beforeSave`, `beforeAction`, `beforeLogin`…).

## Вызов своего события

```php
namespace app\components;

use yii\base\Component;
use yii\base\Event;

class MessageEvent extends Event
{
    public $message;           // свои данные — в наследнике Event
}

class Mailer extends Component
{
    const EVENT_MESSAGE_SENT = 'messageSent';   // имя — константой: без опечаток, видно в IDE

    public function send($message)
    {
        // ...отправка...
        $this->trigger(self::EVENT_MESSAGE_SENT, new MessageEvent(['message' => $message]));
    }
}
```

Класс должен наследовать `yii\base\Component`. Без объекта события `trigger()` создаст пустой `Event`.

## Отписка

```php
$foo->off(Foo::EVENT_HELLO, 'function_name');
$foo->off(Foo::EVENT_HELLO, $anonymousFunction);   // замыкание нужно сохранить в переменную при подписке
$foo->off(Foo::EVENT_HELLO);                        // все обработчики события
```

## События уровня класса

Слушать событие **всех** экземпляров класса и его потомков — статический `Event::on()`:

```php
use yii\base\Event;
use yii\db\ActiveRecord;

Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, function ($event) {
    Yii::debug(get_class($event->sender) . ' добавлен');
});

Event::trigger(Foo::class, Foo::EVENT_HELLO);    // событие без объекта: $event->sender === null
Event::off(Foo::class, Foo::EVENT_HELLO);
```

Порядок: сначала обработчики экземпляра, затем — класса. Осторожно с базовыми классами вроде `BaseObject`: подписка на них сработает для всего приложения.

### На уровне интерфейса

Первым аргументом `Event::on()` может быть интерфейс — обработчик получит события всех классов, которые его реализуют:

```php
interface DanceEventInterface { const EVENT_DANCE = 'dance'; }

Event::on(DanceEventInterface::class, DanceEventInterface::EVENT_DANCE, function ($event) {
    Yii::debug(get_class($event->sender) . ' танцует');
});
```

Вызвать `Event::trigger()` для интерфейса нельзя — только для конкретного класса.

## Глобальные события

Никакого отдельного механизма: событие вешают на синглтон — приложение:

```php
Yii::$app->on('app.mail.sent', function ($event) { /* ... */ });
Yii::$app->trigger('app.mail.sent', new Event(['sender' => $mailer]));
```

Пространство имён одно на всё приложение — давайте событиям осмысленные префиксы.

## Где события уже есть

:::kv
Приложение — `beforeRequest`, `afterRequest`, `beforeAction`, `afterAction`
Контроллер / модуль — `beforeAction`, `afterAction`
Model — `beforeValidate`, `afterValidate`
ActiveRecord — `init`, `afterFind`, `beforeInsert/Update/Delete`, `afterInsert/Update/Delete`, `afterRefresh`
View — `beforeRender`, `afterRender`, `beginPage`, `endPage`, `beginBody`, `endBody`
User — `beforeLogin`, `afterLogin`, `beforeLogout`, `afterLogout`
Response — `beforeSend`, `afterPrepare`, `afterSend`
Connection — `afterOpen`, `beginTransaction`, `commitTransaction`, `rollbackTransaction`
:::

:::quiz Проверь себя
Q: Что нужно, чтобы класс мог генерировать события?
A: Наследовать `yii\base\Component` и вызывать `$this->trigger($name, $event)`.
Q: Как остановить выполнение остальных обработчиков события?
A: Установить `$event->handled = true` в обработчике.
Q: В чём разница между `$obj->on()` и `Event::on(Class::class, ...)`?
A: Первый слушает конкретный объект; второй — все экземпляры класса и его потомков (и вызывается после обработчиков экземпляра).
Q: Как передать обработчику события дополнительные данные?
A: Аргументом `$data`: третьим у `$obj->on()` и четвёртым у `Event::on()`; они доступны как `$event->data`. Данные, известные в момент события, передают через свой класс `Event` в `trigger()`.
Q: Как подписаться на событие компонента прямо в конфигурации?
A: Ключом `'on имяСобытия' => $handler` в массиве конфигурации компонента.
:::
