---
id: controllers
title: Контроллеры и действия
part: structure
summary: Как маршрут превращается в вызов метода, чем встроенные действия отличаются от отдельных, откуда берутся параметры и что может вернуть действие.
sources: structure-controllers
---

:::lead
Контроллер принимает запрос, дёргает модели и отдаёт результат в представление. Он состоит из **действий** — публичных методов `actionXxx()` или отдельных классов. Маршрут `post/view` — это `PostController::actionView()`.
:::

## Минимальный контроллер

```php title="controllers/PostController.php"
namespace app\controllers;

use Yii;
use app\models\Post;
use yii\web\Controller;
use yii\web\NotFoundHttpException;

class PostController extends Controller
{
    public function actionView($id)
    {
        $model = Post::findOne($id);
        if ($model === null) {
            throw new NotFoundHttpException();          // → страница 404
        }
        return $this->render('view', ['model' => $model]);
    }

    public function actionCreate()
    {
        $model = new Post();
        if ($model->load(Yii::$app->request->post()) && $model->save()) {
            return $this->redirect(['view', 'id' => $model->id]);
        }
        return $this->render('create', ['model' => $model]);
    }
}
```

Веб-контроллеры наследуют `yii\web\Controller`, консольные — `yii\console\Controller`.

## Маршруты и имена

Маршрут: `контроллер/действие` или `модуль/контроллер/действие`. Идентификаторы — в нижнем регистре, слова через дефис.

| ID контроллера | Класс |
|---|---|
| `article` | `app\controllers\ArticleController` |
| `post-comment` | `app\controllers\PostCommentController` |
| `admin/post-comment` | `app\controllers\admin\PostCommentController` (подпапка без модуля) |

Пространство имён задаёт `controllerNamespace` приложения (по умолчанию `app\controllers`). Если соглашение не подходит — например, контроллер из чужой библиотеки — используйте карту:

```php
'controllerMap' => [
    'account' => 'app\controllers\UserController',
    'article' => [
        'class' => 'app\controllers\PostController',
        'enableCsrfValidation' => false,
    ],
],
```

Маршрут без действия → `defaultAction` контроллера (`index`); запрос без маршрута → `defaultRoute` приложения (`site`). Оба можно переопределить:

```php
class SiteController extends Controller
{
    public $defaultAction = 'home';
}
```

## Действия {#deystviya}

### Встроенные (inline)

Публичный метод с префиксом `action`. Имя метода — из ID действия: `hello-world` → `actionHelloWorld`.

> [!GOTCHA]
> Имена регистрозависимы: `ActionIndex()` действием не считается. Методы `protected`/`private` тоже — только `public`.

### Отдельные (standalone)

Класс, унаследованный от `yii\base\Action`, с методом `run()`. Регистрируется в карте действий контроллера. Так удобно переиспользовать действия между контроллерами и в расширениях:

```php
public function actions()
{
    return [
        'error' => 'yii\web\ErrorAction',                      // страница ошибки
        'captcha' => ['class' => 'yii\captcha\CaptchaAction'],
        'page' => ['class' => 'yii\web\ViewAction', 'viewPrefix' => 'pages'],   // статические страницы
    ];
}
```

```php title="components/HelloWorldAction.php"
namespace app\components;

use yii\base\Action;

class HelloWorldAction extends Action
{
    public $greeting = 'Hello';

    public function run($name = 'World')
    {
        return "{$this->greeting}, {$name}";
    }
}
```

ID отдельных действий могут быть любыми — они заданы явно в `actions()`.

### Результат действия

| Что вернули | Что произойдёт |
|---|---|
| строка | станет телом ответа (обычно результат `$this->render()`) |
| объект `Response` | отправится как есть — так работает `$this->redirect()` |
| массив / любые данные | попадёт в `Response::data` и отформатируется по `Response::format` (JSON, XML…) |
| число в консоли | код выхода команды |

```php
public function actionForward()
{
    return $this->redirect('https://example.com');   // redirect() возвращает Response
}

public function actionInfo()
{
    Yii::$app->response->format = \yii\web\Response::FORMAT_JSON;
    return ['message' => 'hello', 'code' => 100];
}
```

### Параметры действий

Параметры метода заполняются из `$_GET` по имени (в консоли — из аргументов командной строки):

```php
public function actionView($id, $version = null) { /* ... */ }
```

- `?r=post/view&id=123` → `$id = '123'`, `$version = null`;
- `?r=post/view` → `BadRequestHttpException` — обязательный параметр не передан;
- `?r=post/view&id[]=123` → `BadRequestHttpException` — ожидался скаляр, пришёл массив.

Чтобы принять массив, укажите тип: `public function actionView(array $id)` — тогда скаляр автоматически обернётся в массив.

> [!TIP]
> Именно поэтому `Post::findOne($id)` с параметром действия безопасен: Yii гарантирует, что `$id` — скаляр. А вот `findOne(Yii::$app->request->get('id'))` — нет: пользователь может передать массив и подменить условие поиска.

## Жизненный цикл контроллера

:::steps
1. **`init()`** — контроллер создан и сконфигурирован.
2. **Создание действия** по ID: сначала карта `actions()`, затем метод `actionXxx()`, иначе `InvalidRouteException`.
3. **`beforeAction()`** последовательно у приложения, модуля и контроллера. Вернул `false` — остальные пропускаются, действие не выполняется. Здесь работают [фильтры](filters).
4. **Выполнение действия** с параметрами из запроса.
5. **`afterAction()`** в обратном порядке: контроллер → модуль → приложение.
6. **Результат** уходит в компонент `response`.
:::

## Что ещё умеет контроллер

:::kv
`render($view, $params)` — представление + шаблон (layout)
`renderPartial($view, $params)` — без шаблона
`renderAjax($view, $params)` — без шаблона, но с зарегистрированными JS/CSS — для ответов на AJAX
`renderContent($html)` — обернуть готовую строку в шаблон
`redirect($url, $statusCode = 302)` — перенаправление; `$url` может быть маршрутом-массивом
`goHome()`, `goBack()`, `refresh()` — на главную, на предыдущий URL (см. `Url::remember()`), перезагрузка текущей страницы
`asJson($data)`, `asXml($data)` — ответ в нужном формате без правки `response->format`
`behaviors()` — фильтры контроллера: доступ, HTTP-методы, кеш
`$layout` — свой шаблон для этого контроллера; `false` — без шаблона
`$enableCsrfValidation` — проверка CSRF-токена для POST (по умолчанию включена)
:::

## Типичный CRUD

Так выглядит контроллер, который генерирует Gii, — хороший образец «тонкого» контроллера:

```php
use yii\filters\VerbFilter;
use yii\web\NotFoundHttpException;

class PostController extends Controller
{
    public function behaviors()
    {
        return [
            'verbs' => [
                'class' => VerbFilter::class,
                'actions' => ['delete' => ['POST']],
            ],
        ];
    }

    public function actionIndex()
    {
        $searchModel = new PostSearch();
        $dataProvider = $searchModel->search(Yii::$app->request->queryParams);
        return $this->render('index', compact('searchModel', 'dataProvider'));
    }

    public function actionUpdate($id)
    {
        $model = $this->findModel($id);
        if ($model->load(Yii::$app->request->post()) && $model->save()) {
            Yii::$app->session->setFlash('success', 'Сохранено');
            return $this->redirect(['view', 'id' => $model->id]);
        }
        return $this->render('update', ['model' => $model]);
    }

    public function actionDelete($id)
    {
        $this->findModel($id)->delete();
        return $this->redirect(['index']);
    }

    protected function findModel($id)
    {
        if (($model = Post::findOne($id)) !== null) {
            return $model;
        }
        throw new NotFoundHttpException('Запись не найдена.');
    }
}
```

> [!WHY]
> Контроллер должен быть тонким: читать запрос, вызывать модели и сервисы, выбирать представление. Бизнес-логика живёт в [моделях](models), HTML — в [представлениях](views). Если контроллер разросся, это сигнал вынести код.

:::quiz Проверь себя
Q: Какой метод будет вызван для маршрута `admin/post-comment/create-reply`, если модуля `admin` нет?
A: `app\controllers\admin\PostCommentController::actionCreateReply()` — префикс до слеша трактуется как подпапка пространства имён.
Q: Чем отдельное действие лучше встроенного?
A: Это самостоятельный класс: его можно переиспользовать в разных контроллерах, настраивать через конфигурацию и распространять в расширениях (`ErrorAction`, `CaptchaAction`, `ViewAction`).
Q: Что случится, если действие объявлено как `actionView($id)`, а в запросе нет `id`?
A: Будет выброшено `BadRequestHttpException` (HTTP 400) ещё до выполнения действия.
Q: Как вернуть JSON из действия?
A: Установить `Yii::$app->response->format = Response::FORMAT_JSON` и вернуть массив, либо вызвать `return $this->asJson($data)`.
Q: В каком порядке вызываются `beforeAction()` приложения, модуля и контроллера?
A: Приложение → модуль → контроллер; любой `false` останавливает цепочку.
:::
