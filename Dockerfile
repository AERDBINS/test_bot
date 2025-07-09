# Python 3.11.9 bazaviy image
FROM python:3.11.9-slim

# Ishchi papkani belgilash
WORKDIR /app

# Tizim kutubxonalarini o‘rnatish (kerakli bo‘lsa)
RUN apt-get update && apt-get install -y gcc libpq-dev libjpeg-dev zlib1g-dev

# requirements.txt faylini yuklash va kutubxonalarni o‘rnatish
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Butun loyiha papkasini konteynerga ko‘chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]
