import unittest
from Bot.weather.core import Weather
from datetime import date
from Bot.callbacks import CURRENT


class TestWeather(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = Weather((55.30, 61.22), date(2023, 7, 5), CURRENT)
        self.obj2 = Weather((55.30, 61.22), date(2023, 7, 23), CURRENT)

    def test_weekend_days(self):
        self.assertEqual(self.obj._weekend_days(),
                         (date(2023, 7, 8), date(2023, 7, 9)),
                         "Вычисление выходных дней")
        self.assertEqual(self.obj2._weekend_days(), (date(2023, 7, 29), date(2023, 7, 30)),
                         "Запрос выходных дней в воскресенье")
