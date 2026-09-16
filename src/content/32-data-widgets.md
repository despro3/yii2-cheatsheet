---
id: data-widgets
title: Виджеты данных
part: output
summary: DetailView для одной модели, ListView со своим шаблоном элемента, GridView с колонками DataColumn/ActionColumn/CheckboxColumn/SerialColumn, фильтрами, сортировкой и форматами; работа со связями (joinWith), Pjax, несколько таблиц на странице.
sources: output-data-widgets
---

:::lead
Три виджета, которые закрывают 90% вывода данных: `DetailView` — карточка одной записи, `ListView` — список произвольной вёрстки, `GridView` — таблица с сортировкой, фильтрами и пагинацией. Все берут данные из [провайдера](data-providers) и форматируют через [formatter](formatting).
:::

## DetailView

```php
use yii\widgets\DetailView;

echo DetailView::widget([
    'model' => $model,
    'attributes' => [
        'title',                                    // атрибут как есть (формат text)
        'description:html',                         // атрибут:формат
        'created_at:datetime',
        [
            'label' => 'Владелец',
            'value' => $model->owner->name,          // значение или замыкание function ($model, $widget)
        ],
        [
            'attribute' => 'status',
            'format' => 'raw',
            'value' => $model->status ? '<span class="badge">активен</span>' : 'нет',
        ],
        'owner.email',                              // через связь — вложенное свойство
        ['attribute' => 'secret', 'visible' => Yii::$app->user->can('admin')],
    ],
    'template' => '<tr><th>{label}</th><td>{value}</td></tr>',
    'options' => ['class' => 'table table-striped'],
]);
```

`model` может быть объектом или массивом. Форматы — любые из `Formatter`.

## ListView

```php
use yii\widgets\ListView;

echo ListView::widget([
    'dataProvider' => $dataProvider,
    // views/post/_post.php, получает $model, $key, $index, $widget
    'itemView' => '_post',
    // 'itemView' => function ($model, $key, $index, $widget) { return Html::tag('div', $model->title); },
    'viewParams' => ['fullView' => true],           // дополнительно в $itemView
    'itemOptions' => ['class' => 'item'],
    'layout' => "{summary}\n{items}\n{pager}",      // также {sorter}
    'summary' => 'Показано {begin}–{end} из {totalCount}',
    'emptyText' => 'Ничего не найдено',
    'pager' => ['class' => LinkPager::class, 'maxButtonCount' => 5],
    'sorter' => ['attributes' => ['title', 'created_at']],
]);
```

```php title="views/post/_post.php"
<article>
    <h2><?= Html::a(Html::encode($model->title), ['view', 'id' => $model->id]) ?></h2>
    <?= Yii::$app->formatter->asDate($model->created_at) ?>
</article>
```

## GridView

```php
use yii\grid\GridView;

echo GridView::widget([
    'dataProvider' => $dataProvider,
    'filterModel' => $searchModel,                  // строка фильтров над таблицей
    'columns' => [
        ['class' => 'yii\grid\SerialColumn'],       // №
        'id',
        'name',
        'email:email',
        'created_at:date',
        ['class' => 'yii\grid\ActionColumn'],       // просмотр / правка / удаление
    ],
    'layout' => "{summary}\n{items}\n{pager}",
    'tableOptions' => ['class' => 'table table-striped'],
    'rowOptions' => function ($model, $key, $index, $grid) {
        return ['class' => $model->is_deleted ? 'text-muted' : ''];
    },
]);
```

Без `columns` виджет покажет все атрибуты модели.

### DataColumn — обычная колонка

Строка `'name:format:label'` или массив:

```php
[
    'attribute' => 'price',
    'label' => 'Цена',
    'format' => ['currency', 'RUB'],
    'value' => function ($model, $key, $index, $column) { return $model->price / 100; },   // или 'owner.name'
    'contentOptions' => ['class' => 'text-end'],
    'headerOptions' => ['style' => 'width: 100px'],
    'enableSorting' => true,
    // <select> вместо текстового поля; false — без фильтра
    'filter' => ['1' => 'Активен', '0' => 'Заблокирован'],
    'filterInputOptions' => ['class' => 'form-control', 'placeholder' => 'Поиск'],
    'visible' => !Yii::$app->user->isGuest,
    'content' => function ($model) { … },   // полностью свой HTML (не экранируется)
],
```

`format => 'raw'` выводит HTML без экранирования — только для доверенного содержимого.

### ActionColumn

```php
[
    'class' => 'yii\grid\ActionColumn',
    'template' => '{view} {update} {delete} {custom}',
    'controller' => 'admin/user',                   // другой контроллер (по умолчанию текущий)
    'buttons' => [
        'custom' => function ($url, $model, $key) {
            return Html::a('<i class="bi bi-star"></i>', $url, ['title' => 'Избранное']);
        },
    ],
    'urlCreator' => function ($action, $model, $key, $index) {
        return Url::to([$action, 'id' => $model->id, 'slug' => $model->slug]);
    },
    'visibleButtons' => ['delete' => function ($model, $key, $index) { return $model->canDelete(); }],
],
```

Кнопка `delete` уже имеет `data-confirm` и `data-method="post"` — обрабатывается `yii.js`.

### CheckboxColumn

```php
['class' => 'yii\grid\CheckboxColumn', 'checkboxOptions' => function ($model) { return ['value' => $model->id]; }],
```

```js
var keys = $('#grid').yiiGridView('getSelectedRows');   // массив ключей отмеченных строк
```

Чекбокс в заголовке отмечает всё. Имя поля — `selection[]` (`name` колонки).

### SerialColumn

Порядковый номер строки с учётом страницы.

## Фильтрация и поисковая модель

Стандартный паттерн (Gii генерирует именно так):

```php title="models/PostSearch.php"
class PostSearch extends Post
{
    public function rules()
    {
        return [[['id', 'status'], 'integer'], [['title', 'author.name'], 'safe']];
    }

    public function search($params)
    {
        $query = Post::find();
        $dataProvider = new ActiveDataProvider(['query' => $query]);

        if (!($this->load($params) && $this->validate())) {
            return $dataProvider;
        }

        $query->andFilterWhere(['id' => $this->id, 'status' => $this->status])
              ->andFilterWhere(['like', 'title', $this->title]);

        return $dataProvider;
    }
}
```

```php title="controllers/PostController.php"
public function actionIndex()
{
    $searchModel = new PostSearch();
    $dataProvider = $searchModel->search(Yii::$app->request->queryParams);
    return $this->render('index', compact('searchModel', 'dataProvider'));
}
```

`filterModel` рисует поля фильтров по атрибутам с правилами; `andFilterWhere` игнорирует пустые — фильтр работает «как есть».

### Фильтр и сортировка по связи

```php title="models/PostSearch.php"
public $authorName;                       // виртуальный атрибут для фильтра

public function rules() { return [[['authorName'], 'safe'], …]; }

public function search($params)
{
    $query = Post::find()->joinWith(['author']);          // JOIN нужен для where по чужой таблице
    $dataProvider = new ActiveDataProvider(['query' => $query]);

    $dataProvider->sort->attributes['authorName'] = [
        'asc' => ['user.name' => SORT_ASC],
        'desc' => ['user.name' => SORT_DESC],
    ];

    $this->load($params);
    $query->andFilterWhere(['like', 'user.name', $this->authorName]);
    return $dataProvider;
}
```

```php
// колонка
['attribute' => 'authorName', 'value' => 'author.name', 'label' => 'Автор'],
```

Для `hasMany` при `joinWith` строки дублируются — добавьте `->groupBy('post.id')` или используйте `->with()` + подзапрос `exists`. Чтобы оптимизировать, `joinWith('author', false)` + `with('author')`.

## Pjax — таблица без перезагрузки

```php
<?php Pjax::begin(['id' => 'post-grid']) ?>
<?= GridView::widget([...]) ?>
<?php Pjax::end() ?>
```

Пагинация, сортировка и фильтры внутри работают через AJAX. Кнопки `ActionColumn` тоже, но после `delete` нужно обновить: `$.pjax.reload({container: '#post-grid'})`. Ссылки, которые не должны идти через Pjax, помечайте `data-pjax="0"`.

## Несколько GridView на странице

```php
$userProvider->pagination->pageParam = 'user-page';
$userProvider->sort->sortParam = 'user-sort';
$postProvider->pagination->pageParam = 'post-page';
$postProvider->sort->sortParam = 'post-sort';
```

Иначе страницы и сортировка будут делить одни и те же GET-параметры.

## Быстрый рецепт CRUD-списка

:::steps
1. `PostSearch extends Post` с `search($params)` — `ActiveDataProvider` + `andFilterWhere`.
2. В действии: `$dataProvider = $searchModel->search(Yii::$app->request->queryParams)`.
3. `GridView` с `filterModel`, колонками и `ActionColumn`; обернуть в `Pjax`.
4. Для связей — `joinWith` + виртуальный атрибут + `sort->attributes`.
5. Массовые действия — `CheckboxColumn` + `yiiGridView('getSelectedRows')`.
:::

:::quiz Проверь себя
Q: Что означает `'created_at:datetime:Создано'` в списке колонок?
A: Атрибут `created_at`, формат `datetime`, заголовок «Создано».
Q: Зачем поисковой модели наследовать AR-модель?
A: Чтобы получить атрибуты, подписи и типы; `rules()` переопределяются под фильтр, а `search()` строит провайдер.
Q: Почему фильтр по `author.name` не работает без `joinWith`?
A: Условие `where` на столбец другой таблицы требует JOIN; `with()` делает отдельный запрос и не подходит.
Q: Как получить ключи отмеченных строк `CheckboxColumn`?
A: `$('#grid').yiiGridView('getSelectedRows')` в JS или `selection[]` из POST.
Q: Что даёт обёртка GridView в `Pjax`?
A: Пагинация, сортировка и фильтрация обновляют только таблицу без перезагрузки страницы.
:::
