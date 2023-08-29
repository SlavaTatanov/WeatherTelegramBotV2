from aiogram import types
from aiogram.dispatcher import FSMContext
import asyncio
from Bot import dp, bot, WeatherState, set_commands
from Bot.keboards import replay_get_location, inline_get_weather_type, inline_get_weather_places, inline_weather_type
from Bot.CALLBACKS import WEATHER_TIMES, CURRENT, FREQUENCY, WEEKEND, COMMON, TOMORROW, SHORT, FIVE_DAY, \
    CURRENT_PLACE, EXIT
from Bot.Weather.core import Weather
from Bot.background_task import back_task
from Bot.Database import create_indexes
from Bot.utils import state_save_related_msg, state_clean_with_messages
from Bot.Database.models import UserInfo


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " в данный момент доступны только короткие прогнозы погоды. Часть функций может не работать"
    await message.answer(answer_for_user)


@dp.message_handler(commands=['weather'], state="*")
async def weather(message: types.Message):
    """
    Выбираем когда мы хотим прогноз погоды, сегодня, завтра ...
    Даем пользователю inline клавиатуру с кнопками
    """
    # Чистим предыдущие состояния
    await state_clean_with_messages(message.from_user.id)
    await WeatherState.weather_time.set()
    # Получаем состояние, связанное сообщение, сохраняем
    state = dp.current_state(user=message.from_user.id)
    msg = await message.answer("Какую погоду вы хотите узнать?", reply_markup=inline_get_weather_type(message.date.date()))
    await state_save_related_msg(state, msg)
    # Чистим сообщение юзера - это '/weather'
    await message.delete()


@dp.callback_query_handler(lambda callback: callback.data in WEATHER_TIMES, state=WeatherState.weather_time)
async def weather_time(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловим время для которого необходимо узнать погоду и пишем его в контекст
    После запрашиваем тип погоды (почасовая, обычный, краткий прогноз) если погода текущая, либо сразу место.
    """
    async with state.proxy() as data:
        # Запоминаем когда пользователь хочет узнать погоду (сегодня, завтра)
        data["weather_time"] = callback.data
        # Запоминаем текущую дату
        data["start_date"] = callback.message.date.date()

    if callback.data in [CURRENT, TOMORROW, WEEKEND]:
        await WeatherState.next()
        await callback.message.edit_text("Выберете детализацию погоды", reply_markup=inline_weather_type(callback.data))
    else:
        async with state.proxy() as data:
            # Сразу устанавливаем детализацию погоды
            data["type"] = SHORT
        await WeatherState.weather_place.set()
        await callback.message.edit_text("Отправьте гео-позицию или выберете из списка",
                                         reply_markup=inline_get_weather_places())


@dp.callback_query_handler(lambda callback: callback.data in FREQUENCY, state=WeatherState.weather_type)
async def weather_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["type"] = callback.data
    await WeatherState.next()
    # Получаем список мест юзера
    user_id = callback.from_user.id
    user = await UserInfo.get_user(user_id)
    places = user.get_places_names()
    await callback.message.edit_text("Отправьте гео-позицию или выберете из списка",
                                     reply_markup=inline_get_weather_places(places))


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
