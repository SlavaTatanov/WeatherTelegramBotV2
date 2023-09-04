# WeatherTelegramBotV2

⛅  ⛈  🌧  🌨  🌩  💨

Телеграм бот, который предоставляет информацию о погоде. 
Пользователь отправляет свою гео-позицию и получает информацию о погоде.
Пользователи могут составлять список собственных мест, где их интересует погода,
для ускорения взаимодействия с ботом.

Можно получить информацию о погоде:
- Сегодня
- Завтра
- На 5 дней
- На выходные

Доступен краткий и подробный прогноз погоды.

![photo_2023-09-04_20-36-27](https://github.com/SlavaTatanov/WeatherTelegramBotV2/assets/107018438/1f220b97-089d-4346-b6f1-d9409e8b8081)

Есть возможность обратной связи пользователей через меню настроек. Можно сообщить об ошибке или написать свои пожелания.
Для администратора есть возможность контролировать количество запросов которое бот делает к API.

## Реализация
- Python 3.10 и выше
- aiogram v2
- MongoDB

Запосы погоды осуществляются в бесплатном API - [Open-meteo](https://open-meteo.com/).

## Развертывание
Используя Docker compose

1. Клонируем репозиторий
2. Файл _config.py переименуем в config.py и заполняем
3. В корне проекта выполняем:
```shell
docker-compose up
```
## О тестировании
Для тестирования моделей предоставляющих обьекты MongoDB используется асинхронный мок - [mongomock-motor](https://pypi.org/project/mongomock-motor/).
