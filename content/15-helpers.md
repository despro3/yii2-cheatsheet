---
id: helpers
title: Хелперы
icon: 🧰
summary: ArrayHelper, Html, Url, Json, StringHelper, FileHelper, Inflector и другие.
---

# Хелперы

Статические классы в `yii\helpers`. У каждого есть базовый класс (`BaseArrayHelper`) —
используйте всегда конкретный (`ArrayHelper`), а для подмены реализации наследуйте базовый
и подставьте через `Yii::$classMap`.

Полный список: `ArrayHelper`, `Html`, `HtmlPurifier`, `Url`, `Json`, `StringHelper`,
`FileHelper`, `Inflector`, `Console`, `FormatConverter`, `Markdown`, `VarDumper`,
`IpHelper`, `Imagine` (расширение `yii2-imagine`).

## ArrayHelper

```php
use yii\helpers\ArrayHelper;

// Чтение вложенных значений — без isset-лапши
ArrayHelper::getValue($array, 'foo.bar.name', 'по умолчанию');
ArrayHelper::getValue($user, fn ($u, $default) => $u->firstName . ' ' . $u->lastName);
ArrayHelper::setValue($array, 'key.in', ['arr' => 'val']);
$type = ArrayHelper::remove($array, 'type');            // вернуть и удалить

ArrayHelper::keyExists('username', $data, false);       // без учёта регистра

// Столбцы, индексация, пары
ArrayHelper::getColumn($rows, 'id');
ArrayHelper::index($rows, 'id');                        // ['123' => [...], ...]
ArrayHelper::index($rows, null, 'class');               // группировка
ArrayHelper::map($rows, 'id', 'name');                  // для dropDownList
ArrayHelper::map($rows, 'id', 'name', 'class');         // с группировкой

// Сортировка и проверки
ArrayHelper::multisort($data, ['age', 'name'], [SORT_ASC, SORT_DESC]);
ArrayHelper::isIndexed($array);  ArrayHelper::isAssociative($array);
ArrayHelper::isIn('a', $traversable);  ArrayHelper::isSubset($a, $b);

// Прочее
ArrayHelper::merge($a, $b, $c);                         // рекурсивное слияние
ArrayHelper::htmlEncode($data);  ArrayHelper::htmlDecode($data);
ArrayHelper::flatten($nested, '.');                     // ['a.b.c' => 1]
ArrayHelper::filter($array, ['A', '!A.B']);             // выборка по путям
ArrayHelper::toArray($posts, [
    Post::class => ['id', 'title', 'createTime' => 'created_at',
                    'length' => fn ($post) => strlen($post->content)],
]);
```

> Важно: `ArrayHelper::merge()` перезаписывает строковые ключи последним значением
> (в отличие от `array_merge_recursive`), а элементы с числовыми ключами — добавляет.
> Именно поэтому им удобно сливать конфиги.

## Html

```php
use yii\helpers\Html;

Html::encode($text);  Html::decode($html);
Html::tag('p', Html::encode($name), ['class' => 'username']);
Html::beginTag('div', $options) . Html::endTag('div');

// CSS-классы и стили в массиве опций
Html::addCssClass($options, ['btn-success', 'btn-lg']);      // без дублей
Html::removeCssClass($options, 'btn-default');
Html::addCssStyle($options, ['height' => '200px']);
Html::removeCssStyle($options, ['width', 'height']);
Html::cssStyleFromArray($styles);  Html::cssStyleToArray($style);

// Ссылки, письма, картинки, списки
Html::a('Профиль', ['user/view', 'id' => $id], ['class' => 'link']);
Html::mailto('Написать', 'admin@example.com');
Html::img('@web/images/logo.png', ['alt' => 'Логотип']);
Html::ul($items, ['item' => fn ($item, $i) => Html::tag('li', $item)]);
Html::ol($items);

// Стили и скрипты
Html::style('.danger { color: #f00 }', ['media' => 'print']);
Html::script('alert(1);');
Html::cssFile('@web/css/print.css', ['media' => 'print']);
Html::jsFile('@web/js/main.js');
Html::csrfMetaTags();

// Формы
Html::beginForm(['order/update', 'id' => $id], 'post', ['enctype' => 'multipart/form-data']);
Html::endForm();
Html::submitButton('Отправить');  Html::button('Кнопка');  Html::resetButton('Сброс');

// Поля ввода: обычные и «active» (значение берётся из модели)
Html::textInput('username', $value, $options);
Html::activeTextInput($model, 'username', $options);
Html::activeHiddenInput($model, 'version');
Html::activePasswordInput($model, 'password');
Html::activeFileInput($model, 'file');
Html::activeTextarea($model, 'about');
Html::activeCheckbox($model, 'agree');   Html::activeRadio($model, 'type');
Html::activeDropDownList($model, 'id', ArrayHelper::map($rows, 'id', 'name'));
Html::activeListBox($model, 'ids', $items);
Html::activeCheckboxList($model, 'roles', $items);
Html::activeRadioList($model, 'role', $items);

// Метки, ошибки, служебные имена
Html::activeLabel($model, 'username');
Html::errorSummary($models, ['class' => 'errors']);
Html::error($model, 'title');
Html::getInputName($model, 'title');    // Post[title]
Html::getInputId($model, 'title');      // post-title
Html::getAttributeValue($model, '[0]authors[0]');
Html::getAttributeName('dates[0]');     // dates
```

Обработка массива опций: `null` — атрибут не выводится, `true/false` — логический атрибут,
значения экранируются, `'data' => ['id' => 1]` → `data-id="1"`, вложенный массив в
data-атрибуте → JSON.

```php
use yii\helpers\HtmlPurifier;
echo HtmlPurifier::process($userHtml);              // очистка HTML от XSS (медленно — кешируйте)
```

## Url

```php
use yii\helpers\Url;

Url::home();  Url::home(true);  Url::home('https');
Url::base();  Url::base(true);
Url::toRoute('site/index');
Url::toRoute(['post/view', 'id' => 42, '#' => 'comments']);
Url::to(['post/index', 'page' => 2]);
Url::to('@web/images/logo.gif', true);
Url::to();                                   // текущий URL
Url::current(['page' => 2]);                 // текущий маршрут + изменённые GET-параметры
Url::current(['src' => null]);               // удалить параметр
Url::canonical();
Url::remember();  Url::previous();
Url::remember(['product/view', 'id' => 42], 'product');  Url::previous('product');
Url::isRelative('test/it');
```

## Json

```php
use yii\helpers\Json;

Json::encode($data);                        // JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
Json::encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
Json::htmlEncode($data);                    // безопасно для вставки в HTML/JS
Json::decode($json);                        // в массив
Json::$prettyPrint = YII_DEBUG;             // глобально

Json::encode(['fn' => new \yii\web\JsExpression('function () { return 1; }')]);  // JS-выражение не экранируется
```

## StringHelper

```php
use yii\helpers\StringHelper;

StringHelper::byteLength($str);  StringHelper::byteSubstr($str, 0, 10);
StringHelper::truncate($str, 30, '…');
StringHelper::truncateWords($str, 10);
StringHelper::startsWith($str, 'Yii');  StringHelper::endsWith($str, '.php');
StringHelper::basename('app\models\Post');       // Post — удобно для имени класса
StringHelper::dirname($path);
StringHelper::explode('a, b, c', ',', true, true);
StringHelper::countWords($str);
StringHelper::normalizeNumber('4.2');
StringHelper::base64UrlEncode($str);  StringHelper::base64UrlDecode($str);
StringHelper::matchWildcard('*.example.com', $host);
StringHelper::mb_ucfirst($str);  StringHelper::mb_ucwords($str);
```

## FileHelper

```php
use yii\helpers\FileHelper;

FileHelper::createDirectory('@runtime/export', 0775, true);
FileHelper::copyDirectory($src, $dst, ['only' => ['*.php'], 'except' => ['.svn/']]);
FileHelper::removeDirectory($dir);
FileHelper::findFiles('@app/views', ['only' => ['*.php'], 'recursive' => true]);
FileHelper::findDirectories($dir);
FileHelper::getMimeType('/path/file.pdf');
FileHelper::getExtensionsByMimeType('image/jpeg');
FileHelper::normalizePath($path);
FileHelper::localize('@app/views/site/index.php');   // версия под текущий язык
```

## Inflector

```php
use yii\helpers\Inflector;

Inflector::pluralize('box');          // boxes
Inflector::singularize('boxes');      // box
Inflector::camelize('post_comment');  // PostComment
Inflector::camel2words('PostComment');// Post Comment
Inflector::camel2id('PostComment');   // post-comment
Inflector::id2camel('post-comment');  // PostComment
Inflector::underscore('PostComment'); // post_comment
Inflector::slug('Привет, мир!', '-'); // privet-mir (нужен intl для транслитерации)
Inflector::titleize($str);
Inflector::ordinalize(21);            // 21st
Inflector::sentence(['a', 'b', 'c']); // a, b and c
```

## Прочее

```php
use yii\helpers\{VarDumper, Markdown, FormatConverter, IpHelper, Console};

VarDumper::dump($var, 10, true);              // безопасный var_dump с подсветкой
VarDumper::export($var);                      // валидный PHP-код
echo Markdown::process($text, 'gfm');         // Markdown → HTML
FormatConverter::convertDateIcuToPhp('yyyy-MM-dd');
IpHelper::inRange('192.168.1.5', '192.168.0.0/16');
Console::stdout(Console::ansiFormat('OK', [Console::FG_GREEN]));
```
