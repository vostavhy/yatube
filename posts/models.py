from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields import files
from sorl.thumbnail import ImageField

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    group = models.ForeignKey(
        Group, verbose_name='Группа', blank=True, null=True, on_delete=models.CASCADE, related_name='group'
    )
    image = files.ImageField(upload_to='posts/', blank=True, null=True)  # поле для картинки

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentator')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')  # кто подписывается
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')  # на кого подписываются

    def __str__(self):
        return 'Кто подписывается:' + str(self.user) + ' ' + 'На кого подписывается: ' + str(self.author)
