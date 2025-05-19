# Приложение "AlgEdu"
#### Проект можно запустить и использовать, только пользуясь ОС Windows.

## Оглавление:
1. [Технологический стек](#технологический-стек)
2. [Инструкция по настройке проекта](#инструкция-по-настройке-проекта)
3. [Запуск проекта](#запуск-проекта)
4. [Тестирование проекта](#тестирование-проекта)
5. [Создание документации проекта](#создание-документации-проекта)
6. [Запуск cpplint](#запуск-cpplint)

## Технологический стек:
- [C++ стандарт ISO 14](https://github.com/google/googletest.git)
- [imgui v1.91.9](https://github.com/ocornut/imgui/tree/v1.91.9-docking)
- [googletest](https://github.com/google/googletest.git)
- [doxygen](https://www.doxygen.nl/index.html)
- [python v3.12](https://www.python.org/downloads/release/python-3120/) (Для cpplint)

## Инструкция по настройке проекта:
1. Склонировать репозиторий проекта:
    ``` bash
    git clone https://gitlab.informatics.ru/2024-2025/hse/s105/final-project.git AlgEdu
    ```
2. Открыть папку проекта и перейти в папку с файлами данного приложения:
   ```bash
   cd "application"
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
7. Открыть файл application.sln в Visual Studio 2022.

## Запуск проекта:
1.

## Тестирование проекта:
1. 

## Запуск cpplint:
1. 
   ```bash
   cpplint --recursive \
        --filter=-build/include_subdir,-build/header_guard \
        --repository=. \
        --linelength=120 \
        --exclude="vendor/*" \
        .
   ```
