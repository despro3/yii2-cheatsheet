---
id: behaviors
title: Поведения
part: concepts
summary: Поведения (миксины Yii) добавляют компоненту методы, свойства и реакции на события без наследования; встроенные TimestampBehavior, BlameableBehavior, SluggableBehavior и сравнение с трейтами.
sources: concept-behaviors
---

:::lead
Поведение — объект `yii\base\Behavior`, «прикреплённый» к компоненту: его публичные методы и свойства становятся методами и свойствами компонента, а `events()` подписывает его на события владельца. Самый известный пример — `TimestampBehavior`, который сам проставляет `created_at`/`updated_at`.
:::

## Как выглядит поведение

```php
namespace app\components;

use yii\base\Behavior;
use yii\db\ActiveRecord;

class MyBehavior extends Behavior
{
    public $prop1;
    private $_prop2;

    public function getProp2() { return $this->_prop2; }
    public function setProp2($value) { $this->_prop2 = $value; }

    public function foo()
    {
        return $this->owner->id;          // $this->owner — компонент, к которому прикреплены
    }

    public function events()             // реакция на события владельца
    {
        return [
            ActiveRecord::EVENT_BEFORE_VALIDATE => 'beforeValidate',
        ];
    }

    public function beforeValidate($event)
    {
        // ...
    }
}
```

Обработчик в `events()` — имя метода поведения, массив `[$obj, 'method']` или замыкание.

## Прикрепление

```php
class User extends ActiveRecord
{
    public function behaviors()
    {
        return [
            MyBehavior::class,                              // анонимное
            'myBehavior2' => MyBehavior::class,             // именованное
            [                                               // с конфигурацией
                'class' => MyBehavior::class,
                'prop1' => 'value1',
            ],
            'myBehavior4' => ['class' => MyBehavior::class, 'prop1' => 'value1'],
        ];
    }
}

// динамически
$component->attachBehavior('myBehavior', new MyBehavior());
$component->attachBehaviors(['a' => MyBehavior::class, 'b' => ['class' => MyBehavior::class]]);
$component->detachBehavior('myBehavior');
$component->detachBehaviors();

// в конфигурации — ключ 'as имя'
'as myBehavior' => ['class' => MyBehavior::class, 'prop1' => 'value1'],
```

После прикрепления:

```php
$component->prop1 = 'x';          // свойство поведения
$component->foo();                // метод поведения
$component->getBehavior('myBehavior2');
$component->getBehaviors();
```

Если два поведения объявили одноимённый метод, побеждает то, что прикреплено раньше.

## Встроенные поведения

### TimestampBehavior

```php
use yii\behaviors\TimestampBehavior;
use yii\db\Expression;

public function behaviors()
{
    return [
        [
            'class' => TimestampBehavior::class,
            'attributes' => [                       // так и по умолчанию — можно не писать
                ActiveRecord::EVENT_BEFORE_INSERT => ['created_at', 'updated_at'],
                ActiveRecord::EVENT_BEFORE_UPDATE => ['updated_at'],
            ],
            // 'value' => new Expression('NOW()'),  // если столбцы DATETIME, а не INT с unix timestamp
        ],
    ];
}

$user->touch('login_at');   // проставить текущее время в атрибут и сохранить
```

### Другие

:::kv
`BlameableBehavior` — записывает ID текущего пользователя в `created_by` / `updated_by`
`SluggableBehavior` — строит URL-slug из атрибута (`'attribute' => 'title'`), с опциями уникальности и неизменности
`AttributeBehavior` — общий случай: значение (или замыкание) в атрибуты по событиям
`AttributeTypecastBehavior` — приведение типов атрибутов при валидации/сохранении
`OptimisticLockBehavior` — оптимистичная блокировка через версию (см. [Active Record](active-record))
`yii2tech\ar\softdelete\SoftDeleteBehavior` — «мягкое» удаление (стороннее)
:::

## Поведения против трейтов

:::cols
=== Поведения
- наследуются, настраиваются конфигурацией;
- прикрепляются и отвязываются на лету, без правки класса;
- умеют слушать события владельца;
- конфликты имён решаются порядком прикрепления.
=== Трейты
- быстрее: нет дополнительных объектов;
- поддерживаются IDE как конструкция языка;
- требуют правки класса и ручного разрешения конфликтов.
:::

Они дополняют друг друга: трейт — для чистого переиспользования кода, поведение — когда нужны конфигурация, динамика и события.

:::quiz Проверь себя
Q: Как поведение узнаёт, к какому объекту оно прикреплено?
A: Через свойство `$this->owner`, которое устанавливается при `attachBehavior()`.
Q: Что вернёт `events()` поведения и зачем это нужно?
A: Массив «событие владельца → обработчик»; так `TimestampBehavior` подписывается на `beforeInsert`/`beforeUpdate` и заполняет даты.
Q: Чем поведение принципиально отличается от трейта?
A: Это объект: его можно настроить, прикрепить и отвязать во время выполнения, и оно может реагировать на события.
Q: Как прикрепить поведение к компоненту приложения через конфигурацию?
A: Ключом `'as имя' => [...]` в массиве конфигурации компонента.
:::
