---
id: helpers
title: Хелперы
part: special
summary: Статические классы yii\helpers — ArrayHelper (getValue, map, index, merge, multisort, toArray), Html (теги, ссылки, формы, active-поля, CSS-классы), Json (encode/decode, JsExpression, htmlEncode), Url (to, toRoute, current, canonical, remember/previous), а также Inflector, StringHelper, FileHelper, VarDumper, Console, Markdown.
sources: helper-overview, helper-array, helper-html, helper-json, helper-url
---

:::lead
Хелперы — статические классы для рутины: безопасно достать значение из массива, собрать тег с экранированием, построить URL по маршруту, закодировать JSON. Расширяются наследованием: `class Html extends BaseHtml` — каждый хелпер состоит из `BaseXxx` с логикой и тонкого `Xxx`, который можно подменить.
:::

## ArrayHelper

```php
use yii\helpers\ArrayHelper;

// достать значение — из массива или объекта, с вложенностью и значением по умолчанию
$name = ArrayHelper::getValue($user, 'name', 'anon');
// $user['address']['street'] или $user->address->street
$street = ArrayHelper::getValue($user, 'address.street');
$val = ArrayHelper::getValue($arr, ['x', 'y']);                     // ключ с точкой — массивом
$fullName = ArrayHelper::getValue($user, function ($user, $default) { return $user->first . ' ' . $user->last; });
ArrayHelper::setValue($array, 'key.subkey', $value);
ArrayHelper::keyExists('Name', $array, false);                      // регистронезависимо
ArrayHelper::remove($array, 'type', 'default');                     // достать и удалить

// столбцы, карты, индексы
ArrayHelper::getColumn($posts, 'id');                               // [1, 2, 3]
ArrayHelper::getColumn($posts, function ($p) { return $p->title; });
ArrayHelper::map($countries, 'code', 'name');                       // ['RU' => 'Россия'] — для dropDownList
ArrayHelper::map($countries, 'code', 'name', 'continent');          // с группировкой
ArrayHelper::index($users, 'id');                                   // [id => row]
ArrayHelper::index($users, 'id', 'group');                          // [group => [id => row]]
ArrayHelper::index($users, null, 'group');                          // [group => [row, row]]

// объединение и сортировка
// рекурсивно, с UnsetArrayValue / ReplaceArrayValue
$config = ArrayHelper::merge($base, $override);
ArrayHelper::multisort($data, ['age', 'name'], [SORT_ASC, SORT_DESC]);
ArrayHelper::multisort($data, function ($item) { return $item['a'] . $item['b']; });

// прочее
ArrayHelper::toArray($model, [User::class => ['id', 'email', 'fullName' => function ($u) { return $u->name; }]]);
ArrayHelper::isAssociative($arr); ArrayHelper::isIndexed($arr);
ArrayHelper::isIn('a', $arr); ArrayHelper::isSubset(['a'], $arr);
ArrayHelper::htmlEncode($data); ArrayHelper::htmlDecode($data);     // рекурсивно
ArrayHelper::filter($array, ['A.B', '!A.C']);                       // оставить/исключить ключи
ArrayHelper::isTraversable($x);
```

`merge()` — то, что `yii\web\Application` делает с конфигурациями: `new \yii\helpers\UnsetArrayValue()` удаляет ключ, `ReplaceArrayValue` заменяет массив целиком вместо слияния.

## Html

Все методы **экранируют** данные (кроме уже готового HTML в `content`):

```php
use yii\helpers\Html;

Html::encode($text); Html::decode($html);
// null — атрибут не выводится
Html::tag('div', Html::encode($content), ['class' => 'box', 'data' => ['id' => 5], 'id' => null]);
Html::beginTag('div', ['class' => 'x']) … Html::endTag('div');
Html::a('Профиль', ['user/view', 'id' => 42], ['class' => 'btn']);   // маршрут → URL через Url::to()
Html::a('Сайт', 'https://example.com', ['target' => '_blank']);
Html::mailto('Написать', 'admin@example.com');
Html::img('@web/images/logo.png', ['alt' => 'Logo']);                // псевдонимы понимает
Html::img('/img/x.png', ['srcset' => ['100w' => '/x@1.png', '200w' => '/x@2.png']]);
Html::ul($items, ['item' => function ($item, $index) { return Html::tag('li', Html::encode($item)); }]);
Html::ol($items, ['encode' => true]);
Html::style('.x{color:red}'); Html::script('alert(1)'); Html::cssFile('@web/css/a.css'); Html::jsFile('@web/js/a.js');
Html::csrfMetaTags();
```

### CSS-классы и стили

```php
$options = ['class' => 'btn'];
Html::addCssClass($options, 'btn-primary');            // 'btn btn-primary'; дубли не добавляются
Html::addCssClass($options, ['btn-lg', 'x']);
Html::removeCssClass($options, 'btn');
Html::addCssStyle($options, 'width: 100px');           // 'style' => 'width: 100px'
Html::addCssStyle($options, ['color' => 'red'], false); // не перезаписывать существующее
Html::removeCssStyle($options, 'width');
Html::cssStyleFromArray(['width' => '100px']); Html::cssStyleToArray('width: 100px');
Html::renderTagAttributes(['class' => 'a', 'data' => ['x' => 1]]);   // ' class="a" data-x="1"'
```

### Формы

```php
Html::beginForm(['order/update', 'id' => $id], 'post', ['enctype' => 'multipart/form-data']) … Html::endForm();
Html::input('text', 'username', $value, ['class' => 'form-control']);
Html::textInput('username', $value); Html::passwordInput('pw'); Html::hiddenInput('id', 1);
Html::textarea('text', $value, ['rows' => 5]);
Html::checkbox('agree', $checked, ['label' => 'Согласен', 'uncheck' => 0]);
Html::radio('type', $checked, ['value' => 'a']);
Html::dropDownList('country', $selected, $items, ['prompt' => '—', 'options' => ['RU' => ['disabled' => true]]]);
Html::listBox('tags', $selected, $items, ['multiple' => true]);
Html::checkboxList('tags', $selected, $items, ['separator' => '<br>']);
Html::radioList('type', $selected, $items, ['item' => function ($index, $label, $name, $checked, $value) { … }]);
Html::submitButton('Сохранить', ['class' => 'btn']); Html::resetButton(); Html::button('Кнопка');
Html::fileInput('file');

// active* — по модели и атрибуту: имя LoginForm[username], id loginform-username, значение из модели
Html::activeTextInput($model, 'username', ['class' => 'form-control']);
Html::activeDropDownList($model, 'country', $items);
Html::activeLabel($model, 'username'); Html::activeHint($model, 'username');
Html::error($model, 'username'); Html::errorSummary($model);
Html::activeCheckbox($model, 'agree');
Html::getInputName($model, 'attr'); Html::getInputId($model, 'attr');
```

`ActiveForm` и `ActiveField` — обёртки над этими `active*` методами.

## Json

```php
use yii\helpers\Json;
use yii\web\JsExpression;

// JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES по умолчанию (2.0.x), объекты Arrayable → массивы
Json::encode($data);
// без кавычек — для JS-конфигураций виджетов
Json::encode(['fn' => new JsExpression('function () { return 1; }')]);
Json::htmlEncode($data);                   // безопасно для вставки в HTML-атрибуты и <script>
// всегда массив (assoc = true); бросает InvalidArgumentException при ошибке
Json::decode($json);
Json::decode($json, false);                // stdClass
Json::$prettyPrint = true;                 // отладка (статическое свойство)
Json::errorSummary($model);                // ошибки модели как JSON
```

`JsExpression` — единственный способ вставить в JSON JS-код (например, колбэк в опции jQuery-плагина).

## Url

```php
use yii\helpers\Url;

Url::to(['post/view', 'id' => 1]);           // маршрут → /post/1 через urlManager
Url::to(['post/view', 'id' => 1], true);     // абсолютный: https://host/post/1
Url::to(['post/view', 'id' => 1], 'https'); // с заданной схемой
// ведущий / — от корня приложения (не относительно модуля/контроллера)
Url::to(['/site/index']);
Url::to(['index']);                          // относительно текущего контроллера
Url::to(['']);                               // текущий маршрут (с параметрами — нет; см. current)
Url::to('@web/images/logo.png');             // псевдоним
Url::to('/images/x.png'); Url::to('https://…');   // как есть
Url::to();                                   // текущий URL

Url::toRoute('post/index'); Url::toRoute(['post/view', 'id' => 1]);
Url::current();                              // текущий URL со всеми GET-параметрами
Url::current(['page' => 2]);                 // …с добавленным/заменённым параметром
Url::current(['page' => null]);              // …без параметра
Url::home(); Url::base(); Url::base(true);   // домашняя, базовая (с/без хоста)
Url::canonical();                            // для <link rel="canonical"> — маршрут + параметры действия
Url::remember(); Url::previous();            // сохранить/достать URL (в сессии) — для «вернуться назад»
Url::isRelative($url); Url::ensureScheme('//host/path', 'https');
```

Правило: маршруты в `Html::a()`, `redirect()`, `Url::to()` — всегда массивом `['controller/action', 'param' => …]`, а не строками, чтобы работали правила `urlManager`.

## Остальные хелперы

:::kv
`Inflector` — `pluralize('person')` → people, `singularize`, `camelize`, `camel2id('PostTag')` → post-tag, `id2camel`, `humanize`, `slug('Привет мир')` → privet-mir, `titleize`, `classify`, `tableize`, `ordinalize(1)` → 1st
`StringHelper` — `byteLength`, `byteSubstr`, `truncate($s, 20, '…')`, `truncateWords`, `startsWith`, `endsWith`, `explode($s, ',', true, true)` (строка первым аргументом; trim + skip empty), `basename`, `dirname`, `mb_ucfirst`, `base64UrlEncode`
`FileHelper` — `normalizePath`, `findFiles($dir, ['only' => ['*.php'], 'except' => ['/tests/']])`, `createDirectory`, `removeDirectory`, `copyDirectory`, `getMimeType`, `getExtensionsByMimeType`, `localize`
`VarDumper` — `dump($var, $depth, $highlight)`, `dumpAsString`, `export` — читаемый вывод любых структур
`Console` — цвета, `ansiFormat`, `prompt`, `confirm`, `select`, прогресс-бары, `wrapText`, `getScreenSize`
`Markdown` — `process($md, 'gfm')`, `processParagraph`
`HtmlPurifier` — `process($html, $config)` — очистка HTML
`FormatConverter` — ICU ↔ PHP форматы дат (`convertDateIcuToPhp`)
`IpHelper` — `inRange`, `expandIPv6`, `getIpVersion`, `ip2bin`
`BaseObject`-хелперы для подмены: `class Html extends \yii\helpers\BaseHtml` и `Yii::$classMap['yii\helpers\Html'] = '@app/components/Html.php'`
:::

Подмена хелпера: наследуйте от `BaseHtml`, назовите класс `Html` в своём пространстве имён и импортируйте его вместо `yii\helpers\Html`; либо через `classMap`, чтобы подменить глобально (включая код фреймворка).

:::quiz Проверь себя
Q: Как безопасно получить `$user['address']['city']`, если ключей может не быть?
A: `ArrayHelper::getValue($user, 'address.city', $default)` — работает и с объектами.
Q: Чем `ArrayHelper::map()` отличается от `index()`?
A: `map()` строит `[ключ => значение поля]` (для списков), `index()` — `[ключ => целый элемент]`.
Q: Как передать JavaScript-функцию в JSON-опции виджета?
A: Обернуть в `new JsExpression('function () {…}')` — `Json::encode()` вставит её без кавычек.
Q: В чём разница между `Url::to(['index'])` и `Url::to(['/index'])`?
A: Без `/` маршрут относительно текущего контроллера (`post/index`), с `/` — абсолютный маршрут от корня приложения, даже внутри модуля.
Q: Как добавить CSS-класс к массиву опций, не затирая существующие?
A: `Html::addCssClass($options, 'new-class')`.
:::
