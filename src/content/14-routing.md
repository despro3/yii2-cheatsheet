---
id: routing
title: Маршрутизация и URL
part: runtime
summary: Как URL превращается в маршрут и обратно: обычный формат и ЧПУ, правила с параметрами, суффиксы, HTTP-методы, свои классы правил и Url::to().
sources: runtime-routing
---

:::lead
**Роутинг** — разбор URL в маршрут (`post/view`) и параметры; **генерация URL** — обратный процесс. Обоими занимается компонент `urlManager`. Включив ЧПУ и описав правила, вы меняете вид адресов, не трогая код контроллеров: `Url::to(['post/view', 'id' => 100])` сам подстроится.
:::

## Два формата URL

| Формат | Пример | Настройка |
|---|---|---|
| обычный | `/index.php?r=post/view&id=100` | не нужна, работает везде |
| ЧПУ (pretty URL) | `/post/100` | `enablePrettyUrl => true` + правила + перезапись на сервере |

```php title="config/web.php"
'urlManager' => [
    'enablePrettyUrl' => true,
    'showScriptName' => false,       // без /index.php в адресах — нужна настройка веб-сервера
    'enableStrictParsing' => false,  // true: URL без подходящего правила → 404
    'rules' => [
        'posts' => 'post/index',
        'post/<id:\d+>' => 'post/view',
    ],
],
```

Без `showScriptName => false` сервер сам находит `index.php`; с ним нужны правила перезаписи из раздела [Установка](install#nastroyka-veb-servera).

## Как разбирается маршрут

После получения маршрута (из `r` или по правилам) он делится по слешам, и приложение идёт по частям:

:::steps
1. **Текущий модуль — приложение.** Часть ищется в его `controllerMap` → найден контроллер, переход к шагу 4.
2. **Иначе — среди модулей** (`modules`) → модуль становится текущим, повторяем с шага 1 для следующей части.
3. **Иначе часть — ID контроллера**, создаётся по соглашению об именах.
4. **Следующая часть — ID действия**: сначала карта `actions()`, затем метод `actionXxx()`.
:::

Любой промах — `NotFoundHttpException`. Пустой маршрут → `defaultRoute` приложения (`site/index`), маршрут из одного ID модуля → `defaultRoute` модуля (`default`) → `defaultAction` контроллера (`index`).

Режим обслуживания — все запросы в одно действие:

```php
'catchAll' => ['site/offline', 'reason' => 'update'],
```

## Генерация URL

```php
use yii\helpers\Url;

Url::to(['post/index']);                                  // /posts
Url::to(['post/view', 'id' => 100]);                      // /post/100
Url::to(['post/view', 'id' => 100, '#' => 'comments']);   // /post/100#comments
Url::to(['post/view', 'id' => 100, 'src' => 'ad']);       // /post/100?src=ad — лишние параметры уходят в query
Url::to(['post/index'], true);                            // https://example.com/posts — абсолютный
Url::to(['post/index'], 'https');                         // с явной схемой

Url::to('@web/images/logo.png');   // строка: псевдоним или URL как есть
Url::to();                         // текущий URL
Url::home();  Url::base();  Url::canonical();  Url::current(['page' => 2]);
Url::remember();  Url::previous();               // запомнить и вернуться — так работает goBack()
```

Маршрут в массиве **контекстно-зависим** — как относительный путь:

| Маршрут | Значение (текущий модуль `admin`, контроллер `post`) |
|---|---|
| `''` | текущий маршрут `admin/post/index` |
| `index` | действие текущего контроллера: `admin/post/index` |
| `post/index` | относительно текущего модуля: `admin/post/index` |
| `/post/index` | абсолютный: `post/index` |
| `@posts` | псевдоним, объявленный как маршрут |

> [!GOTCHA]
> В представлениях и виджетах, которые могут рендериться из разных модулей, пишите маршруты со слешем в начале: `['/post/view', 'id' => 1]`. Иначе ссылка «поедет» вместе с контекстом.

## Правила URL

Правило — `yii\web\UrlRule` (или свой класс): шаблон + маршрут + опции. Правила проверяются **по порядку** до первого совпадения — и при разборе, и при генерации.

```php
'rules' => [
    // краткая форма: шаблон => маршрут
    'posts' => 'post/index',
    'posts/<year:\d{4}>/<category>' => 'post/index',
    'post/<id:\d+>' => 'post/view',

    // параметры в маршруте: одно правило вместо шести
    '<controller:(post|comment)>/<id:\d+>/<action:(create|update|delete)>' => '<controller>/<action>',
    '<controller:(post|comment)>/<id:\d+>' => '<controller>/view',
    '<controller:(post|comment)>s' => '<controller>/index',

    // полная форма — когда нужны опции
    [
        'pattern' => 'posts/<page:\d+>/<tag>',
        'route' => 'post/index',
        // необязательные параметры: /posts, /posts/2, /posts/2/news, /posts/news
        'defaults' => ['page' => 1, 'tag' => ''],
        'suffix' => '.json',
    ],

    // ограничение по HTTP-методу учитывается только при разборе;
    // при генерации ссылки метод не смотрят, поэтому правило может сработать и там
    'PUT,POST post/<id:\d+>' => 'post/update',
    'DELETE post/<id:\d+>' => 'post/delete',

    // имена серверов: поддомен → параметр
    'http://<language:\w+>.example.com/posts' => 'post/index',
    'https://admin.example.com/login' => 'admin/user/login',
],
```

Именованный параметр `<name:regexp>` без регулярки принимает всё, кроме `/`. Разобранные параметры попадают в `$_GET` и в аргументы действия.

### Суффиксы и нормализация

```php
'urlManager' => [
    // все URL — с .html; без суффикса → 404 (хорошо для SEO); '/' — завершающий слеш
    'suffix' => '.html',
    'normalizer' => [
        'class' => 'yii\web\UrlNormalizer',   // /path/ и /path//x → 301 на канонический вид
        'action' => \yii\web\UrlNormalizer::ACTION_REDIRECT_TEMPORARY,
    ],
],
```

Суффикс и нормализатор можно переопределить у отдельного правила (`'suffix' => '.json'`, `'normalizer' => false`).

### Правила из модулей

Добавлять правила нужно на этапе [предзагрузки](lifecycle), иначе они не успеют к разбору запроса:

```php
public function bootstrap($app)
{
    $app->urlManager->addRules([
        ['class' => 'yii\web\GroupUrlRule', 'prefix' => 'forum', 'rules' => [
            'posts' => 'post/index',
            'post/<id:\d+>' => 'post/view',
        ]],
    ], false);
}
```

`GroupUrlRule` объединяет правила с общим префиксом — быстрее, чем перебирать их по одному.

### Свой класс правила

Когда шаблон зависит от данных (например, `/Марка/Модель` из БД), реализуют `UrlRuleInterface`:

```php
namespace app\components;

use yii\base\BaseObject;
use yii\web\UrlRuleInterface;

class CarUrlRule extends BaseObject implements UrlRuleInterface
{
    public function createUrl($manager, $route, $params)
    {
        if ($route === 'car/index' && isset($params['manufacturer'])) {
            return $params['manufacturer'] . (isset($params['model']) ? '/' . $params['model'] : '');
        }
        return false;   // правило не применимо
    }

    public function parseRequest($manager, $request)
    {
        if (preg_match('%^(\w+)(/(\w+))?$%', $request->pathInfo, $m)) {
            // проверить $m[1], $m[3] по базе и вернуть ['car/index', $params]
        }
        return false;
    }
}
```

```php
'rules' => [['class' => 'app\components\CarUrlRule']],
```

## Производительность

- Правила с параметрами в маршруте (`<controller>/<action>`) заменяют десятки конкретных.
- Частые и узкие правила — выше в списке.
- Правила с общим префиксом — в `GroupUrlRule`.
- Для REST — готовый `yii\rest\UrlRule` (см. [REST](rest)).

:::quiz Проверь себя
Q: Чем отличаются `enableStrictParsing = true` и `false`?
A: При строгом разборе URL без подходящего правила даёт 404; иначе путь трактуется как маршрут напрямую (`/posts/php` → маршрут `posts/php`).
Q: Что произойдёт при `Url::to(['post/index', 'category' => 'php'])`, если ни одно правило не подходит?
A: URL соберётся «в лоб»: `/post/index?category=php` — маршрут как путь, параметры как query string.
Q: Учитывается ли HTTP-метод правила при генерации ссылки?
A: Нет: `verb` смотрят только при разборе запроса. Само правило из генерации не исключается — `Url::to(['post/delete', 'id' => 1])` вполне может собрать адрес по правилу `'DELETE post/<id:\d+>'`. Чтобы правило работало только на разбор, задайте ему `'mode' => UrlRule::PARSING_ONLY`.
Q: Как сделать параметр правила необязательным?
A: Указать его значение по умолчанию в `defaults` полной формы правила.
Q: Где модуль должен регистрировать свои правила URL?
A: В методе `bootstrap()` (модуль включён в `bootstrap` приложения), не в `init()`.
:::
