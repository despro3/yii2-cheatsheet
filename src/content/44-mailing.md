---
id: mailing
title: Отправка почты
part: special
summary: Компонент mailer (yii2-symfonymailer / swiftmailer) — compose(), setFrom/setTo/setSubject, текст и HTML, представления писем и layout, вложения и встроенные изображения, массовая отправка sendMultiple, транспорт SMTP, файловый транспорт для разработки и тестов.
sources: tutorial-mailing
---

:::lead
`Yii::$app->mailer` — единый интерфейс к почтовой библиотеке. В новых шаблонах это `yiisoft/yii2-symfonymailer` (Symfony Mailer), в старых — `yii2-swiftmailer`. Письма собираются из представлений с layout, вложениями и картинками, а в разработке падают в файлы вместо отправки.
:::

## Настройка

```php title="config/web.php"
'components' => [
    'mailer' => [
        'class' => \yii\symfonymailer\Mailer::class,
        'viewPath' => '@app/mail',                 // представления писем
        'useFileTransport' => YII_ENV_DEV,         // в dev — писать в @runtime/mail вместо отправки
        'transport' => [
            'scheme' => 'smtps',                   // smtp | smtps | sendmail | native
            'host' => 'smtp.example.com',
            'port' => 465,
            'username' => 'user', 'password' => 'secret',
            'dsn' => 'smtp://user:pass@smtp.example.com:587',   // альтернатива — одной строкой
        ],
        'messageConfig' => [
            'from' => ['noreply@example.com' => 'My Site'],   // отправитель по умолчанию
            'charset' => 'UTF-8',
        ],
    ],
],
```

Для swiftmailer — `yii\swiftmailer\Mailer` с `transport => ['class' => 'Swift_SmtpTransport', 'host' => …, 'encryption' => 'tls']`. Пароли — вне репозитория.

## Отправка

```php
Yii::$app->mailer->compose()
    ->setFrom('from@domain.com')
    ->setTo('to@domain.com')                          // строка, массив, ['email' => 'Имя']
    ->setCc('cc@domain.com')->setBcc(['a@x.io', 'b@x.io'])
    ->setReplyTo('support@domain.com')
    ->setSubject('Тема')
    ->setTextBody('Текстовая версия')
    ->setHtmlBody('<b>HTML-версия</b>')
    ->send();                                          // true/false
```

С представлением:

```php
Yii::$app->mailer->compose('passwordReset', ['user' => $user])     // mail/passwordReset.php + layouts/html.php
    ->setTo($user->email)
    ->setSubject('Восстановление пароля')
    ->send();

// разные шаблоны для HTML и текста
Yii::$app->mailer->compose(['html' => 'passwordReset-html', 'text' => 'passwordReset-text'], ['user' => $user])
```

```php title="mail/passwordReset.php"
<?php
use yii\helpers\Html;
use yii\helpers\Url;

// абсолютный URL!
$resetLink = Url::to(['site/reset-password', 'token' => $user->password_reset_token], true);
?>
<p>Здравствуйте, <?= Html::encode($user->username) ?>!</p>
<p>Для сброса пароля перейдите по ссылке: <?= Html::a(Html::encode($resetLink), $resetLink) ?></p>
```

`$message` (объект письма) доступен в представлении — можно `$message->setSubject()` прямо там. Layout — `mail/layouts/html.php` и `text.php` (`htmlLayout`/`textLayout`); `false` — без layout. Внутри layout — `$content` и `$this->head()`/`beginBody()`/`endBody()`, как в обычных.

## Вложения и картинки

```php
$message = Yii::$app->mailer->compose();
$message->attach('/path/to/report.pdf');
$message->attach('/path/to/file', ['fileName' => 'отчёт.pdf', 'contentType' => 'application/pdf']);
$message->attachContent($csvString, ['fileName' => 'data.csv', 'contentType' => 'text/csv']);

// встроенное изображение: сначала embed, потом cid в HTML
$imgSrc = $message->embed('/path/to/logo.png');
$message->setHtmlBody('<img src="' . $imgSrc . '"> Привет!');
// или из представления: $message->embed(…) внутри mail/…php
```

## Массовая отправка

```php
$messages = [];
foreach ($users as $user) {
    $messages[] = Yii::$app->mailer->compose('newsletter', ['user' => $user])
        ->setTo($user->email)
        ->setSubject('Новости');
}
$sent = Yii::$app->mailer->sendMultiple($messages);   // число отправленных; одно соединение SMTP
```

Большие рассылки — из консольной команды или очереди (`yii2-queue`), не из web-запроса. В консоли задайте `urlManager.hostInfo`, чтобы `Url::to(…, true)` строил ссылки.

## Разработка и тесты

```php
'useFileTransport' => true,
'fileTransportPath' => '@runtime/mail',      // по умолчанию
// 'fileTransportCallback' => function ($mailer, $message) { return 'message-' . time() . '.eml'; },
```

Письма сохраняются как `.eml` — открываются почтовым клиентом или панелью Mail в [отладчике](dev-tools). В функциональных тестах модуль `Yii2` Codeception: `$I->seeEmailIsSent()`, `$I->grabLastSentEmail()`, `$I->grabSentEmails()`.

## События и расширение

- `mailer` генерирует `beforeSend` (`$event->isValid = false` — отменить) и `afterSend`.
- Свой mailer — наследовать `yii\mail\BaseMailer` (`sendMessage()`) и `yii\mail\BaseMessage`; так работают расширения для Mailgun, SES, SendGrid.
- Шаблоны с Twig/Smarty — те же рендереры представлений.

> [!GOTCHA]
> Относительные ссылки и картинки в письмах не работают: всегда `Url::to([...], true)` и абсолютные `src`. Не забывайте текстовую версию (`setTextBody`) — без неё письма чаще попадают в спам. `From` должен совпадать с доменом SMTP-аккаунта (SPF/DKIM).

:::quiz Проверь себя
Q: Как в разработке посмотреть письмо, не отправляя его?
A: `useFileTransport => true` — письма пишутся в `@runtime/mail` как `.eml`; видны и в панели Mail отладчика.
Q: Где ищутся представления писем при `compose('welcome')`?
A: В `viewPath` (по умолчанию `@app/mail`): `welcome.php` + layout `layouts/html.php`.
Q: Как вставить картинку в тело письма?
A: `$src = $message->embed($path)` и `<img src="…">` с полученным cid.
Q: Почему ссылка в письме ведёт на `/site/index` без домена?
A: Использован относительный URL; нужен `Url::to([...], true)` (в консоли — с настроенным `hostInfo`).
Q: Чем `sendMultiple()` лучше цикла `send()`?
A: Одно соединение с SMTP на все письма и возврат числа отправленных.
:::
