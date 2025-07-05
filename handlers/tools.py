from aiogram import types, Dispatcher

async def show_user_id(message: types.Message):
    await message.reply(f"👤 Sizning Telegram ID: `{message.from_user.id}`", parse_mode="Markdown")

def register_tool_handlers(dp: Dispatcher):
    dp.register_message_handler(show_user_id, commands=["id"], state="*")
