---
id: cheatsheet
title: Памятка на одну страницу
part: extra
summary: Самое нужное из всего руководства в одном месте — команды, конфигурация, контроллер, модель, Active Record, формы, URL, доступ, кэш, миграции, консоль, REST. Для быстрого «как это писалось».
sources:
---

:::lead
Самое сжатое, что есть в курсе: только код и короткие пояснения. Заголовок каждого блока ведёт в подробный раздел. Держите открытой рядом с редактором.
:::

## Установка и команды → [Установка](install)

```bash
# шаблон basic
composer create-project --prefer-dist yiisoft/yii2-app-basic myapp
# шаблон advanced (после установки: cd myapp && php init)
composer create-project --prefer-dist yiisoft/yii2-app-advanced myapp

./yii serve --port=8080          # dev-сервер → http://localhost:8080
./yii help                       # все команды
./yii migrate                    # применить миграции
./yii cache/flush-all            # сбросить кэш
./yii gii/model --tableName=post --modelClass=Post
```

## Конфигурация → [Конфигурации](configurations), [Приложение](app)

```php title="config/web.php"
return [
    'id' => 'app',
    'basePath' => dirname(__DIR__),
    'bootstrap' => ['log'],
    'language' => 'ru-RU',
    'aliases' => ['@uploads' => '@webroot/uploads'],
    'components' => [
        'db' => [
            'class' => 'yii\db\Connection',
            'dsn' => 'mysql:host=localhost;dbname=app',
            'username' => 'root',
            'password' => '',
            'charset' => 'utf8mb4',
            'enableSchemaCache' => !YII_DEBUG,
        ],
        'cache' => ['class' => 'yii\caching\FileCache'],
        'user' => ['identityClass' => 'app\models\User', 'enableAutoLogin' => true],
        'request' => [
            'cookieValidationKey' => 'random-string',
            'parsers' => ['application/json' => 'yii\web\JsonParser'],
        ],
        'urlManager' => [
            'enablePrettyUrl' => true,
            'showScriptName' => false,
            'rules' => ['post/<id:\d+>' => 'post/view'],
        ],
        'errorHandler' => ['errorAction' => 'site/error'],
        'log' => [
            'traceLevel' => YII_DEBUG ? 3 : 0,
            'targets' => [
                ['class' => 'yii\log\FileTarget', 'levels' => ['error', 'warning']],
            ],
        ],
        'mailer' => ['class' => \yii\symfonymailer\Mailer::class, 'useFileTransport' => YII_ENV_DEV],
    ],
    'modules' => ['admin' => ['class' => 'app\modules\admin\Module']],
    'params' => ['adminEmail' => 'admin@example.com'],
];
```

```php
// любой объект по конфигурации
$obj = Yii::createObject([
    'class' => Foo::class,
    'prop' => 1,
    'on eventName' => $handler,     // подписка на событие
    'as behaviorName' => [...],     // поведение
]);

// псевдонимы: @app @web @webroot @runtime @vendor @yii
Yii::getAlias('@app/runtime');
Yii::$app->params['adminEmail'];
```

## Контроллер → [Контроллеры](controllers), [Фильтры](filters), [Запрос и ответ](request-response)

```php
class PostController extends Controller
{
    public function behaviors()
    {
        return [
            'access' => [
                'class' => AccessControl::class,
                'rules' => [['allow' => true, 'roles' => ['@']]],
            ],
            'verbs' => [
                'class' => VerbFilter::class,
                'actions' => ['delete' => ['POST']],
            ],
        ];
    }

    public function actions()
    {
        return ['error' => 'yii\web\ErrorAction'];
    }

    public function actionView($id)                 // ?id=1 → $id; нет параметра → 400
    {
        $model = Post::findOne($id);
        if ($model === null) {
            throw new NotFoundHttpException();
        }
        return $this->render('view', ['model' => $model]);   // views/post/view.php + layout
    }

    public function actionCreate()
    {
        $model = new Post();
        if ($model->load(Yii::$app->request->post()) && $model->save()) {
            Yii::$app->session->setFlash('success', 'Сохранено');
            return $this->redirect(['view', 'id' => $model->id]);
        }
        return $this->render('create', ['model' => $model]);
    }

    public function actionApi()
    {
        return $this->asJson(['ok' => true]);
    }
}
```

```php
// запрос
$r = Yii::$app->request;
$r->get('id');  $r->post();  $r->isPost;  $r->isAjax;
$r->headers->get('X-Token');  $r->userIP;

// ответ
$this->redirect(['site/index']);   $this->goBack();   $this->goHome();   $this->refresh();
Yii::$app->response->sendFile($path);
Yii::$app->response->statusCode = 201;

// хуки действия
public function beforeAction($action) { /* … */ return parent::beforeAction($action); }
public function afterAction($action, $result) { return parent::afterAction($action, $result); }
```

## Модель и валидация → [Модели](models), [Валидация](validation), [Валидаторы](validators)

```php
class ContactForm extends Model
{
    public $name;
    public $email;
    public $body;

    public function rules()
    {
        return [
            [['name', 'email', 'body'], 'required'],
            [['name', 'email'], 'trim'],
            ['email', 'email'],
            ['name', 'string', 'max' => 50],
            ['body', 'filter', 'filter' => 'strip_tags'],
            ['age', 'integer', 'min' => 18, 'on' => 'adult'],
            ['url', 'url', 'defaultScheme' => 'https'],
            ['status', 'in', 'range' => [1, 2]],
            ['status', 'default', 'value' => 1],
            ['password_repeat', 'compare', 'compareAttribute' => 'password'],
            ['username', 'unique', 'targetClass' => User::class],
            ['category_id', 'exist', 'targetClass' => Category::class, 'targetAttribute' => 'id'],
            ['file', 'file', 'extensions' => 'png, jpg', 'maxSize' => 1024 * 1024],
            ['tags', 'each', 'rule' => ['string']],
            ['name', 'validateName'],                                   // inline-валидатор
            ['state', 'required', 'when' => fn ($m) => $m->country === 'US'],
        ];
    }

    public function attributeLabels() { return ['email' => 'E-mail']; }

    public function scenarios()
    {
        return ['create' => ['name', 'email', 'body'], 'update' => ['name']];
    }
}
```

```php
$model->load(Yii::$app->request->post());   // массовое присваивание безопасных атрибутов
$model->validate();                          // true / false
$model->errors;  $model->getFirstErrors();  $model->addError('name', 'Занято');

DynamicModel::validateData(compact('email'), [['email', 'email']]);   // без класса
```

## Active Record → [Active Record](active-record), [Query Builder](query-builder), [DAO](dao)

```php
class Post extends ActiveRecord
{
    public static function tableName() { return '{{%post}}'; }

    public function behaviors() { return [TimestampBehavior::class]; }

    public function getAuthor()
    {
        return $this->hasOne(User::class, ['id' => 'author_id']);
    }

    public function getTags()
    {
        return $this->hasMany(Tag::class, ['id' => 'tag_id'])
            ->viaTable('post_tag', ['post_id' => 'id']);
    }
}
```

```php
// чтение
Post::findOne(1);
Post::findOne(['slug' => $slug]);
Post::findAll(['status' => 1]);
Post::find()
    ->where(['status' => 1])
    ->andWhere(['like', 'title', $q])
    ->andFilterWhere(['author_id' => $authorId])   // пропускается, если пусто
    ->with('author')                                // отдельный запрос для связи
    ->joinWith('tags')                              // JOIN — можно фильтровать по tags.*
    ->orderBy(['id' => SORT_DESC])
    ->limit(10)->offset(20)
    ->all();
// ->one()  ->count()  ->exists()  ->column()  ->scalar()  ->asArray()
// ->indexBy('id')  ->batch(100)  ->cache(60)

// форматы where
->where('status = 1')
->where(['status' => 1, 'type' => [1, 2], 'deleted_at' => null])   // = , IN, IS NULL
->where(['and', ['>', 'id', 10], ['or', ['a' => 1], ['b' => 2]]])
->where(['between', 'price', 10, 100])
->where(['not in', 'id', $ids])

// запись
$post = new Post();
$post->attributes = $data;
$post->save();              // валидация + INSERT/UPDATE
$post->save(false);         // без валидации
$post->delete();
$post->refresh();
Post::updateAll(['status' => 0], ['<', 'created_at', $ts]);   // без событий
Post::deleteAll(['status' => 0]);
$post->updateCounters(['views' => 1]);

// связи
$post->author;                       // ленивая загрузка
$post->link('tags', $tag);
$post->unlink('tags', $tag, true);

// транзакции и DAO
Yii::$app->db->transaction(function ($db) { /* … */ });
$db->createCommand('SELECT * FROM post WHERE id = :id', [':id' => 1])->queryOne();
$db->createCommand()->insert('post', ['title' => 'x'])->execute();
// batchInsert()  update()  delete()  upsert()
```

## Представления и формы → [Представления](views), [Формы](forms), [Виджеты данных](data-widgets)

```php title="views/post/create.php"
<?php
$this->title = 'Новый пост';
$this->params['breadcrumbs'][] = $this->title;
$this->registerJs("console.log('hi')");
AppAsset::register($this);
?>
<h1><?= Html::encode($this->title) ?></h1>
<?= $this->render('_form', ['model' => $model]) ?>
```

```php title="views/post/_form.php"
<?php $form = ActiveForm::begin([
    'id' => 'post-form',
    'options' => ['enctype' => 'multipart/form-data'],
]) ?>

<?= $form->field($model, 'title')->textInput(['maxlength' => true]) ?>
<?= $form->field($model, 'body')->textarea(['rows' => 6]) ?>
<?= $form->field($model, 'category_id')->dropDownList(
    ArrayHelper::map(Category::find()->all(), 'id', 'name'),
    ['prompt' => '—']
) ?>
<?= $form->field($model, 'agree')->checkbox() ?>
<?= $form->field($model, 'file')->fileInput() ?>

<?= Html::submitButton('Сохранить', ['class' => 'btn btn-primary']) ?>

<?php ActiveForm::end() ?>
```

```php
// файл из формы
$model->file = UploadedFile::getInstance($model, 'file');
$model->file->saveAs('@webroot/uploads/' . $model->file->name);

// список
$dataProvider = new ActiveDataProvider([
    'query' => Post::find(),
    'pagination' => ['pageSize' => 20],
    'sort' => ['defaultOrder' => ['id' => SORT_DESC]],
]);

echo GridView::widget([
    'dataProvider' => $dataProvider,
    'filterModel' => $searchModel,
    'columns' => [
        'id',
        'title',
        'created_at:datetime',
        ['class' => ActionColumn::class],
    ],
]);

echo DetailView::widget([
    'model' => $model,
    'attributes' => ['title', 'author.name', 'created_at:date'],
]);
// ListView::widget(['dataProvider' => $dp, 'itemView' => '_item'])
```

## URL и маршруты → [Маршрутизация](routing)

```php
'rules' => [
    '' => 'site/index',
    'login' => 'site/login',
    'post/<id:\d+>' => 'post/view',
    'posts/<page:\d+>' => 'post/index',
    '<controller:\w+>/<action:\w+>' => '<controller>/<action>',
    'PUT,PATCH users/<id>' => 'user/update',
    'DELETE users/<id>' => 'user/delete',
    ['class' => 'yii\rest\UrlRule', 'controller' => 'user'],
    'http://<sub:\w+>.example.com/<page>' => 'site/page',
],
```

```php
Url::to(['post/view', 'id' => 1]);        // /post/1
Url::to(['/site/index'], true);           // абсолютный, от корня приложения
Url::current(['page' => 2]);              // текущий URL с изменённым параметром
Html::a('Пост', ['post/view', 'id' => 1]);

// маршрут: module/controller/action
// PostTagController → post-tag, actionViewAll → view-all
```

## Пользователи и доступ → [Аутентификация](authentication), [Авторизация](authorization), [Безопасность](security)

```php
// модель User реализует IdentityInterface:
// findIdentity(), findIdentityByAccessToken(), getId(), getAuthKey(), validateAuthKey()

Yii::$app->user->login($user, $rememberMe ? 3600 * 24 * 30 : 0);
Yii::$app->user->logout();
Yii::$app->user->isGuest;   Yii::$app->user->id;   Yii::$app->user->identity;
Yii::$app->user->can('updatePost', ['post' => $post]);

Yii::$app->security->generatePasswordHash($password);
Yii::$app->security->validatePassword($password, $hash);
Yii::$app->security->generateRandomString();
```

```php
// ACF
'rules' => [
    ['allow' => true, 'actions' => ['login'], 'roles' => ['?']],   // гости
    ['allow' => true, 'roles' => ['@']],                            // вошедшие
    ['allow' => true, 'matchCallback' => fn () => Yii::$app->user->identity->isAdmin],
    // также: 'ips', 'verbs', 'controllers', 'denyCallback'
],

// RBAC
$auth = Yii::$app->authManager;
$updatePost = $auth->createPermission('updatePost');
$auth->add($updatePost);
$author = $auth->createRole('author');
$auth->add($author);
$auth->addChild($author, $updatePost);
$auth->assign($author, $userId);
// правило: class MyRule extends Rule { public function execute($user, $item, $params) {…} }
```

Безопасность по умолчанию: CSRF включён, `Html::encode()` везде, параметры в SQL, `YII_DEBUG = false` в production, случайный `cookieValidationKey`.

## Сессии, флеши, cookie → [Сессии и cookie](sessions)

```php
$session = Yii::$app->session;
$session->set('key', $value);   $session->get('key', $default);   $session->remove('key');
$session['key'] = $value;       $session->has('key');

$session->setFlash('success', 'Готово');          // показать на следующей странице
$session->getFlash('success');   $session->hasFlash('success');   $session->getAllFlashes();

Yii::$app->response->cookies->add(new Cookie([
    'name' => 'lang',
    'value' => 'ru',
    'expire' => time() + 86400 * 365,
]));
Yii::$app->request->cookies->getValue('lang', 'en');   // cookie подписаны cookieValidationKey
```

## Кэш → [Кэширование данных](caching), [Кэширование вывода](caching-output)

```php
$posts = Yii::$app->cache->getOrSet(['posts', $page], function () {
    return Post::find()->all();
}, 3600, new TagDependency(['tags' => 'posts']));

TagDependency::invalidate(Yii::$app->cache, 'posts');   // сбросить по тегу
$cache->set($key, $value, 60);   $cache->get($key);   $cache->delete($key);   $cache->flush();
Post::find()->cache(60)->all();                          // кэш запроса
```

```php
// фрагмент представления
<?php if ($this->beginCache('sidebar', ['duration' => 600, 'variations' => [Yii::$app->language]])) { ?>
    …
<?php $this->endCache(); } ?>

// страница целиком и HTTP-кэш — фильтры контроллера
['class' => PageCache::class, 'only' => ['index'], 'duration' => 60],
['class' => HttpCache::class, 'lastModified' => fn () => $timestamp, 'etagSeed' => fn () => $seed],
```

## Миграции → [Миграции](migrations)

```bash
./yii migrate/create create_post_table \
    --fields="title:string:notNull,body:text,author_id:integer:notNull:foreignKey(user)"
./yii migrate/create add_status_column_to_post_table --fields="status:smallInteger:defaultValue(1)"

./yii migrate              # применить
./yii migrate/down         # откатить последнюю
./yii migrate/redo         # откатить и применить снова
./yii migrate/history      # что применено
./yii migrate/new          # что ещё нет
./yii migrate --migrationPath=@yii/rbac/migrations --interactive=0
```

```php
public function safeUp()
{
    $this->createTable('{{%post}}', [
        'id' => $this->primaryKey(),
        'title' => $this->string()->notNull(),
        'author_id' => $this->integer()->notNull(),
        'created_at' => $this->integer(),
    ]);
    $this->createIndex('idx-post-title', '{{%post}}', 'title');
    $this->addForeignKey('fk-post-author', '{{%post}}', 'author_id', '{{%user}}', 'id', 'CASCADE');
}

public function safeDown()
{
    $this->dropTable('{{%post}}');
}
```

## События, поведения, DI → [События](events), [Поведения](behaviors), [DI](di)

```php
// события
$obj->on(Foo::EVENT_X, function ($event) {
    $event->sender;   $event->data;
    $event->handled = true;                        // остановить остальные обработчики
}, $data);
$obj->trigger(Foo::EVENT_X, new Event());
Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, $handler);   // на класс

// поведения
public function behaviors()
{
    return [
        TimestampBehavior::class,
        ['class' => SluggableBehavior::class, 'attribute' => 'title'],
        BlameableBehavior::class,
    ];
}

// DI
Yii::$container->set('app\components\PaymentInterface', 'app\components\Stripe');
Yii::$container->setSingleton(Mailer::class, [...]);
$obj = Yii::createObject(Foo::class, [$arg]);

// внедрение в контроллер
public function __construct($id, $module, PaymentInterface $payment, $config = [])
{
    $this->payment = $payment;
    parent::__construct($id, $module, $config);
}
```

## Консоль, REST, i18n, почта → [Консоль](console), [REST](rest), [i18n](i18n), [Почта](mailing)

```php
// ./yii import/run data.csv --dry=1
class ImportController extends \yii\console\Controller
{
    public $dry = false;

    public function options($actionID) { return ['dry']; }

    public function actionRun($file, array $ids = [])
    {
        $this->stdout("ok\n", Console::FG_GREEN);
        return ExitCode::OK;
    }
}

// REST: + yii\rest\UrlRule, JsonParser, HttpBearerAuth
class UserController extends \yii\rest\ActiveController
{
    public $modelClass = User::class;
}
public function fields()
{
    $fields = parent::fields();
    unset($fields['password_hash']);
    return $fields;
}
public function extraFields() { return ['profile']; }

// i18n: messages/ru-RU/app.php, извлечение — ./yii message
Yii::t('app', 'Hello, {name}! {n, plural, one{# message} other{# messages}}', [
    'name' => $name,
    'n' => $count,
]);

// почта
Yii::$app->mailer->compose('welcome', ['user' => $user])
    ->setTo($user->email)
    ->setSubject('Добро пожаловать')
    ->send();

// логи, профилирование, исключения
Yii::info('msg', 'category');   Yii::warning();   Yii::error();   Yii::debug();
Yii::beginProfile('block');   Yii::endProfile('block');
throw new NotFoundHttpException();      // 404; также Forbidden (403), BadRequest (400)
throw new UserException('Текст');       // сообщение показывается пользователю
```

## Хелперы → [Хелперы](helpers), [Форматирование](formatting)

```php
ArrayHelper::getValue($arr, 'user.name', $default);
ArrayHelper::map($rows, 'id', 'name');       ArrayHelper::index($rows, 'id');
ArrayHelper::getColumn($rows, 'id');         ArrayHelper::merge($a, $b);

Html::encode($text);                         Html::a($text, ['post/view', 'id' => 1]);
Html::img('@web/img/logo.png');              Html::tag('div', $content, ['class' => 'x']);
Html::addCssClass($options, 'active');

Json::encode($data);   Json::decode($json);   new JsExpression('function () {}');
Url::to([...]);   Url::current();   Url::home();   Url::previous();

Inflector::slug('Привет мир');               // privet-mir
Inflector::pluralize('post');                Inflector::camel2id('PostTag');
StringHelper::truncate($text, 50);           VarDumper::dump($value, 10, true);

$f = Yii::$app->formatter;
$f->asDate($ts, 'php:d.m.Y');   $f->asDatetime($ts);   $f->asRelativeTime($ts);
$f->asCurrency($sum, 'RUB');    $f->asDecimal($n, 2);   $f->asShortSize($bytes);
$f->asBoolean($flag);           $f->asNtext($text);
```
