from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📥 Savol tuzish")],
        [KeyboardButton("📝 Testni yechish")]
    ],
    resize_keyboard=True
)
