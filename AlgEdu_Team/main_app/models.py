from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class Map(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maps')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.map.title}"


class LikeMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_maps')
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'map')

    def __str__(self):
        return f"Like by {self.user.username} on {self.map.title}"


class FavoriteMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_maps')
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'map')  

    def __str__(self):
        return f"Favorite by {self.user.username} on {self.map.title}"


class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_comments')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  

    def __str__(self):
        return f"Like by {self.user.username} on comment {self.comment.id}"


class ReportComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_comments')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} on comment {self.comment.id}"


class ReportMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_maps')
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user.username} on map {self.map.title}"