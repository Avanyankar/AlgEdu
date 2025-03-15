# Сайт "AlgEdu Team"

## Технологический стек:
- Python 3.12
- Django 5.1+
- SQLite

## Инструкция по настройке проекта:
1. Склонировать проект.
2. Открыть папку проекта и перейти в папку данного сайта:
   ```bash
   cd "AlgEdu_Team"
   ```
3. Создать виртуальное окружение:
   ```bash
   python -m venv .venv
   ```
4. Открыть терминал в PyCharm виртуальное окружение активировать:
   ```bash
   source .venv/bin/activate
   ```
5. Обновить pip:
   ```bash
   pip install --upgrade pip
   ```
6. Установить в виртуальное окружение необходимые пакеты: 
   ```bash
   pip install -r requirements.txt
   ```
7. Создать уникальный ключ приложения.  
   Генерация делается в консоли Python при помощи команд:
   ```bash
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Далее полученное значение подставляется в соответствующую переменную.
   Внимание! Без выполнения этого пункта никакие команды далее не запустятся.
8. Синхронизировать структуру базы данных с моделями: 
   ```bash
   python manage.py migrate
   ```
