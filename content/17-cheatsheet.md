---
id: cheatsheet
title: Быстрая шпаргалка
icon: ⌨️
summary: Yii::$app, частые сниппеты, консольные команды, структура проекта — всё на одной странице.
---

# Быстрая шпаргалка

## Yii::$app — что где лежит

```php
Yii::$app->request        // GET/POST, заголовки, куки, IP
Yii::$app->response       // код, заголовки, формат, файлы, редиректы
Yii::$app->db             // соединение с БД
Yii::$app->user           // identity, id, isGuest, login(), logout(), can()
Yii::$app->session        // сессия, flash-сообщения
Yii::$app->cache          // кеш
Yii::$app->urlManager     // разбор/создание URL
Yii::$app->view           // рендеринг, registerJs/registerCss
Yii::$app->assetManager   // публикация ресурсов
Yii::$app->formatter      // даты, числа, размеры
Yii::$app->i18n           // переводы
Yii::$app->mailer         // почта
Yii::$app->security       // хеши, шифрование, случайные строки
Yii::$app->authManager    // RBAC
Yii::$app->errorHandler   // текущее исключение
Yii::$app->log            // цели логов
Yii::$app->params['key']  // свои параметры
Yii::$app->language       // текущий язык
Yii::$app->controller     // текущий контроллер (и ->action, ->module)
Yii::$app->getModule('admin')
Yii::$container           // DI-контейнер
```

## Статические методы Yii

```php
Yii::getAlias('@app/runtime');       Yii::setAlias('@img', '@webroot/img');
Yii::createObject($config);          Yii::configure($object, $config);
Yii::t('app', 'Сообщение', $params);
Yii::debug($msg, __METHOD__);  Yii::info();  Yii::warning();  Yii::error();
Yii::beginProfile('x');  Yii::endProfile('x');
Yii::$classMap['Foo'] = '@app/Foo.php';
Yii::getVersion();
```

## Частые сниппеты контроллера

```php
// данные запроса
$id = Yii::$app->request->get('id');
$data = Yii::$app->request->post();
$isAjax = Yii::$app->request->isAjax;

// ответы
return $this->render('view', ['model' => $model]);
return $this->renderAjax('_form', ['model' => $model]);
return $this->redirect(['view', 'id' => $model->id]);
return $this->goBack();  return $this->goHome();  return $this->refresh();
return $this->asJson(['ok' => true]);
Yii::$app->response->format = Response::FORMAT_JSON;  return $data;

// flash + сохранение
if ($model->load(Yii::$app->request->post()) && $model->save()) {
    Yii::$app->session->setFlash('success', 'Сохранено');
    return $this->redirect(['index']);
}

// ошибки
throw new \yii\web\NotFoundHttpException('Не найдено');
throw new \yii\web\ForbiddenHttpException('Нет прав');

// типовой findModel
protected function findModel($id)
{
    if (($model = Post::findOne(['id' => $id])) !== null) {
        return $model;
    }
    throw new \yii\web\NotFoundHttpException('Запись не найдена.');
}
```

## Шпаргалка по Active Record

```php
Post::findOne($id);                         Post::findOne(['slug' => $slug]);
Post::findAll(['status' => 1]);
Post::find()->where(['status' => 1])->andWhere(['>', 'created_at', $ts])
    ->orderBy(['created_at' => SORT_DESC])->limit(10)->all();
Post::find()->with('author', 'tags')->all();          // жадная загрузка
Post::find()->joinWith('author')->where(['user.status' => 1])->all();
Post::find()->count();  Post::find()->exists();  Post::find()->asArray()->all();
Post::find()->select(['status', 'cnt' => 'COUNT(*)'])->groupBy('status')->all();

$post = new Post(['title' => 'X']);  $post->save();
$post->updateAttributes(['views' => 1]);              // без валидации и событий
$post->updateCounters(['views' => 1]);
Post::updateAll(['status' => 0], ['<', 'created_at', $ts]);
$post->delete();  Post::deleteAll(['status' => 0]);
$post->link('tags', $tag);  $post->unlink('tags', $tag, true);
```

## Консольные команды

```bash
php yii                                  # список команд
php yii serve --port=8080                # встроенный сервер
php yii migrate                          # применить миграции
php yii migrate/create create_post_table --fields="title:string,body:text"
php yii migrate/down 1                   # откатить
php yii cache/flush-all                  # сбросить кеши
php yii cache/flush-schema db            # сбросить кеш схемы
php yii asset assets.php config/assets-prod.php
php yii message config/i18n.php          # извлечь строки для перевода
php yii fixture/load "*"
php yii gii/model --tableName=post --modelClass=Post
php yii help <команда>
```

## Конфигурация: минимальный «боевой» набор

```php
return [
    'id' => 'app',
    'basePath' => dirname(__DIR__),
    'language' => 'ru-RU',
    'timeZone' => 'UTC',
    'bootstrap' => ['log'],
    'components' => [
        'request' => [
            'cookieValidationKey' => getenv('COOKIE_KEY'),
            'parsers' => ['application/json' => 'yii\web\JsonParser'],
        ],
        'db' => [
            'class' => 'yii\db\Connection',
            'dsn' => getenv('DB_DSN'),
            'username' => getenv('DB_USER'),
            'password' => getenv('DB_PASS'),
            'charset' => 'utf8mb4',
            'enableSchemaCache' => !YII_DEBUG,
        ],
        'cache' => ['class' => 'yii\caching\FileCache'],
        'user' => ['identityClass' => 'app\models\User', 'enableAutoLogin' => true],
        'session' => ['class' => 'yii\web\DbSession'],
        'errorHandler' => ['errorAction' => 'site/error'],
        'urlManager' => [
            'enablePrettyUrl' => true,
            'showScriptName' => false,
            'rules' => [],
        ],
        'log' => [
            'traceLevel' => YII_DEBUG ? 3 : 0,
            'targets' => [['class' => 'yii\log\FileTarget', 'levels' => ['error', 'warning']]],
        ],
    ],
    'params' => require __DIR__ . '/params.php',
];
```

## Структура проекта (basic)

```
basic/
  commands/        консольные команды
  config/          web.php, console.php, db.php, params.php
  controllers/     контроллеры
  mail/            представления писем
  migrations/      миграции
  models/          модели, формы, AR
  runtime/         логи, кеш (на запись)
  tests/           тесты
  vendor/          зависимости Composer
  views/           представления + layouts/
  web/             ПУБЛИЧНЫЙ корень: index.php, assets/, css/, js/
  yii              консольная точка входа
```

## Соглашения об именовании

| Сущность | Правило | Пример |
|---|---|---|
| Контроллер | `<Имя>Controller` в `app\controllers` | `post-comment` → `PostCommentController` |
| Действие | `action<Имя>` | `create-comment` → `actionCreateComment()` |
| Представление | `views/<controller-id>/<view>.php` | `views/post-comment/index.php` |
| Маршрут | `[модуль/]контроллер/действие` | `admin/post/update` |
| Таблица ↔ AR | `camel2id`, `{{%prefix}}` | `OrderItem` → `order_item` |
| Миграция | `m<YYMMDD_HHMMSS>_<name>` | `m150101_185401_create_news_table` |
| Asset bundle | класс-наследник `AssetBundle` | `app\assets\AppAsset` |

## Мини-словарь

- **alias** — строка с `@` вместо пути/URL (`@app`, `@web`).
- **component** — объект-наследник `Component` со свойствами, событиями и поведениями.
- **application component** — компонент в реестре `Yii::$app` (ленивый синглтон).
- **behavior** — «примесь»: добавляет объекту свойства/методы и слушает его события.
- **attribute** — свойство модели с данными (бизнес-логика).
- **asset / bundle** — файл ресурса / набор файлов с зависимостями.
- **module** — мини-приложение внутри приложения (свои MVC).
- **scenario** — режим модели, определяющий набор активных и безопасных атрибутов.
- **fixture** — фиксированный набор данных для повторяемых тестов.

## Если пришли из Yii 1.1

| Yii 1.1 | Yii 2.0 |
|---|---|
| `CComponent` | `yii\base\BaseObject` (свойства) + `yii\base\Component` (+ события, поведения) |
| `CWebApplication`, `Yii::app()` | `yii\web\Application`, `Yii::$app` |
| `CActiveRecord::model()->findAll()` | `Post::find()->all()` |
| `relations()` | геттеры `getOrders()` с `hasMany()`/`hasOne()` |
| `CDbCriteria` | `yii\db\ActiveQuery` / `yii\db\Query` |
| `$this` в виде = контроллер | `$this` = объект `View`, контроллер — `$this->context` |
| `renderPartial()` в виде | `echo $this->render()` (возвращает строку) |
| фильтры `filters()` | поведения `behaviors()` + `yii\base\ActionFilter` |
| `CWebUser`, `CUserIdentity` | `yii\web\User` + `yii\web\IdentityInterface` |
| пакеты скриптов | asset bundles (`yii\web\AssetBundle`) |
| scopes | свои классы `ActiveQuery` с методами-фильтрами |
| `unsafe` валидатор | `scenarios()` и префикс `!` |

## Куда смотреть дальше

- Полное руководство: <https://www.yiiframework.com/doc/guide/2.0/ru>
- Описание классов (API): <https://www.yiiframework.com/doc/api/2.0>
- Расширения: <https://www.yiiframework.com/extensions>
- Форум и чат сообщества: <https://forum.yiiframework.com>, Telegram/Gitter `yiisoft/yii2`
