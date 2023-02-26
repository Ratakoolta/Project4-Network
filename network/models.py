from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="autor")
    post = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publicación {self.id} hecha por {self.user} el {self.date.strftime('%d %b %Y %H:%M:%S')}"

