# Bu yerga faqat admin user IDlarini yozasiz
import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# API tokenni olish
API_TOKEN = os.getenv("API_TOKEN")

# Adminlar ro‘yxatini olish (vergul bilan ajratilgan bo‘ladi)
ADMINS = list(map(int, os.getenv("ADMINS", "").split(",")))
