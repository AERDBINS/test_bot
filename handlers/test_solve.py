import os
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from database import get_db, get_test_by_name, save_result
from services.ranking import send_ranking_to_admins

def get_test_by_name(name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, answer_key FROM tests WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "answer_key": row[2]}
    return None

async def start_solving(message: types.Message, state: FSMContext):
    await message.answer("Test nomini kiriting (masalan: matematika):")
    await state.set_state("awaiting_test_name")

async def process_test_name(message: types.Message, state: FSMContext):
    test_name = message.text.strip().lower()
    test = get_test_by_name(test_name)

    if not test:
        await message.answer("❌ Bunday test topilmadi.")
        await state.finish()
        return

    test_id = test["id"]
    folder = f"data/files/{test_id}"
    if not os.path.exists(folder):
        await message.answer("❌ Bu test uchun fayllar mavjud emas.")
        await state.finish()
        return

    files = os.listdir(folder)
    for file in files:
        path = os.path.join(folder, file)
        if file.endswith((".pdf", ".docx")):
            await message.answer_document(InputFile(path))
        elif file.endswith((".jpg", ".jpeg", ".png")):
            await message.answer_photo(InputFile(path))

    await message.answer(f"✅ Endi quyidagicha javob yuboring:\n`/{test_name}/abcdabcd...`", parse_mode="Markdown")
    await state.finish()



async def handle_answer_submission(message: types.Message):
    text = message.text.strip()
    if not (text.startswith("/") and "/" in text[1:]):
        return

    try:
        _, test_name, user_answers = text.split("/", maxsplit=2)
        test_name = test_name.lower()
        user_answers = user_answers.strip().lower()
    except:
        await message.reply("❌ Format noto‘g‘ri. Foydalanish: `/testnom/javoblar`")
        return

    test = get_test_by_name(test_name)
    if not test:
        await message.reply("❌ Bunday test topilmadi.")
        return

    correct_answers = test["answer_key"].strip().lower()
    test_id = test["id"]

    correct = wrong = skipped = 0
    correct_nums = []
    wrong_nums = []
    skipped_nums = []

    for i, user_char in enumerate(user_answers):
        if i >= len(correct_answers):
            break
        correct_char = correct_answers[i]
        question_num = i + 1

        if user_char == ".":
            skipped += 1
            skipped_nums.append(str(question_num))
        elif user_char == correct_char:
            correct += 1
            correct_nums.append(str(question_num))
        else:
            wrong += 1
            wrong_nums.append(str(question_num))

    # Saqlash
    save_result(message.from_user.id, test_id, user_answers, correct, wrong, skipped)

    # 🔥 Reytingni adminlarga yuborish (birinchi javob asosida)
    await send_ranking_to_admins(test_id, message.bot)

    total = correct + wrong + skipped

    # Natija matni
    result_text = (
        f"📊 Test natijasi:\n"
        f"✅ To‘g‘ri: {correct} ta" + (f" — ({', '.join(correct_nums)})" if correct_nums else "") + "\n"
        f"❌ Noto‘g‘ri: {wrong} ta" + (f" — ({', '.join(wrong_nums)})" if wrong_nums else "") + "\n"
        f"⏭ Tashlab ketilgan: {skipped} ta" + (f" — ({', '.join(skipped_nums)})" if skipped_nums else "") + "\n"
        f"📄 Umumiy: {total} ta savol"
    )

    await message.reply(result_text)

def register_test_solve_handlers(dp: Dispatcher):
    dp.register_message_handler(start_solving, lambda msg: msg.text == "📝 Testni yechish", state="*")
    dp.register_message_handler(process_test_name, state="awaiting_test_name")
    dp.register_message_handler(handle_answer_submission, lambda msg: msg.text.startswith("/") and msg.text.count("/") >= 2, state="*")
