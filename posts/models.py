from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()


class Post(models.Model):
    text = models.TextField(max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
