from datetime import date
from aiohttp import ClientSession


def date_formatting(date_for_format: date):
    months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
              "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return f"{days[date_for_format.weekday()]}, {date_for_format.day} {months[int(date_for_format.month) - 1]}"


class Weather:
    def __init__(self, coord, cur_date):
        self.coord = coord
        self._cur_date = cur_date

    async def _request_weather(self, start_date: date, end_date: date):
        """
        Запрос погоды API
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.coord[0],
            "longitude": self.coord[1],
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

    def _weekend_days(self):
        year, week, _ = self._cur_date.isocalendar()
        saturday = date.fromisocalendar(year, week, 6)
        sunday = date.fromisocalendar(year, week, 7)
        return saturday, sunday
