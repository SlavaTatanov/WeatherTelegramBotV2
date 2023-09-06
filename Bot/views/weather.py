import Bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from Bot.utils import state_clean_with_messages, state_save_related_msg
from Bot.keboards import inline_get_weather_type, inline_get_weather_places, inline_weather_type
from Bot.CALLBACKS import CURRENT, TOMORROW, WEEKEND, SHORT
from Bot.Database.models import UserInfo


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
    msg = await message.answer("Какую погоду вы хотите узнать?", reply_markup=inline_get_weather_type(message.date.date()))
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
