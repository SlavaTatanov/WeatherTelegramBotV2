from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
from Bot import dp, bot, WeatherState
from Bot.keboards import replay_get_location, inline_get_weather_type, inline_get_weather_places, inline_weather_type
from Bot.CALLBACKS import WEATHER_TIMES, CURRENT, FREQUENCY, WEEKEND, COMMON, TOMORROW
from Bot.Weather.core import date_formatting, Weather
from Bot.background_task import back_task
from datetime import date


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " и скоро он будет доступен для использования. "
    await message.answer(answer_for_user)


@dp.message_handler(commands=['weather'], state="*")
async def weather(message: types.Message):
    """
    Выбираем когда мы хотим прогноз погоды, сегодня, завтра ...
    Даем пользователю inline клавиатуру с кнопками
    """
    await WeatherState.weather_time.set()
    await message.answer("Какую погоду вы хотите узнать?", reply_markup=inline_get_weather_type())


@dp.callback_query_handler(lambda callback: callback.data in WEATHER_TIMES, state=WeatherState.weather_time)
async def weather_time(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловим время для которого необходимо узнать погоду и пишем его в контекст
    После запрашиваем тип погоды (почасовая, обычный, краткий прогноз) если погода текущая, либо сразу место.
    """
    async with state.proxy() as data:
        data["weather_time"] = callback.data
        # Запоминаем сообщение откуда приходит callback, потом удалим
        data["msg"] = callback.message
        # Запоминаем текущую дату
        data["start_date"] = callback.message.date.date()

    if callback.data in [CURRENT, TOMORROW, WEEKEND]:
        await WeatherState.next()
        await callback.message.edit_text("Выберете детализацию погоды", reply_markup=inline_weather_type(callback.data))
    else:
        async with state.proxy() as data:
            # Сразу устанавливаем детализацию погоды
            data["weather_type"] = COMMON
        await WeatherState.weather_place.set()
        await callback.message.edit_text("Выберете место", reply_markup=inline_get_weather_places())


@dp.callback_query_handler(lambda callback: callback.data in FREQUENCY, state=WeatherState.weather_type)
async def weather_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["type"] = callback.data
    await WeatherState.next()
    await callback.message.edit_text("Выберете место", reply_markup=inline_get_weather_places())


@dp.callback_query_handler(lambda callback: callback.data == "current_place", state=WeatherState.weather_place)
async def current_place(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["weather_type"] = callback.data
        data["location_req"] = await bot.send_message(callback.from_user.id, "Укажите геопозицию",
                                                      reply_markup=replay_get_location())


@dp.message_handler(content_types=["location"], state=WeatherState.weather_place)
async def weather_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Удаляем inline сообщение и запрос позиции
        await data["msg"].delete()
        await bot.delete_message(data["location_req"]["chat"]["id"], data["location_req"]["message_id"])

        lat, lon = message.location.latitude, message.location.longitude
        res = await Weather((lat, lon), data["start_date"])._request_weather((lat, lon),data["start_date"], data["start_date"])
        await bot.send_message(message.from_user.id, f"{date_formatting(data['start_date'])}\n\n"
                                                     f"{res}")
    await message.delete()


@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    print(Weather._request_weather.cache_info())
    await Weather((55.43, 54.32), date(2023, 7, 6))._request_weather((55.43, 54.32), date(2023, 7, 6),date(2023, 7, 6))


# Запускаем бота и фоновую задачу
async def main():
    asyncio.create_task(back_task())
    await dp.start_polling()

# Получаем loop
loop = asyncio.new_event_loop()
# Запускаем
loop.run_until_complete(main())

