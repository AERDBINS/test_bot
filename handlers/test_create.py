import os
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from mimetypes import guess_type
from database import get_db
from aiogram.types import InputFile
from config import ADMINS

class TestCreateState(StatesGroup):
    awaiting_test_name = State()
    awaiting_files = State()
    awaiting_answer_key = State()


async def start_creating(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("⛔ Bu bo‘lim faqat adminlar uchun.")
        return

    await message.answer("📝 Yangi test nomini kiriting (masalan: matematika):")
    await state.set_state(TestCreateState.awaiting_test_name)


async def receive_test_name(message: types.Message, state: FSMContext):
    test_name = message.text.strip().lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tests WHERE name = ?", (test_name,))
    exists = cursor.fetchone()

    if exists:
        await message.answer("❌ Bunday test nomi mavjud. Boshqa nom kiriting.")
        return

    cursor.execute(
        "INSERT INTO tests (name, created_by) VALUES (?, ?)",
        (test_name, message.from_user.id)
    )
    conn.commit()
    test_id = cursor.lastrowid
    conn.close()

    await state.update_data(test_id=test_id, test_name=test_name)
    await message.answer("📎 Endi test fayllarini yuboring (pdf, docx yoki rasm).\nTugagach 'Tayyor' deb yozing.")
    await state.set_state(TestCreateState.awaiting_files)


async def receive_files(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    folder = f"data/files/{test_id}"
    os.makedirs(folder, exist_ok=True)

    conn = get_db()
    cursor = conn.cursor()

    saved = False

    if message.document:
        doc = message.document
        file_name = doc.file_name
        file_path = os.path.join(folder, file_name)
        await doc.download(destination_file=file_path)
        file_type = guess_type(file_name)[0] or "unknown"
        saved = True

    elif message.photo:
        photo = message.photo[-1]
        file_name = f"{photo.file_unique_id}.jpg"
        file_path = os.path.join(folder, file_name)
        await photo.download(destination_file=file_path)
        file_type = "image/jpeg"
        saved = True

    if saved:
        cursor.execute(
            "INSERT INTO test_files (test_id, file_name, file_type, file_path) VALUES (?, ?, ?, ?)",
            (test_id, file_name, file_type, file_path)
        )
        conn.commit()
        await message.answer("✅ Fayl saqlandi. Yana yuboring yoki 'Tayyor' deb yozing.")
    else:
        await message.answer("❌ Faqat pdf, docx yoki rasm yuboring.")

    conn.close()


async def finish_file_upload(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == "tayyor":
        await message.answer("✅ Endi testning to‘g‘ri javoblarini yuboring (masalan: abcdabcd...)")
        await state.set_state(TestCreateState.awaiting_answer_key)


async def receive_answer_key(message: types.Message, state: FSMContext):
    answers = message.text.strip().lower()
    data = await state.get_data()
    test_id = data['test_id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tests SET answer_key = ? WHERE id = ?",
        (answers, test_id)
    )
    conn.commit()
    conn.close()

    await message.answer("✅ Test muvaffaqiyatli saqlandi.")
    await state.finish()


def register_test_create_handlers(dp: Dispatcher):
    dp.register_message_handler(start_creating, lambda msg: msg.text == "📥 Savol tuzish", state="*")
    dp.register_message_handler(receive_test_name, state=TestCreateState.awaiting_test_name)
    dp.register_message_handler(finish_file_upload, lambda msg: msg.text.lower() == "tayyor", state=TestCreateState.awaiting_files)
    dp.register_message_handler(receive_files, content_types=types.ContentTypes.ANY, state=TestCreateState.awaiting_files)
    dp.register_message_handler(receive_answer_key, state=TestCreateState.awaiting_answer_key)
