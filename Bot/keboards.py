from aiogram import types
from Bot.CALLBACKS import CURRENT, FIVE_DAY, WEEKEND, SHORT, HOURLY


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
    Клавиатура для выбора погоды
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for text, callback in {"Текущая": CURRENT, "На 5 дней": FIVE_DAY, "На выходные": WEEKEND}.items():
        btn = types.InlineKeyboardButton(text=text, callback_data=callback)
        keyboard.add(btn)
    return keyboard


def inline_get_weather_places(places: dict = None) -> types.InlineKeyboardMarkup:
    """
    Клавиатура для выбора геопозиции
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("Текущее место", callback_data="current_place"))
    return keyboard


def inline_weather_type():
    """
    Клавиатура с типами погоды (Краткий прогноз, почасовой)
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Краткий прогноз", callback_data=SHORT))
    keyboard.add(types.InlineKeyboardButton("Почасовой", callback_data=HOURLY))
    return keyboard