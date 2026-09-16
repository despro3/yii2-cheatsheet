---
id: output
title: Вывод данных
icon: 📊
summary: Форматтер, пагинация, сортировка, провайдеры данных, GridView/ListView/DetailView, JS/CSS, темы.
sources: output-formatting, output-pagination, output-sorting, output-data-providers, output-data-widgets, output-client-scripts, output-theming
---

# Вывод данных

## Форматтер

```php
$f = Yii::$app->formatter;

$f->asDate('2014-01-01', 'long');      // 1 января 2014 г.
$f->asDate('now', 'php:d.m.Y');        // через формат date()
$f->asDatetime($ts);  $f->asTime($ts);  $f->asTimestamp($date);
$f->asRelativeTime($ts);               // «час назад»
$f->asDuration(3720);                  // «1 час 2 минуты»

$f->asInteger(42);  $f->asDecimal(2542.123);  $f->asPercent(0.125, 2);
$f->asCurrency(420, 'EUR');  $f->asScientific(42000);
$f->asSize(1024 * 410);  $f->asShortSize(1024 * 410);

$f->asText($str);  $f->asNtext($str);  $f->asParagraphs($str);
$f->asHtml($str);  $f->asRaw($str);
$f->asEmail($m);  $f->asUrl($u);  $f->asImage($src);  $f->asBoolean(true);

$f->format($value, 'date');            // по имени формата
$f->format(0.125, ['percent', 2]);     // формат с параметрами
$f->asDate(null);                      // «(не задано)» — nullDisplay
```

```php
'formatter' => [
    'dateFormat' => 'dd.MM.yyyy',
    'datetimeFormat' => 'dd.MM.yyyy HH:mm',
    'decimalSeparator' => ',',
    'thousandSeparator' => ' ',
    'currencyCode' => 'UAH',
    'nullDisplay' => '—',
    'locale' => 'ru-RU',
    'timeZone' => 'Europe/Kyiv',
],
```

Локализация работает при установленном расширении `intl`; иначе форматы будут
«английскими» и без локализованных названий месяцев. Форматы `short`/`medium`/`long`/`full`
зависят от локали, кастомные — либо синтаксис ICU, либо `php:` + формат `date()`.

> Совет: храните дату/время в UTC (лучше всего UNIX-timestamp), а часовой пояс задавайте
> в приложении/форматтере — тогда одни и те же данные корректно покажутся любому
> пользователю.

## Пагинация и сортировка

```php
$query = Article::find()->where(['status' => 1]);
$pages = new \yii\data\Pagination([
    'totalCount' => $query->count(),
    'pageSize' => 20,
    'pageSizeParam' => false,      // не читать per-page из URL
]);
$models = $query->offset($pages->offset)->limit($pages->limit)->all();
```

```php
echo \yii\widgets\LinkPager::widget(['pagination' => $pages, 'maxButtonCount' => 5]);
```

```php
$sort = new \yii\data\Sort([
    'attributes' => [
        'age',
        'name' => [
            'asc' => ['first_name' => SORT_ASC, 'last_name' => SORT_ASC],
            'desc' => ['first_name' => SORT_DESC, 'last_name' => SORT_DESC],
            'default' => SORT_DESC,
            'label' => 'Имя',
        ],
    ],
    'defaultOrder' => ['age' => SORT_ASC],
]);

$articles = Article::find()->orderBy($sort->orders)->all();
echo $sort->link('name') . ' | ' . $sort->link('age');
```

Направление сортировки читается из GET-параметра `sort` (настраивается через `sortParam`).
В запрос передавайте `$sort->orders`, а не `attributeOrders` — составные атрибуты иначе
не раскроются.

## Провайдеры данных

```php
use yii\data\ActiveDataProvider;

$provider = new ActiveDataProvider([
    'query' => Post::find()->where(['status' => 1]),
    'pagination' => ['pageSize' => 20],
    'sort' => ['defaultOrder' => ['created_at' => SORT_DESC]],
    'key' => 'slug',                     // или функция: fn ($model) => md5($model->id)
]);

$provider->getModels();  $provider->getKeys();
$provider->getCount();   $provider->getTotalCount();
```

| Класс | Источник |
|---|---|
| `ActiveDataProvider` | `yii\db\Query` или `ActiveQuery` (AR-объекты или массивы) |
| `SqlDataProvider` | сырой SQL + обязательный `totalCount` |
| `ArrayDataProvider` | готовый массив (`allModels`) — всё грузится в память |

Свой провайдер — наследник `yii\data\BaseDataProvider` с методами `prepareModels()`,
`prepareKeys()`, `prepareTotalCount()`.

## GridView

```php
use yii\grid\GridView;

echo GridView::widget([
    'dataProvider' => $dataProvider,
    'filterModel' => $searchModel,
    'summary' => 'Показано {begin}–{end} из {totalCount}',
    'columns' => [
        ['class' => 'yii\grid\SerialColumn'],
        'id',
        'title',
        'author.name',                                  // атрибут связи
        'created_at:datetime',                          // формат
        [
            'attribute' => 'status',
            'value' => fn ($model) => $model->statusLabel,
            'filter' => ['0' => 'Черновик', '1' => 'Опубликован'],
            'filterInputOptions' => ['class' => 'form-control', 'prompt' => 'Все'],
            'contentOptions' => ['class' => 'text-center'],
        ],
        [
            'class' => 'yii\grid\ActionColumn',
            'template' => '{view} {update} {delete}',
            'buttons' => [
                'view' => fn ($url, $model, $key) => Html::a('👁', $url),
            ],
            'visibleButtons' => [
                'update' => fn ($model) => Yii::$app->user->can('updatePost', ['post' => $model]),
            ],
            'urlCreator' => fn ($action, $model, $key, $index) => Url::to([$action, 'id' => $model->id]),
        ],
        ['class' => 'yii\grid\CheckboxColumn'],
    ],
]);
```

Классы колонок: `DataColumn` (по умолчанию), `SerialColumn`, `ActionColumn`,
`CheckboxColumn`, `RadioButtonColumn`. Общие свойства любой колонки: `header`, `footer`,
`visible`, `content`, `headerOptions`, `contentOptions`, `filterOptions`, `footerOptions`.

Выбранные чекбоксами строки на клиенте: `$('#grid').yiiGridView('getSelectedRows')`.

### Фильтрация: модель поиска

```php
class PostSearch extends Post
{
    public $createdFrom;
    public $createdTo;

    public function rules()
    {
        return [
            [['id'], 'integer'],
            [['title', 'created_at', 'author.name', 'createdFrom', 'createdTo'], 'safe'],
        ];
    }

    public function scenarios() { return \yii\base\Model::scenarios(); }  // все атрибуты активны

    public function attributes()
    {
        return array_merge(parent::attributes(), ['author.name']);   // атрибут связи для поиска
    }

    public function search($params)
    {
        $query = Post::find();
        $dataProvider = new ActiveDataProvider(['query' => $query]);

        $query->joinWith(['author' => fn ($q) => $q->from(['author' => 'user'])]);
        $dataProvider->sort->attributes['author.name'] = [
            'asc' => ['author.name' => SORT_ASC],
            'desc' => ['author.name' => SORT_DESC],
        ];

        if (!($this->load($params) && $this->validate())) {
            return $dataProvider;
        }

        $query->andFilterWhere(['id' => $this->id])
            ->andFilterWhere(['like', 'title', $this->title])
            ->andFilterWhere(['like', 'author.name', $this->getAttribute('author.name')])
            ->andFilterWhere(['>=', 'created_at', $this->createdFrom])
            ->andFilterWhere(['<=', 'created_at', $this->createdTo]);

        return $dataProvider;
    }
}
```

```php
$searchModel = new PostSearch();
$dataProvider = $searchModel->search(Yii::$app->request->queryParams);
```

Альтернатива для сложных выборок — SQL-VIEW + отдельная AR-модель на него: сортировка и
фильтры по всем полям работают «из коробки» и быстрее, но доменная логика в такой модели
дублируется.

**Несколько GridView на странице** — разведите параметры:

```php
$userProvider->pagination->pageParam = 'user-page';
$userProvider->sort->sortParam = 'user-sort';
```

## ListView и DetailView

```php
echo \yii\widgets\ListView::widget([
    'dataProvider' => $dataProvider,
    'itemView' => '_post',                 // в виде доступны $model, $key, $index, $widget
    'viewParams' => ['fullView' => true],
    'layout' => "{summary}\n{items}\n{pager}",
]);

echo \yii\widgets\DetailView::widget([
    'model' => $model,
    'attributes' => [
        'title',
        'description:html',
        ['label' => 'Автор', 'value' => $model->author->name],
        'created_at:datetime',
    ],
]);
```

## JS и CSS из PHP

```php
$this->registerJs("$('#b').on('click', fn);", View::POS_READY, 'my-handler');
$this->registerJsFile('@web/js/main.js', ['depends' => [\yii\web\JqueryAsset::class]]);
$this->registerCss('body { background: #f00 }');
$this->registerCssFile('@web/css/print.css', ['media' => 'print']);
$this->registerJsVar('yiiOptions', $options);     // безопасная передача данных в JS
```

Позиции: `POS_HEAD`, `POS_BEGIN`, `POS_END`, `POS_READY` (по умолчанию, `$(document).ready`),
`POS_LOAD`. Передача данных из PHP в JS — только через `Json::htmlEncode()`:

```php
$this->registerJs('var opts = ' . \yii\helpers\Json::htmlEncode($options) . ';', View::POS_HEAD, 'opts');
```

> Совет: для постоянных файлов используйте asset bundles, а не `registerJsFile()` —
> получите управление зависимостями, объединение и минификацию.

## Темизация

```php
'components' => [
    'view' => [
        'theme' => [
            'basePath' => '@app/themes/basic',
            'baseUrl' => '@web/themes/basic',
            'pathMap' => [
                '@app/views' => '@app/themes/basic',
                '@app/modules' => '@app/themes/basic/modules',   // темы для модулей
                '@app/widgets' => '@app/themes/basic/widgets',
            ],
        ],
    ],
],
```

Замена работает по частичному совпадению пути: `@app/views/site/about.php` →
`@app/themes/basic/site/about.php`. В представлении доступны `$this->theme->getUrl(...)`
и `$this->theme->getPath(...)`. Значением `pathMap` может быть массив путей — тогда
используется первый существующий файл (удобно для наследования тем).
