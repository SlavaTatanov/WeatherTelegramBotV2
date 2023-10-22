from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from os import getenv
from Bot.config import TOKEN, DEVELOPMENT, TEST_TOKEN
import Bot.views.settings as view_settings
import Bot.views.admin as view_admin
import Bot.views.weather as view_weather
from Bot.callbacks import ADMIN_MENU, ADMIN_API_LOG, ADMIN_API_LOG_5, ADMIN_API_LOG_MAX, SETTINGS, \
    SETTINGS_PLACES, SETTINGS_FEEDBACK, SETTINGS_PLC_ADD, SETTINGS_PLC_DEL, SETTINGS_PLC_DEL_CONFIRM, WEATHER_TIMES, \
    FREQUENCY, CURRENT_PLACE, SETTINGS_FEED_BAG, SETTINGS_FEED_FEATURE, SETTINGS_PLC_FIND, SETTINGS_PLC_RIGHT, \
    SETTINGS_PLC_NO


def get_token() -> str:
    """
    Определяем какого бота необходимо использовать
    """
    # Смотрим есть ли ключик в переменных среды, если нет то дефолтный
    dev_status = int(getenv("DEVELOPMENT", DEVELOPMENT))
    if dev_status:
        return TEST_TOKEN
    return TOKEN


storage = MemoryStorage()

bot = Bot(get_token(), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


# Создаем классы для машины состояний
class WeatherState(StatesGroup):
    """
    Состояния для запроса погоды
    """
    weather_time = State()
    weather_type = State()
    weather_place = State()


class UserPlaces(StatesGroup):
    """
    Состояния для добавления мест
    """
    places_add = State()
    places_add_coord = State()
    place_del = State()
    place_del_name = State()
    place_confirm = State()


class Feedback(StatesGroup):
    """
    Состояния для добавления фидбека
    """
    feature = State()
    bug = State()


# Регистрация handlers

# -- weather --
dp.register_message_handler(view_weather.weather, commands=["weather"], state="*")
dp.register_callback_query_handler(view_weather.weather_time,
                                   lambda callback: callback.data in WEATHER_TIMES,
                                   state=WeatherState.weather_time)
dp.register_callback_query_handler(view_weather.weather_type,
                                   lambda callback: callback.data in FREQUENCY,
                                   state=WeatherState.weather_type)
dp.register_callback_query_handler(view_weather.current_place,
                                   lambda callback: callback.data == CURRENT_PLACE,
                                   state=WeatherState.weather_place)
dp.register_callback_query_handler(view_weather.current_place_from_user,
                                   lambda callback: callback.data != CURRENT_PLACE,
                                   state=WeatherState.weather_place)
dp.register_message_handler(view_weather.weather_place, content_types=['location'],
                            state=WeatherState.weather_place)
dp.register_message_handler(view_weather.weather_text_place, content_types=['text'],
                            state=WeatherState.weather_place)

# -- settings --
dp.register_message_handler(view_settings.settings_menu, commands=["settings"], state="*")
dp.register_callback_query_handler(view_settings.settings_menu_callback,
                                   lambda callback: callback.data == SETTINGS, state="*")
dp.register_callback_query_handler(view_settings.settings_places_menu,
                                   lambda callback: callback.data == SETTINGS_PLACES, state="*")
dp.register_callback_query_handler(view_settings.settings_feed_menu,
                                   lambda callback: callback.data == SETTINGS_FEEDBACK, state="*")
dp.register_callback_query_handler(view_settings.settings_place_add,
                                   lambda callback: callback.data == SETTINGS_PLC_ADD, state="*")
dp.register_message_handler(view_settings.settings_place_add_coord, content_types=['text'],
                            state=UserPlaces.places_add)
dp.register_message_handler(view_settings.settings_place_add_final, content_types=['location'],
                            state=UserPlaces.places_add_coord)
dp.register_callback_query_handler(view_settings.settings_place_find,
                                   lambda callback: callback.data == SETTINGS_PLC_FIND,
                                   state=UserPlaces.places_add_coord)
dp.register_callback_query_handler(view_settings.settings_place_confirm,
                                   lambda callback: callback.data == SETTINGS_PLC_RIGHT,
                                   state=UserPlaces.place_confirm)
dp.register_callback_query_handler(view_settings.settings_place_del,
                                   lambda callback: callback.data == SETTINGS_PLC_DEL, state="*")
dp.register_callback_query_handler(view_settings.settings_place_del_confirm,
                                   state=UserPlaces.place_del)
dp.register_callback_query_handler(view_settings.settings_place_del_final,
                                   lambda callback: callback.data == SETTINGS_PLC_DEL_CONFIRM,
                                   state=UserPlaces.place_del_name)
dp.register_callback_query_handler(view_settings.feedback_bag,
                                   lambda callback: callback.data == SETTINGS_FEED_BAG,
                                   state="*")
dp.register_callback_query_handler(view_settings.feedback_feature,
                                   lambda callback: callback.data == SETTINGS_FEED_FEATURE,
                                   state="*")
dp.register_message_handler(view_settings.feedback_text, content_types=['text'], state=Feedback.feature)
dp.register_message_handler(view_settings.bug_text, content_types=['text'], state=Feedback.bug)

# -- admin --
dp.register_callback_query_handler(view_admin.admin_menu,
                                   lambda callback: callback.data == ADMIN_MENU, state="*")
dp.register_callback_query_handler(view_admin.admin_log_api,
                                   lambda callback: callback.data == ADMIN_API_LOG, state="*")
dp.register_callback_query_handler(view_admin.admin_api_log_5_day,
                                   lambda callback: callback.data == ADMIN_API_LOG_5, state="*")
dp.register_callback_query_handler(view_admin.admin_api_log_max,
                                   lambda callback: callback.data == ADMIN_API_LOG_MAX, state="*")


async def set_commands(disp: Dispatcher):
    await disp.bot.set_my_commands([BotCommand("weather", "Погода"),
                                    BotCommand("settings", "Настройки"),
                                    BotCommand("help", "Помощь")])
