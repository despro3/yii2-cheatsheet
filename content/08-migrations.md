---
id: migrations
title: Миграции
icon: 📐
summary: Создание, применение и откат миграций, генераторы, типы столбцов, несколько БД.
sources: db-migrations
---

# Миграции баз данных

Миграция — PHP-класс с методами `up()`/`down()` (или транзакционными `safeUp()`/`safeDown()`),
лежащий в системе контроля версий рядом с кодом. Применённые миграции регистрируются в
таблице `migration`.

## Команды

```bash
yii migrate/create create_news_table     # создать миграцию
yii migrate                              # применить все новые
yii migrate 3                            # применить 3 следующие
yii migrate/to 150101_185401             # применить/откатить до конкретной миграции
yii migrate/down                         # откатить последнюю
yii migrate/down 3                       # откатить 3 последние
yii migrate/redo                         # откатить и применить заново
yii migrate/history all                  # применённые миграции
yii migrate/new all                      # ещё не применённые
yii migrate/mark 150101_185401           # отметить применённой, ничего не выполняя
yii migrate/fresh                        # очистить БД и применить всё заново (не для прода!)
yii help migrate
```

Опции: `--interactive=0` (для CI), `--migrationPath=@app/migrations`,
`--migrationTable=migration`, `--db=db2`, `--templateFile=...`.

## Анатомия миграции

```php
use yii\db\Migration;

class m150101_185401_create_news_table extends Migration
{
    public function safeUp()        // safeUp/safeDown выполняются в транзакции
    {
        $this->createTable('{{%news}}', [
            'id' => $this->primaryKey(),
            'title' => $this->string(255)->notNull(),
            'content' => $this->text(),
            'author_id' => $this->integer()->notNull(),
            'status' => $this->smallInteger()->defaultValue(1),
            'created_at' => $this->integer()->notNull(),
        ], $this->db->driverName === 'mysql' ? 'ENGINE=InnoDB DEFAULT CHARSET=utf8mb4' : null);

        $this->createIndex('idx-news-author_id', '{{%news}}', 'author_id');
        $this->addForeignKey('fk-news-author_id', '{{%news}}', 'author_id', '{{%user}}', 'id', 'CASCADE');
        $this->insert('{{%news}}', ['title' => 'Первая новость', 'created_at' => time()]);
    }

    public function safeDown()      // обратный порядок операций
    {
        $this->dropForeignKey('fk-news-author_id', '{{%news}}');
        $this->dropTable('{{%news}}');
    }
}
```

Если миграция необратима — верните `false` в `down()`.

### Методы миграции

`execute`, `insert`, `batchInsert`, `upsert`, `update`, `delete`, `createTable`,
`renameTable`, `dropTable`, `truncateTable`, `addColumn`, `renameColumn`, `alterColumn`,
`dropColumn`, `addPrimaryKey`, `dropPrimaryKey`, `addForeignKey`, `dropForeignKey`,
`createIndex`, `dropIndex`, `addCommentOnTable`, `addCommentOnColumn`.
Соединение доступно как `$this->db`.

### Типы столбцов (SchemaBuilderTrait)

```php
$this->primaryKey()        $this->bigPrimaryKey()
$this->string(64)          $this->text()          $this->char(2)
$this->integer()           $this->bigInteger()    $this->smallInteger()  $this->tinyInteger()
$this->decimal(10, 2)      $this->float()         $this->double()        $this->money()
$this->boolean()           $this->binary()        $this->json()
$this->date()              $this->time()          $this->dateTime()      $this->timestamp()

// модификаторы — цепочкой
$this->string(12)->notNull()->unique()->defaultValue('x')->comment('Комментарий')->after('id')
```

Абстрактные типы вместо `varchar(255)` делают миграцию независимой от СУБД. Старый стиль
через константы `yii\db\Schema::TYPE_PK`, `TYPE_STRING` тоже работает.

## Генераторы миграций

Имя миграции задаёт содержимое: `create_xxx_table`, `drop_xxx_table`,
`add_xxx_column_to_yyy_table`, `drop_xxx_column_from_yyy_table`,
`create_junction_table_for_xxx_and_yyy_tables`.

```bash
yii migrate/create create_post_table --fields="title:string(12):notNull:unique,body:text"

yii migrate/create create_post_table \
  --fields="author_id:integer:notNull:foreignKey(user),category_id:integer:foreignKey,title:string,body:text"

yii migrate/create add_position_column_to_post_table --fields=position:integer
yii migrate/create create_junction_table_for_post_and_tag_tables
```

Первичный ключ `id` добавляется сам (`--fields=name:primaryKey` меняет имя). Ключевое
слово `foreignKey(таблица)` создаёт индекс + внешний ключ с `CASCADE`; его позиция в
описании поля не важна.

## Несколько БД и отдельные пути миграций

```php
// config/console.php
'controllerMap' => [
    'migrate' => [
        'class' => 'yii\console\controllers\MigrateController',
        'migrationPath' => null,                      // отключить путь по умолчанию
        'migrationNamespaces' => [
            'app\migrations',
            'module\migrations',
            'some\extension\migrations',
        ],
        'migrationTable' => '{{%migration}}',
    ],
],
```

```bash
yii migrate --db=db2                              # мигрировать другую базу
yii migrate --migrationPath=@app/migrations/shop  # отдельный набор миграций
```

> Важно: не используйте в миграциях классы Active Record. Бизнес-логика меняется, а
> миграция должна выполняться одинаково всегда — работайте через `$this->insert()`,
> `$this->update()` и Query Builder.

> Совет: миграции годятся не только для схемы — ими удобно заполнять справочники,
> строить иерархию RBAC и чистить кеш после изменения структуры.
