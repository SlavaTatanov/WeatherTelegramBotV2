from aiogram import types
from Bot.CALLBACKS import CURRENT, FIVE_DAY, WEEKEND, SHORT, COMMON, TOMORROW


def replay_get_location() -> types.ReplyKeyboardMarkup:
    """
    Клавиатура запрашивающая геопозицию
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("Отправить геопозицию", request_location=True)
    keyboard.add(button)
    return keyboard


def inline_get_weather_type() -> types.InlineKeyboardMarkup:
    """
    Клавиатура для выбора погоды (сегодня, завтра, 5 дней, выходные)
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.row(types.InlineKeyboardButton("Сегодня", callback_data=CURRENT),
                 types.InlineKeyboardButton("Завтра", callback_data=TOMORROW))
    keyboard.row(types.InlineKeyboardButton("5 дней", callback_data=FIVE_DAY),
                 types.InlineKeyboardButton("Выходные", callback_data=WEEKEND))
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
