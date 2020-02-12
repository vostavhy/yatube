from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


# класс для формы регистрации
class CreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        # модель уже существует, сошлемся на неё
        model = User
        # укажем, какие поля должны быть видны и в каком порядке
        fields = ('first_name', 'last_name', 'username', 'email')
