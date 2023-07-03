from aiogram import executor, types
from Bot import dp, bot, WeatherState, set_commands
from keboards import replay_get_location, inline_get_weather_type, inline_get_weather_places
from Bot.Weather.CONSTANCE import CURRENT, FIVE_DAY, WEEKEND


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " и скоро он будет доступен для использования. "
    await message.answer(answer_for_user)


@dp.message_handler(commands=['weather'])
async def weather(message: types.Message):
    await message.answer("Какую погоду вы хотите узнать?", reply_markup=inline_get_weather_type())


@dp.callback_query_handler(lambda callback: callback.data in [CURRENT, FIVE_DAY, WEEKEND])
async def weather_type(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберете место", reply_markup=inline_get_weather_places())


@dp.callback_query_handler(lambda callback: callback.data == "current_place")
async def current_place(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, "Укажите геопозицию", reply_markup=replay_get_location())


executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
