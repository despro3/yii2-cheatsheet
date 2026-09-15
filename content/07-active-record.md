---
id: ar
title: Active Record
icon: 🧬
summary: Поиск, сохранение, события, транзакции, оптимистичная блокировка, связи, жадная загрузка.
---

# Active Record

Класс = таблица, объект = строка, атрибут = столбец. AR наследует `yii\base\Model`, поэтому
умеет всё, что умеют модели: валидацию, сценарии, метки, `toArray()`.

## Объявление класса

```php
namespace app\models;

use yii\db\ActiveRecord;

class Customer extends ActiveRecord
{
    const STATUS_ACTIVE = 1;

    public static function tableName()      // по умолчанию: camel2id(имя класса)
    {
        return '{{%customer}}';             // %  → подставится tablePrefix
    }

    public static function getDb()          // другое соединение
    {
        return \Yii::$app->db2;
    }
}
```

## Поиск

```php
Customer::findOne(123);                                   // по первичному ключу
Customer::findOne(['id' => 123, 'status' => 1]);           // по условию-хешу
Customer::findAll([100, 101, 123]);                        // несколько PK
Customer::find()->where(['status' => 1])->orderBy('id')->all();
Customer::find()->where(['status' => 1])->count();
Customer::find()->indexBy('id')->all();
Customer::find()->asArray()->all();                        // массивы вместо объектов — экономнее
Customer::findBySql('SELECT * FROM customer WHERE status=:s', [':s' => 1])->all();
Customer::find()->limit(1)->one();                         // one() сам LIMIT не добавляет!

foreach (Customer::find()->batch(100) as $customers) { }   // пакетная выборка
foreach (Customer::find()->each(100) as $customer) { }
```

> Важно: `findOne($_GET['id'])` небезопасен — пользователь может передать массив и
> поиск пойдёт по другому столбцу. Пишите `findOne(['id' => Yii::$app->request->get('id')])`
> либо получайте `$id` как параметр действия (он гарантированно скаляр).

## Сохранение и удаление

```php
$customer = new Customer();
$customer->name = 'James';
$customer->save();                       // insert + валидация
$customer->save(false);                  // без валидации
$customer->insert();  $customer->update();   // явно

$customer = Customer::findOne(123);
$customer->email = 'new@example.com';
$customer->save();                       // update только «грязных» атрибутов

$customer->attributes = ['name' => 'X']; // массовое присвоение (только безопасные атрибуты)
$customer->loadDefaultValues();          // значения DEFAULT из схемы БД

$post->updateCounters(['view_count' => 1]);          // UPDATE ... SET view_count = view_count + 1
Customer::updateAll(['status' => 1], ['like', 'email', '@example.com']);
Customer::updateAllCounters(['age' => 1]);
$customer->delete();
Customer::deleteAll(['status' => 0]);                // осторожно: без условия удалит всё
```

Полезные состояния:

```php
$customer->isNewRecord;
$customer->getDirtyAttributes();  $customer->markAttributeDirty('name');
$customer->getOldAttributes();  $customer->getOldAttribute('name');
$customer->refresh();
$customer->getPrimaryKey();  Customer::primaryKey();
```

> Важно: `updateAll()`, `deleteAll()`, `updateCounters()`, `updateAllCounters()` работают
> одним SQL-запросом и **не запускают** валидацию и события жизненного цикла.

## Жизненный цикл и события

| Операция | Последовательность |
|---|---|
| `new` | конструктор → `init()` → `EVENT_INIT` |
| выборка | конструктор → `init()` → `afterFind()` / `EVENT_AFTER_FIND` |
| `save()` | `beforeValidate` → валидация → `afterValidate` → `beforeSave` (`EVENT_BEFORE_INSERT`/`UPDATE`) → запись → `afterSave` (`EVENT_AFTER_INSERT`/`UPDATE`) |
| `delete()` | `beforeDelete` → удаление → `afterDelete` |

```php
public function beforeSave($insert)
{
    if (!parent::beforeSave($insert)) { return false; }   // false → сохранение отменяется
    $this->slug = \yii\helpers\Inflector::slug($this->title);
    return true;
}
```

## Транзакции в AR

```php
Customer::getDb()->transaction(function ($db) use ($customer) {
    $customer->save();
    // ...
});
```

Либо декларативно — операции по сценариям:

```php
public function transactions()
{
    return [
        'admin' => self::OP_INSERT,
        'api' => self::OP_ALL,   // OP_INSERT | OP_UPDATE | OP_DELETE
    ];
}
```

## Оптимистичная блокировка

1. Столбец `version` (`BIGINT DEFAULT 0`) в таблице.
2. `public function optimisticLock() { return 'version'; }`
3. Скрытое поле `version` в форме (`Html::activeHiddenInput($model, 'version')`).
4. Ловите `yii\db\StaleObjectException` в действии обновления.

## Приведение типов

При заполнении из БД значения приводятся к типам PHP по схеме (int, bool), но:
float остаётся строкой (точность), unsigned/big integer — строка на 32-битных системах.
Данные из HTTP-запроса **не** приводятся. Для этого есть
`yii\behaviors\AttributeTypecastBehavior`. JSON-столбцы (MySQL/PostgreSQL) декодируются
автоматически, массивы PostgreSQL — в `ArrayExpression`.

## Связи

```php
class Customer extends ActiveRecord
{
    public function getOrders()            // hasMany: ['чужой_столбец' => 'свой_столбец']
    {
        return $this->hasMany(Order::class, ['customer_id' => 'id'])->inverseOf('customer');
    }

    public function getCountry()
    {
        return $this->hasOne(Country::class, ['id' => 'country_id']);
    }

    public function getBigOrders($threshold = 100)   // связь с параметром
    {
        return $this->hasMany(Order::class, ['customer_id' => 'id'])
            ->where(['>', 'subtotal', $threshold]);
    }
}
```

Many-to-many через промежуточную таблицу:

```php
public function getItems()
{
    return $this->hasMany(Item::class, ['id' => 'item_id'])
        ->viaTable('order_item', ['order_id' => 'id']);
}

// или через уже объявленную связь
public function getOrderItems() { return $this->hasMany(OrderItem::class, ['order_id' => 'id']); }
public function getItems()      { return $this->hasMany(Item::class, ['id' => 'item_id'])->via('orderItems'); }
```

Доступ:

```php
$customer->orders;          // массив Order — запрос выполняется один раз и кешируется
$customer->getOrders();     // объект ActiveQuery — можно донастроить
$customer->getOrders()->where(['>', 'subtotal', 200])->all();
unset($customer->orders);   // сбросить кеш связи
```

> Важно: имя связи `relation` зарезервировано — не используйте `getRelation()`.

### Отложенная vs жадная загрузка (проблема N+1)

```php
// 101 запрос — плохо
$customers = Customer::find()->limit(100)->all();
foreach ($customers as $c) { $c->orders; }

// 2 запроса — хорошо
$customers = Customer::find()->with('orders')->limit(100)->all();

// вложенные связи и настройка запроса на лету
Customer::find()->with([
    'country',
    'orders' => fn ($q) => $q->andWhere(['status' => Order::STATUS_ACTIVE]),
    'orders.items',
])->all();
```

При жадной загрузке `N` связей, из которых `M` через промежуточные таблицы, выполняется
`N+M+1` запросов.

> Важно: если используете `select()` вместе с `with()`, обязательно включайте столбцы
> связи — иначе связь не заполнится:
> `Order::find()->select(['id', 'amount', 'customer_id'])->with('customer')`.

### JOIN по связям

```php
// фильтр по связной таблице + жадная загрузка
Customer::find()->joinWith('orders')->where(['order.status' => 1])->all();
Customer::find()->innerJoinWith('orders')->all();
Customer::find()->joinWith('orders', false)->all();            // без жадной загрузки

// псевдоним связной таблицы (с 2.0.7)
$query->joinWith(['orders o'])->orderBy('o.id');
$query->joinWith(['orders o' => fn ($q) => $q->joinWith('product p')])->where('o.amount > 100');

// условие в ON, а не в WHERE: вернутся ВСЕ покупатели, но только активные заказы
Customer::find()->joinWith([
    'orders' => fn ($q) => $q->onCondition(['order.status' => Order::STATUS_ACTIVE]),
])->all();
```

`joinWith()` по умолчанию делает `LEFT JOIN` и включает жадную загрузку. Связи между
разными БД (даже MySQL + MongoDB) работают, но `joinWith()` — только внутри одной СУБД.

### Сохранение связей

```php
$order->link('customer', $customer);        // проставит FK и сохранит
$order->link('items', $item);               // вставит строку в промежуточную таблицу
$customer->unlink('orders', $order);        // FK → null
$customer->unlink('orders', $order, true);  // удалить связную запись/строку связи
$customer->unlinkAll('orders', true);
```

`link()` не валидирует данные и не работает для двух новых (несохранённых) объектов.

## Свой класс запроса

```php
class Comment extends ActiveRecord
{
    public static function find()
    {
        return new CommentQuery(get_called_class());
    }
}

class CommentQuery extends \yii\db\ActiveQuery
{
    public function active($state = true)
    {
        return $this->andWhere(['active' => $state]);   // именно andWhere, не where
    }
}

Comment::find()->active()->all();
Customer::find()->with(['comments' => fn ($q) => $q->active()])->all();
```

Это замена «скоупов» из Yii 1.1. Дополнительные вычисляемые атрибуты:

```php
class Room extends ActiveRecord
{
    public $volume;
}

Room::find()
    ->select(['{{room}}.*', '([[length]] * [[width]] * [[height]]) AS volume'])
    ->orderBy('volume DESC')
    ->all();
```
