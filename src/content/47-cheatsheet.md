---
id: cheatsheet
title: Шпаргалка на одну страницу
part: extra
summary: Самое нужное из всего руководства в одном месте — команды, конфигурация, контроллер, модель, Active Record, формы, URL, доступ, кэш, миграции, консоль, REST. Для быстрого «как это писалось».
sources:
---

:::lead
Сжатая выжимка всего сайта: только код и однострочные пояснения. Каждый блок ведёт в подробный раздел. Держите открытой рядом с редактором.
:::

## Установка и команды → [Установка](install)

```bash
composer create-project --prefer-dist yiisoft/yii2-app-basic myapp      # basic
composer create-project --prefer-dist yiisoft/yii2-app-advanced myapp && php init   # advanced
./yii serve --port=8080                # dev-сервер → http://localhost:8080
./yii help | ./yii migrate | ./yii cache/flush-all | ./yii gii/model --tableName=post --modelClass=Post
```

## Конфигурация → [Конфигурации](configurations), [Приложение](app)

```php
return [
    'id' => 'app', 'basePath' => dirname(__DIR__), 'bootstrap' => ['log'], 'language' => 'ru-RU',
    'aliases' => ['@uploads' => '@webroot/uploads'],
    'components' => [
        'db' => ['class' => 'yii\db\Connection', 'dsn' => 'mysql:host=localhost;dbname=app', 'username' => 'root', 'password' => '', 'charset' => 'utf8mb4', 'enableSchemaCache' => !YII_DEBUG],
        'cache' => ['class' => 'yii\caching\FileCache'],
        'user' => ['identityClass' => 'app\models\User', 'enableAutoLogin' => true],
        'request' => ['cookieValidationKey' => 'random-string', 'parsers' => ['application/json' => 'yii\web\JsonParser']],
        'urlManager' => ['enablePrettyUrl' => true, 'showScriptName' => false, 'rules' => ['post/<id:\d+>' => 'post/view']],
        'errorHandler' => ['errorAction' => 'site/error'],
        'log' => ['traceLevel' => YII_DEBUG ? 3 : 0, 'targets' => [['class' => 'yii\log\FileTarget', 'levels' => ['error', 'warning']]]],
        'mailer' => ['class' => \yii\symfonymailer\Mailer::class, 'useFileTransport' => YII_ENV_DEV],
    ],
    'modules' => ['admin' => ['class' => 'app\modules\admin\Module']],
    'params' => ['adminEmail' => 'admin@example.com'],
];
// объект по конфигурации: ['class' => X::class, 'prop' => 1, 'on event' => $h, 'as behavior' => [...]] → Yii::createObject()
// псевдонимы: @app @web @webroot @runtime @vendor @yii;  Yii::getAlias('@app/runtime')
```

## Контроллер → [Контроллеры](controllers), [Фильтры](filters), [Запрос и ответ](request-response)

```php
class PostController extends Controller
{
    public function behaviors()
    {
        return [
            'access' => ['class' => AccessControl::class, 'rules' => [['allow' => true, 'roles' => ['@']]]],
            'verbs' => ['class' => VerbFilter::class, 'actions' => ['delete' => ['POST']]],
        ];
    }
    public function actions() { return ['error' => 'yii\web\ErrorAction']; }

    public function actionView($id)                       // GET ?id=1 → параметр; отсутствует → 400
    {
        $model = Post::findOne($id) ?? throw new NotFoundHttpException();
        return $this->render('view', ['model' => $model]);   // views/post/view.php внутри layout
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
    public function actionApi() { return $this->asJson(['ok' => true]); }
}
// запрос: $r = Yii::$app->request; $r->get('id'); $r->post(); $r->isPost; $r->isAjax; $r->headers->get('X'); $r->userIP
// ответ: $this->redirect(); $this->goBack(); $this->goHome(); $this->refresh(); Yii::$app->response->sendFile($path); statusCode
// beforeAction($action) → return parent::beforeAction($action);   afterAction($action, $result)
```

## Модель и валидация → [Модели](models), [Валидация](validation), [Валидаторы](validators)

```php
class ContactForm extends Model
{
    public $name, $email, $body, $verifyCode;
    public function rules()
    {
        return [
            [['name', 'email', 'body'], 'required'], [['name', 'email'], 'trim'],
            ['email', 'email'], ['name', 'string', 'max' => 50],
            ['verifyCode', 'captcha'], ['body', 'filter', 'filter' => 'strip_tags'],
            ['age', 'integer', 'min' => 18, 'on' => 'adult'],
            ['url', 'url', 'defaultScheme' => 'https', 'skipOnEmpty' => true],
            ['status', 'in', 'range' => [1, 2]], ['status', 'default', 'value' => 1],
            ['password_repeat', 'compare', 'compareAttribute' => 'password'],
            ['username', 'unique', 'targetClass' => User::class], ['category_id', 'exist', 'targetClass' => Category::class, 'targetAttribute' => 'id'],
            ['file', 'file', 'extensions' => 'png, jpg', 'maxSize' => 1024 * 1024],
            ['tags', 'each', 'rule' => ['string']], ['name', 'validateName'],   // inline
            ['state', 'required', 'when' => fn($m) => $m->country === 'US'],
        ];
    }
    public function attributeLabels() { return ['email' => 'E-mail']; }
    public function scenarios() { return ['create' => ['name', 'email'], 'update' => ['name']]; }
}
// $m->load($post) → $m->validate() → $m->errors / getFirstErrors();  DynamicModel::validateData($data, $rules)
```

## Active Record → [Active Record](active-record), [Query Builder](query-builder), [DAO](dao)

```php
class Post extends ActiveRecord
{
    public static function tableName() { return '{{%post}}'; }
    public function behaviors() { return [TimestampBehavior::class]; }
    public function getAuthor() { return $this->hasOne(User::class, ['id' => 'author_id']); }
    public function getTags() { return $this->hasMany(Tag::class, ['id' => 'tag_id'])->viaTable('post_tag', ['post_id' => 'id']); }
}
Post::findOne(1);  Post::findOne(['slug' => $s]);  Post::findAll(['status' => 1]);
Post::find()->where(['status' => 1])->andWhere(['like', 'title', $q])->andFilterWhere(['author_id' => $a])
    ->with('author')->joinWith('tags')->orderBy(['id' => SORT_DESC])->limit(10)->offset(20)->asArray()->all();
->one() ->count() ->exists() ->column() ->scalar() ->indexBy('id') ->batch(100) ->cache(60)
where: 'a=1' | ['a' => 1, 'b' => [1,2], 'c' => null] | ['and', ['>', 'a', 1], ['or', ..., ...]] | ['between', 'a', 1, 9] | ['not in', 'id', $ids]
$m = new Post(); $m->attributes = $data; $m->save();  $m->save(false);  $m->delete();  $m->refresh();
Post::updateAll(['status' => 0], ['<', 'created_at', $ts]);  Post::deleteAll(['status' => 0]);  $m->updateCounters(['views' => 1]);
$post->link('tags', $tag);  $post->unlink('tags', $tag, true);  $post->author (лениво) / with('author') (жадно)
Yii::$app->db->transaction(function () { ... });  $db->createCommand('SELECT ... WHERE id=:id', [':id' => 1])->queryOne();
$db->createCommand()->insert('t', [...])->execute();  batchInsert  update  delete  upsert
```

## Представления и формы → [Представления](views), [Формы](forms), [Виджеты данных](data-widgets)

```php
<?php $this->title = 'Заголовок'; $this->params['breadcrumbs'][] = $this->title; ?>
<?= Html::encode($model->title) ?>  <?= $this->render('_item', ['model' => $m]) ?>  <?= $this->context->id ?>
<?php $this->registerJs("alert(1)"); $this->registerCss('.x{}'); AppAsset::register($this); ?>
<?php $form = ActiveForm::begin(['id' => 'f', 'options' => ['enctype' => 'multipart/form-data']]) ?>
    <?= $form->field($model, 'title')->textInput(['maxlength' => true]) ?>
    <?= $form->field($model, 'body')->textarea(['rows' => 6]) ?>
    <?= $form->field($model, 'category_id')->dropDownList(ArrayHelper::map(Category::find()->all(), 'id', 'name'), ['prompt' => '—']) ?>
    <?= $form->field($model, 'agree')->checkbox() ?>  <?= $form->field($model, 'file')->fileInput() ?>
    <?= Html::submitButton('Сохранить', ['class' => 'btn btn-primary']) ?>
<?php ActiveForm::end() ?>
// файл: $model->file = UploadedFile::getInstance($model, 'file'); $model->file->saveAs($path);
// список: GridView::widget(['dataProvider' => $dp, 'filterModel' => $s, 'columns' => ['id', 'title', 'created_at:datetime', ['class' => ActionColumn::class]]]);
// DetailView::widget(['model' => $m, 'attributes' => ['title', 'author.name', 'created_at:date']]);  ListView с itemView
// $dp = new ActiveDataProvider(['query' => Post::find(), 'pagination' => ['pageSize' => 20], 'sort' => ['defaultOrder' => ['id' => SORT_DESC]]]);
```

## URL и маршруты → [Маршрутизация](routing)

```php
'rules' => [
    '' => 'site/index', 'login' => 'site/login',
    'post/<id:\d+>' => 'post/view', 'posts/<page:\d+>' => 'post/index',
    '<controller:\w+>/<action:\w+>' => '<controller>/<action>',
    'PUT,PATCH users/<id>' => 'user/update', 'DELETE users/<id>' => 'user/delete',
    ['class' => 'yii\rest\UrlRule', 'controller' => 'user'],
    'http://<sub:\w+>.example.com/<page>' => 'site/page', '<lang:(ru|en)>/<url:.*>' => '...',
],
Url::to(['post/view', 'id' => 1]);  Url::to(['/site/index'], true);  Url::current(['page' => 2]);  Html::a('x', ['post/view', 'id' => 1]);
// маршрут: module/controller/action;  контроллер `PostTagController` → post-tag;  actionViewAll → view-all
```

## Пользователи и доступ → [Аутентификация](authentication), [Авторизация](authorization), [Безопасность](security)

```php
class User extends ActiveRecord implements IdentityInterface { findIdentity, findIdentityByAccessToken, getId, getAuthKey, validateAuthKey }
Yii::$app->user->login($user, $rememberMe ? 3600 * 24 * 30 : 0);  ->logout();  ->isGuest;  ->id;  ->identity;  ->can('updatePost', ['post' => $p]);
Yii::$app->security->generatePasswordHash($pw);  ->validatePassword($pw, $hash);  ->generateRandomString();
// ACF: ['allow' => true, 'actions' => ['login'], 'roles' => ['?']],  ['allow' => true, 'roles' => ['@']],  'matchCallback' => fn() => ..., 'ips', 'verbs'
// RBAC: $auth = Yii::$app->authManager; $p = $auth->createPermission('updatePost'); $auth->add($p); $r = $auth->createRole('author'); $auth->add($r);
//       $auth->addChild($r, $p); $auth->assign($r, $userId);  Rule::execute($user, $item, $params)
// CSRF включён; Html::encode() везде; параметры в SQL; YII_DEBUG=false в prod; cookieValidationKey
```

## Сессии, флеши, cookie → [Сессии и cookie](sessions)

```php
$s = Yii::$app->session; $s->set('k', $v); $s->get('k', $default); $s->remove('k'); $s['k'] = $v; $s->has('k');
$s->setFlash('success', 'Готово');  $s->getFlash('success');  $s->hasFlash();  $s->getAllFlashes();   // Alert::widget() в layout
Yii::$app->response->cookies->add(new Cookie(['name' => 'lang', 'value' => 'ru', 'expire' => time() + 86400 * 365]));
Yii::$app->request->cookies->getValue('lang', 'en');  ->remove('lang')   // cookie подписаны cookieValidationKey
```

## Кэш → [Кэширование данных](caching), [Кэширование вывода](caching-output)

```php
$data = Yii::$app->cache->getOrSet(['posts', $page], fn() => Post::find()->all(), 3600, new TagDependency(['tags' => 'posts']));
TagDependency::invalidate(Yii::$app->cache, 'posts');  $cache->set/get/delete/exists/flush;  Post::find()->cache(60)->all();
<?php if ($this->beginCache('sidebar', ['duration' => 600, 'variations' => [Yii::$app->language]])) { ?> ... <?php $this->endCache(); } ?>
'behaviors': ['class' => PageCache::class, 'only' => ['index'], 'duration' => 60],  ['class' => HttpCache::class, 'lastModified' => fn() => $ts, 'etagSeed' => fn() => $seed]
```

## Миграции → [Миграции](migrations)

```bash
./yii migrate/create create_post_table --fields="title:string:notNull,body:text,author_id:integer:notNull:foreignKey(user)"
./yii migrate/create add_status_column_to_post_table --fields="status:smallInteger:defaultValue(1)"
./yii migrate | migrate/down | migrate/redo | migrate/history | migrate/new | migrate/fresh | migrate --migrationPath=@yii/rbac/migrations --interactive=0
```

```php
public function safeUp() { $this->createTable('{{%post}}', ['id' => $this->primaryKey(), 'title' => $this->string()->notNull(), 'created_at' => $this->integer()]); $this->createIndex('idx-post-title', '{{%post}}', 'title'); $this->addForeignKey('fk-post-author', '{{%post}}', 'author_id', '{{%user}}', 'id', 'CASCADE'); }
public function safeDown() { $this->dropTable('{{%post}}'); }
```

## События, поведения, DI → [События](events), [Поведения](behaviors), [DI](di)

```php
$obj->on(Foo::EVENT_X, function ($event) { $event->sender; $event->data; $event->handled = true; }, $data);  $obj->trigger(Foo::EVENT_X, new Event());
Event::on(ActiveRecord::class, ActiveRecord::EVENT_AFTER_INSERT, $handler);  'on afterOpen' => $handler в конфигурации
public function behaviors() { return [['class' => TimestampBehavior::class], ['class' => SluggableBehavior::class, 'attribute' => 'title'], BlameableBehavior::class]; }
Yii::$container->set('app\components\PaymentInterface', 'app\components\Stripe');  Yii::$container->setSingleton(...);  Yii::createObject(Foo::class, [$arg]);
public function __construct($id, $module, PaymentInterface $payment, $config = []) { ... parent::__construct($id, $module, $config); }   // в контроллере
```

## Консоль, REST, i18n, почта → [Консоль](console), [REST](rest), [i18n](i18n), [Почта](mailing)

```php
class ImportController extends \yii\console\Controller { public $dry = false; public function options($a) { return ['dry']; }
    public function actionRun($file, array $ids = []) { $this->stdout("ok\n", Console::FG_GREEN); return ExitCode::OK; } }   // ./yii import/run data.csv --dry=1
class UserController extends \yii\rest\ActiveController { public $modelClass = User::class; }   // + yii\rest\UrlRule, JsonParser, HttpBearerAuth
public function fields() { $f = parent::fields(); unset($f['password_hash']); return $f; }  public function extraFields() { return ['profile']; }
Yii::t('app', 'Hello, {name}! You have {n, plural, one{# message} other{# messages}}', ['name' => $n, 'n' => $c]);   // messages/ru-RU/app.php; ./yii message
Yii::$app->mailer->compose('welcome', ['user' => $u])->setTo($u->email)->setSubject('Hi')->send();
Yii::info('msg', 'category'); Yii::warning(); Yii::error(); Yii::debug();  Yii::beginProfile('x'); Yii::endProfile('x');
throw new NotFoundHttpException();  ForbiddenHttpException  BadRequestHttpException  ServerErrorHttpException  UserException (сообщение видно пользователю)
```

## Хелперы → [Хелперы](helpers), [Форматирование](formatting)

```php
ArrayHelper::getValue($a, 'x.y', $def);  ::map($rows, 'id', 'name');  ::index($rows, 'id');  ::getColumn($rows, 'id');  ::merge($a, $b);  ::toArray($obj)
Html::encode($s);  Html::a($text, $route, $opts);  Html::img('@web/i.png');  Html::tag('div', $c, ['class' => 'x']);  Html::addCssClass($opts, 'y')
Json::encode($d);  Json::decode($s);  new JsExpression('function(){}');   Url::to(); Url::current(); Url::home(); Url::previous()
Inflector::slug('Привет мир');  ::pluralize('post');  ::camel2id('PostTag');   StringHelper::truncate($s, 50);   VarDumper::dump($v, 10, true)
Yii::$app->formatter->asDate($t, 'php:d.m.Y');  asDatetime  asRelativeTime  asCurrency($v, 'RUB')  asDecimal($v, 2)  asShortSize($b)  asBoolean  asNtext
```
