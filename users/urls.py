from django.urls import path
from . import views


urlpatterns = [
    # path() для страницы регистрации нового пользователя
    # полный адрес - "auth/signup". префикс "auth/" обрабатывается в головном urls.py
    path('signup/', views.SignUP.as_view(), name='signup')
]
