import logging
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import AbstractUser

logger = logging.getLogger(__name__)

class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def safe_ban(self):
        try:
            self.is_active = False
            self.save(update_fields=['is_active'])
            Field.objects.filter(user=self).update(is_blocked=True)
            Comment.objects.filter(author=self).update(is_blocked=True)
            return True
        except Exception as e:
            logger.error(f"Ошибка бана User %s: %s", self.id, str(e))
            return False

    def __str__(self):
        return str(self.username)

class ProfileComment(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class FieldFile(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    data = models.BinaryField()
    size = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def to_file(self):
        return ContentFile(self.data, name=self.name)


class Field(models.Model):
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

    def block(self):
        self.is_blocked = True
        self.save()

    def unblock(self):
        self.is_blocked = False
        self.save()

        def safe_block(self):
            try:
                if not isinstance(self.cols, int):
                    try:
                        self.cols = int(self.cols) if str(self.cols).isdigit() else 10
                    except (TypeError, ValueError):
                        self.cols = 10
                self.is_blocked = True
                self.save(update_fields=['is_blocked', 'cols'])
                self.comments.update(is_blocked=True)
                return True
            except Exception as e:
                logger.error("Ошибка блокировки Field %s: %s", self.id, str(e))
                return False

    def safe_unblock(self):
        try:
            self.is_blocked = False
            self.save(update_fields=['is_blocked'])
            return True
        except Exception as e:
            logger.error("Ошибка разблокировки Field %s: %s", self.id, str(e))
            return False

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('card-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Карта"
        verbose_name_plural = "Карты"
        permissions = [
            ("can_view_blocked", "Может просматривать заблокированные карты"),
        ]

    def __str__(self):
        return self.title


class Cell(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='cells')
    x = models.IntegerField()  # X координата
    y = models.IntegerField()  # Y координата
    is_blocked = models.BooleanField(default=False)  # Заблокирована ли клетка

    class Meta:
        unique_together = ('field', 'x', 'y')

    def __str__(self):
        return f"Cell ({self.x}, {self.y}) in {self.field.title}"

class Wall(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='walls')
    x = models.IntegerField()  # Начальная X координата
    y = models.IntegerField()  # Начальная Y координата
    width = models.IntegerField(default=1)  # Ширина стены (в клетках)
    height = models.IntegerField(default=1)  # Высота стены (в клетках)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Wall at ({self.x}, {self.y}) in {self.field.title}"

class Comment(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    reports = models.ManyToManyField(User, related_name='reported_comments', blank=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокировано")

    def block(self):
        self.is_blocked = True
        self.save()

    def unblock(self):
        self.is_blocked = False
        self.save()

    def safe_block(self):
        try:
            self.is_blocked = True
            self.save(update_fields=['is_blocked'])
            return True
        except Exception as e:
            logger.error("Ошибка блокировки Comment %s: %s", self.id, str(e))
            return False


    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.field.title}'

    def likes_count(self):
        return self.likes.count()

    def reports_count(self):
        return self.reports.count()


class LikeField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'field')

    def __str__(self):
        return f"Like by {self.user.username} on {self.field.title}"


class FavoriteField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'field')

    def __str__(self):
        return f"Favorite by {self.user.username} on {self.field.title}"


class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"Like by {self.user.username} on comment {self.comment.id}"


class ReportComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} on comment {self.comment.id}"


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



class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_posts', blank=True)

    def __str__(self):
        return str(self.title)
