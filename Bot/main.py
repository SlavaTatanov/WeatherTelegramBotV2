from aiogram import executor, types
from Bot import dp


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    """
    Обработчик команды Старт
    """
    answer_for_user = "Здравствуйте, уважаемый пользователь! Я рад приветствовать вас. " \
                      "Хочу сообщить вам, что в настоящее время бот находится в активной разработке," \
                      " и скоро он будет доступен для использования. "
    await message.answer(answer_for_user)

executor.start_polling(dp, skip_updates=True)
