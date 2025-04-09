from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)


class Field(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_cards', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorited_cards', blank=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокировано")

    def block(self):
        self.is_blocked = True
        self.save()

    def unblock(self):
        self.is_blocked = False
        self.save()

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


class Comment(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокировано")

    def block(self):
        self.is_blocked = True
        self.save()

    def unblock(self):
        self.is_blocked = False
        self.save()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f'Comment by {self.author.username} on {self.field.title}'


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
        return self.title