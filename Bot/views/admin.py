from aiogram import types


# callback "admin-panel"
async def admin_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Меню администратора")
