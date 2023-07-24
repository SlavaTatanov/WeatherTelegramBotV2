import datetime

from aiogram import types
from Bot.CALLBACKS import CURRENT, FIVE_DAY, WEEKEND, SHORT, COMMON, TOMORROW, CURRENT_PLACE, ADMIN_MENU, \
    ADMIN_API_LOG, EXIT, ADMIN_API_LOG_5, ADMIN_API_LOG_MAX, SETTINGS, SETTINGS_PLACES, SETTINGS_FEEDBACK, \
    SETTINGS_PLC_ADD, SETTINGS_PLC_DEL, SETTINGS_FEED_BAG, SETTINGS_FEED_FEATURE
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
    keyboard.add(types.InlineKeyboardButton("Выход", callback_data=EXIT))
    return keyboard


def inline_get_weather_places(places: dict = None) -> types.InlineKeyboardMarkup:
    """
    Клавиатура для выбора геопозиции
    """
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("Текущее место", callback_data=CURRENT_PLACE))
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
    keyboard.add(types.InlineKeyboardButton("Избранные места", callback_data=SETTINGS_PLACES))
    keyboard.add(types.InlineKeyboardButton("Обратная связь", callback_data=SETTINGS_FEEDBACK))
    if user_id in OWNERS:
        keyboard.add(types.InlineKeyboardButton("Админ-меню", callback_data=ADMIN_MENU))
    keyboard.add(types.InlineKeyboardButton("Выход", callback_data=EXIT))
    return keyboard


def inline_admin_menu():
    """
    Меню админа:
    - Логи запросов к API
    - Выход
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Логи-запросов к API", callback_data=ADMIN_API_LOG))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=SETTINGS))
    return keyboard


def inline_admin_api_log():
    """
    Меню выбора типа логов:
    - Запросы за 5 дней
    - Назад (Вернет к админ меню)
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Запросы за 5 дней", callback_data=ADMIN_API_LOG_5))
    keyboard.add(types.InlineKeyboardButton("Максимальное кол-во запросов", callback_data=ADMIN_API_LOG_MAX))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=ADMIN_MENU))
    return keyboard


def inline_settings_places(user_id: int):
    """
    Клавиатура добавить, удалить места
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Добавить место", callback_data=SETTINGS_PLC_ADD))
    keyboard.add(types.InlineKeyboardButton("Удалить место", callback_data=SETTINGS_PLC_DEL))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=SETTINGS))
    return keyboard


def inline_settings_feedback():
    """
    Клавиатура для обратной связи
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Сообщить об ошибке", callback_data=SETTINGS_FEED_BAG))
    keyboard.add(types.InlineKeyboardButton("Пожелания", callback_data=SETTINGS_FEED_FEATURE))
    keyboard.add(types.InlineKeyboardButton("Назад", callback_data=SETTINGS))
    return keyboard


def inline_places():
    """
    Клавиатура добавления/удаления места
    """
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Отмена", callback_data=SETTINGS_PLACES))
    return keyboard
