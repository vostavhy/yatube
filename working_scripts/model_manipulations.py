from posts.models import Post
from django.contrib.auth.models import User


def post_create_instance():
    new_post = Post()
    user = User.objects.get(username='vostavhy')
    new_post.text = 'Созданно из сторонней функции'
    new_post.author = user
    new_post.save()
    print('saving...\n' + str(new_post))

