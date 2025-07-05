import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from handlers import start, test_solve, test_create, test_command
from config import API_TOKEN  # <-- TOKEN endi .env orqali chaqiriladi

# Loglar uchun sozlama
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()  # ✅ FSM uchun zarur
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Handlerlarni ulaymiz
start.register_handlers(dp)
test_solve.register_test_solve_handlers(dp)
test_create.register_test_create_handlers(dp)
test_command.register_test_name_command(dp)

if __name__ == '__main__':
    from database import init_db
    init_db()  # Bazani ishga tushuramiz
    executor.start_polling(dp, skip_updates=True)
