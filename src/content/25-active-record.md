---
id: active-record
title: Active Record
part: db
summary: Модель = строка таблицы — объявление класса, find()/findOne()/findAll(), сохранение и «грязные» атрибуты, события жизненного цикла, транзакции и оптимистичная блокировка, связи hasOne/hasMany/via, жадная загрузка with()/joinWith(), link()/unlink(), собственный ActiveQuery.
sources: db-active-record
---

:::lead
Active Record связывает класс с таблицей: объект — строка, свойства — столбцы. `Customer::findOne(1)` читает, `$customer->save()` пишет, `$customer->orders` подгружает связанные записи. Внутри — тот же [Query Builder](query-builder) и [DAO](dao), поэтому всё, что умеют они, доступно и здесь. Поддерживаются реляционные СУБД, а также Redis, MongoDB, Elasticsearch и Sphinx через расширения.
:::

## Объявление

```php
namespace app\models;

use yii\db\ActiveRecord;

class Customer extends ActiveRecord
{
    const STATUS_INACTIVE = 0;
    const STATUS_ACTIVE = 1;

    public static function tableName()
    {
        return '{{%customer}}';        // по умолчанию — имя класса в snake_case: 'customer'
    }

    // public static function getDb() { return Yii::$app->db2; }   // другое соединение
}
```

Столбцы становятся атрибутами автоматически — по схеме таблицы (`$customer->email`). Как и любая [модель](models), AR поддерживает `rules()`, `scenarios()`, `attributeLabels()`, `load()`, массовое присваивание и валидацию.

> [!TIP]
> Не пишите классы руками — [Gii](dev-tools) сгенерирует их по таблице вместе с правилами, подписями и связями.

## Чтение

```php
// построение через ActiveQuery — все методы Query Builder
$customers = Customer::find()->where(['status' => Customer::STATUS_ACTIVE])->orderBy('id')->all();
$customer  = Customer::find()->where(['id' => 1])->one();
$count     = Customer::find()->where(['status' => 1])->count();

// сокращения — по первичному ключу или условию
$customer  = Customer::findOne(123);                        // WHERE id = 123
$customers = Customer::findAll([100, 101, 123]);            // WHERE id IN (…)
$customer  = Customer::findOne(['id' => 123, 'status' => 1]);
$customers = Customer::findAll(['status' => 1]);

// сырой SQL
$customers = Customer::findBySql('SELECT * FROM customer WHERE status=:status', [':status' => 1])->all();
```

> [!GOTCHA] Инъекция через findOne()
> `Customer::findOne(Yii::$app->request->get('id'))` — опасно: если в `id` передать массив `['id' => 1, 'status' => 1]`, он превратится в условие. Приводите тип (`(int)$id`) или пишите `findOne(['id' => $id])` явно. С 2.0.15 фреймворк отбрасывает часть таких массивов, но полагаться на это не стоит: ключами по-прежнему могут быть настоящие столбцы таблицы.

### Форма результата

```php
// массивы вместо объектов — быстрее, но без приведения типов и связей-объектов
$rows = Customer::find()->asArray()->all();
$customers = Customer::find()->indexBy('id')->all();

foreach (Customer::find()->batch(100) as $customers) { }   // пакетами, как в Query
foreach (Customer::find()->with('orders')->each() as $customer) { }   // связи тоже грузятся по пакетам
```

### Доступ к данным

```php
$customer = Customer::findOne(1);
$id = $customer->id;                 // атрибут — свойство объекта
$customer->email = 'new@example.com';

$customer->attributes;               // все атрибуты массивом
$customer->getAttributes(['id', 'email']);
$customer->isNewRecord;              // true у только что созданного объекта
$customer->primaryKey;
Customer::primaryKey();              // ['id']
Customer::getTableSchema()->columns;
```

Значения приходят в PHP-типах согласно схеме (`int`, `string`, `float`, `bool`, `null`), в отличие от DAO, где всё — строки. Даты остаются строками.

## Сохранение

```php
$customer = new Customer();
$customer->name = 'James';
$customer->email = 'james@example.com';
$customer->save();                   // INSERT (isNewRecord == true)

$customer = Customer::findOne(123);
$customer->email = 'james@newexample.com';
$customer->save();                   // UPDATE

$customer->insert(); $customer->update();   // явно; save() выбирает сам
```

`save()` сначала выполняет **валидацию**: при ошибках вернёт `false`, ничего не записав, — проверяйте результат и `$model->errors`. `save(false)` пропускает валидацию (когда данные уже проверены).

### Грязные атрибуты

В `UPDATE` попадают только изменённые (dirty) атрибуты; если их нет — запрос не выполняется вовсе:

```php
$customer->dirtyAttributes;          // ['email' => 'new@…']
$customer->oldAttributes;            // значения на момент загрузки
$customer->getOldAttribute('email');
$customer->markAttributeDirty('email');   // принудительно
```

Сравнение строгое (`===`): `1` и `'1'` — разные значения.

### Значения по умолчанию, приведение типов, счётчики

```php
$customer = new Customer();
$customer->loadDefaultValues();      // DEFAULT из схемы таблицы

// UPDATE post SET view_count = view_count + 1 — атомарно, без гонок
$post->updateCounters(['view_count' => 1]);

// массово, без загрузки объектов (события не срабатывают!)
Customer::updateAll(['status' => 1], 'status = 2');
Customer::updateAllCounters(['age' => 1], ['status' => 1]);
Customer::deleteAll(['status' => 0]);
```

`updateAll()`/`deleteAll()` не вызывают события и поведения (`TimestampBehavior` не обновит `updated_at`) — цена скорости.

## Удаление

```php
$customer = Customer::findOne(123);
$customer->delete();                  // DELETE одной записи, с событиями

Customer::deleteAll(['status' => 0]); // массово
```

## Жизненный цикл

Именно в него встраиваются [поведения](behaviors) и переопределённые методы.

:::kv
`new` — `__construct()` → `init()` → событие `EVENT_INIT`
`find()` / `findOne()` — конструктор → `init()` → `EVENT_INIT` → заполнение атрибутов → `afterFind()` → `EVENT_AFTER_FIND`
`save()` — `beforeValidate()` → `EVENT_BEFORE_VALIDATE` → валидация → `afterValidate()` → `EVENT_AFTER_VALIDATE` → `beforeSave()` → `EVENT_BEFORE_INSERT/UPDATE` → INSERT/UPDATE → `afterSave()` → `EVENT_AFTER_INSERT/UPDATE`
`delete()` — `beforeDelete()` → `EVENT_BEFORE_DELETE` → DELETE → `afterDelete()` → `EVENT_AFTER_DELETE`
`refresh()` — перечитать из БД → `afterRefresh()` → `EVENT_AFTER_REFRESH`
:::

```php
public function beforeSave($insert)
{
    if (!parent::beforeSave($insert)) {
        return false;                 // отменить сохранение
    }
    if ($insert) {
        $this->token = Yii::$app->security->generateRandomString();
    }
    return true;
}
```

Возврат `false` из `beforeValidate()`, `beforeSave()`, `beforeDelete()` отменяет операцию. Не забывайте `parent::…()` — иначе не сработают события и поведения.

## Транзакции

```php
// вручную — как в DAO
Customer::getDb()->transaction(function ($db) use ($customer, $order) {
    $customer->save();
    $order->save();
});

// декларативно: какие операции всегда обернуть в транзакцию
class Post extends ActiveRecord
{
    public function transactions()
    {
        return [
            'admin' => self::OP_INSERT,
            'api'   => self::OP_INSERT | self::OP_UPDATE | self::OP_DELETE,
            // 'default' => self::OP_ALL,
        ];
    }
}
```

`transactions()` привязан к сценариям: в сценарии `api` любой `save()`/`delete()` — вместе с `beforeSave()`/`afterSave()` — выполняется внутри транзакции.

## Оптимистичная блокировка

Защищает от ситуации «два пользователя редактируют одну запись»:

```php
// 1. столбец version INT в таблице
// 2. в модели
public function optimisticLock() { return 'version'; }
// 3. в форме — скрытое поле
echo $form->field($model, 'version')->hiddenInput();
// 4. в контроллере
try {
    $model->save();
} catch (\yii\db\StaleObjectException $e) {
    // запись уже изменили — показать diff, предложить перезагрузить
}
```

Если версия в БД отличается от отправленной, `update()`/`delete()` выбросят `StaleObjectException`. Готовое решение — `OptimisticLockBehavior`.

## Связи

### Объявление

```php
class Customer extends ActiveRecord
{
    public function getOrders()
    {
        return $this->hasMany(Order::class, ['customer_id' => 'id']);
        //                       связанный класс   [столбец в Order => столбец в Customer]
    }
}

class Order extends ActiveRecord
{
    public function getCustomer()
    {
        return $this->hasOne(Customer::class, ['id' => 'customer_id']);
    }

    public function getBigItems()               // связь с условием
    {
        return $this->hasMany(Item::class, ['id' => 'item_id'])
            ->viaTable('order_item', ['order_id' => 'id'])
            ->where(['>', 'subtotal', 100])
            ->orderBy('id');
    }
}
```

Массив соответствий читается как «столбец связанного класса ⇒ столбец текущего». Порядок — сначала *чужой* столбец — самая частая ошибка.

### Доступ

```php
$customer = Customer::findOne(123);
$orders   = $customer->orders;            // ленивая загрузка: SELECT * FROM order WHERE customer_id = 123
$orders   = $customer->orders;            // второй раз — из кэша объекта, без запроса
$customer->orders = null; unset($customer->orders);   // сбросить кэш

$query = $customer->getOrders();          // объект ActiveQuery — можно достроить
$orders = $query->where(['status' => 1])->orderBy('id')->all();
```

`$customer->orders` вернёт массив объектов для `hasMany` и объект либо `null` для `hasOne`.

### Связь через промежуточную таблицу

```php
public function getItems()
{
    return $this->hasMany(Item::class, ['id' => 'item_id'])
        ->viaTable('order_item', ['order_id' => 'id']);        // таблица без класса
}

public function getOrderItems()
{
    return $this->hasMany(OrderItem::class, ['order_id' => 'id']);
}
public function getItems()
{
    return $this->hasMany(Item::class, ['id' => 'item_id'])
        ->via('orderItems');                                     // через другую связь
}
```

### Жадная загрузка — против N+1

```php
// плохо: 1 + N запросов
$customers = Customer::find()->limit(100)->all();
foreach ($customers as $customer) {
    $orders = $customer->orders;
}

// хорошо: 2 запроса — SELECT * FROM customer …; SELECT * FROM order WHERE customer_id IN (…)
$customers = Customer::find()->with('orders')->limit(100)->all();

// несколько связей и вложенность
Customer::find()->with('orders.items', 'country')->all();
// с настройкой запроса связи
Customer::find()->with([
    'orders' => function (\yii\db\ActiveQuery $query) {
        $query->andWhere(['status' => Order::STATUS_ACTIVE]);
    },
])->all();
// дозагрузить уже выбранным объектам
$customer->populateRelation('orders', $orders);
```

### JOIN по связи

`with()` не добавляет JOIN — фильтровать основную выборку по связанной таблице через него нельзя. Для этого `joinWith()`:

```php
$orders = Order::find()
    ->joinWith('customer')                       // LEFT JOIN customer ON …
    ->where(['customer.status' => 1])            // теперь можно
    ->orderBy('customer.id, order.id')
    ->all();

Order::find()->innerJoinWith('customer');
Order::find()->joinWith('customer', false);      // только JOIN, без загрузки связи (eager = false)
Order::find()->joinWith(['books' => function ($q) { $q->onCondition(['book.category_id' => 1]); }]);
Order::find()->joinWith('customer')->with('items');   // комбинировать можно
```

> [!GOTCHA] Неоднозначные столбцы
> После `joinWith` у таблиц одинаковые имена столбцов (`id`, `status`) — квалифицируйте: `['customer.status' => 1]`, а в `select()` перечисляйте с префиксом таблицы. И помните: JOIN с `hasMany` даёт дубли строк основной таблицы — `count()` и `limit` считают их.

### Условия связи: onCondition, псевдонимы, inverseOf

```php
public function getActiveOrders()
{
    return $this->hasMany(Order::class, ['customer_id' => 'id'])
        ->onCondition(['status' => 1]);   // попадёт в ON при joinWith и в WHERE при ленивой загрузке
}

Customer::find()->joinWith(['orders o'])->where(['o.status' => 1]);   // псевдоним связанной таблицы (2.0.7)
Customer::find()->joinWith(['orders' => function ($q) { $q->alias('o'); }]);

public function getOrders()
{
    return $this->hasMany(Order::class, ['customer_id' => 'id'])->inverseOf('customer');
}
$orders = $customer->orders;
$orders[0]->customer === $customer;   // true — обратная связь без запроса
```

### Связи между разными БД

Возможны: `Customer` в MySQL, `Comment` в MongoDB — просто не используйте `joinWith`.

### Сохранение связей

```php
$customer = Customer::findOne(123);
$order = new Order(['subtotal' => 100]);
$order->link('customer', $customer);     // выставит customer_id и сохранит $order
$customer->link('orders', $order);       // то же с другой стороны

$order->link('items', $item);            // для via/viaTable — добавит строку в промежуточную таблицу
$order->unlink('items', $item, true);    // true — удалить строку промежуточной таблицы / связанную запись
```

Оба объекта должны быть сохранены до `link()`; `link()` сам вызывает `save(false)` — предварительно валидируйте.

## Собственный ActiveQuery

Общие условия выборки — в один класс:

```php
namespace app\models;

use yii\db\ActiveQuery;

class CommentQuery extends ActiveQuery
{
    public function active($state = true)
    {
        return $this->andWhere(['active' => $state]);
    }
}

class Comment extends ActiveRecord
{
    public static function find()
    {
        return new CommentQuery(get_called_class());
    }
}

Comment::find()->active()->all();
$customer->getComments()->active()->all();   // и в связях
Customer::find()->with(['comments' => function (CommentQuery $q) { $q->active(); }])->all();
```

Условие «по умолчанию» для всех запросов — переопределить `init()` запроса или `where()`… но осторожно: `updateAll()`/`deleteAll()` через него не проходят.

## Дополнительные поля из запроса

```php
class Room extends ActiveRecord
{
    public $volume;      // НЕ столбец таблицы — заполнится из псевдонима в SELECT
}

$rooms = Room::find()
    ->select(['{{room}}.*', '([[length]] * [[width]] * [[height]]) AS volume'])
    ->where(['>', 'volume', 10])        // по вычисленному столбцу можно фильтровать и сортировать
    ->orderBy('volume DESC')
    ->all();
```

Заполняются публичные свойства, которых **нет** среди столбцов таблицы. Объявлять так
существующий столбец бессмысленно: его значение уйдёт в атрибуты, а одноимённое
свойство останется пустым — и вычисление по нему даст ноль. Так же добавляют агрегаты по связям: `->select(['customer.*', 'ordersCount' => 'COUNT(o.id)'])->joinWith('orders o', false)->groupBy('customer.id')`.

:::quiz Проверь себя
Q: Что означает `['customer_id' => 'id']` в `$this->hasMany(Order::class, ['customer_id' => 'id'])`?
A: Столбец `customer_id` таблицы `Order` (связанный класс) равен столбцу `id` текущей модели `Customer`.
Q: Чем `with()` отличается от `joinWith()`?
A: `with()` делает отдельный запрос для связи (без JOIN) и не позволяет фильтровать по её столбцам; `joinWith()` добавляет JOIN и позволяет `where` по связанной таблице.
Q: Почему `save()` вернул `false`, но исключения нет?
A: Не прошла валидация: сохранение отменено, ошибки в `$model->errors`.
Q: Обновит ли `Customer::updateAll(['status' => 1])` поле `updated_at` через `TimestampBehavior`?
A: Нет — массовые операции не создают объекты и не вызывают события и поведения.
Q: Что такое «грязные» атрибуты?
A: Атрибуты, изменённые после загрузки; только они попадают в `UPDATE`. Если изменений нет, `save()` не выполняет запрос.
Q: Для чего `optimisticLock()`?
A: Защита от перезаписи чужих правок: при несовпадении версии `save()` бросит `StaleObjectException`.
:::
