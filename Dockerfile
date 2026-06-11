# Имя базового образа
FROM python:3.11-slim

# Переменные окружения для стабильной работы
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99

# Установка системных утилит и Xvfb (libgconf-2-4 удален)
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11-utils \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-noto-color-emoji \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Обновление pip
RUN pip install --no-cache-dir --upgrade pip

# Установка ваших Python библиотек
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    onnxruntime \
    python-multipart \
    watchfiles \
    playwright \
    pyvirtualdisplay

# Установка браузеров Playwright и всех актуальных системных зависимостей для Debian Trixie
RUN playwright install --with-deps chromium

# Копирование исходного кода
COPY ./app /app

# Скрипт для запуска Xvfb и Uvicorn
CMD xvfb-run --server-args="-screen 0 1280x1024x24 -ac +extension GLX +render -noreset" \
    uvicorn main:app --host 0.0.0.0 --port 8000