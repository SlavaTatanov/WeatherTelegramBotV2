from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from Bot import dp, bot, set_commands, WeatherState
from keboards import replay_get_location, inline_get_weather_type, inline_get_weather_places, inline_weather_type
from Bot.CALLBACKS import WEATHER_TIMES, CURRENT, FREQUENCY


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
    await WeatherState.weather_time.set()
    await message.answer("Какую погоду вы хотите узнать?", reply_markup=inline_get_weather_type())


@dp.callback_query_handler(lambda callback: callback.data in WEATHER_TIMES, state=WeatherState.weather_time)
async def weather_type(callback: types.CallbackQuery, state: FSMContext):
    """
    Ловим время для которого необходимо узнать погоду и пишем его в контекст
    После запрашиваем тип погоды (почасовая, краткий прогноз) если погода текущая, либо сразу место.
    """
    async with state.proxy() as data:
        data["weather_time"] = callback.data
        # Запоминаем сообщение откуда приходит callback, потом удалим
        data["msg"] = callback.message
    if callback.data == CURRENT:
        print(state)
        await WeatherState.next()
        await callback.message.edit_text("Выберете детализацию погоды", reply_markup=inline_weather_type())
    else:
        await WeatherState.weather_place.set()
        await callback.message.edit_text("Выберете место", reply_markup=inline_get_weather_places())


@dp.callback_query_handler(lambda callback: callback.data in FREQUENCY, state=WeatherState.weather_type)
async def weather_type(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await data["msg"].delete()
    await bot.send_message(callback.from_user.id, "Вот твоя погода")


@dp.callback_query_handler(lambda callback: callback.data == "current_place", state=WeatherState.weather_place)
async def current_place(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["weather_type"] = callback.data
        data["msg1"] = await bot.send_message(callback.from_user.id, "Укажите геопозицию",
                                           reply_markup=replay_get_location())


@dp.message_handler(content_types=["location"], state=WeatherState.weather_place)
async def weather_place(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Удаляем inline сообщение и запрос позиции
        await data["msg"].delete()
        await bot.delete_message(data["msg1"]["chat"]["id"], data["msg1"]["message_id"])
    await message.delete()
    await bot.send_message(message.from_user.id, "Вот твоя погода")


executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
