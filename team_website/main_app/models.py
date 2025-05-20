"""
Модели Django для приложения, включая пользователей, поля, комментарии, стены, клетки,
файлы, жалобы и посты.

Этот модуль определяет структуру данных приложения, включая связи между моделями,
методы для управления состоянием объектов и мета-данные для настройки поведения.

:mod:`main_app.models`
"""

import logging
from typing import Optional, List, Tuple
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser

logger: logging.Logger = logging.getLogger(__name__)

class User(AbstractUser):
    """
    Модель пользователя, расширяющая базовую модель Django :class:`django.contrib.auth.models.AbstractUser`.

    :attribute birth_date: Дата рождения пользователя.
    :type birth_date: Optional[:class:`django.db.models.DateField`]
    :attribute bio: Краткое описание пользователя (до 500 символов).
    :type bio: str
    :attribute location: Местоположение пользователя (до 100 символов).
    :type location: str
    :attribute avatar: Аватар пользователя, загружаемый в папку 'avatars/'.
    :type avatar: Optional[:class:`django.db.models.ImageField`]
    """
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def safe_ban(self) -> bool:
        """
        Безопасно блокирует пользователя, деактивируя аккаунт и блокируя связанные поля и комментарии.

        :returns: ``True``, если блокировка успешна, иначе ``False``.
        :rtype: bool
        :raises Exception: Если происходит ошибка при сохранении изменений.
        """
        try:
            self.is_active = False
            self.save(update_fields=['is_active'])
            Field.objects.filter(user=self).update(is_blocked=True)
            Comment.objects.filter(author=self).update(is_blocked=True)
            return True
        except Exception as e:
            logger.error("Ошибка бана User %s: %s", self.id, str(e))
            return False

    def __str__(self) -> str:
        """
        Возвращает строковое представление пользователя.

        :returns: Имя пользователя.
        :rtype: str
        """
        return str(self.username)

class ProfileComment(models.Model):
    """
    Модель комментария к профилю пользователя.

    :attribute profile: Пользователь, к профилю которого относится комментарий.
    :type profile: :class:`main_app.models.User`
    :attribute author: Автор комментария.
    :type author: :class:`main_app.models.User`
    :attribute text: Текст комментария (до 500 символов).
    :type text: str
    :attribute created_at: Дата и время создания комментария.
    :type created_at: :class:`django.db.models.DateTimeField`
    """
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Мета-данные для модели.

        :attribute ordering: Сортировка по убыванию даты создания.
        :type ordering: List[str]
        """
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Возвращает строковое представление комментария к профилю.

        :returns: Описание комментария.
        :rtype: str
        """
        return f"Комментарий от {self.author.username} к профилю {self.profile.username}"

class FieldFile(models.Model):
    """
    Модель для хранения файлов, связанных с полями.

    :attribute name: Имя файла (до 255 символов).
    :type name: str
    :attribute content_type: MIME-тип файла (до 100 символов).
    :type content_type: str
    :attribute data: Бинарные данные файла.
    :type data: bytes
    :attribute size: Размер файла в байтах.
    :type size: int
    :attribute created_at: Дата и время создания файла.
    :type created_at: :class:`django.db.models.DateTimeField`
    """
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    data = models.BinaryField()
    size = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def to_file(self) -> ContentFile:
        """
        Преобразует данные файла в объект :class:`django.core.files.base.ContentFile`.

        :returns: Объект файла с данными и именем.
        :rtype: :class:`django.core.files.base.ContentFile`
        """
        return ContentFile(self.data, name=self.name)

    def __str__(self) -> str:
        """
        Возвращает строковое представление файла.

        :returns: Имя файла.
        :rtype: str
        """
        return str(self.name)

class Field(models.Model):
    """
    Модель поля, представляющего карту в приложении.

    :attribute user: Пользователь, создавший поле.
    :type user: :class:`main_app.models.User`
    :attribute title: Название поля (до 255 символов).
    :type title: str
    :attribute description: Описание поля.
    :type description: str
    :attribute created_at: Дата и время создания поля.
    :type created_at: :class:`django.db.models.DateTimeField`
    :attribute updated_at: Дата и время последнего обновления поля.
    :type updated_at: :class:`django.db.models.DateTimeField`
    :attribute likes: Пользователи, лайкнувшие поле.
    :type likes: :class:`django.db.models.ManyToManyField`
    :attribute favorites: Пользователи, добавившие поле в избранное.
    :type favorites: :class:`django.db.models.ManyToManyField`
    :attribute is_blocked: Флаг, указывающий, заблокировано ли поле.
    :type is_blocked: bool
    :attribute cols: Количество столбцов в поле (по умолчанию 10).
    :type cols: int
    :attribute rows: Количество строк в поле (по умолчанию 10).
    :type rows: int
    :attribute file: Связанный файл (если есть).
    :type file: Optional[:class:`main_app.models.FieldFile`]
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_cards', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorited_cards', blank=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокировано")
    cols = models.IntegerField(default=10)
    rows = models.IntegerField(default=10)
    file = models.OneToOneField(FieldFile, on_delete=models.SET_NULL, null=True, blank=True)

    def block(self) -> None:
        """
        Блокирует поле, устанавливая флаг ``is_blocked`` в ``True``.
        """
        self.is_blocked = True
        self.save()

    def unblock(self) -> None:
        """
        Разблокирует поле, устанавливая флаг ``is_blocked`` в ``False``.
        """
        self.is_blocked = False
        self.save()

    def safe_unblock(self) -> bool:
        """
        Безопасно разблокирует поле, обновляя только поле ``is_blocked``.

        :returns: ``True``, если разблокировка успешна, иначе ``False``.
        :rtype: bool
        :raises Exception: Если происходит ошибка при сохранении изменений.
        """
        try:
            self.is_blocked = False
            self.save(update_fields=['is_blocked'])
            return True
        except Exception as e:
            logger.error("Ошибка разблокировки Field %s: %s", self.id, str(e))
            return False

    def get_absolute_url(self) -> str:
        """
        Возвращает абсолютный URL для поля.

        :returns: URL страницы деталей поля.
        :rtype: str
        """
        from django.urls import reverse
        return reverse('card-detail', kwargs={'pk': self.pk})

    class Meta:
        """
        Мета-данные для модели.

        :attribute verbose_name: Название модели в единственном числе.
        :type verbose_name: str
        :attribute verbose_name_plural: Название модели во множественном числе.
        :type verbose_name_plural: str
        :attribute permissions: Разрешения для модели.
        :type permissions: List[Tuple[str, str]]
        """
        verbose_name = "Карта"
        verbose_name_plural = "Карты"
        permissions = [
            ("can_view_blocked", "Может просматривать заблокированные карты"),
        ]

    def __str__(self) -> str:
        """
        Возвращает строковое представление поля.

        :returns: Название поля.
        :rtype: str
        """
        return str(self.title)

class Cell(models.Model):
    """
    Модель клетки в поле, представляющей координаты и состояние.

    :attribute field: Поле, к которому относится клетка.
    :type field: :class:`main_app.models.Field`
    :attribute x: Координата X клетки.
    :type x: int
    :attribute y: Координата Y клетки.
    :type y: int
    :attribute is_blocked: Флаг, указывающий, заблокирована ли клетка.
    :type is_blocked: bool
    """
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='cells')
    x = models.IntegerField()
    y = models.IntegerField()
    is_blocked = models.BooleanField(default=False)

    class Meta:
        """
        Мета-данные для модели.

        :attribute unique_together: Уникальность комбинации полей.
        :type unique_together: Tuple[str, str]
        """
        unique_together = ('field', 'x', 'y')

    def __str__(self) -> str:
        """
        Возвращает строковое представление клетки.

        :returns: Описание клетки с координатами и названием поля.
        :rtype: str
        """
        return f"Cell ({self.x}, {self.y}) in {self.field.title}"

class Wall(models.Model):
    """
    Модель стены в поле, представляющей прямоугольную область.

    :attribute field: Поле, к которому относится стена.
    :type field: :class:`main_app.models.Field`
    :attribute x: Начальная координата X стены.
    :type x: int
    :attribute y: Начальная координата Y стены.
    :type y: int
    :attribute width: Ширина стены в клетках (по умолчанию 1).
    :type width: int
    :attribute height: Высота стены в клетках (по умолчанию 1).
    :type height: int
    :attribute created_by: Пользователь, создавший стену.
    :type created_by: :class:`main_app.models.User`
    """
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='walls')
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Возвращает строковое представление стены.

        :returns: Описание стены с координатами и названием поля.
        :rtype: str
        """
        return f"Wall at ({self.x}, {self.y}) in {self.field.title}"

class Comment(models.Model):
    """
    Модель комментария к полю.

    :attribute field: Поле, к которому относится комментарий.
    :type field: :class:`main_app.models.Field`
    :attribute author: Автор комментария.
    :type author: :class:`main_app.models.User`
    :attribute text: Текст комментария.
    :type text: str
    :attribute created_at: Дата и время создания комментария.
    :type created_at: :class:`django.db.models.DateTimeField`
    :attribute likes: Пользователи, лайкнувшие комментарий.
    :type likes: :class:`django.db.models.ManyToManyField`
    :attribute reports: Пользователи, сообщившие о нарушении.
    :type reports: :class:`django.db.models.ManyToManyField`
    :attribute is_blocked: Флаг, указывающий, заблокирован ли комментарий.
    :type is_blocked: bool
    """
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    reports = models.ManyToManyField(User, related_name='reported_comments', blank=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокировано")

    def block(self) -> None:
        """
        Блокирует комментарий, устанавливая флаг ``is_blocked`` в ``True``.
        """
        self.is_blocked = True
        self.save()

    def unblock(self) -> None:
        """
        Разблокирует комментарий, устанавливая флаг ``is_blocked`` в ``False``.
        """
        self.is_blocked = False
        self.save()

    def safe_block(self) -> bool:
        """
        Безопасно блокирует комментарий, обновляя только поле ``is_blocked``.

        :returns: ``True``, если блокировка успешна, иначе ``False``.
        :rtype: bool
        :raises Exception: Если происходит ошибка при сохранении изменений.
        """
        try:
            self.is_blocked = True
            self.save(update_fields=['is_blocked'])
            return True
        except Exception as e:
            logger.error("Ошибка блокировки Comment %s: %s", self.id, str(e))
            return False

    class Meta:
        """
        Мета-данные для модели.

        :attribute ordering: Сортировка по убыванию даты создания.
        :type ordering: List[str]
        :attribute verbose_name: Название модели в единственном числе.
        :type verbose_name: str
        :attribute verbose_name_plural: Название модели во множественном числе.
        :type verbose_name_plural: str
        """
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        """
        Возвращает строковое представление комментария.

        :returns: Описание комментария с автором и названием поля.
        :rtype: str
        """
        return f'Комментарий от {self.author.username} к {self.field.title}'

    def likes_count(self) -> int:
        """
        Возвращает количество лайков комментария.

        :returns: Количество лайков.
        :rtype: int
        """
        return self.likes.count()

    def reports_count(self) -> int:
        """
        Возвращает количество жалоб на комментарий.

        :returns: Количество жалоб.
        :rtype: int
        """
        return self.reports.count()

class LikeField(models.Model):
    """
    Модель лайка для поля.

    :attribute user: Пользователь, поставивший лайк.
    :type user: :class:`main_app.models.User`
    :attribute field: Поле, к которому относится лайк.
    :type field: :class:`main_app.models.Field`
    :attribute created_at: Дата и время создания лайка.
    :type created_at: :class:`django.db.models.DateTimeField`
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Мета-данные для модели.

        :attribute unique_together: Уникальность комбинации полей.
        :type unique_together: Tuple[str, str]
        """
        unique_together = ('user', 'field')

    def __str__(self) -> str:
        """
        Возвращает строковое представление лайка.

        :returns: Описание лайка с пользователем и названием поля.
        :rtype: str
        """
        return f"Like by {self.user.username} on {self.field.title}"

class FavoriteField(models.Model):
    """
    Модель избранного для поля.

    :attribute user: Пользователь, добавивший поле в избранное.
    :type user: :class:`main_app.models.User`
    :attribute field: Поле, добавленное в избранное.
    :type field: :class:`main_app.models.Field`
    :attribute created_at: Дата и время добавления в избранное.
    :type created_at: :class:`django.db.models.DateTimeField`
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Мета-данные для модели.

        :attribute unique_together: Уникальность комбинации полей.
        :type unique_together: Tuple[str, str]
        """
        unique_together = ('user', 'field')

    def __str__(self) -> str:
        """
        Возвращает строковое представление избранного.

        :returns: Описание избранного с пользователем и названием поля.
        :rtype: str
        """
        return f"Favorite by {self.user.username} on {self.field.title}"

class LikeComment(models.Model):
    """
    Модель лайка для комментария.

    :attribute user: Пользователь, поставивший лайк.
    :type user: :class:`main_app.models.User`
    :attribute comment: Комментарий, к которому относится лайк.
    :type comment: :class:`main_app.models.Comment`
    :attribute created_at: Дата и время создания лайка.
    :type created_at: :class:`django.db.models.DateTimeField`
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Мета-данные для модели.

        :attribute unique_together: Уникальность комбинации полей.
        :type unique_together: Tuple[str, str]
        """
        unique_together = ('user', 'comment')

    def __str__(self) -> str:
        """
        Возвращает строковое представление лайка комментария.

        :returns: Описание лайка с пользователем и ID комментария.
        :rtype: str
        """
        return f"Like by {self.user.username} on comment {self.comment.id}"

class ReportComment(models.Model):
    """
    Модель жалобы на комментарий.

    :attribute user: Пользователь, подавший жалобу.
    :type user: :class:`main_app.models.User`
    :attribute comment: Комментарий, на который подана жалоба.
    :type comment: :class:`main_app.models.Comment`
    :attribute reason: Причина жалобы.
    :type reason: str
    :attribute created_at: Дата и время подачи жалобы.
    :type created_at: :class:`django.db.models.DateTimeField`
    :attribute is_resolved: Флаг, указывающий, рассмотрена ли жалоба.
    :type is_resolved: bool
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)



class FieldReport(models.Model):
    REASON_CHOICES = [
        ('spam', 'Спам'),
        ('abuse', 'Оскорбительное содержание'),
        ('illegal', 'Незаконный контент'),
        ('other', 'Другое'),
    ]
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Жалоба одобрена'),
        ('rejected', 'Жалоба отклонена'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Жалоба на {self.field.title} ({self.get_reason_display()})"
