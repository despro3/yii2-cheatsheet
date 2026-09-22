---
id: testing
title: Тестирование
part: tools
summary: Codeception в шаблонах Yii — модульные, функциональные и приёмочные тесты; настройка окружения и БД для тестов; фикстуры ActiveFixture с dataFile и зависимостями, загрузка через _fixtures() и команду fixture; что тестировать и как.
sources: test-overview, test-environment-setup, test-unit, test-functional, test-acceptance, test-fixtures
---

:::lead
Yii дружит с Codeception, а шаблоны приложений уже содержат папку `tests/` с конфигурацией. Три уровня: **unit** — класс изолированно, **functional** — запрос к приложению без браузера, **acceptance** — реальный браузер через Selenium/WebDriver. Плюс **фикстуры** — воспроизводимые данные в БД.
:::

## Три вида тестов

| Вид | Что проверяет | Скорость | Инструмент |
|---|---|---|---|
| Модульные (unit) | метод/класс: модель, хелпер, сервис | быстро | Codeception unit / PHPUnit |
| Функциональные | контроллер + модель + представление, HTTP без веб-сервера | средне | модуль `Yii2` Codeception |
| Приёмочные (acceptance) | сценарий пользователя в браузере, JS | медленно | WebDriver / PhpBrowser |

Пирамида: много unit, меньше функциональных, единицы приёмочных.

## Окружение

```bash
# уже есть в шаблонах
composer require --dev codeception/codeception codeception/module-asserts codeception/module-yii2
cp .env.example .env    # (advanced) или config/test_db.php
./yii_test migrate      # (advanced: yii_test — консоль с тестовой конфигурацией)
vendor/bin/codecept run                     # все тесты
vendor/bin/codecept run unit                # только модульные
vendor/bin/codecept run functional LoginCest
vendor/bin/codecept run --coverage --coverage-html   # покрытие (xdebug/pcov)
```

```
tests/
    unit/          # *Test.php — PHPUnit-стиль
    functional/    # *Cest.php
    acceptance/    # *Cest.php
    _data/         # фикстуры и данные
    _support/      # хелперы, UnitTester/FunctionalTester
    unit.suite.yml, functional.suite.yml, acceptance.suite.yml
codeception.yml
```

Тестовая конфигурация приложения — `config/test.php` (basic) с отдельной БД `yii2basic_test` (`config/test_db.php`); входной скрипт `web/index-test.php` с `YII_ENV = 'test'`. В acceptance-тестах приложение должно быть доступно по URL (`./yii serve` или веб-сервер) с `index-test.php`.

## Модульные тесты

```php title="tests/unit/models/UserTest.php"
namespace tests\unit\models;

use app\models\User;
use app\tests\fixtures\UserFixture;

class UserTest extends \Codeception\Test\Unit
{
    /** @var \UnitTester */
    protected $tester;

    public function _fixtures()
    {
        return ['users' => UserFixture::class];      // загружаются перед каждым тестом
    }

    public function testFindUserById()
    {
        verify($user = User::findIdentity(100))->notEmpty();
        verify($user->username)->equals('admin');
        verify(User::findIdentity(999))->empty();
    }

    public function testValidateWrongPassword()
    {
        $user = $this->tester->grabFixture('users', 'admin');
        verify($user->validatePassword('wrong'))->false();
    }
}
```

Модели тестируют «в лоб»: создать, задать атрибуты, `validate()`, проверить `errors`. Сервисы с зависимостями — через конструкторное внедрение и заглушки (`$this->make()`, `Stub::make()`) или подмену компонентов `Yii::$app->set('mailer', $stub)`.

## Функциональные тесты

```php title="tests/functional/LoginCest.php"
class LoginCest
{
    public function _before(\FunctionalTester $I)
    {
        $I->amOnRoute('site/login');
    }

    public function loginWithEmptyCredentials(\FunctionalTester $I)
    {
        $I->submitForm('#login-form', []);
        $I->expectTo('see validations errors');
        $I->see('Username cannot be blank.');
    }

    public function loginSuccessfully(\FunctionalTester $I)
    {
        $I->submitForm('#login-form', ['LoginForm[username]' => 'admin', 'LoginForm[password]' => 'admin']);
        $I->see('Logout (admin)');
        $I->dontSeeElement('form#login-form');
    }

    public function checkAsLoggedUser(\FunctionalTester $I)
    {
        $I->amLoggedInAs(100);                          // модуль Yii2: войти без формы
        $I->amOnPage('/profile');
        $I->seeResponseCodeIs(200);
        $I->seeRecord('app\models\User', ['id' => 100]); // проверка БД
        $I->sendAjaxPostRequest('/api/ping', []);
    }
}
```

Модуль `Yii2` в `functional.suite.yml` (`configFile: config/test.php`) даёт `amOnRoute`, `amLoggedInAs`, `seeRecord`, `grabRecord`, `seeEmailIsSent`, доступ к `Yii::$app` и транзакцию вокруг каждого теста (`cleanup: true`).

## Приёмочные тесты

```php title="tests/acceptance/HomeCest.php"
class HomeCest
{
    public function ensureThatHomePageWorks(\AcceptanceTester $I)
    {
        $I->amOnPage(Yii::$app->homeUrl);
        $I->see('My Company');
        $I->seeLink('About');
        $I->click('About');
        $I->wait(2);                       // JS/анимации
        $I->see('This is the About page.');
    }
}
```

`acceptance.suite.yml`: `PhpBrowser` (быстрый, без JS) или `WebDriver` (`url`, `browser: chrome`) — нужен запущенный Selenium/ChromeDriver и сервер приложения. Здесь проверяют только ключевые сценарии: регистрация, оплата, поиск.

## Фикстуры

Фикстура приводит БД (или другое состояние) к известному виду перед тестом и убирает после.

```php title="tests/fixtures/UserFixture.php"
namespace app\tests\fixtures;

use yii\test\ActiveFixture;

class UserFixture extends ActiveFixture
{
    public $modelClass = 'app\models\User';        // или $tableName
    public $dataFile = '@tests/_data/user.php';    // по умолчанию — tests/fixtures/data/user.php
    public $depends = ['app\tests\fixtures\ProfileFixture'];   // сначала загрузятся зависимости
}
```

```php title="tests/_data/user.php"
return [
    'admin' => [
        'username' => 'admin', 'email' => 'admin@example.com',
        'auth_key' => 'key', 'password_hash' => '$2y$13$…',
    ],
    'user1' => [
        'username' => 'user1', 'email' => 'user1@example.com',
        'auth_key' => 'key2', 'password_hash' => '…',
    ],
];
```

Ключ строки (`admin`) — псевдоним записи; поле `id` подставится автоматически. `ActiveFixture::load()` очищает таблицу и вставляет данные; `unload()` — очищает. Своя логика — наследовать `yii\test\Fixture` (`load`/`unload`) или `DbFixture`.

### Использование

```php
// в тесте
public function _fixtures()
{
    return [
        'users' => ['class' => UserFixture::class, 'dataFile' => '@tests/_data/user.php'],
        'profiles' => ProfileFixture::class,
    ];
}
$user = $this->tester->grabFixture('users', 'admin');   // модель ActiveRecord
$this->tester->grabFixture('users');                     // весь объект фикстуры; ->data — исходные массивы

// в PHPUnit без Codeception — FixtureTrait: fixtures() + loadFixtures()/unloadFixtures(), $this->users('admin')
```

### Консольная загрузка

```bash
# загрузить фикстуру User из namespace (по умолчанию tests\unit\fixtures)
./yii fixture/load User
./yii fixture/load "*"                  # все
./yii fixture/load User Profile --namespace=app\\tests\\fixtures
./yii fixture/unload User
./yii fixture/load "*" -except=User
./yii fixture/load User --globalFixtures=InitDb      # общие (InitDbFixture: отключает проверку FK на время)
```

Фикстуры — не только БД: `Fixture` может готовить файлы, кэш, внешние сервисы. Данные для фикстур можно генерировать с Faker через расширение `yii2-faker` (`./yii fixture/generate`).

## Что покрывать в первую очередь

:::cards
- **Модели** — правила валидации, бизнес-методы, связи: дёшево и ловит большинство ошибок
- **Формы и сценарии** — какие атрибуты безопасны, что запрещено
- **Критичные маршруты** — вход, регистрация, оплата, API — функциональными тестами
- **Права** — гость не видит, автор может, админ может всё
- **Регрессии** — каждый пойманный баг превращается в тест
:::

:::quiz Проверь себя
Q: Чем функциональный тест отличается от приёмочного?
A: Функциональный отправляет запрос в приложение напрямую (без браузера и сервера), приёмочный — через реальный браузер и HTTP.
Q: Как войти под пользователем в функциональном тесте без формы?
A: `$I->amLoggedInAs($idOrIdentity)` — метод модуля `Yii2`.
Q: Что делает `ActiveFixture::load()` и кто чистит таблицу?
A: `load()` только вставляет строки из `dataFile`. Таблицу опустошает `unload()` (через `resetTable()`), а `FixtureTrait` вызывает выгрузку перед загрузкой — поэтому со стороны кажется, будто чистит `load()`.
Q: Для чего псевдонимы строк в файле данных фикстуры?
A: Чтобы получать конкретную запись в тесте: `$this->tester->grabFixture('users', 'admin')`.
Q: Как гарантировать порядок загрузки связанных фикстур?
A: Свойством `depends` — зависимости загружаются раньше.
:::
