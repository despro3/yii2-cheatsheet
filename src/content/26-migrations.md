---
id: migrations
title: Миграции
part: db
summary: Версионирование схемы БД — создание миграции, up/down и safeUp/safeDown, генерация по шаблонам (create_table, add_column, junction), методы Migration, команды migrate/up|down|redo|fresh|mark|history|new, несколько БД и пространства имён.
sources: db-migrations
---

:::lead
Миграция — PHP-класс с методами «применить» и «откатить», который меняет структуру или данные БД. Файлы лежат в репозитории, применяются командой `./yii migrate`, а таблица `migration` помнит, что уже выполнено. Так схема эволюционирует синхронно с кодом на всех машинах команды и серверах.
:::

## Создать миграцию

```bash
./yii migrate/create create_news_table
# → migrations/m150101_185401_create_news_table.php
```

Имя файла `m<YYMMDD_HHMMSS>_<имя>` — порядок применения определяется временной меткой.

```php title="migrations/m150101_185401_create_news_table.php"
use yii\db\Migration;

class m150101_185401_create_news_table extends Migration
{
    public function up()
    {
        $this->createTable('news', [
            'id' => $this->primaryKey(),
            'title' => $this->string()->notNull(),
            'content' => $this->text(),
            'created_at' => $this->integer()->notNull()->defaultValue(0),
        ]);
        $this->createIndex('idx-news-title', 'news', 'title');
    }

    public function down()
    {
        $this->dropTable('news');
        // return false;   // если откат невозможен
    }
}
```

### up/down или safeUp/safeDown

`safeUp()`/`safeDown()` оборачивают всё в транзакцию: исключение — и всё откатывается. Используйте их по умолчанию; `up()`/`down()` — только если СУБД не умеет транзакционный DDL (MySQL коммитит неявно на каждый `CREATE TABLE`, так что там разницы почти нет).

## Строитель типов столбцов

Вместо строк `'string NOT NULL'` — переносимые методы `yii\db\SchemaBuilderTrait`:

```php
'id'         => $this->primaryKey(),          // pk: INT AUTO_INCREMENT PRIMARY KEY (bigPrimaryKey())
'title'      => $this->string(255)->notNull()->unique(),
'content'    => $this->text(),
'price'      => $this->decimal(10, 2)->defaultValue(0),
'is_active'  => $this->boolean()->defaultValue(true),
'created_at' => $this->timestamp()->defaultExpression('CURRENT_TIMESTAMP'),
'status'     => $this->smallInteger()->notNull()->defaultValue(1)->comment('статус'),
'user_id'    => $this->integer()->notNull()->after('id'),   // after()/first() — только MySQL
// также: char, float, double, money, date, time, dateTime, binary, tinyInteger, json (2.0.14)
```

Строковые типы тоже работают: `'string NOT NULL'`, `'pk'`, `'bigpk'`, `'text'` — конвертируются под СУБД.

## Методы Migration

:::kv
`createTable($table, $columns, $options)` / `dropTable` / `renameTable` / `truncateTable` — таблицы; `$options` — например `'ENGINE=InnoDB'` для MySQL
`addColumn` / `dropColumn` / `renameColumn` / `alterColumn` — столбцы
`addPrimaryKey` / `dropPrimaryKey` — первичные ключи
`addForeignKey($name, $table, $columns, $refTable, $refColumns, $delete, $update)` / `dropForeignKey` — внешние ключи (`'CASCADE'`, `'SET NULL'`, `'RESTRICT'`)
`createIndex($name, $table, $columns, $unique = false)` / `dropIndex` — индексы
`addCommentOnColumn` / `addCommentOnTable` / `dropCommentFrom…` — комментарии
`insert` / `batchInsert` / `update` / `delete` / `upsert` — данные
`execute($sql, $params)` — произвольный SQL
:::

Все они выводят время выполнения и работают через `$this->db`. Обычные `Yii::$app->db->createCommand()` тоже доступны, но прогресса не покажут.

```php
$this->createTable('{{%post}}', [...]);        // {{%…}} — с префиксом таблиц
$this->addForeignKey('fk-post-author_id', '{{%post}}', 'author_id', '{{%user}}', 'id', 'CASCADE');
$this->insert('{{%category}}', ['name' => 'Общее']);
```

## Генерация по имени

Команда `migrate/create` понимает шаблоны имён и заполняет тело за вас:

```bash
./yii migrate/create create_post_table                       # createTable + dropTable
./yii migrate/create create_post_table --fields="title:string(12):notNull:unique,body:text"
./yii migrate/create create_post_table --fields="author_id:integer:notNull:foreignKey(user),category_id:integer:defaultValue(1):foreignKey"
./yii migrate/create drop_post_table --fields="title:string(12):notNull"    # dropTable + createTable в down
./yii migrate/create add_position_column_to_post_table --fields="position:integer"
./yii migrate/create drop_position_column_from_post_table --fields="position:integer"
./yii migrate/create create_junction_table_for_post_and_tag_tables   # post_tag(post_id, tag_id) + PK + FK
```

Поле `id:primaryKey` добавляется автоматически, если не задано. `foreignKey(user)` создаст индекс и внешний ключ на `user.id`. Формат `--fields`: `имя:тип(args):модификатор(args):…`.

## Применить и откатить

```bash
./yii migrate                    # применить все новые (спросит подтверждение)
./yii migrate 3                  # только 3 следующие
./yii migrate/to 150101_185401   # до указанной (или m150101_185401_create_news_table, или timestamp, или 'yyyy-mm-dd hh:mm:ss')
./yii migrate/down               # откатить последнюю
./yii migrate/down 3             # три последние; migrate/down all — все
./yii migrate/redo               # откатить и снова применить последнюю (redo 3, redo all)
./yii migrate/fresh              # ⚠ удалить все таблицы и применить всё с нуля — только dev
./yii migrate/history            # что применено (history 5 / history all)
./yii migrate/new                # что ещё не применено
./yii migrate/mark 150101_185401 # пометить как применённую без выполнения (mark m000000_000000_base — сбросить всё)
./yii migrate --interactive=0    # без вопросов — для CI
```

## Настройка

```bash
./yii migrate --migrationPath=@app/modules/forum/migrations
./yii migrate --migrationTable=my_migrations
./yii migrate --db=db2                                   # другое соединение
./yii migrate --migrationPath=@yii/rbac/migrations        # миграции расширений (RBAC, i18n, queue…)
```

Постоянно — в консольной конфигурации:

```php title="config/console.php"
'controllerMap' => [
    'migrate' => [
        'class' => 'yii\console\controllers\MigrateController',
        'migrationPath' => null,                 // отключить старый механизм
        'migrationNamespaces' => [               // миграции с пространствами имён (2.0.10)
            'app\migrations',
            'some\extension\migrations',
        ],
        // 'migrationPath' => ['@app/migrations', '@app/modules/forum/migrations'],   // или несколько путей
    ],
],
```

Именованная миграция создаётся `./yii migrate/create app\\migrations\\CreateUserTable` → класс `M150101185401CreateUserTable` в папке псевдонима `@app/migrations`.

### Несколько БД

Либо своя команда с `--db`, либо переопределить `getDb()` в миграции. Разложить по папкам (`migrations/db1`, `migrations/db2`) и запускать с разными `--migrationPath`.

> [!WARNING] Данные — тоже миграции
> Справочники, роли RBAC, начальные записи тоже стоит заносить миграциями (`$this->insert()`), чтобы окружения были воспроизводимы. А вот большие импорты — нет: делайте их отдельными консольными командами.

## Быстрый рецепт

:::steps
1. `./yii migrate/create create_post_table --fields="title:string:notNull,body:text,author_id:integer:notNull:foreignKey(user)"`
2. Проверить сгенерированный файл, поправить типы, добавить индексы.
3. `./yii migrate` локально; закоммитить файл миграции.
4. На сервере после деплоя: `./yii migrate --interactive=0`.
5. Ошибка после деплоя — `./yii migrate/down` вернёт схему назад.
:::

:::quiz Проверь себя
Q: Чем `safeUp()` отличается от `up()`?
A: `safeUp()` выполняется внутри транзакции — при исключении всё откатывается (если СУБД поддерживает транзакционный DDL).
Q: Что произойдёт при `./yii migrate`, если миграция уже применена?
A: Ничего: применённые миграции помнит таблица `migration`, выполняются только новые.
Q: Как сгенерировать миграцию с готовыми полями и внешним ключом?
A: `./yii migrate/create create_post_table --fields="author_id:integer:notNull:foreignKey(user)"`.
Q: Как применить миграции расширения, например RBAC?
A: `./yii migrate --migrationPath=@yii/rbac/migrations` или добавить путь/пространство имён в конфигурацию `controllerMap`.
Q: Когда `down()` должен вернуть `false`?
A: Когда откат невозможен (например, данные уничтожены); тогда `migrate/down` остановится с сообщением.
:::
