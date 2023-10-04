from datetime import date, timedelta
from aiohttp import ClientSession
from async_lru import alru_cache
from Bot.utils import req_counter
from copy import deepcopy
from Bot.callbacks import SHORT


class Weather:
    """
    Класс описывающий данные о погоде.
    Получить погоду на сегодня weather.current_weather()
    Получить погоду на завтра weather.tomorrow_weather()
    """
    def __init__(self, coord, cur_date, weather_type, place_name=None):
        self.coord = coord
        self._cur_date = cur_date
        self._weather_type = weather_type
        self.place_name = place_name

    @staticmethod
    @alru_cache(maxsize=15)
    @req_counter("API_REQ")
    async def _request_weather(coord, start_date: date):
        """
        Запрос погоды API, его данные кешируются
        """
        end_date = start_date + timedelta(days=6)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coord[0],
            "longitude": coord[1],
            "start_date": str(start_date),
            "end_date": str(end_date),
            "hourly": "temperature_2m,precipitation_probability,"
                      "rain,showers,snowfall,cloudcover,windspeed_10m,"
                      "winddirection_10m,windgusts_10m,weathercode",
            "timezone": "auto"
        }
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                res = await response.json()
                return res

    async def _get_weather(self):
        """
        Делаем запрос к АПИ и форматируем его для дальнейшей работы
        """
        req = await self._request_weather(self.coord, self._cur_date)
        req = deepcopy(req)
        normal_data = self._data_normalize(req)
        return normal_data

    @staticmethod
    def _data_normalize(api_req):
        """
        Переформатирует данные для дальнейшего использования
        """
        data = api_req["hourly"]
        time_points = [*enumerate(data.pop("time"))]
        res = {}
        for i, t in time_points:
            inner = []
            for k, v in data.items():
                inner.append((k, v[i]))
            res[t] = {k: v for k, v in inner}
            inner.clear()
        return res

    async def current_weather(self):
        """
        Получить погоду на сегодня
        """
        req = await self._get_weather()
        res = self._filter_data_by_date(self._cur_date, req)
        res_header = self._header_create(self._cur_date)
        res_body = self._day_formatting(res)
        return res_header + res_body

    async def tomorrow_weather(self):
        """
        Получить погоду на завтра
        """
        req = await self._get_weather()
        tomorrow = self._cur_date + timedelta(days=1)
        res = self._filter_data_by_date(tomorrow, req)
        res_header = self._header_create(tomorrow)
        res_body = self._day_formatting(res)
        return res_header + res_body

    async def weekend_weather(self):
        """
        Получить погоду на выходные, работает как генератор
        """
        req = await self._get_weather()
        saturday, sunday = self._weekend_days()
        for day in (saturday, sunday):
            res = self._filter_data_by_date(day, req)
            res_header = self._header_create(day)
            res_body = self._day_formatting(res)
            yield res_header + res_body

    async def five_day_weather(self):
        """
        Погода на 5 дней
        """
        req = await self._get_weather()
        first = self._cur_date
        second = self._cur_date + timedelta(days=1)
        third = self._cur_date + timedelta(days=2)
        fourth = self._cur_date + timedelta(days=3)
        five = self._cur_date + timedelta(days=4)
        for day in (first, second, third, fourth, five):
            res = self._filter_data_by_date(day, req)
            res_header = self._header_create(day)
            res_body = self._day_formatting(res)
            yield res_header + res_body

    def _header_create(self, day_in_msg):
        """
        Создает шапку сообщения, если есть имя места то добавляет его
        """
        header = self._date_formatting(day_in_msg)
        if self.place_name:
            header += "\n"
            header += self.place_name
        return header + "\n\n"

    def _weekend_days(self) -> tuple[date, date]:
        """
        Возвращает кортеж из субботы, воскресенья типа date
        """
        year, week, _ = self._cur_date.isocalendar()
        saturday = date.fromisocalendar(year, week, 6)
        sunday = date.fromisocalendar(year, week, 7)
        # Если день воскресенье, вернем след выходные
        if sunday == self._cur_date:
            saturday = date.fromisocalendar(year, week + 1, 6)
            sunday = date.fromisocalendar(year, week + 1, 7)
        return saturday, sunday

    def _day_formatting(self, day: dict):
        if self._weather_type == SHORT:
            return self._short_formatting(day)
        else:
            return self._common_formatting(day)

    def _short_formatting(self, day_info: dict):
        """
        Сообщение для короткого прогноза погоды
        """
        night = [v for k, v in day_info.items() if k[-5:] <= "05:00"]
        morning = [v for k, v in day_info.items() if "05:00" < k[-5:] <= "11:00"]
        day = [v for k, v in day_info.items() if "11:00" < k[-5:] <= "17:00"]
        evening = [v for k, v in day_info.items() if "17:00" < k[-5:] <= "23:00"]
        info = self._get_avg_max_sum_min(
            {"Ночь": night, "Утро": morning, "День": day, "Вечер": evening}
        )
        msg = self._create_msg(info)
        return msg

    def _common_formatting(self, day_info: dict):
        """
        Сообщение для подробного прогноза погоды
        """
        time_2 = [v for k, v in day_info.items() if k[-5:] <= '03:00']
        time_5 = [v for k, v in day_info.items() if '03:00' < k[-5:] <= '06:00']
        time_8 = [v for k, v in day_info.items() if '06:00' < k[-5:] <= '09:00']
        time_11 = [v for k, v in day_info.items() if '09:00' < k[-5:] <= '12:00']
        time_14 = [v for k, v in day_info.items() if '12:00' < k[-5:] <= '15:00']
        time_17 = [v for k, v in day_info.items() if '15:00' < k[-5:] <= '18:00']
        time_20 = [v for k, v in day_info.items() if '18:00' < k[-5:] <= '21:00']
        time_23 = [v for k, v in day_info.items() if '21:00' < k[-5:]]
        info = self._get_avg_max_sum_min(
            {"2:00": time_2, "5:00": time_5, "8:00": time_8, "11:00": time_11, "14:00": time_14,
             "17:00": time_17, "20:00": time_20, "23:00": time_23}
        )
        msg = self._create_msg(info)
        return msg

    @staticmethod
    def _create_msg(info):
        msg = ""
        for k, v in info.items():
            clouds = Clouds(
                v["avg"]['cloudcover'],
                v["avg"]['rain'], v["avg"]['showers'],
                v['avg']['snowfall'],
                v["max"]["weathercode"]
            )
            wind = Wind(v["avg"]['windspeed_10m'], int(v['avg']['winddirection_10m']), v['max']['windgusts_10m'])
            min_temp = int(v['min']['temperature_2m'])
            avg_temp = int(v['avg']['temperature_2m'])
            max_temp = int(v['max']['temperature_2m'])
            weather_code = WeatherCode(v["max"]["weathercode"])
            rain = Rain(v['sum']['rain'], v['sum']['showers'])
            temp = Temperature(min_temp, max_temp, avg_temp)
            msg += f"<b>{k}</b> {clouds}\n" \
                   f"<i>{weather_code}</i>\n\n" \
                   f"🌡 Темп.: {temp}\n" \
                   f"💨 Ветер: {wind}"
            if rain:
                msg += f"\n☔️ Дождь: {rain}"
            msg += "\n\n"
        return msg

    def _get_avg_max_sum_min(self, info: dict):
        """
        Собирает словарь с минимальными, средними, и суммированными значениями
        """
        res = {}
        for k, v in info.items():
            res[k] = {
                "avg": self._get_average_fields(v),
                "max": self._get_max_fields(v),
                "sum": self._get_sum_fields(v),
                "min": self._get_min_fields(v)
            }
        return res

    @staticmethod
    def _get_average_fields(data: list) -> dict[str, float]:
        """
        Принимает список с данными для нескольких часов, и сводит их в один усредняя значения
        """
        average_dict = {}
        for field in data[0].keys():
            # field это перебор всех ключей, в данном случае для первого элемента
            # будет 'cloudcover', 'precipitation_probability' ...
            values = [item[field] for item in data]  # Получить все значения для данного поля
            average_dict[field] = round(sum(values) / len(values), 2)  # Доб усредненное значение в рез словарь
        return average_dict

    @staticmethod
    def _get_max_fields(data: list):
        """
        Получаем максимальные значения для полей
        """
        max_fields = {}
        for field in data[0].keys():
            values = [item[field] for item in data]
            max_fields[field] = max(values)
        return max_fields

    @staticmethod
    def _get_min_fields(data: list):
        """
        Получаем минимальные значения
        """
        min_fields = {}
        for field in data[0].keys():
            values = [item[field] for item in data]
            min_fields[field] = min(values)
        return min_fields

    @staticmethod
    def _get_sum_fields(data: list):
        """
        Получаем сумму для поля
        """
        sum_fields = {}
        for field in data[0].keys():
            values = [item[field] for item in data]
            sum_fields[field] = sum(values)
        return sum_fields

    @staticmethod
    def _filter_data_by_date(date_input: date, data: dict) -> dict:
        """
        Фильтрует данные по текущей дате
        """
        return {k: v for k, v in data.items() if str(date_input) in k}

    @staticmethod
    def _date_formatting(date_for_format: date):
        months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
                  "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return f"{days[date_for_format.weekday()]}, {date_for_format.day} {months[int(date_for_format.month) - 1]}"

    @classmethod
    def clean_api_cache(cls):
        """Чистим кеш функции запроса к апи"""
        cls._request_weather.cache_clear()


class Wind:
    """
    Класс описывающий ветер, имеет строковое представление вида
    f"{self.speed} м/с (до {self.gusts} м/с) {self.direction}"
    """
    def __init__(self, speed, direction, gusts=None):
        """
        Скорость и порывы принимает в км/ч переводит в м/с
        """
        speed *= 0.28
        if gusts:
            gusts = round(gusts * 0.28, 1)
        self.speed = str(float(round(speed, 1)))
        self.direction = self.direction_str(direction)
        self.gusts = gusts

    def __str__(self):
        if self.gusts:
            return f"{self.speed} м/с (до {self.gusts} м/с) {self.direction}"
        else:
            return f"{self.speed} м/с {self.direction}"

    @staticmethod
    def direction_str(direction):
        """
        Определяет направление ветра и возвращает строковое представление
        """
        if 22.5 < direction <= 67.5:
            return "СВ ⇙"
        elif 67.5 < direction <= 112.5:
            return "В ⇐"
        elif 112.5 < direction <= 157.5:
            return "ЮВ ⇖"
        elif 157.5 < direction <= 202.5:
            return "Ю ⇑"
        elif 202.5 < direction <= 247.5:
            return "ЮЗ ⇗"
        elif 247.5 < direction <= 292.5:
            return "З ⇒"
        elif 292.5 < direction <= 337.5:
            return "СЗ ⇘"
        else:
            return "С ⇓"


class Clouds:
    """
    Класс определяющий иконку облаков, осадков, гроз
    """
    def __init__(self, cloud_cover, rain, showers, snow, weather_code):
        self._cloud_cover = cloud_cover
        self._rain = rain + showers
        self._snow = snow
        self._weather_code = weather_code

    def __str__(self):
        return f"{self._get_image()}"

    def _get_image(self):
        # Передаем объект вида [cloud, rain, snow]
        # И начинаем сопоставлять
        match [self._cloud_cover, self._rain, self._snow, self._weather_code]:
            case [_, rain, _, code] if rain > 0 and code in [95, 96, 99]:
                return "⛈"
            case [_, _, _, code] if code in [95, 96, 99]:
                return "🌩"
            case [_, _, snow, _] if snow > 0:
                return "🌨"
            case [cloud, rain, _, _] if rain > 0 and cloud < 50:
                return "🌦"
            case [cloud, rain, _, _] if rain > 0 and cloud >= 50:
                return "🌧"
            case [cloud, _, _, _] if cloud <= 20:
                return "☀️"
            case [cloud, _, _, _] if cloud <= 40:
                return "🌤"
            case [cloud, _, _, _] if cloud <= 60:
                return "⛅"
            case [cloud, _, _, _] if cloud <= 80:
                return "🌥"
            case [cloud, _, _, _] if cloud <= 100:
                return "☁️"


class WeatherCode:
    """
    Класс имеющий строковое представление - описание погоды по коду
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        get_str = self._get_description()
        if get_str:
            return f"{get_str}"
        else:
            return ""

    def _get_description(self):
        match self.code:
            case 0:
                return "Ясно"
            case 1:
                return "Преимущественно ясно"
            case 2:
                return "Переменная облачность"
            case 3:
                return "Пасмурно"
            case 45:
                return "Туман"
            case 48:
                return "Туман с изморозью"
            case 51:
                return "Легкий моросящий дождь"
            case 53:
                return "Умеренный моросящий дождь"
            case 55:
                return "Плотный моросящий дождь"
            case 56:
                return "Легкий ледяной моросящий дождь"
            case 57:
                return "Плотный ледяной моросящий дождь"
            case 61:
                return "Легкий дождь"
            case 63:
                return "Умеренный дождь"
            case 65:
                return "Сильный дождь"
            case 66:
                return "Легкий ледяной дождь"
            case 67:
                return "Сильный ледяной дождь"
            case 71:
                return "Легкий снегопад"
            case 73:
                return "Средний снегопад"
            case 75:
                return "Сильный снегопад"
            case 77:
                return "Снежный зерна"
            case 80:
                return "Дождь"
            case 81:
                return "Ливень"
            case 82:
                return "Сильный ливень"
            case 85:
                return "Сильный снегопад"
            case 86:
                return "Очень сильный снегопад"
            case code if code in [95, 96, 99]:
                return "Гроза"


class Rain:
    """
    Класс имеющий строковое представление дождя
    """
    def __init__(self, rain, showers):
        """
        Получаем дождь, ливни, вероятность, дождь и ливни для простоты складываем
        """
        self.rain = rain
        self.showers = showers
        self.all_rain = self.rain + self.showers

    def __str__(self):
        """
        Строковое представление дождя, с округлением
        """
        return f"{round(self.all_rain, 1)} мм"

    def __bool__(self):
        """
        Проверяет что объект дождь не пустой
        """
        return bool(self.all_rain)


class Temperature:
    """
    Класс формирующий строковое представление температуры
    """
    def __init__(self, min_temp, max_temp, avg_temp):
        self.avg = avg_temp
        if min_temp != max_temp:
            self.min_max = f"(от {min_temp}℃ до {max_temp}℃)"
        else:
            self.min_max = None

    def __str__(self):
        msg = f"{self.avg}℃"
        if self.min_max:
            msg += f" {self.min_max}"
        return msg
