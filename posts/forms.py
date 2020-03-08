from django import forms
from .models import Post, Comment


# класс формы для создания постов
class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        # поля для отображения
        fields = ('group', 'text', 'image')


# класс формы для создания комментариев
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        # поля для отображения
        fields = ('text',)

