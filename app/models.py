from django.db import models


# Create your models here.

class Post(models.Model):
    author = models.CharField(max_length=50, default='Anonymous')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author}: {self.content}"
