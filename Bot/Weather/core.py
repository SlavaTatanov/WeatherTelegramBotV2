from datetime import date, timedelta
from aiohttp import ClientSession
from async_lru import alru_cache
from Bot.utils import req_counter
from copy import deepcopy
from Bot.CALLBACKS import SHORT


def date_formatting(date_for_format: date):
    months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
              "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return f"{days[date_for_format.weekday()]}, {date_for_format.day} {months[int(date_for_format.month) - 1]}"


class Weather:
    def __init__(self, coord, cur_date, weather_type):
        self.coord = coord
        self._cur_date = cur_date
        self._weather_type = weather_type

    @staticmethod
    @alru_cache(maxsize=15)
    @req_counter("API_REQ")
    async def _request_weather(coord, start_date: date):
        """
        Запрос погоды API
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
                      "winddirection_10m,windgusts_10m",
            "timezone": "auto"
        }
        async with ClientSession() as session:
            async with session.get(url, params=params) as response:
                res = await response.json()
                return res

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
        req = await self._request_weather(self.coord, self._cur_date)
        req = deepcopy(req)
        normal_data = self._data_normalize(req)
        res = {k: v for k, v in normal_data.items() if str(self._cur_date) in k}
        res_header = date_formatting(self._cur_date) + "\n\n"
        res_body = self._day_formatting(res)
        return res_header + res_body

    def _weekend_days(self):
        year, week, _ = self._cur_date.isocalendar()
        saturday = date.fromisocalendar(year, week, 6)
        sunday = date.fromisocalendar(year, week, 7)
        return saturday, sunday

    def _day_formatting(self, day: dict):
        if self._weather_type == SHORT:
            return self._short_formatting(day)
        else:
            return self._common_formatting(day)

    def _short_formatting(self, day_info: dict):
        night = [v for k, v in day_info.items() if k[-5:] <= "05:00"]
        morning = [v for k, v in day_info.items() if "05:00" < k[-5:] <= "11:00"]
        day = [v for k, v in day_info.items() if "11:00" < k[-5:] <= "17:00"]
        evening = [v for k, v in day_info.items() if "17:00" < k[-5:] <= "23:00"]
        info = {
            "Ночь": self._get_average_fields(night),
            "Утро": self._get_average_fields(morning),
            "День": self._get_average_fields(day),
            "Вечер": self._get_average_fields(evening)
        }
        msg = ""
        for k, v in info.items():
            msg += f"{k}\n\n" \
                   f"🌡: {int(v['temperature_2m'])}℃\n" \
                   f"💨: {Wind(v['windspeed_10m'], int(v['winddirection_10m']), v['windgusts_10m'])}" \
                   f"\n\n"
        return msg

    @staticmethod
    def _common_formatting(day: dict):
        pass

    @staticmethod
    def _get_average_fields(data):
        average_dict = {}
        for field in data[0].keys():
            # field это перебор всех ключей, в данном случае для первого элемента
            # будет 'cloudcover', 'precipitation_probability' ...
            values = [item[field] for item in data]  # Получить все значения для данного поля
            average_dict[field] = round(sum(values) / len(values), 2)
        return average_dict


class Wind:
    def __init__(self, speed, direction, gusts=None):
        """
        Скорость и порывы принимает в км/ч переводит в м/с
        """
        speed = speed * 0.28
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
