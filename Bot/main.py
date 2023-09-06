from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
from Bot import dp, bot, WeatherState, set_commands
from Bot.keboards import replay_get_location
from Bot.CALLBACKS import CURRENT, WEEKEND, TOMORROW, FIVE_DAY, CURRENT_PLACE, EXIT
from Bot.Weather.core import Weather
from Bot.background_task import back_task
from Bot.Database import create_indexes
from Bot.Database.models import UserInfo


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " в данный момент доступны только короткие прогнозы погоды. Часть функций может не работать"
    await message.answer(answer_for_user)


@dp.callback_query_handler(lambda callback: callback.data == CURRENT_PLACE, state=WeatherState.weather_place)
async def current_place(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["weather_type"] = callback.data
        data["location_req"] = await bot.send_message(callback.from_user.id, "Укажите геопозицию",
                                                      reply_markup=replay_get_location())


@dp.callback_query_handler(lambda callback: callback.data != CURRENT_PLACE, state=WeatherState.weather_place)
async def current_place_from_user(callback: types.CallbackQuery, state: FSMContext):
    # Получаем инфу юзера, и координаты места
    user_info = await UserInfo.get_user(callback.from_user.id)
    place_coord = tuple(user_info.get_place_coord(callback.data))

    async with state.proxy() as data:
        res = Weather(place_coord, data["start_date"], data["type"])

        # Отвечаем юзеру в зависимости от типа погоды
        if data["weather_time"] == CURRENT:
            res_msg = await res.current_weather()
            await bot.send_message(callback.from_user.id, res_msg)
        elif data["weather_time"] == TOMORROW:
            res_msg = await res.tomorrow_weather()
            await bot.send_message(callback.from_user.id, res_msg)
        elif data["weather_time"] == FIVE_DAY:
            async for msg in res.five_day_weather():
                await bot.send_message(callback.from_user.id, msg)
        elif data["weather_time"] == WEEKEND:
            async for msg in res.weekend_weather():
                await bot.send_message(callback.from_user.id, msg)
        else:
            await callback.answer("Что то пошло не так!")
    await callback.message.delete()


@dp.message_handler(content_types=["location"], state=WeatherState.weather_place)
async def weather_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Удаляем inline сообщение и запрос позиции
        await data["msg"].delete()
        try:
            await bot.delete_message(data["location_req"]["chat"]["id"], data["location_req"]["message_id"])
        except KeyError:
            pass

        lat, lon = message.location.latitude, message.location.longitude
        res = Weather((lat, lon), data["start_date"], data["type"])

        # Отвечаем юзеру в зависимости от типа погоды
        if data["weather_time"] == CURRENT:
            res_msg = await res.current_weather()
            await message.answer(res_msg)
        elif data["weather_time"] == TOMORROW:
            res_msg = await res.tomorrow_weather()
            await message.answer(res_msg)
        elif data["weather_time"] == FIVE_DAY:
            async for msg in res.five_day_weather():
                await message.answer(msg)
        elif data["weather_time"] == WEEKEND:
            async for msg in res.weekend_weather():
                await message.answer(msg)
        else:
            await message.answer("Что то пошло не так!")

    await message.delete()
    await state.finish()


@dp.callback_query_handler(lambda callback: callback.data == EXIT, state="*")
async def exit_menu(callback: types.CallbackQuery):
    await callback.message.delete()


@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    pass


# Запускаем бота и фоновую задачу
async def main():
    # Создаем индексы, устанавливаем команды бота
    await create_indexes()
    await set_commands(dp)
    # Запускаем фоновую задачу
    asyncio.create_task(back_task())
    # Запускаем бота
    await dp.start_polling()

# Получаем loop
loop = asyncio.new_event_loop()
# Запускаем
loop.run_until_complete(main())
