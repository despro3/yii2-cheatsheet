---
id: caching
title: Кеширование
icon: ⚡
summary: Кеш данных, зависимости, кеш запросов, фрагменты, страницы, HTTP-кеш.
sources: caching-overview, caching-data, caching-fragment, caching-page, caching-http
---

# Кеширование

Четыре уровня: данные → запросы → фрагменты → страница, плюс HTTP-кеш на стороне клиента.

## Кеш данных

```php
$cache = Yii::$app->cache;

// классический паттерн
$data = $cache->get($key);
if ($data === false) {
    $data = $this->calculate();
    $cache->set($key, $data, 3600);
}

// то же самое одной строкой (с 2.0.11)
$data = $cache->getOrSet($key, fn () => $this->calculate(), 3600, $dependency);
```

| Метод | Действие |
|---|---|
| `get($key)` | значение или `false` |
| `set($key, $value, $duration, $dependency)` | записать |
| `add()` | записать, только если ключа ещё нет |
| `getOrSet($key, $callable, $duration, $dependency)` | получить или вычислить и запомнить |
| `multiGet()`, `multiSet()`, `multiAdd()` | пакетные операции |
| `exists()`, `delete()`, `flush()` | проверка, удаление, полная очистка |

`Cache` реализует `ArrayAccess`: `$cache['key'] = $value`.

> Важно: не кешируйте само значение `false` — `get()` использует его как признак промаха.
> Оборачивайте в массив.

### Хранилища

| Класс | Особенности |
|---|---|
| `yii\caching\FileCache` | файлы; хорош для больших объёмов, работает везде |
| `yii\caching\ApcCache` | APCu, самый быстрый на одном сервере |
| `yii\caching\MemCache` | memcache/memcached, для нескольких серверов |
| `yii\redis\Cache` | Redis (расширение `yii2-redis`) |
| `yii\caching\DbCache` | таблица в БД |
| `yii\caching\ArrayCache` | только в пределах запроса |
| `yii\caching\DummyCache` | заглушка: код с кешем работает без кеша |

```php
'components' => [
    'cache' => [
        'class' => 'yii\caching\MemCache',
        'keyPrefix' => 'myapp',          // если хранилище общее для нескольких приложений
        'defaultDuration' => 3600,
        'servers' => [
            ['host' => 'server1', 'port' => 11211, 'weight' => 100],
            ['host' => 'server2', 'port' => 11211, 'weight' => 50],
        ],
    ],
],
```

### Ключи и зависимости

Ключ — строка или любое значение (сериализуется). Составляйте его из всех значимых
частей: `[__CLASS__, $db->dsn, $tableName]`.

```php
$dependency = new \yii\caching\DbDependency(['sql' => 'SELECT MAX(updated_at) FROM post']);
$cache->set($key, $data, 30, $dependency);
```

| Зависимость | Инвалидируется, когда |
|---|---|
| `DbDependency` | меняется результат SQL-запроса |
| `FileDependency` | меняется время модификации файла |
| `ExpressionDependency` | меняется результат PHP-выражения |
| `CallbackDependency` | меняется результат коллбэка |
| `TagDependency` | вызван `TagDependency::invalidate($cache, 'tag')` |
| `ChainedDependency` | изменилась любая зависимость в цепочке |

```php
$cache->set($key, $data, 0, new \yii\caching\TagDependency(['tags' => ['post', "post-$id"]]));
\yii\caching\TagDependency::invalidate(Yii::$app->cache, "post-$id");
```

## Кеш запросов к БД

```php
$result = $db->cache(function ($db) {
    return Customer::find()->where(['id' => 1])->one();
}, $duration, $dependency);

$db->cache(function ($db) {
    $db->noCache(function ($db) {
        // этот запрос не кешируется
    });
});

// точечно для одной команды
$db->createCommand($sql)->cache(60)->queryOne();
$db->createCommand($sql)->noCache()->queryOne();
```

Настройки соединения: `enableQueryCache`, `queryCacheDuration`, `queryCache` (ID
компонента). Не работает с ресурсами (BLOB-хендлеры) и превышающими лимит хранилища
результатами.

Отдельно стоит включить кеш схемы — он экономит запросы вида `SHOW COLUMNS`:

```php
'db' => [
    'enableSchemaCache' => true,
    'schemaCacheDuration' => 3600,
    'schemaCache' => 'cache',
],
```

## Кеш фрагментов

```php
if ($this->beginCache($id, [
    'duration' => 3600,
    'dependency' => ['class' => 'yii\caching\DbDependency', 'sql' => 'SELECT MAX(updated_at) FROM post'],
    'variations' => [Yii::$app->language],
    'enabled' => Yii::$app->request->isGet,
])) {

    // ... тяжёлая генерация содержимого ...

    $this->endCache();
}
```

Фрагменты можно вкладывать друг в друга (у внутреннего может быть свой срок и свои
зависимости). Динамические вставки внутри кешированного фрагмента:

```php
echo $this->renderDynamic('return Yii::$app->user->identity->name;');
```

## Кеш страницы

```php
public function behaviors()
{
    return [
        [
            'class' => 'yii\filters\PageCache',
            'only' => ['index'],
            'duration' => 60,
            'variations' => [Yii::$app->language],
            'dependency' => [
                'class' => 'yii\caching\DbDependency',
                'sql' => 'SELECT COUNT(*) FROM post',
            ],
        ],
    ];
}
```

Это фильтр действия (в отличие от фрагментов — виджета). Поддерживает те же
`duration`, `dependency`, `variations`, `enabled`.

## HTTP-кеш

```php
public function behaviors()
{
    return [
        [
            'class' => 'yii\filters\HttpCache',
            'only' => ['index', 'view'],
            'lastModified' => fn ($action, $params) => Post::find()->max('updated_at'),
            'etagSeed' => fn ($action, $params) => serialize([$this->findModel()->title]),
            'cacheControlHeader' => 'public, max-age=300',
            'sessionCacheLimiter' => '',
        ],
    ];
}
```

Работает только для `GET` и `HEAD`: отдаёт `304 Not Modified`, если у клиента свежая
версия. Заголовки: `Last-Modified` / `If-Modified-Since`, `ETag` / `If-None-Match`,
`Cache-Control`.

## Очистка

```bash
yii cache                     # список кеширующих компонентов
yii cache/flush cache1 cache2
yii cache/flush-all
yii cache/flush-schema db     # сброс кеша схемы БД
```

> Важно: у консольного приложения свой конфиг — проверьте, что кеширующие компоненты в
> `console.php` и `web.php` совпадают, иначе `yii cache/flush` очистит «не тот» кеш.
