```sudo make build-dev```

```sudo make dev```

## Переменные окружения

* DRIVER - драйвер для подключения к БД
* DATABASE - название БД
* DATABASE_HOST - хост БД
* DATABASE_PORT - порт БД
* POSTGRES_USER - пользователь БД
* POSTGRES_PASSWORD - пароль от БД
* DRIVER_ALEMBIC - драйвер для миграций

* PORT_SERVER - порт запуска внутри контейнера
* PORT_LOADING - порт сервиса загрузки(внешний)
* PORT_METRICS - порт сервиса метрик(внешний)

* UPLOAD_DIR - директория, куда выгружать файлы

* OPEN_AI_FOLDER - folder ID Yandex AI Studio
* OPEN_AI_KEY - API Key Yandex AI Studio