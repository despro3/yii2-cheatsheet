---
id: sessions
title: Сессии и куки
part: runtime
summary: Компонент session, хранилища сессий (файлы, БД, кеш, Redis), flash-сообщения, чтение и отправка кук, валидация кук подписью.
sources: runtime-sessions-cookies
---

:::lead
Сессии и куки хранят данные между запросами. Yii оборачивает `$_SESSION` и `$_COOKIE` в объекты: сессия открывается сама при первом обращении, куки подписываются секретным ключом и не могут быть подделаны на клиенте.
:::

## Сессия

```php
$session = Yii::$app->session;

$session->isActive;   $session->open();   $session->close();   $session->destroy();

// три эквивалентных способа — компонент сам откроет сессию
$session->set('language', 'ru');    $session['language'] = 'ru';    $_SESSION['language'] = 'ru';
$session->get('language');          $session['language'];
$session->remove('language');       unset($session['language']);
$session->has('language');          isset($session['language']);
foreach ($session as $name => $value) { }
```

> [!GOTCHA]
> Через компонент нельзя менять элементы вложенного массива: `$session['captcha']['number'] = 5` **не сработает**. Варианты: записать массив целиком, использовать `$_SESSION` напрямую (после `open()`), хранить `ArrayObject` или — лучше всего — плоские ключи с префиксом: `$session['captcha.number'] = 5`.

### Хранилища

По умолчанию сессии — файлы на сервере. Для нескольких серверов или высокой нагрузки:

| Класс | Где хранит |
|---|---|
| `yii\web\Session` | файлы PHP (по умолчанию) |
| `yii\web\DbSession` | таблица БД |
| `yii\web\CacheSession` | компонент кеша (с оговоркой: кеш может вытеснять данные) |
| `yii\redis\Session` | Redis — рекомендуемый вариант, если он есть |
| `yii\mongodb\Session` | MongoDB |

```php
'session' => [
    'class' => 'yii\web\DbSession',
    // 'db' => 'db', 'sessionTable' => 'session',
],
```

```sql
CREATE TABLE session (
    id CHAR(40) NOT NULL PRIMARY KEY,   -- 64, если session.hash_function = sha256
    expire INTEGER,
    data BLOB                           -- LONGBLOB в MySQL, BYTEA в PostgreSQL
)
```

API у всех классов одинаковый — хранилище меняется конфигурацией, без правки кода.

### Flash-сообщения

Живут ровно до следующего запроса — идеальны для «Сохранено» после редиректа:

```php
// запрос 1
Yii::$app->session->setFlash('success', 'Пост удалён.');
Yii::$app->session->addFlash('alerts', 'Ещё одно сообщение');   // накапливает в массив

// запрос 2
Yii::$app->session->getFlash('success');      // 'Пост удалён.'
Yii::$app->session->getFlash('alerts');       // массив
Yii::$app->session->hasFlash('success');
Yii::$app->session->getAllFlashes();

// запрос 3: сообщений уже нет
```

Не смешивайте `setFlash()` и `addFlash()` для одного ключа — первый хранит значение, второй массив. В шаблоне basic flash-сообщения выводит виджет `Alert`.

## Куки

Две коллекции: входящие — в `request`, исходящие — в `response`.

```php
// чтение
$cookies = Yii::$app->request->cookies;
$language = $cookies->getValue('language', 'en');
if (($cookie = $cookies->get('language')) !== null) { $language = $cookie->value; }
$cookies->has('language');   isset($cookies['language']);

// отправка
$cookies = Yii::$app->response->cookies;
$cookies->add(new \yii\web\Cookie([
    'name' => 'language',
    'value' => 'ru',
    'expire' => time() + 86400 * 365,
    // 'domain', 'path', 'secure', 'httpOnly' (по умолчанию true), 'sameSite'
]));
$cookies->remove('language');   unset($cookies['language']);
```

### Валидация кук

Каждая кука, записанная через `response`, подписывается ключом; изменённая на клиенте кука просто не попадёт в `request->cookies`. Ключ обязателен:

```php
'request' => [
    'cookieValidationKey' => 'длинная-случайная-строка',   // не коммитьте в репозиторий
],
```

Отключать `enableCookieValidation` не рекомендуется. Куки, прочитанные напрямую из `$_COOKIE` или записанные `setcookie()`, валидацию не проходят.

:::quiz Проверь себя
Q: Нужно ли вызывать `session_start()` перед чтением `Yii::$app->session['x']`?
A: Нет — компонент открывает сессию автоматически при первом обращении. Только при прямой работе с `$_SESSION` нужен `open()`.
Q: Почему `$session['cart']['qty'] = 2` не сохраняет значение?
A: `ArrayAccess` возвращает копию массива; изменение копии не попадает в сессию. Записывайте массив целиком или используйте плоские ключи.
Q: Сколько запросов живёт flash-сообщение?
A: Устанавливается в одном запросе, доступно в следующем, после чего удаляется автоматически.
Q: Что произойдёт, если пользователь поправит значение куки в браузере?
A: Подпись не совпадёт, и `request->cookies` куку не вернёт; в `$_COOKIE` она по-прежнему есть.
Q: Какое хранилище сессий выбрать для кластера из нескольких серверов?
A: Общее для всех узлов: БД (`DbSession`) или лучше Redis (`yii\redis\Session`); файлы не подходят.
:::
