from database import (
    get_db,
    get_test_by_name_by_id,
    get_ranking_message,
    save_ranking_message,
)
from config import ADMINS

async def send_ranking_to_admins(test_id: int, bot):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.user_id, r.correct_count
        FROM results r
        WHERE r.test_id = ?
        AND r.id = (
            SELECT MIN(id)
            FROM results
            WHERE test_id = ? AND user_id = r.user_id
        )
        ORDER BY r.correct_count DESC
    """, (test_id, test_id))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    test = get_test_by_name_by_id(test_id)
    text = f"📊 *{test['name'].title()}* bo‘yicha reyting:\n\n"

    for i, row in enumerate(rows, 1):
        user_id = row[0]
        correct = row[1]

        try:
            user = await bot.get_chat(user_id)
            name = user.full_name
            if user.username:
                link = f"https://t.me/{user.username}"
            else:
                link = f"tg://user?id={user_id}"
        except:
            name = f"ID:{user_id}"
            link = f"tg://user?id={user_id}"

        text += f"{i}. [{name}]({link}) — ✅ {correct} ta to‘g‘ri\n"

    # Har bir admin uchun xabarni yangilash yoki yaratish
    for admin_id in ADMINS:
        existing = get_ranking_message(test_id)

        if existing and existing["chat_id"] == admin_id:
            try:
                await bot.edit_message_text(
                    chat_id=admin_id,
                    message_id=existing["message_id"],
                    text=text,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            except:
                pass  # xabar o‘chirilgan yoki tahrirlab bo‘lmaydi
        else:
            try:
                msg = await bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                save_ranking_message(test_id, admin_id, msg.message_id)
            except:
                pass

def get_test_by_name_by_id(test_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, answer_key FROM tests WHERE id = ?", (test_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "answer_key": row[2]}
    return None
