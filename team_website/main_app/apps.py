"""
Конфигурация приложения Django для основного приложения.

Этот модуль определяет настройки приложения, включая тип автоинкрементного поля
и имя приложения.

:mod:`main_app.apps`
"""

from django.apps import AppConfig

class MainAppConfig(AppConfig):
    """
    Класс конфигурации для приложения `main_app`.

    :attribute default_auto_field: Тип поля для автоинкрементных первичных ключей.
    :type default_auto_field: str
    :attribute name: Имя приложения.
    :type name: str
    """
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'main_app'
