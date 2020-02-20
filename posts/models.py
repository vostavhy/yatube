from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст', max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
    group = models.ForeignKey(Group, verbose_name='Группа', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.id:
            self.text = self.text + ' Создано в ' + str(datetime.utcnow())
        return super().save(*args, **kwargs)
