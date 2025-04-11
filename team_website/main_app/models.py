from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

class ProfileComment(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Field(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_cards', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorited_cards', blank=True)
    cols = models.IntegerField(default=10)  # Количество колонок
    rows = models.IntegerField(default=10)  # Количество строк

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

    class Meta:
        ordering = ['-created_at']

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


class ReportField(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} on field {self.field.title}"


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_posts', blank=True)

    def __str__(self):
        return self.title