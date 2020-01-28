from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отобрадаться в админке
    list_display = ('pk', 'text', 'pub_date', 'author')
    # интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'  # это свойство сработает для всех колонок: где пусто - там будет эта строка


# при регистрации модели Post, источником информации для неё назначен PostAdmin
admin.site.register(Post, PostAdmin)
admin.site.register(Group)
