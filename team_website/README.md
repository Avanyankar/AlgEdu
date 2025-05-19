# Сайт "AlgEdu Team"
#### Проект можно запустить и использовать, только пользуясь ОС Windows.

## Оглавление:
1. [Технологический стек](#технологический-стек)
2. [Инструкция по настройке проекта](#инструкция-по-настройке-проекта)
3. [Запуск проекта](#запуск-проекта)
4. [Тестирование проекта](#тестирование-проекта)
5. [Создание документации проекта](#создание-документации-проекта)
6. [Запуск pylint](#запуск-pylint)

## Технологический стек:
- [python v3.12](https://www.python.org/downloads/release/python-3120/)
- [django v5.2.1](https://www.djangoproject.com/)
- [django_registration v5.2.1](https://django-registration.readthedocs.io/en/stable/index.html)
- [gunicorn v23.0.0](https://github.com/benoitc/gunicorn)
- [pylint v3.3.7](https://www.pylint.org/)
- [sphinx v8.3.0](https://www.sphinx-doc.org/en/master/index.html)
- [sphinx-rtd-theme v3.0.2](https://pypi.org/project/sphinx-rtd-theme/)
- [coverage v7.8.0](https://coverage.readthedocs.io/en/7.8.0/)
- [SQLite](https://sqlite.org/index.html)

## Инструкция по настройке проекта:
1. Склонировать репозиторий проекта:
 ``` bash
 git clone https://gitlab.informatics.ru/2024-2025/hse/s105/final-project.git AlgEdu
 ```
2. Открыть папку проекта и перейти в папку с файлами сайта команды:
```bash
cd "team_website"
```
3. Создать виртуальное окружение:
```bash
python -m venv .venv
```
4. Открыть терминал и активировать виртуальное окружение:
```bash
venv\Scripts\activate
```
5. Обновить pip:
```bash
pip install --upgrade pip
```
6. Установить в виртуальное окружение необходимые пакеты: 
```bash
pip install -r requirements.txt
```
7. Сгенерировать уникальный ключ приложения, если отсутствует:
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Далее полученное значение подставляется в переменную SECRET_KEY в файле [settings.py](AlgEdu_Team/settings.py).
Внимание! Без выполнения этого пункта никакие команды далее не запустятся.
8. Создать миграции:
```bash
python manage.py makemigrations
```
9. Применить миграции: 
```bash
python manage.py migrate
```

## Запуск проекта:
1. Создать миграции:
```bash
python manage.py makemigrations
```
2. Применить миграции:
```bash
python manage.py migrate
```
3. Запустить сайт:
```bash
python manage.py runserver
```

## Тестирование проекта:
1. Запуск тестов:
```bash
python manage.py test
```
2. Запустить тесты с измерением покрытия:
```bash
coverage run --omit="*/migrations/*,*/__init__.py" manage.py test
```
3. Просмотреть отчёт:  

Вывод в консоль
```bash
coverage report --fail-under=70
``` 
Вывод в HTML
```bash
coverage html --fail-under=70
```

## Создание документации проекта:
1. Перейти в папку для создания документации:
```bash
cd docs
```
2. Собрать документацию:
```bash
sphinx-build -b html source build
```
3. Вернуться в папку сайта:
```bash
cd ..
```
4. Создать миграции:
```bash
python manage.py makemigrations
```
5. Применить миграции:
```bash
python manage.py migrate
```
6. Запустить сайт:
```bash
python manage.py runserver
```
7. Перейти на страницу документации. (http://127.0.0.1:8000/docs)

## Запуск pylint:
```bash
pylint --fail-under=8.0 --max-line-length=120 --disable=C0114,C0115,C0116,E1101 --ignore-paths=".*\migrations,.*\static,.venv\" .
```
