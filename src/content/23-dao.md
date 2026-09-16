---
id: dao
title: DAO — работа с SQL
part: db
summary: Подключение к БД, выполнение запросов с привязкой параметров, insert/update/delete/batchInsert, экранирование имён и префиксы таблиц, транзакции, репликация master/slave, работа со схемой.
sources: db-dao
---

:::lead
DAO (Data Access Objects) — тонкий объектный слой над PDO: `Connection` → `createCommand($sql)` → `queryAll()`/`execute()`. Самый быстрый способ работать с БД, на нём построены [Query Builder](query-builder) и [Active Record](active-record). Поддерживаются MySQL/MariaDB, PostgreSQL, SQLite, MSSQL, Oracle, CUBRID.
:::

## Подключение

```php title="config/db.php"
return [
    'class' => 'yii\db\Connection',
    'dsn' => 'mysql:host=localhost;dbname=example',
    'username' => 'root',
    'password' => '',
    'charset' => 'utf8mb4',
    // 'tablePrefix' => 'tbl_',
    // 'enableSchemaCache' => true, 'schemaCacheDuration' => 3600,   // см. Производительность
    'on afterOpen' => function ($event) {
        $event->sender->createCommand("SET time_zone = '+00:00'")->execute();   // инициализация сессии
    },
];
```

| СУБД | DSN |
|---|---|
| MySQL, MariaDB | `mysql:host=localhost;dbname=mydb` |
| PostgreSQL | `pgsql:host=localhost;port=5432;dbname=mydb` |
| SQLite | `sqlite:/path/to/database.sqlite` |
| MS SQL Server | `sqlsrv:Server=localhost;Database=mydb` (или `dblib:`, `mssql:`) |
| Oracle | `oci:dbname=//localhost:1521/mydb` |
| через ODBC | `odbc:Driver={MySQL};Server=…` + `'driverName' => 'mysql'` |

Реальное соединение открывается лениво — при первом запросе или `open()`. Компонентов может быть несколько (`db`, `db2`).

## Запросы

```php
$db = Yii::$app->db;

$posts  = $db->createCommand('SELECT * FROM post')->queryAll();            // массив строк (ассоц. массивы)
$post   = $db->createCommand('SELECT * FROM post WHERE id=1')->queryOne(); // одна строка или false
$titles = $db->createCommand('SELECT title FROM post')->queryColumn();     // первый столбец
$count  = $db->createCommand('SELECT COUNT(*) FROM post')->queryScalar();  // одно значение или false

$db->createCommand('UPDATE post SET status=1 WHERE id=1')->execute();       // число затронутых строк
```

Значения приходят **строками**, даже из числовых столбцов — так PDO сохраняет точность.

### Привязка параметров

Единственно правильный способ подставлять данные в SQL:

```php
$post = $db->createCommand('SELECT * FROM post WHERE id=:id AND status=:status')
    ->bindValue(':id', $id)
    ->bindValue(':status', 1)
    ->queryOne();

$post = $db->createCommand('SELECT * FROM post WHERE id=:id', [':id' => $id])->queryOne();   // сразу

// подготовленный запрос многократно
$command = $db->createCommand('SELECT * FROM post WHERE id=:id');
$post1 = $command->bindValue(':id', 1)->queryOne();
$post2 = $command->bindValue(':id', 2)->queryOne();

// по ссылке: значение читается в момент выполнения
$command = $db->createCommand('SELECT * FROM post WHERE id=:id')->bindParam(':id', $id);
$id = 1; $post1 = $command->queryOne();
$id = 2; $post2 = $command->queryOne();
```

> [!GOTCHA]
> `"SELECT * FROM user WHERE name = '$name'"` — это SQL-инъекция. Никакой конкатенации пользовательских данных: только плейсхолдеры `:name`. Имена таблиц и столбцов привязать нельзя — их проверяют по белому списку или экранируют `[[col]]`/`{{table}}`.

### INSERT, UPDATE, DELETE без SQL

```php
$db->createCommand()->insert('user', ['name' => 'Sam', 'age' => 30])->execute();
// один запрос
$db->createCommand()->batchInsert('user', ['name', 'age'], [['Tom', 30], ['Jane', 20]])->execute();
$db->createCommand()->update('user', ['status' => 1], 'age > 30')->execute();
// условие в формате массива
$db->createCommand()->update('user', ['status' => 1], ['id' => [1, 2, 3]])->execute();
$db->createCommand()->delete('user', 'status = 0')->execute();
// INSERT … ON DUPLICATE KEY UPDATE
$db->createCommand()->upsert('user', ['email' => 'a@b.c', 'name' => 'A'])->execute();
```

Эти методы только строят команду — `execute()` обязателен.

## Экранирование имён и префикс

```php
$count = $db->createCommand('SELECT COUNT([[id]]) FROM {{employee}}')->queryScalar();
// MySQL: SELECT COUNT(`id`) FROM `employee`;  PostgreSQL: "id", "employee"

// с tablePrefix = 'tbl_':
$db->createCommand('SELECT * FROM {{%employee}}');   // → `tbl_employee`
```

`[[столбец]]` и `{{таблица}}` работают во всех СУБД, `%` заменяется на `tablePrefix`.

## Транзакции

```php
$db->transaction(function ($db) {
    $db->createCommand($sql1)->execute();
    $db->createCommand($sql2)->execute();
});   // исключение внутри → rollback и проброс наружу

// то же с ручным контролем
$transaction = $db->beginTransaction();
try {
    $db->createCommand($sql1)->execute();
    $db->createCommand($sql2)->execute();
    $transaction->commit();
} catch (\Throwable $e) {
    $transaction->rollBack();
    throw $e;
}
```

Уровень изоляции — вторым аргументом `transaction()` / `beginTransaction()`: `Transaction::READ_UNCOMMITTED`, `READ_COMMITTED`, `REPEATABLE_READ`, `SERIALIZABLE` (или строка, понятная СУБД). Вложенные транзакции работают через savepoints, если СУБД их поддерживает. Ограничения: SQLite знает только два уровня, PostgreSQL меняет уровень уже после старта (`setIsolationLevel()`), MSSQL и SQLite задают уровень на всё соединение.

## Репликация: чтение с реплик, запись в мастер

```php
'db' => [
    'class' => 'yii\db\Connection',
    'dsn' => 'dsn мастера', 'username' => 'master', 'password' => '',
    'slaveConfig' => [
        'username' => 'slave', 'password' => '',
        'attributes' => [PDO::ATTR_TIMEOUT => 10],   // «мёртвая» реплика определяется по таймауту
    ],
    'slaves' => [
        ['dsn' => 'dsn реплики 1'],
        ['dsn' => 'dsn реплики 2'],
    ],
    // несколько мастеров: 'masterConfig' + 'masters' => [...] (тогда dsn/username выше игнорируются)
],
```

Дальше всё автоматически: `query*()` идут на случайную живую реплику, `execute()` — на мастер, транзакции — на мастер. Недоступные серверы запоминаются в `serverStatusCache` на `serverRetryInterval` секунд.

```php
$db->useMaster(function ($db) {                     // прочитать именно с мастера
    return $db->createCommand('SELECT …')->queryAll();
});
$db->enableSlaves = false;                          // всё на мастер
$transaction = $db->slave->beginTransaction();      // транзакция на реплике (редко)
```

## Схема базы данных

```php
$db->createCommand()->createTable('post', [
    'id' => 'pk',
    'title' => 'string NOT NULL',
    'text' => 'text',
])->execute();
// также: renameTable, dropTable, truncateTable, addColumn, renameColumn, dropColumn, alterColumn,
// addPrimaryKey, dropPrimaryKey, addForeignKey, dropForeignKey, createIndex, dropIndex

$table = $db->getTableSchema('post');   // TableSchema: columns, primaryKey, foreignKeys
$db->schema->getTableNames();
```

Эти же методы, но с выводом прогресса, есть у [миграций](migrations) — там им и место.

:::quiz Проверь себя
Q: Почему `queryScalar()` для `COUNT(*)` возвращает строку `'5'`, а не число?
A: PDO отдаёт все значения строками ради точности; приводите тип сами или используйте Active Record, который приводит по схеме.
Q: Как безопасно подставить имя столбца, пришедшее от пользователя, в ORDER BY?
A: Привязать параметром нельзя; проверьте значение по белому списку допустимых столбцов и оберните в `[[...]]`.
Q: Что произойдёт с транзакцией, если в замыкании `transaction()` выброшено исключение?
A: Будет выполнен `rollBack()`, а исключение проброшено дальше.
Q: Куда уйдёт `SELECT` внутри транзакции при настроенной репликации?
A: На мастер: в рамках транзакции все запросы используют соединение с мастером.
Q: Что означает `{{%post}}`?
A: Имя таблицы `post` с автоматической подстановкой `tablePrefix` и экранированием под текущую СУБД.
:::
