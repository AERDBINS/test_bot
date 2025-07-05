import sqlite3
import os

DB_PATH = "data/quiz.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    # test fayllari jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        file_name TEXT,
        file_type TEXT,
        file_path TEXT,
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
    )
    """)

    # testlar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        answer_key TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # natijalar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_id INTEGER,
        user_answer TEXT,
        correct_count INTEGER,
        wrong_count INTEGER,
        skipped_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Reyting xabar IDlarini saqlash
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ranking_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER UNIQUE,
        chat_id INTEGER,
        message_id INTEGER
    )
    """)


    conn.commit()
    conn.close()

def get_test_by_name(test_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, answer_key FROM tests WHERE name = ?", (test_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "answer_key": row[2]
        }
    return None
def delete_test_by_name(name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tests WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def get_files_by_test_id(test_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT file_name, file_type, file_path FROM test_files WHERE test_id = ?",
        (test_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"file_name": row[0], "file_type": row[1], "file_path": row[2]}
        for row in rows
    ]

def save_result(user_id: int, test_id: int, user_answer: str,
                correct: int, wrong: int, skipped: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results (user_id, test_id, user_answer, correct_count, wrong_count, skipped_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, test_id, user_answer, correct, wrong, skipped))
    conn.commit()
    conn.close()

def get_results_by_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tests.name, r.correct_count, r.wrong_count, r.skipped_count, r.created_at
        FROM results r
        JOIN tests ON r.test_id = tests.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return rows
def get_ranking_message(test_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chat_id, message_id FROM ranking_messages WHERE test_id = ?
    """, (test_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"chat_id": row[0], "message_id": row[1]}
    return None

def save_ranking_message(test_id: int, chat_id: int, message_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO ranking_messages (test_id, chat_id, message_id)
        VALUES (?, ?, ?)
    """, (test_id, chat_id, message_id))
    conn.commit()
    conn.close()


def get_test_by_name_by_id(test_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, answer_key FROM tests WHERE id = ?", (test_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "answer_key": row[2]
        }
    return None
