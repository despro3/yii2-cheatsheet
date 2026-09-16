---
id: caching
title: Кэширование данных
part: caching
summary: Компонент cache и его хранилища (File, Apcu, Memcached, Redis, Db, Array, Dummy), API get/set/add/delete/getOrSet, множественные операции, зависимости (Tag, File, Expression, Db, Chained), кэширование запросов к БД (cache()/noCache()), ключи и префиксы.
sources: caching-overview, caching-data
---

:::lead
Кэширование в Yii — четыре уровня: **данные** (любое значение по ключу), **фрагменты** страниц, **страницы** целиком и **HTTP-кэш** на стороне клиента. Все они опираются на компонент `cache` с единым API, поэтому хранилище можно сменить конфигурацией — код не изменится.
:::

## Хранилища

```php
'components' => [
    'cache' => [
        'class' => 'yii\caching\FileCache',                 // файлы в @runtime/cache
        // APCu — быстрее всего, но локально и в памяти процесса
        // 'class' => 'yii\caching\ApcCache',
        // 'class' => 'yii\caching\MemCache', 'servers' => [['host' => 'server1', 'port' => 11211, 'weight' => 100]],
        // 'class' => 'yii\redis\Cache',                    // расширение yii2-redis
        // 'class' => 'yii\caching\DbCache', 'cacheTable' => 'cache',   // таблица в БД
        // 'class' => 'yii\caching\ArrayCache',             // на время запроса (тесты, dev)
        // 'class' => 'yii\caching\DummyCache',             // заглушка: код с кэшем работает, но не кэширует
        'keyPrefix' => 'myapp',                             // разделить приложения на одном сервере
        'defaultDuration' => 3600,
        // 'serializer' => false,                           // для хранилищ с собственной сериализацией
    ],
],
```

| Класс | Где хранит | Когда |
|---|---|---|
| `FileCache` | файлы | по умолчанию; один сервер |
| `ApcCache` | APCu, память PHP | самый быстрый; сбрасывается при рестарте; не для CLI |
| `MemCache` | memcached | несколько серверов |
| `yii\redis\Cache` | Redis | несколько серверов, персистентность |
| `DbCache` | таблица БД | когда нет ничего другого |
| `ArrayCache` | массив | внутри одного запроса |
| `DummyCache` | нигде | отключить кэш, не меняя код |
| `WinCache`, `XCache`, `ZendDataCache` | устаревшие | — |

Можно объявить несколько компонентов (`cache`, `apcCache`) — быстрый для мелкого, распределённый для общего.

## API

```php
$cache = Yii::$app->cache;

$cache->set($key, $data, $duration, $dependency);   // записать; duration 0 — навсегда
$cache->get($key);                                  // значение или false
$cache->exists($key);
$cache->add($key, $data);                           // только если ключа ещё нет
$cache->delete($key);
$cache->flush();                                    // всё

// «получить или вычислить и сохранить» — самый частый паттерн
$data = $cache->getOrSet($key, function () {
    return Post::find()->where(['status' => 1])->all();
}, 3600, $dependency);

// несколько ключей
$cache->multiSet(['k1' => 'v1', 'k2' => 'v2'], 600);
$cache->multiGet(['k1', 'k2']);
$cache->multiAdd([...]);
```

Хранить можно любое сериализуемое значение (объекты, массивы). `false` кэшировать не стоит — неотличимо от промаха; оборачивайте в массив.

### Ключи

Ключ — строка или массив (сериализуется и хэшируется):

```php
$key = [__CLASS__, 'posts', $userId, $page];    // безопасно и читаемо
$cache->set($key, $data);
```

`keyPrefix` добавляется автоматически, чтобы несколько приложений не мешали друг другу в одном memcached/Redis.

## Зависимости

Кэш инвалидируется не только по времени, но и по условию:

```php
use yii\caching\{TagDependency, FileDependency, DbDependency, ExpressionDependency, ChainedDependency};

// по тегу — самый гибкий способ
$cache->set('posts', $posts, 0, new TagDependency(['tags' => ['posts', 'homepage']]));
TagDependency::invalidate($cache, 'posts');          // сбросить всё с этим тегом (например, в afterSave поста)

// по файлу: изменился mtime — кэш устарел
new FileDependency(['fileName' => 'example.txt']);

// по результату SQL
new DbDependency(['sql' => 'SELECT MAX(updated_at) FROM post']);

// по PHP-выражению
new ExpressionDependency(['expression' => 'Yii::$app->language']);

// несколько сразу
new ChainedDependency(['dependencies' => [$dep1, $dep2]]);
```

При `get()` зависимость пересчитывается; если изменилась — запись считается отсутствующей. `reusable => true` у зависимости позволяет пересчитать её один раз за запрос.

## Кэширование запросов к БД

```php
$db = Yii::$app->db;
$duration = 60;
$dependency = new DbDependency(['sql' => 'SELECT MAX(updated_at) FROM customer']);

$result = $db->cache(function ($db) use ($dependency) {
    return $db->createCommand('SELECT * FROM customer WHERE id=1')->queryOne();   // будет закэширован
}, $duration, $dependency);

// исключить часть запросов внутри cache()
$result = $db->cache(function ($db) {
    $r1 = …;                                    // кэшируется
    $db->noCache(function ($db) { … });        // нет
    return $r1;
});

// один запрос AR / Query
$customers = Customer::find()->where(['status' => 1])->cache(60, $dependency)->all();
$rows = (new Query())->from('user')->cache(120)->all();

// для DAO-команды
$db->createCommand($sql)->cache($duration)->queryAll();
```

Настройки соединения: `enableQueryCache` (по умолчанию `true`), `queryCacheDuration` (3600), `queryCache` (ID компонента кэша). Кэш работает для `query*()`, но не для `execute()`, и не для ресурсов (курсоры). Кэшируется результат по SQL + параметрам, поэтому одинаковые запросы дают попадание.

> [!TIP] Кэш схемы
> Отдельно от данных: `enableSchemaCache => true`, `schemaCacheDuration => 3600` в `db` — чтобы Active Record не читал структуру таблиц на каждом запросе. Один из первых шагов [оптимизации](performance). После миграций — `./yii cache/flush-schema`.

## Консольные команды

```bash
./yii cache                 # список компонентов кэша
./yii cache/flush cache     # очистить указанный
./yii cache/flush-all
./yii cache/flush-schema    # кэш схемы БД
```

Внимание: команды видят компоненты из консольной конфигурации; `ApcCache` из CLI не очистить — память веб-процессов другая.

## Где что кэшировать

:::kv
Результаты тяжёлых выборок, агрегаты, меню, справочники — `getOrSet()` с `TagDependency`, сброс в `afterSave()`/`afterDelete()` модели
Ответы внешних API — `set()` с коротким `duration`
Запросы AR в списках — `->cache()` на запросе
Схема таблиц — `enableSchemaCache`
Сессии, RBAC-иерархия (`authManager.cache`), URL-правила (`urlManager.cache`) — те же компоненты кэша
:::

:::quiz Проверь себя
Q: Что вернёт `Yii::$app->cache->get($key)` при промахе?
A: `false` — поэтому не кэшируйте само значение `false`, а оборачивайте в массив.
Q: Как сбросить кэш всех списков постов после сохранения одного поста?
A: Записывать с `TagDependency(['tags' => 'posts'])` и вызывать `TagDependency::invalidate(Yii::$app->cache, 'posts')` в `afterSave()`.
Q: Как закэшировать результат одного AR-запроса на минуту?
A: `Post::find()->where(…)->cache(60)->all()`.
Q: Зачем `keyPrefix`?
A: Чтобы несколько приложений в одном memcached/Redis/APCu не перезаписывали ключи друг друга.
Q: Чем `DummyCache` полезен?
A: Позволяет писать код с кэшем как обычно, но реально ничего не хранить — например, в dev или тестах.
:::
