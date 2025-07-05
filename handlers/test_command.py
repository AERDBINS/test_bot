import os
from aiogram import types, Dispatcher
from aiogram.types import InputFile
from database import get_test_by_name, get_files_by_test_id


async def handle_test_command(message: types.Message):
    text = message.text.strip()
    if not text.startswith("/"):
        return

    test_name = text[1:].split()[0].lower()  # "/math" → "math"

    test = get_test_by_name(test_name)
    if not test:
        await message.reply("❌ Bunday test topilmadi.")
        return

    test_id = test["id"]

    # 📦 Fayllarni SQLdan o‘qiymiz
    files = get_files_by_test_id(test_id)
    if not files:
        await message.reply("❌ Bu test uchun fayllar mavjud emas.")
        return

    for file in files:
        file_path = file["file_path"]
        file_type = file["file_type"]

        if not os.path.exists(file_path):
            continue  # Agar fayl yo‘q bo‘lsa — tashlab ketamiz

        if file_type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            await message.answer_document(InputFile(file_path))
        elif file_type.startswith("image/"):
            await message.answer_photo(InputFile(file_path))

    await message.answer(
        f"✅ Endi quyidagi formatda javob yuboring:\n`/{test_name}/abcdabcd...`",
        parse_mode="Markdown"
    )


def register_test_name_command(dp: Dispatcher):
    dp.register_message_handler(
        handle_test_command,
        lambda msg: msg.text.startswith("/") and msg.text.count("/") == 1,
        state="*"
    )
