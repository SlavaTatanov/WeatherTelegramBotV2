import datetime

from aiogram import types
from Bot.CALLBACKS import CURRENT, FIVE_DAY, WEEKEND, SHORT, COMMON, TOMORROW
from Bot.config import OWNERS
from Bot.utils import is_sunday


def replay_get_location() -> types.ReplyKeyboardMarkup:
    """
    Клавиатура запрашивающая геопозицию
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("Отправить геопозицию", request_location=True)
    keyboard.add(button)
    return keyboard


def inline_get_weather_type(day: datetime.date) -> types.InlineKeyboardMarkup:
    """
    Клавиатура для выбора погоды (сегодня, завтра, 5 дней, выходные)
    """
    if is_sunday(day):
        weekend = "След. выходные"
    else:
        weekend = "Выходные"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.row(types.InlineKeyboardButton("Сегодня", callback_data=CURRENT),
                 types.InlineKeyboardButton("Завтра", callback_data=TOMORROW))
    keyboard.row(types.InlineKeyboardButton("5 дней", callback_data=FIVE_DAY),
                 types.InlineKeyboardButton(weekend, callback_data=WEEKEND))
    return keyboard


def inline_get_weather_places(places: dict = None) -> types.InlineKeyboardMarkup:
    """
    Клавиатура для выбора геопозиции
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("Текущее место", callback_data="current_place"))
    return keyboard


def inline_weather_type(weather_type=None):
    """
    Клавиатура с типами погоды (Краткий прогноз, обычный, почасовой)
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Краткий", callback_data=SHORT))
    keyboard.add(types.InlineKeyboardButton("Обычный", callback_data=COMMON))
    return keyboard


def inline_settings_menu(user_id: int):
    """
    Клавиатура настроек:
    - Добавить место
    - Удалить место
    - Админ-панель (у админа)
    """
    keyboard = types.InlineKeyboardMarkup()
    if user_id in OWNERS:
        keyboard.add(types.InlineKeyboardButton("Админ-меню", callback_data="admin-panel"))
    return keyboard


def inline_admin_menu():
    """
    Меню админа:
    - Логи запросов к API
    - Выход
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Логи-запросов к API", callback_data="api_log"))
    keyboard.add(types.InlineKeyboardButton("Выход", callback_data="exit"))
    return keyboard


def inline_admin_api_log():
    """
    Меню выбора типа логов:
    - Запросы за 5 дней
    - Назад (Вернет к админ меню)
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Запросы за 5 дней", callback_data="api_log_5_days"))
    keyboard.add(types.InlineKeyboardButton("Максимальное кол-во запросов", callback_data="api_log_max"))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="admin-panel"))
    return keyboard
