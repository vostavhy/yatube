from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from working_scripts.rendering_scripts import get_pagination_info
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required


def index(request):
    # получаем результат из нашей БД
    related_posts = Post.objects.select_related('author').order_by('-pub_date').all()
    page, paginator = get_pagination_info(request, posts=related_posts)

    return render(request, 'index.html', {'page': page, 'paginator': paginator})


# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.select_related('author').filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})


@login_required
def new_post(request):
    # проверяем, что это POST запрос
    if request.method == 'POST':
        form = PostForm(request.POST)

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
    if username == request.user.username:
        post = Post.objects.get(author__username=username, id=post_id)
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post.group = form.cleaned_data['group']
                post.text = form.cleaned_data['text']
                post.save()
                return HttpResponseRedirect(reverse_lazy('post', kwargs={'username': username, 'post_id': post_id}))

            return render(request, 'new_post.html', {'form': form})

        # write appropriate information into the form fields
        form = PostForm({'group': post.group, 'text': post.text})
        return render(request, 'new_post.html', {'form': form})
    return HttpResponseRedirect(reverse_lazy('post', kwargs={'username': username, 'post_id': post_id}))


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    count = Post.objects.filter(author__username=username).count()
    return render(request, 'post.html', {'post': post, 'count': count})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by("-pub_date")
    page, paginator = get_pagination_info(request=request, posts=posts)

    return render(request, 'profile.html', {'page': page, 'paginator': paginator})
