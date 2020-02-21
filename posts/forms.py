from django import forms
from .models import Post


# класс формы для создания постов
class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        # поля, которые должны быть видны
        fields = ('group', 'text')
