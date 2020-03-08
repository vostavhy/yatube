from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from working_scripts.rendering_scripts import get_pagination_info
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.decorators.cache import cache_page


# @cache_page(15)  # кеширование страницы на 15 секунд, начиная с момента последнего запроса
def index(request):
    # получаем результат из нашей БД
    related_posts = Post.objects.select_related('author', 'group') \
        .order_by('-pub_date') \
        .all() \
        .annotate(comment_count=Count('comment'))
    page, paginator = get_pagination_info(request, posts=related_posts)

    # проверяем, подписан ли на кого-то пользователь
    following = True
    if request.user.is_authenticated:
        if not Follow.objects.filter(user=request.user):
            following = False

    return render(request, 'index.html', {'page': page, 'paginator': paginator, 'following': following})


# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    related_posts = Post.objects.select_related('author', 'group') \
        .filter(group=group) \
        .order_by("-pub_date") \
        .all() \
        .annotate(comment_count=Count('comment'))
    page, paginator = get_pagination_info(request, posts=related_posts)
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    # проверяем, что это POST запрос
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)

        # проверяем данные на валидность и если данные валидны, создаем новый пост
        if form.is_valid():

            # author = request.user
            # text = form.cleaned_data['text']
            # group = form.cleaned_data['group']
            # Post.objects.create(author=author, text=text, group=group)

            post = form.save(commit=False)
            # Here we can modify the post
            post.author = request.user
            post.save()

            return redirect('index')

        # вернём пользователю страницу с HTML-формой и передадим полученный объект формы на страницу,
        # чтобы вернуть информацию об ошибке

        # заодно автоматически заполним прошедшими валидацию данными все поля,
        # чтобы не заставлять пользователя второй раз заполнять их

        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            # post.group = form.cleaned_data['group']
            # post.text = form.cleaned_data['text']
            # post.save()
            form.save()
            return HttpResponseRedirect(reverse_lazy('post', kwargs={'username': username, 'post_id': post_id}))
        return render(request, 'new_post.html', {'form': form})

    return render(request, 'new_post.html', {'form': form, 'post': post})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    author = post.author
    count = Post.objects.filter(author__username=username).count()
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    return render(request, 'post.html', {'post': post,
                                         'count': count,
                                         'author': author,
                                         'comments': comments,
                                         'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author', 'group')\
        .filter(author=author)\
        .order_by("-pub_date")\
        .all().annotate(comment_count=Count('comment'))
    page, paginator = get_pagination_info(request=request, posts=posts)

    following = True

    # try необходим, т.к. user может быть анонимусом
    try:
        if not Follow.objects.filter(author=author, user=request.user):
            following = False
    except:
        pass

    return render(request, 'profile.html',
                  {'page': page, 'paginator': paginator, 'author': author, 'profile': author, 'following': following})


def page_not_found(request, exception):
    # exception содержит отладочную информацию
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


# добавить комментарий
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            # Here we can modify the comment
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, {'form': form})
    return redirect('post', username=username, post_id=post_id)


# отображать страницу с подписками
@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    following_authors = [follow.author for follow in follows]  # .filter(author__following__user=request.user)

    related_posts = Post.objects.select_related('author', 'group') \
        .filter(author__in=following_authors) \
        .order_by("-pub_date") \
        .all() \
        .annotate(comment_count=Count('comment'))
    page, paginator = get_pagination_info(request, posts=related_posts)
    return render(request, "follow.html", {'page': page, 'paginator': paginator, 'following': True})


# подписаться
@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user.username != username and not Follow.objects.filter(user=request.user, author=author):
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


# отписаться
@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.get(user=request.user, author=author)
    follow.delete()
    return redirect('profile', username=username)
