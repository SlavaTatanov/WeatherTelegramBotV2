import Bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from Bot.utils import state_clean_with_messages, state_save_related_msg
from Bot.keboards import inline_get_weather_type, inline_get_weather_places, inline_weather_type, replay_get_location
from Bot.CALLBACKS import CURRENT, TOMORROW, WEEKEND, SHORT, FIVE_DAY
from Bot.Database.models import UserInfo
from Bot.Weather.core import Weather


# /weather
async def weather(message: types.Message):
    """
    Выбираем когда мы хотим прогноз погоды, сегодня, завтра ...
    Даем пользователю inline клавиатуру с кнопками
    """
    # Чистим предыдущие состояния
    await state_clean_with_messages(message.from_user.id)
    await Bot.WeatherState.weather_time.set()
    # Получаем состояние, связанное сообщение, сохраняем
    state = Bot.dp.current_state(user=message.from_user.id)
    msg = await message.answer("Какую погоду вы хотите узнать?",
                               reply_markup=inline_get_weather_type(message.date.date()))
    await state_save_related_msg(state, msg)
    # Чистим сообщение юзера - это '/weather'
    await message.delete()


# callback = WEATHER_TIMES
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
        await Bot.WeatherState.next()
        await callback.message.edit_text("Выберете детализацию погоды", reply_markup=inline_weather_type(callback.data))
    else:
        async with state.proxy() as data:
            # Сразу устанавливаем детализацию погоды
            data["type"] = SHORT
        await Bot.WeatherState.weather_place.set()
        # Получаем список мест юзера
        user_id = callback.from_user.id
        user = await UserInfo.get_user(user_id)
        places = user.get_places_names()
        await callback.message.edit_text("Отправьте гео-позицию или выберете из списка",
                                         reply_markup=inline_get_weather_places(places))


# callback = FREQUENCY
async def weather_type(callback: types.CallbackQuery, state: FSMContext):
    """
    Получаем тип погоды которая нужна, короткая, подробная.
    И спрашиваем у юзера место.
    """
    async with state.proxy() as data:
        data["type"] = callback.data
    await Bot.WeatherState.next()
    # Получаем список мест юзера
    user_id = callback.from_user.id
    user = await UserInfo.get_user(user_id)
    places = user.get_places_names()
    await callback.message.edit_text("Отправьте гео-позицию или выберете из списка",
                                     reply_markup=inline_get_weather_places(places))


# callback = CURRENT_PLACE
async def current_place(callback: types.CallbackQuery, state: FSMContext):
    """
    Если пользователь нажимает текущее место даем ему клавиатуру с кнопкой отправить место
    """
    async with state.proxy() as data:
        data["weather_type"] = callback.data
        data["location_req"] = await Bot.bot.send_message(callback.from_user.id, "Укажите геопозицию",
                                                          reply_markup=replay_get_location())


# callback != CURRENT_PLACE
async def current_place_from_user(callback: types.CallbackQuery, state: FSMContext):
    """
    Если пользователь жмет место из своих мест, берем его координаты и даем погоду
    """
    # Получаем инфу юзера, и координаты места
    user_info = await UserInfo.get_user(callback.from_user.id)
    place_coord = tuple(user_info.get_place_coord(callback.data))
    place_name = callback.data

    async with state.proxy() as data:
        res = Weather(place_coord, data["start_date"], data["type"], place_name=place_name)

        # Отвечаем юзеру в зависимости от типа погоды
        if data["weather_time"] == CURRENT:
            res_msg = await res.current_weather()
            await Bot.bot.send_message(callback.from_user.id, res_msg)
        elif data["weather_time"] == TOMORROW:
            res_msg = await res.tomorrow_weather()
            await Bot.bot.send_message(callback.from_user.id, res_msg)
        elif data["weather_time"] == FIVE_DAY:
            async for msg in res.five_day_weather():
                await Bot.bot.send_message(callback.from_user.id, msg)
        elif data["weather_time"] == WEEKEND:
            async for msg in res.weekend_weather():
                await Bot.bot.send_message(callback.from_user.id, msg)
        else:
            await callback.answer("Что то пошло не так!")
    await callback.message.delete()


# location
async def weather_place(message: types.Message, state: FSMContext):
    """
    Если пользователь отправил позицию, то даем погоду с этой локации
    """
    async with state.proxy() as data:
        # Удаляем inline сообщение и запрос позиции
        await data["msg"].delete()
        try:
            await Bot.bot.delete_message(data["location_req"]["chat"]["id"], data["location_req"]["message_id"])
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
