# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Команда по умолчанию (можно переопределить в docker-compose)
CMD ["gunicorn", "retail_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
