---
id: glossary
title: Глоссарий
part: extra
summary: Ключевые термины Yii 2 в алфавитном порядке с короткими определениями и ссылками на разделы, где о них рассказано подробно.
sources:
---

:::lead
Короткие определения терминов, которые встречаются по всему руководству. Ссылка ведёт в раздел, где термин разобран.
:::

## А–Д

:::kv
`Active Record (AR)` — класс, представляющий строку таблицы: атрибуты = столбцы, `save()`/`delete()`, связи `hasOne`/`hasMany`. → [Active Record](active-record)
`ActiveDataProvider` — провайдер данных, который берёт страницу моделей из `ActiveQuery` с пагинацией и сортировкой. → [Провайдеры данных](data-providers)
`ActiveForm` / `ActiveField` — виджет формы и одно её поле, привязанные к модели: label, input, ошибка, JS-валидация. → [Формы](forms)
`ActiveQuery` — объект запроса для AR (наследует `Query`): `where()`, `with()`, `joinWith()`, `all()`. → [Active Record](active-record)
`Asset Bundle` — класс с набором CSS/JS-файлов и зависимостями; регистрируется в представлении и публикуется в `web/assets`. → [Ассеты](assets)
`ACF (Access Control Filter)` — фильтр `AccessControl` с правилами allow/deny по ролям, IP, методам. → [Авторизация](authorization)
`Псевдоним (alias)` — имя вида `@app`, заменяющее путь или URL; `Yii::getAlias()`. → [Конфигурации](configurations)
`Действие (action)` — метод контроллера `actionXxx()` или класс `Action`; конечная точка маршрута. → [Контроллеры](controllers)
`Автозагрузка` — поиск файла класса по namespace и псевдониму (`app\models\User` → `@app/models/User.php`). → [Конфигурации](configurations)
`Аутентификация` — установление личности пользователя; компонент `user` + `IdentityInterface`. → [Аутентификация](authentication)
`Авторизация` — проверка прав: ACF или RBAC (`can()`). → [Авторизация](authorization)
`Бутстрап (bootstrap)` — компоненты/классы, инициализируемые при старте приложения (`'bootstrap' => ['log']`, `BootstrapInterface`). → [Жизненный цикл](lifecycle)
`Behavior (поведение)` — объект, добавляющий компоненту методы, свойства и обработчики событий без наследования. → [Поведения](behaviors)
`Валидатор` — класс правила проверки (`required`, `email`, свой). → [Валидация](validation), [Валидаторы](validators)
`Виджет` — переиспользуемый блок представления (`Widget::widget()` / `begin()`…`end()`). → [Виджеты](widgets)
`Входной скрипт` — `web/index.php` / `yii`: подключает автозагрузчик, создаёт приложение, `run()`. → [Приложение](app)
`Грязные атрибуты (dirty)` — изменённые после загрузки атрибуты AR; только они попадают в UPDATE. → [Active Record](active-record)
`DAO` — Data Access Objects: `Connection`/`Command` — работа с SQL напрямую, с привязкой параметров. → [DAO](dao)
`DI-контейнер` — `Yii::$container`: создаёт объекты, разрешая зависимости по типам конструктора. → [DI](di)
`DataProvider` — источник постраничных данных для `GridView`/`ListView`/REST. → [Провайдеры данных](data-providers)
`Зависимость кэша` — условие инвалидации (`TagDependency`, `DbDependency`, `FileDependency`…). → [Кэширование данных](caching)
:::

## Ж–П

:::kv
`Жадная загрузка (eager)` — `with('rel')`: связанные записи одним запросом для всех моделей; против N+1. → [Active Record](active-record)
`Ленивая загрузка (lazy)` — `$model->rel`: запрос при первом обращении. → [Active Record](active-record)
`Компонент` — `yii\base\Component`: свойства, события, поведения. Компонент приложения — `Yii::$app->id`. → [Компоненты](components)
`Конфигурация` — массив `['class' => …, 'prop' => …]`, описывающий объект; `Yii::createObject()`. → [Конфигурации](configurations)
`Контроллер` — класс, группирующий действия; `Controller` → `render()`, `redirect()`. → [Контроллеры](controllers)
`Layout (шаблон)` — общая обёртка страниц (`views/layouts/main.php`), получает `$content`. → [Представления](views)
`Массовое присваивание` — `$model->attributes = $data` / `load()`; только безопасные атрибуты. → [Модели](models)
`Миграция` — класс, меняющий схему БД, с `up()`/`down()`; команда `migrate`. → [Миграции](migrations)
`Модель` — `yii\base\Model`: атрибуты, правила, сценарии, подписи, ошибки. → [Модели](models)
`Модуль` — мини-приложение с контроллерами, моделями и представлениями; `modules` в конфигурации. → [Модули](modules)
`Маршрут (route)` — строка `module/controller/action`; `urlManager` разбирает и строит URL. → [Маршрутизация](routing)
`N+1` — 1 запрос за списком + по запросу на связь каждой строки; лечится `with()`. → [Active Record](active-record)
`Оптимистичная блокировка` — столбец версии; при несовпадении `StaleObjectException`. → [Active Record](active-record)
`Пагинация` — `Pagination` + `LinkPager`: `page`, `per-page`, `offset`/`limit`. → [Провайдеры данных](data-providers)
`Параметры (params)` — `Yii::$app->params['adminEmail']` — произвольные настройки приложения. → [Приложение](app)
`Провайдер данных` — см. DataProvider.
`Представление (view)` — PHP-шаблон в `views/`; `$this` — `yii\web\View`. → [Представления](views)
:::

## Р–Я

:::kv
`RBAC` — управление доступом на основе ролей: разрешения, роли, правила, `authManager`. → [Авторизация](authorization)
`REST` — `yii\rest\ActiveController` + `UrlRule`: CRUD-API поверх AR. → [REST](rest)
`Расширение` — Composer-пакет `yii2-extension` с `bootstrap` и псевдонимами. → [Расширения](extensions)
`Связь (relation)` — `hasOne`/`hasMany` (+`via`/`viaTable`) между AR-классами. → [Active Record](active-record)
`Сервис-локатор` — `Yii::$app`/модуль: хранит компоненты по ID, создаёт лениво. → [DI](di)
`Сессия` — `Yii::$app->session`: данные между запросами; flash-сообщения. → [Сессии и cookie](sessions)
`Событие` — `on()`/`trigger()`; `Event` с `sender`, `data`, `handled`, `isValid`. → [События](events)
`Сценарий (scenario)` — режим модели, определяющий активные правила и безопасные атрибуты. → [Модели](models)
`Тема (theme)` — подмена путей представлений (`pathMap`) без изменения кода. → [Представления](views)
`Фильтр` — поведение контроллера с `beforeAction`/`afterAction`: `AccessControl`, `VerbFilter`, `PageCache`, `Cors`… → [Фильтры](filters)
`Фикстура` — воспроизводимые данные для тестов (`ActiveFixture`). → [Тестирование](testing)
`Форматтер` — `Yii::$app->formatter`: `asDate`, `asCurrency`, `asSize`… → [Форматирование](formatting)
`Фрагментное кэширование` — `beginCache()`/`endCache()` в представлении. → [Кэширование вывода](caching-output)
`Хелпер` — статический класс-утилита: `Html`, `Url`, `ArrayHelper`, `Json`. → [Хелперы](helpers)
`Шаблон приложения` — basic (одно приложение) или advanced (frontend/backend/console/common). → [Установка](install)
`CSRF` — подделка межсайтовых запросов; токен `_csrf` в формах и заголовке. → [Безопасность](security)
`Gii` — генератор кода: модели, CRUD, контроллеры, модули. → [Инструменты](dev-tools)
`HATEOAS` — ссылки `_links` в ответах API (`Linkable`). → [REST](rest)
`Identity` — класс, реализующий `IdentityInterface`; `Yii::$app->user->identity`. → [Аутентификация](authentication)
`i18n` — интернационализация: `Yii::t()`, источники переводов, ICU-формат. → [i18n](i18n)
`Pjax` — виджет, обновляющий часть страницы через AJAX + pushState. → [Виджеты](widgets)
`Query Builder` — `yii\db\Query`: объектная сборка SQL под любую СУБД. → [Query Builder](query-builder)
`Response` — `Yii::$app->response`: статус, заголовки, формат, `sendFile()`. → [Запрос и ответ](request-response)
`Service Locator` — см. Сервис-локатор.
`UrlManager` — компонент разбора и генерации URL по правилам. → [Маршрутизация](routing)
`View (объект)` — `yii\web\View`: `render()`, `registerJs()`, `title`, `params`, блоки. → [Представления](views)
:::
