---
id: data-providers
title: Провайдеры данных, пагинация, сортировка
part: output
summary: ActiveDataProvider, SqlDataProvider, ArrayDataProvider и свой провайдер; классы Pagination и Sort — как они читают параметры из URL, строят ссылки и подключаются к запросам; LinkPager и ссылки сортировки вручную.
sources: output-data-providers, output-pagination, output-sorting
---

:::lead
Провайдер данных — объект `DataProviderInterface`, который отдаёт страницу моделей с учётом **пагинации** и **сортировки** из параметров запроса. Его принимают `GridView`, `ListView`, REST-контроллеры. Вы описываете источник (запрос AR, SQL или массив) — остальное делают классы `Pagination` и `Sort`.
:::

## Три провайдера

:::tabs
=== ActiveDataProvider
```php
use yii\data\ActiveDataProvider;

$query = Post::find()->where(['status' => 1]);
$provider = new ActiveDataProvider([
    'query' => $query,
    'pagination' => ['pageSize' => 10],
    'sort' => ['defaultOrder' => ['created_at' => SORT_DESC, 'title' => SORT_ASC]],
]);

$posts = $provider->getModels();   // страница моделей
$provider->getTotalCount();        // всего строк (отдельный COUNT)
$provider->getKeys();              // первичные ключи страницы
$provider->getCount();             // моделей на странице
```
Принимает любой `QueryInterface`, в том числе обычный `Query` — тогда модели будут массивами. Сортировка по умолчанию настроена по атрибутам модели. Соединение — `db`, можно задать другое.
=== SqlDataProvider
```php
use yii\data\SqlDataProvider;

$count = Yii::$app->db
    ->createCommand('SELECT COUNT(*) FROM post WHERE status=:status', [':status' => 1])
    ->queryScalar();

$provider = new SqlDataProvider([
    'sql' => 'SELECT * FROM post WHERE status=:status',
    'params' => [':status' => 1],
    'totalCount' => $count,              // обязательно — сам провайдер считать не умеет
    'sort' => ['attributes' => ['title', 'view_count', 'created_at']],
    'pagination' => ['pageSize' => 20],
]);
$rows = $provider->getModels();          // массивы
```
Провайдер сам допишет `ORDER BY`, `LIMIT` и `OFFSET` к вашему SQL.
=== ArrayDataProvider
```php
use yii\data\ArrayDataProvider;

$provider = new ArrayDataProvider([
    'allModels' => $data,                // массив массивов или объектов
    'key' => 'id',                       // ключ (по умолчанию индекс)
    'pagination' => ['pageSize' => 10],
    'sort' => ['attributes' => ['id', 'username', 'email']],
]);
```
Сортирует и режет массив в памяти — подходит для небольших и уже выбранных данных. Для БД используйте первые два: там LIMIT применяется в запросе.
:::

## Ключи

Каждой модели соответствует ключ (`getKeys()`), который `GridView` кладёт в `data-key` строк, а `CheckboxColumn` отправляет на сервер. Для AR это первичный ключ (составной — сериализуется), для `SqlDataProvider` и `ArrayDataProvider` — свойство `key` (имя столбца или замыкание), иначе индекс.

## Pagination

Хранит `totalCount`, `pageSize`, `page` и читает их из запроса:

```php
use yii\data\Pagination;

$query = Article::find()->where(['status' => 1]);
$countQuery = clone $query;
$pages = new Pagination(['totalCount' => $countQuery->count(), 'pageSize' => 20]);
$models = $query->offset($pages->offset)->limit($pages->limit)->all();

// в представлении
echo LinkPager::widget(['pagination' => $pages]);
```

:::kv
`pageParam`, `pageSizeParam` — имена GET-параметров (`page`, `per-page`)
`pageSize`, `defaultPageSize`, `pageSizeLimit` — размер страницы: из запроса, но в пределах `[1, 50]` по умолчанию; `pageSizeLimit = false` — без ограничений
`page` — номер страницы, считается с 0 (в URL — с 1, `validatePage` обрезает по `pageCount`)
`forcePageParam` — добавлять `page=1` даже для первой (по умолчанию `true`)
`route`, `params`, `urlManager` — как строить ссылки; по умолчанию текущий маршрут и все GET-параметры
`pageCount`, `offset`, `limit`, `getLinks()` — вычисляемые
`createUrl($page)`, `getPageCount()` — вручную
:::

```php
$pages->createUrl(2);          // /index.php?r=article%2Findex&page=3
$pages->getLinks();            // ['self' => …, 'first' => …, 'prev' => …, 'next' => …, 'last' => …] — для REST
```

В провайдере: `'pagination' => false` отключает пагинацию, `['pageSize' => 0]` — без LIMIT, но с ссылками.

### LinkPager

```php
echo LinkPager::widget([
    'pagination' => $provider->pagination,
    'maxButtonCount' => 5,
    'firstPageLabel' => '«', 'lastPageLabel' => '»',
    'prevPageLabel' => '‹', 'nextPageLabel' => '›',
    'hideOnSinglePage' => true,
    'options' => ['class' => 'pagination justify-content-center'],
    // Bootstrap 4/5
    'linkContainerOptions' => ['class' => 'page-item'], 'linkOptions' => ['class' => 'page-link'],
]);
```

## Sort

Читает GET-параметр `sort` (`?sort=age,-name` — минус означает DESC), строит `ORDER BY` и ссылки:

```php
use yii\data\Sort;

$sort = new Sort([
    'attributes' => [
        'age',                                           // просто столбец
        'name' => [
            'asc' => ['first_name' => SORT_ASC, 'last_name' => SORT_ASC],
            'desc' => ['first_name' => SORT_DESC, 'last_name' => SORT_DESC],
            'default' => SORT_DESC,
            'label' => 'Имя',
        ],
    ],
    'defaultOrder' => ['age' => SORT_ASC],
    'enableMultiSort' => true,       // несколько атрибутов сразу (по умолчанию false)
]);

$models = Article::find()->orderBy($sort->orders)->all();

// ссылки в представлении
echo $sort->link('name') . ' | ' . $sort->link('age');
echo $sort->link('age', ['class' => 'sort-link']);
$sort->createUrl('age');
$sort->getAttributeOrder('age');   // SORT_ASC | SORT_DESC | null
```

:::kv
`attributes` — что можно сортировать; строка = столбец, массив = правила для `asc`/`desc`, `default`, `label`
`defaultOrder` — если параметр не передан
`enableMultiSort`, `separator` (`,`) — несколько атрибутов
`sortParam` — имя GET-параметра (`sort`)
`route`, `params`, `urlManager` — построение ссылок
`orders` — итоговый `ORDER BY` в формате `['col' => SORT_ASC]`
`attributeOrders` — текущая сортировка по атрибутам
:::

Ссылки `link()` получают класс `asc`/`desc` по текущему направлению — удобно рисовать стрелки CSS.

## Сортировка по связи в ActiveDataProvider

Провайдер знает только атрибуты модели; связанные столбцы добавляются вручную:

```php
$query = Post::find()->joinWith('author');
$provider = new ActiveDataProvider(['query' => $query]);
$provider->sort->attributes['author.name'] = [
    'asc' => ['user.name' => SORT_ASC],
    'desc' => ['user.name' => SORT_DESC],
];
```

Тот же приём нужен для фильтров GridView по связям — см. [виджеты данных](data-widgets).

## Свой провайдер

```php
class CsvDataProvider extends \yii\data\BaseDataProvider
{
    public $filename;

    protected function prepareModels()
    {
        // прочитать файл с учётом $this->getPagination()->offset/limit и $this->getSort()->orders
    }
    protected function prepareKeys($models) { return array_keys($models); }
    protected function prepareTotalCount() { return /* число строк */; }
}
```

Три метода — и всё остальное (`getModels()`, `getKeys()`, `getTotalCount()`, кэширование результата) уже есть в `BaseDataProvider`.

## Несколько провайдеров на странице

Чтобы `page` и `sort` одного списка не влияли на другой, дайте параметрам разные имена:

```php
$providerA = new ActiveDataProvider([
    'query' => Post::find(),
    'pagination' => ['pageParam' => 'post-page'],
    'sort' => ['sortParam' => 'post-sort'],
]);
```

Или задайте `id` провайдеру — тогда параметры станут `id-page` и `id-sort` автоматически.

:::quiz Проверь себя
Q: Почему `SqlDataProvider` требует `totalCount`, а `ActiveDataProvider` — нет?
A: По объекту `Query` провайдер сам строит `COUNT(*)`, а произвольный SQL он переделать не может.
Q: С какого номера начинаются страницы в `Pagination::page` и в URL?
A: В объекте — с 0, в URL-параметре `page` — с 1.
Q: Что означает `?sort=-created_at,title`?
A: Сортировка по `created_at` по убыванию, затем по `title` по возрастанию (при `enableMultiSort = true`).
Q: Как ограничить размер страницы, который пользователь передаёт через `per-page`?
A: `pageSizeLimit` в `Pagination` (по умолчанию `[1, 50]`).
Q: Как разрешить сортировку по столбцу связанной таблицы?
A: Сделать `joinWith()` в запросе и добавить атрибут в `$provider->sort->attributes` с `asc`/`desc` по столбцу связанной таблицы.
:::
