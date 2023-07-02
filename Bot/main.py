from aiogram import executor, types
from Bot import dp
from Bot.Database import mongo_client
from Bot.Database.models import UserInfo


@dp.message_handler(content_types=['text'])
async def send_welcome(message: types.Message):
    if message.text == 'err':
        raise SystemExit
    elif message.text == 'db':
        await message.reply(f"Подключение к БД {mongo_client}")
        UserInfo.get_user(12)
    else:
        await message.reply("Привет!")


executor.start_polling(dp, skip_updates=True)
