from django.shortcuts import render
from django.http import HttpResponse
from .models import Post


def index(request):
    # получаем результат из нашей БД
    latest = Post.objects.order_by('-pub_date')[:10]

    return render(request, 'index.html', {'posts': latest})
