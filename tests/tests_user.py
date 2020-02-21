from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class EmailTest(TestCase):

    def setUp(self):
        # Создаем web клиент
        self.client = Client()

    def test_send_email(self):

        # регистрируемся
        resp = self.client.post(reverse('signup'),
                                {'username': 'nick', 'password1': '12kajshsj31', 'password2': '12kajshsj31'})

        # проверяем, что авторизация прошла
        self.assertRedirects(resp, reverse('login'))

        # проверяем, что только что созданный пользователь существует
        user = User.objects.filter(username='nick')
        self.assertIsNotNone(user)

        # Проверяем, что письмо лежит в исходящих
        self.assertEqual(len(mail.outbox), 1)

        # Проверяем, что тема первого письма правильная.
        self.assertEqual(mail.outbox[0].subject, f'Greetings {user[0].username}')
