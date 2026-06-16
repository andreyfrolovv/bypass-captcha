FROM python:3.11-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

RUN apt-get update && apt-get install -y \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libgtk-3-0 \
    libgtk2.0-0 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libgbm1 \
    libnspr4 \
    libnss3 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Отключаем буферизацию логов Python и генерацию .pyc файлов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN python -m pip install --upgrade pip

# Копируем список зависимостей
COPY requirements.txt .

RUN apt-get update && apt-get install -y git

# Устанавливаем Python-пакеты, системные библиотеки для браузеров 
# и кешируем кастомные браузеры invisible-playwright на этапе сборки
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install-deps

RUN pip install git+https://github.com/feder-cr/invisible_playwright.git
RUN python -m invisible_playwright fetch

CMD xvfb-run --server-args="-screen 0 1280x1024x24 -ac +extension GLX +render -noreset"

#RUN python -c "from invisible_playwright.async_api import InvisiblePlaywright; import asyncio; asyncio.run(InvisiblePlaywright().__aenter__())"
# Копируем остальной код приложения
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем uvicorn (без флага --reload для максимальной производительности в Docker)
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]