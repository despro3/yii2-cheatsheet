---
id: query-builder
title: Query Builder
part: db
summary: Построение SQL-запросов методами yii\db\Query — select/from/where/join/orderBy/limit, форматы условий (строка, хеш, оператор, объект), filterWhere, агрегаты, пакетная выборка batch/each, подзапросы и Expression.
sources: db-query-builder
---

:::lead
`yii\db\Query` собирает запрос объектно и независимо от СУБД: вы описываете *что* нужно, а построитель сам экранирует имена, привязывает параметры и генерирует SQL под конкретную базу. Тот же API используют `ActiveQuery` и Active Record, так что выучить его придётся один раз.
:::

## Скелет запроса

```php
use yii\db\Query;

$rows = (new Query())
    ->select(['id', 'email'])
    ->from('user')
    ->where(['status' => 1])
    ->orderBy('id')
    ->limit(10)
    ->all();                 // массив строк; ->all($db2) — через другое соединение

// посмотреть, что получилось
$sql = (new Query())->from('user')->createCommand()->getRawSql();
```

Методы построения возвращают `$this` — цепочка в любом порядке. Выполнение: `all()`, `one()`, `column()`, `scalar()`, `exists()`, `count()`, `sum('col')`, `average()`, `max()`, `min()`.

## SELECT и FROM

```php
$query->select('id, email');                              // строка — в простых случаях
$query->select(['id', 'email']);                          // массив — безопаснее, всё экранируется
$query->select(['user_id' => 'user.id', 'email']);        // псевдоним столбца
$query->select(['user.id AS user_id', 'email']);          // так тоже можно
$query->select(["CONCAT(first_name, ' ', last_name) AS full_name", 'email']);   // выражения не экранируются
$query->select(['id', 'count' => $subQuery]);             // подзапрос как столбец
$query->select('user_id')->distinct();                    // DISTINCT
$query->addSelect(['email']);                             // добавить к выбранным

$query->from('user');
$query->from(['public.user u', 'public.post p']);          // несколько таблиц с псевдонимами
$query->from(['u' => 'public.user', 'p' => 'public.post']);
$query->from(['u' => $subQuery]);                         // подзапрос в FROM
```

Если `select()` не вызван, будет `SELECT *`.

## WHERE — три формата условий

### Строковый

```php
$query->where('status=1');
$query->where('status=:status', [':status' => $status]);          // параметры обязательно через плейсхолдеры
$query->where('YEAR(somedate) = 2015');
$query->where('status=:status')->addParams([':status' => $status]);
```

### Хеш — «столбец → значение»

```php
$query->where([
    'status' => 10,
    'type' => null,               // → type IS NULL
    'id' => [4, 8, 15],           // → id IN (4, 8, 15)
]);
$query->where(['id' => $userQuery]);   // → id IN (SELECT id FROM user WHERE …)
```

Все значения привязываются параметрами. Нужен именно этот формат, когда данные пришли от пользователя.

### Операторный — `[оператор, операнд1, операнд2, …]`

| Оператор | Пример | SQL |
|---|---|---|
| `and`, `or` | `['and', 'id=1', 'id=2']` | `id=1 AND id=2` |
| `not` | `['not', ['status' => 1]]` | `NOT (status=1)` |
| `between`, `not between` | `['between', 'id', 1, 10]` | `id BETWEEN 1 AND 10` |
| `in`, `not in` | `['in', 'id', [1, 2, 3]]` | `id IN (1, 2, 3)` |
| `in` по составному ключу | `['in', ['id', 'name'], [['id' => 1, 'name' => 'a']]]` | `(id, name) IN ((1, 'a'))` |
| `like`, `not like` | `['like', 'name', 'tester']` | `name LIKE '%tester%'` |
| `like` c массивом | `['like', 'name', ['test', 'sample']]` | `name LIKE '%test%' AND name LIKE '%sample%'` |
| `like` без `%` | `['like', 'name', '%tester', false]` | `name LIKE '%tester'` (экранирование выключено) |
| `or like`, `or not like` | `['or like', 'name', ['a', 'b']]` | `name LIKE '%a%' OR name LIKE '%b%'` |
| `exists`, `not exists` | `['exists', $subQuery]` | `EXISTS (SELECT …)` |
| `>`, `<`, `=`, `!=`, `>=`, … | `['>=', 'id', 10]` | `id >= 10` |

Операнды `and`/`or` могут быть вложенными массивами любого формата:

```php
$query->where([
    'and',
    ['status' => 1],
    ['or', ['type' => 1], ['>', 'created_at', $ts]],
]);
```

### Объектный (с 2.0.14)

```php
use yii\db\conditions\{AndCondition, BetweenCondition, InCondition, LikeCondition};

$query->where(new AndCondition([
    new InCondition('id', 'in', [1, 2, 3]),
    new BetweenCondition('created_at', 'between', $from, $to),
]));
```

Каждому оператору соответствует класс в `yii\db\conditions\*`; они удобны для программной сборки и расширяемы через `QueryBuilder::conditionClasses`.

## Достраивание условий

```php
$query->where(['status' => 1])
      ->andWhere(['>', 'id', 100])      // AND (…)
      ->orWhere(['type' => 2]);         // OR (…)

// фильтр: пустые значения ('' , ' ', null, []) просто пропускаются
$query->filterWhere(['username' => $username, 'email' => $email]);
$query->andFilterWhere(['like', 'title', $search]);
$query->andFilterCompare('price', '>=100');   // разбирает оператор из строки: '>=100' → price >= 100
```

`filterWhere` — идеальный инструмент для поисковых форм: `WHERE username=:u` появится, только если поле заполнено.

## Остальные части

```php
$query->orderBy(['id' => SORT_ASC, 'name' => SORT_DESC]);   // или строка 'id ASC, name DESC'
$query->orderBy(new Expression('RAND()'));
$query->addOrderBy('created_at');

$query->groupBy(['id', 'status'])->addGroupBy('type');
$query->having(['status' => 1])->andHaving(['>', 'age', 30]);   // те же форматы, что у where
$query->filterHaving([...]);

$query->limit(10)->offset(20);   // отрицательные/null — без ограничения

$query->join('LEFT JOIN', 'post', 'post.user_id = user.id');
$query->leftJoin('post', 'post.user_id = user.id');
$query->innerJoin(['p' => $subQuery], 'p.user_id = user.id');   // rightJoin тоже есть

$query1->union($query2);              // UNION; union($q, true) — UNION ALL

// WITH posts AS (…) — общие табличные выражения (2.0.35)
$query->withQuery($cte, 'posts', $recursive = false);
```

## Выполнение и результат

```php
$rows  = $query->all();                     // все строки
$row   = $query->one();                     // первая строка или false; LIMIT 1 сам не добавляет
$col   = $query->column();                  // массив значений первого столбца
$value = $query->scalar();                  // первый столбец первой строки
$bool  = $query->exists();
$n     = $query->count();                   // SELECT COUNT(*) — с учётом where/join, без limit/orderBy
$sum   = $query->sum('amount'); $avg = $query->average('amount');   // max(), min()

// индексировать результат столбцом или замыканием
$users = $query->from('user')->indexBy('id')->all();                 // ['id' => row]
$users = $query->indexBy(function ($row) { return $row['id'] . $row['username']; })->all();
```

`count()` и другие агрегаты сохраняют условия исходного запроса, но игнорируют `orderBy`, `limit`, `offset` — это удобно для пагинации.

> [!GOTCHA]
> `one()` **не** добавляет `LIMIT 1` — запрос уходит в базу как есть, просто из результата берётся первая строка. На большой выборке это лишняя работа для БД, поэтому ставьте `limit(1)` сами. И если в `select()` указаны только выражения без имён столбцов, `indexBy` не найдёт ключ — давайте псевдонимы.

## Пакетная выборка

Миллион строк через `all()` не влезет в память. `batch()`/`each()` читают курсором порциями:

```php
$query = (new Query())->from('user')->orderBy('id');

foreach ($query->batch() as $users) {        // по 100 строк за итерацию
    // $users — массив из ≤100 строк
}

foreach ($query->each(500) as $user) {       // по одной строке, порция 500
    // $user — одна строка
}

// с indexBy ключи внутри порции сохраняются
foreach ($query->indexBy('username')->batch() as $users) { }
```

> [!WARNING] MySQL и буферизация
> В MySQL пакетная выборка работает по-настоящему только с небуферизованным соединением: `PDO::MYSQL_ATTR_USE_BUFFERED_QUERY => false`. Но пока такой курсор открыт, на этом соединении нельзя выполнять другие запросы — заведите второе `Connection` (например, `unbufferedDb`) специально для batch. Для PostgreSQL параметр `fetchMode`/лимит настраивать не нужно.

## Выражения и подзапросы

```php
use yii\db\Expression;

$query->select(['id', new Expression('NOW() AS now')]);
$query->where(new Expression('YEAR(created_at) = :y', [':y' => 2024]));
$query->where(['>', 'expires', new Expression('NOW()')]);

$sub = (new Query())->select('user_id')->from('post')->where(['status' => 1]);
// WHERE id IN (SELECT user_id FROM post WHERE status=1)
$q   = (new Query())->from('user')->where(['id' => $sub]);
```

`Expression` вставляется в SQL как есть — никогда не подставляйте в него пользовательские данные без параметров.

## Query как строитель для DAO

```php
$command = (new Query())->from('user')->where(['status' => 1])->createCommand();
echo $command->sql;         // SELECT * FROM `user` WHERE `status`=:qp0
$command->params;           // [':qp0' => 1]
$rows = $command->queryAll();
```

Так можно применить построитель, но выполнить запрос вручную — например, через другое соединение или с дополнительной обработкой.

:::quiz Проверь себя
Q: Какой формат `where()` выбрать, если значения пришли из формы поиска?
A: Хеш или операторный формат с `filterWhere()`: значения привязываются параметрами, а пустые поля игнорируются.
Q: Что вернёт `['id' => [4, 8, 15]]` внутри `where()`?
A: `id IN (4, 8, 15)`; `null` в значении даст `IS NULL`.
Q: Чем `andFilterWhere()` отличается от `andWhere()`?
A: `andFilterWhere()` пропускает условия с пустыми значениями (`''`, `' '`, `null`, `[]`), `andWhere()` добавляет всегда.
Q: Как выбрать миллион строк, не исчерпав память?
A: `foreach ($query->batch(1000) as $rows)` или `each()`; в MySQL — с небуферизованным соединением.
Q: Учитывает ли `count()` вызванный ранее `limit(10)`?
A: Нет — агрегаты игнорируют `limit`, `offset` и `orderBy`, но сохраняют `where`, `join`, `groupBy`.
:::
