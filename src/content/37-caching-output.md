---
id: caching-output
title: Кэширование фрагментов, страниц и HTTP
part: caching
summary: beginCache()/endCache() с duration, dependency, variations и enabled; вложенные фрагменты и динамическое содержимое renderDynamic(); фильтр PageCache; HTTP-кэш через HttpCache — Last-Modified, ETag, Cache-Control, а также session cache limiter и SEO-эффект.
sources: caching-fragment, caching-page, caching-http
---

:::lead
Дальше данных: можно кэшировать готовый HTML — кусок представления, всю страницу, — и даже не отдавать страницу вовсе, если браузер уже имеет свежую копию (HTTP 304). Всё это те же зависимости и то же хранилище, что и в [кэшировании данных](caching).
:::

## Фрагменты

```php
<?php if ($this->beginCache($id, $options)) { ?>
    ...содержимое, которое дорого генерировать...
<?php $this->endCache(); } ?>
```

`beginCache()` вернул `true` — кэша нет, содержимое генерируется и сохраняется; `false` — кэш есть, он уже выведен, тело пропускается.

### Опции

```php
$options = [
    'duration' => 3600,                                  // по умолчанию 60 секунд; 0 — навсегда
    'dependency' => [
        'class' => 'yii\caching\DbDependency',
        'sql' => 'SELECT COUNT(*) FROM post',
    ],
    'variations' => [Yii::$app->language, Yii::$app->user->id],   // отдельный кэш для каждой комбинации
    'enabled' => !YII_ENV_DEV,                           // включать по условию
    'cache' => 'cache',                                  // компонент
];
```

:::kv
`duration` — секунды жизни
`dependency` — объект или конфигурация зависимости (Tag, Db, File, Expression, Chained)
`variations` — массив значений, которые влияют на вывод (язык, пользователь, тема); входят в ключ
`enabled` — `false` — просто выводить без кэша (удобно для отладки)
`cache` — имя компонента кэша
:::

### Вложенные фрагменты

```php
<?php if ($this->beginCache($id1)) { ?>
    ...внешний фрагмент...
    <?php if ($this->beginCache($id2, $options2)) { ?>
        ...внутренний...
    <?php $this->endCache(); } ?>
    ...
<?php $this->endCache(); } ?>
```

Внутренний может иметь короче срок, чем внешний, но пока жив внешний — внутренний не пересоберётся (он часть внешнего HTML).

### Динамическое содержимое внутри кэша

```php
<?php if ($this->beginCache($id)) { ?>
    ...статичная часть...
    <?= $this->renderDynamic('return Yii::$app->user->identity->name;') ?>
    <?= $this->renderDynamic(function ($view, $params) { return date('H:i:s'); }) ?>
<?php $this->endCache(); } ?>
```

`renderDynamic()` вставляет плейсхолдер, который выполняется при **каждом** показе — даже когда фрагмент из кэша. Код передаётся строкой PHP или замыканием (замыкание — с 2.0.14).

## Кэширование страниц

Фильтр `PageCache` в контроллере — кэш целого ответа, включая заголовки:

```php
public function behaviors()
{
    return [
        [
            'class' => 'yii\filters\PageCache',
            'only' => ['index'],
            'duration' => 60,
            'variations' => [Yii::$app->language],
            'dependency' => ['class' => 'yii\caching\DbDependency', 'sql' => 'SELECT COUNT(*) FROM post'],
            // 'enabled' => …, 'cache' => 'cache', 'cacheCookies' => false, 'cacheHeaders' => true
        ],
    ];
}
```

Работает как фрагмент, но на уровне `beforeAction()`: при попадании действие не выполняется вовсе. Кэшируется только успешный ответ (`statusCode == 200`); cookie и заголовки — настраиваемо. `variations` — обязательно добавьте всё, что меняет страницу (пользователь, язык), иначе гость увидит чужие данные.

## HTTP-кэширование

Не генерировать ответ, если у клиента уже свежая копия. Фильтр `HttpCache`:

```php
public function behaviors()
{
    return [
        [
            'class' => 'yii\filters\HttpCache',
            'only' => ['index'],
            'lastModified' => function ($action, $params) {
                return (new \yii\db\Query())->from('post')->max('updated_at');   // timestamp
            },
            'etagSeed' => function ($action, $params) {
                // что угодно, что меняется с содержимым
                return serialize([$this->page->title, $this->page->content]);
            },
            'cacheControlHeader' => 'public, max-age=3600',
            'sessionCacheLimiter' => 'public',
            // 'params' => [...], 'enabled' => true
        ],
    ];
}
```

:::kv
`lastModified` — колбэк, возвращает UNIX-время последнего изменения → заголовок `Last-Modified`; браузер шлёт `If-Modified-Since`
`etagSeed` — колбэк, возвращает «семя» для `ETag` (хэшируется); браузер шлёт `If-None-Match`. Точнее, чем время, но требует вычислить содержимое
`cacheControlHeader` — `Cache-Control` (по умолчанию `public, max-age=3600`)
`sessionCacheLimiter` — `session_cache_limiter()`: PHP по умолчанию отправляет `Cache-Control: no-store`, из-за чего браузеры не кэшируют; `''` — не менять, `'public'`/`'private'`/`'nocache'`
:::

При совпадении фильтр отвечает **304 Not Modified** без выполнения действия. Достаточно одного из `lastModified`/`etagSeed`; при обоих проверяются оба. Для `ETag` Yii ставит «weak» ETag, если `weakEtag = true` (2.0.8).

> [!NOTE] SEO
> Поисковики учитывают `Last-Modified`/`ETag` — правильные заголовки уменьшают нагрузку от ботов и помогают индексации. Для статичных файлов заголовки настраивают на веб-сервере.

## Что выбрать

:::cols
=== Фрагмент
Дорогой кусок страницы (меню категорий, блок «популярное»), остальное динамическое. `variations` по языку/роли.
=== Страница
Публичные страницы без персонализации: лендинги, статьи для гостей. Осторожно с cookie и CSRF-токенами в формах.
=== HTTP
Всё публичное, что можно отдать браузеру и CDN: лента, API-ответы, картинки. Экономит трафик и время генерации.
:::

Уровни комбинируются: страница закэширована `PageCache`, а `HttpCache` перед ним вообще не отдаёт тело, если ETag совпал.

:::quiz Проверь себя
Q: Что означает `true` от `$this->beginCache($id)`?
A: Кэша нет — содержимое нужно сгенерировать; при `false` оно уже выведено из кэша.
Q: Как показать имя текущего пользователя внутри закэшированного фрагмента?
A: Через `$this->renderDynamic()` — этот код выполняется при каждом показе.
Q: Зачем `variations` для `PageCache`?
A: Чтобы для каждого языка/пользователя/устройства был свой экземпляр кэша, иначе один вариант получат все.
Q: Что произойдёт при совпадении `ETag` в `HttpCache`?
A: Ответ 304 Not Modified без тела; действие контроллера не выполняется.
Q: Почему браузер не кэшировал страницу с сессией?
A: PHP ставит `Cache-Control: no-store` через session cache limiter; задайте `sessionCacheLimiter => 'public'` или `''`.
:::
