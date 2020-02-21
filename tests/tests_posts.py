from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from posts.models import Post


class TestingPostsManipulations(TestCase):
    def setUp(self):

        # Создаем пользователя
        self.user = User.objects.create_user(username='nick', password='12345')

        # Создаем пост
        Post.objects.create(text='Тестовый пост 1', author=self.user)

        # Создаем web клиент
        self.client = Client()

    def test_profile_and_index(self):
        # авторизуемся
        self.client.login(username='nick', password='12345')

        # т.к тесты для страниц index и profile полностью идентичны
        # можем добавить их в список и затем последовательно проверить
        resp_list = list()

        # формируем GET-запрос к странице профиля
        resp_list.append(self.client.get('/nick/'))

        # формируем запрос к главной странице сайта
        resp_list.append(self.client.get(reverse('index')))

        for resp in resp_list:

            # проверяем что страница найдена
            self.assertEqual(resp.status_code, 200)

            # проверяем, что при отрисовке страницы был получен список из 1 записи
            self.assertEqual(len(resp.context['page']), 1)

            # проверяем, что текст записи совпадает
            self.assertEquals(resp.context['page'][0].text, 'Тестовый пост 1')

            # проверяем, что автор записи совпадает
            self.assertEquals(resp.context['page'][0].author.username, self.user.username)

            # проверяем, что дата публикации совпадает
            self.assertEquals(resp.context['page'][0].pub_date, Post.objects.get(id=1).pub_date)

    def test_post(self):
        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что страница найдена
        self.assertEqual(resp.status_code, 200)

        # проверяем, что текст записи совпадает
        self.assertEquals(resp.context['post'].text, 'Тестовый пост 1')

        # проверяем, что автор записи совпадает
        self.assertEquals(resp.context['post'].author.username, self.user.username)

        # проверяем, что дата публикации совпадает
        self.assertEquals(resp.context['post'].pub_date, Post.objects.get(id=1).pub_date)

    def test_redirect_from_edit_if_not_author(self):
        author2 = User.objects.create_user(username='author2', password='12345')
        self.client.login(username='author2', password='12345')
        resp = self.client.get(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}), follow=True)

        # проверяем что пользователь залогинился
        self.assertEqual(resp.context['user'].username, author2.username)

        # проверяем что его редиректит на страницу поста
        self.assertRedirects(resp, reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

    def test_cannot_edit_without_authorization(self):
        resp = self.client.get(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, f'/auth/login/?next=/{self.user.username}/1/edit')

    def test_author_can_edit_their_posts(self):
        self.client.login(username='nick', password='12345')
        resp = self.client.get(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'nick')

        # проверяем что у авторизованного пользователя есть доступ странице 'nick/1/edit'
        self.assertEqual(resp.status_code, 200)

        # проверяем что пользователь может изменить свой пост
        resp = self.client.post(reverse('post_edit',
                                        kwargs={'username': self.user.username, 'post_id': 1}),
                                {'text': 'Это измененный текст'})

        self.assertRedirects(resp, reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что запись изменилась на главной, в профиле и на странице поста
        resp = self.client.get(reverse('index'))
        self.assertEquals(resp.context['page'][0].text, 'Это измененный текст')

        resp = self.client.get('/nick/')
        self.assertEquals(resp.context['page'][0].text, 'Это измененный текст')

        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))
        self.assertEquals(resp.context['post'].text, 'Это измененный текст')

    def test_redirect_from_new_if_not_logged_in(self):
        resp = self.client.get(reverse('new_post'))
        self.assertRedirects(resp, '/auth/login/?next=/new/')

    def test_logged_has_access_to_new(self):
        self.client.login(username='nick', password='12345')
        resp = self.client.get(reverse('new_post'))

        # проверяем что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'nick')
        # проверяем что у авторизованного пользователя есть доступ странице '/new'
        self.assertEqual(resp.status_code, 200)

    def test_logged_can_create_new_post(self):
        self.client.login(username='nick', password='12345')

        # проверяем что пользователь может создать новый пост
        resp = self.client.post(reverse('new_post'), {'author': self.user, 'text': 'Тестовый текст2'})
        self.assertRedirects(resp, reverse('index'))

        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что страница найдена
        self.assertEqual(resp.status_code, 200)

        # проверяем что количество постов на главной увеличилось
        resp = self.client.get(reverse('index'))
        self.assertEqual(len(resp.context['page']), 2)

        # проверяем что количество постов на странице автора увеличилось
        resp = self.client.get('/nick/')
        self.assertEqual(len(resp.context['page']), 2)
