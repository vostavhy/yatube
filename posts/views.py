from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.contrib.auth.decorators import login_required


def index(request):
    # получаем результат из нашей БД
    related_posts = Post.objects.select_related('author').order_by('-pub_date').all()
    paginator = Paginator(related_posts, 10)  # показывать по 10 записей на странице

    page_number = request.GET.get('page')  # переменная в url с номером запрошеной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением

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

        return render(request, 'index.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    return render(request, 'profile.html', {})


def post_view(request, username, post_id):
    return render(request, 'post.html', {})


def post_edit(request, user_name, post_id):
    return render(request, 'new_post.html', {})
