# Определяем базовый образ
FROM python:3.11-slim

# Устанавливаем переменную для поиска модулей приложения
ENV PYTHONPATH="$PYTHONPATH:/app"

# Настраиваем переменные среды
# Тут ставим настройку что локальный MongoDB - 0 (false)
# И для токена по умолчанию, есть тестовый и боевой, если DEVELOPMENT - 0 приложение возьмет боевой
ENV LOCAL_MONGO=0
ENV DEVELOPMENT=0

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения
COPY . .

# Запускаем бот, флаг -u небуфферизованный вывод, дает возможность видить print
CMD python3 -u Bot/main.py