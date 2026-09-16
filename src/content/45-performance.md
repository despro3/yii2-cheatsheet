---
id: performance
title: Производительность
part: special
summary: Чек-лист оптимизации — production-режим и opcache, кэш схемы и запросов, оптимизация автозагрузчика Composer, сборка ассетов, сессии в БД/кэше, тяжёлые выборки (asArray, batch, with), логирование и профилирование, где искать узкие места.
sources: tutorial-performance-tuning
---

:::lead
Yii быстр по умолчанию, но большинство «медленных сайтов» — это выключенный кэш, включённый debug и N+1 запросов. Ниже — порядок действий: сначала бесплатные переключатели, потом кэширование, потом профилирование и точечные правки.
:::

## 1. Бесплатные переключатели

:::steps
1. **Production-режим**: в `index.php` `YII_DEBUG = false`, `YII_ENV = 'prod'` (или не задавать — умолчания именно такие). Отладчик и Gii не подключать.
2. **OPcache**: `opcache.enable=1`, `opcache.validate_timestamps=0` (сбрасывать при деплое), `opcache.memory_consumption=256`. Самый большой выигрыш.
3. **Автозагрузчик**: `composer install --no-dev --optimize-autoloader` (или `dump-autoload -o --classmap-authoritative`).
4. **Кэш схемы БД**: `'enableSchemaCache' => true, 'schemaCacheDuration' => 3600` в `db` — иначе AR читает структуру таблиц каждым запросом. Сбрасывать `./yii cache/flush-schema` после миграций.
5. **Логи**: `traceLevel => 0` в production (трассировка стека дорогая), `flushInterval`/`exportInterval` побольше, только нужные `levels`/`categories`.
6. **Xdebug** выключен на production.
:::

## 2. Кэширование

- Данные — `getOrSet()` с зависимостями ([кэширование данных](caching)); хранилище — APCu для одного сервера, Redis/Memcached для нескольких.
- Запросы — `Query::cache()`, `Connection::cache()`; схема — выше.
- Фрагменты/страницы/HTTP — [кэширование вывода](caching-output).
- RBAC: `authManager.cache`, URL-правила: `urlManager.cache` (по умолчанию используют компонент `cache`).
- Переводы `PhpMessageSource` кэшируются opcache сами; `DbMessageSource` — `cachingDuration`.

## 3. Сессии

Файловые сессии на одном сервере — нормально; при нескольких серверах или тысячах пользователей:

```php
'session' => ['class' => 'yii\web\DbSession', 'sessionTable' => 'session'],   // или CacheSession с Redis/Memcached
```

Не открывать сессию, когда не нужно (например, для API: `enableSession => false`); сборка мусора — `gcProbability`. Кэшированная сессия быстрее, но теряется при рестарте кэша.

## 4. База данных

- Индексы по столбцам из `where`, `join`, `orderBy`; смотрите EXPLAIN в панели Database отладчика.
- **N+1**: `with()` для связей в списках; `joinWith('rel', false)` + `with()`, если нужен фильтр по связи.
- `asArray()` для больших выборок только на чтение; `select()` только нужных столбцов; `batch()`/`each()` для экспорта.
- `count()` дорог на больших таблицах — кэшируйте или храните счётчик (`updateCounters`).
- Массовые операции — `updateAll()`/`deleteAll()`/`batchInsert()` вместо циклов `save()`.
- DAO там, где AR избыточен (агрегаты, отчёты).
- Реплики: `slaves` в соединении — чтение с реплик, запись в мастер.
- Постоянные соединения (`attributes => [PDO::ATTR_PERSISTENT => true]`) — с осторожностью.

## 5. Ассеты и фронтенд

```bash
./yii asset/template assets.php      # шаблон конфигурации сборки
./yii asset assets.php config/assets-prod.php
```

Команда объединяет и минифицирует CSS/JS бандлов (нужны closure-compiler/yuicompressor или свои `jsCompressor`/`cssCompressor`); результат подключается через `assetManager.bundles`. Плюс: `appendTimestamp => true` (кэш браузера), `linkAssets => true` (симлинки вместо копирования), отдача статики веб-сервером с gzip/brotli и заголовками кэша, CDN для `jquery`/`bootstrap` через переопределение бандлов.

## 6. Код приложения

- Не вызывайте тяжёлое в `init()`/конструкторах компонентов, которые создаются на каждом запросе; ленивые компоненты создаются только при обращении — не тяните их в `bootstrap` без нужды.
- `Html::encode` дешевле `HtmlPurifier::process` — чистите HTML при сохранении, а не при показе (или кэшируйте).
- `Yii::t()` с intl быстрее без — но и файлы переводов не должны быть гигантскими.
- Widgets/`render` в цикле — заменить на один `ListView`/строковую сборку.
- `Yii::$app->formatter` для тысяч ячеек — предварительно вычислить формат один раз.
- Уменьшайте `traceLevel`, отключайте `profiling` в production.

## 7. Измерять, а не гадать

```php
Yii::beginProfile('block');
// …
Yii::endProfile('block');
```

Панель Profiling и Database в [отладчике](dev-tools) показывают время по блокам и запросам. На production — `yii\log\FileTarget` с `levels => ['profile']` на короткое время, APM (Blackfire, Xhprof, New Relic), медленные запросы в логах СУБД. `ab`/`wrk`/`k6` для нагрузочного теста до и после изменений.

## Чек-лист перед выкладкой

:::cards
- **YII_DEBUG=false**, debug/gii выключены
- **OPcache** включён, `validate_timestamps=0`
- **composer** `--no-dev -o`
- **enableSchemaCache** и `cache` не `DummyCache`/`FileCache` на нескольких серверах
- **Сессии** в БД/Redis при нескольких серверах
- **N+1** проверен в панели Database на ключевых страницах
- **Ассеты** собраны, `appendTimestamp`, gzip на сервере
- **Логи** только error/warning, `traceLevel=0`
:::

:::quiz Проверь себя
Q: Какая одна настройка `db` сильнее всего влияет на скорость Active Record?
A: `enableSchemaCache => true` — иначе схема таблицы читается при каждом запросе.
Q: Почему `YII_DEBUG = true` на production — проблема не только безопасности?
A: Включаются трассировка, профилирование и подробные логи, что заметно замедляет каждый запрос.
Q: Как найти N+1 на странице списка?
A: Открыть панель Database отладчика: десятки одинаковых `SELECT … WHERE id = ?` — признак; лечится `with()`.
Q: Что делает команда `./yii asset`?
A: Объединяет и минифицирует CSS/JS бандлов по конфигурации в единые файлы для production.
Q: Когда переносить сессии из файлов в БД или кэш?
A: При нескольких веб-серверах (общий доступ) или очень большом числе сессий.
:::
