from aiogram import types, Dispatcher
from keyboards.reply import main_menu

async def start_handler(message: types.Message):
    await message.answer("Assalomu alaykum!\nBotga xush kelibsiz!", reply_markup=main_menu)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'], state="*")
