import os

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from posts.models import Post
from django.conf import settings


class TestingPostsManipulations(TestCase):
    def setUp(self):

        # Создаем пользователя
        self.user = User.objects.create_user(username='nick', password='12345')

        # Создаем пост
        self.text_post1 = 'Тестовый пост 1'
        Post.objects.create(text=self.text_post1, author=self.user)

        # Создаем web клиент
        self.client = Client()

        # прописываем путь к скриншоту
        self.screenshot_path = os.path.join(settings.MEDIA_ROOT, 'posts', 'file.png')
        self.img_tag = '<img'

        # очищаем кеш перед вызовом тестов
        cache.clear()

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
            self.assertEquals(resp.context['page'][0].text, self.text_post1)

            # проверяем, что автор записи совпадает
            self.assertEquals(resp.context['page'][0].author.username, self.user.username)

            # проверяем, что дата публикации совпадает
            self.assertEquals(resp.context['page'][0].pub_date, Post.objects.get(id=1).pub_date)

            # проверяем что страница содержит нужную информацию
            self.assertContains(resp, self.text_post1)

    def test_post(self):
        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что страница найдена
        self.assertEqual(resp.status_code, 200)

        # проверяем, что текст записи совпадает
        self.assertEquals(resp.context['post'].text, self.text_post1)

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
        self.assertRedirects(resp, f'/auth/login/?next=/{self.user.username}/1/edit/')

    def test_author_can_edit_their_posts(self):
        self.client.login(username='nick', password='12345')
        resp = self.client.get(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'nick')

        # проверяем что у авторизованного пользователя есть доступ странице 'nick/1/edit'
        self.assertEqual(resp.status_code, 200)

        # проверяем что пользователь может изменить текст в посте и добавить картинку
        new_text = 'Это измененный текст'
        with open(self.screenshot_path, 'rb') as fp:
            resp = self.client.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}),
                                    {'text': new_text, 'image': fp})

        self.assertRedirects(resp, reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем что запись изменилась на главной, в профиле и на странице поста
        resp = self.client.get(reverse('index'))
        self.assertEquals(resp.context['page'][0].text, new_text)
        self.assertContains(resp, new_text)
        self.assertContains(resp, self.img_tag)

        resp = self.client.get('/nick/')
        self.assertEquals(resp.context['page'][0].text, new_text)
        self.assertContains(resp, new_text)
        self.assertContains(resp, self.img_tag)

        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))
        self.assertEquals(resp.context['post'].text, new_text)
        self.assertContains(resp, new_text)
        self.assertContains(resp, self.img_tag)

        # проверяем что нельзя загрузить неверный формат файла
        screenshot_path = os.path.join(settings.MEDIA_ROOT, 'posts', 'file.log')
        with open(screenshot_path, 'rb') as fp:
            resp = self.client.post(reverse('post_edit', kwargs={'username': self.user.username, 'post_id': 1}),
                                    {'text': new_text, 'image': fp})
        # редиректа не происходит. мы остаемся на той же странице, файл не загружен
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'new_post.html')

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

        # проверяем что пользователь может создать новый пост c картинкой
        text_post2 = 'Тестовый текст2'

        with open(self.screenshot_path, 'rb') as fp:
            resp = self.client.post(reverse('new_post'), {'author': self.user, 'text': text_post2, 'image': fp})
        self.assertRedirects(resp, reverse('index'))

        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 2}))

        # проверяем что страница найдена
        self.assertEqual(resp.status_code, 200)

        # проверяем что страница содержит нужную информацию
        self.assertContains(resp, text_post2)
        self.assertContains(resp, self.img_tag)

        # проверяем что количество постов на главной увеличилось
        resp = self.client.get(reverse('index'))
        self.assertEqual(len(resp.context['page']), 2)

        # проверяем что страница содержит нужную информацию
        self.assertContains(resp, text_post2)
        self.assertContains(resp, self.img_tag)

        # проверяем что количество постов на странице автора увеличилось
        resp = self.client.get('/nick/')
        self.assertEqual(len(resp.context['page']), 2)

        # проверяем что страница содержит нужную информацию
        self.assertContains(resp, text_post2)
        self.assertContains(resp, self.img_tag)

    def test_cannot_create_comments_without_authorization(self):
        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем, что на странице не доступна кнопка для отправки комментариев
        self.assertNotContains(resp, 'Отправить')

    def test_logged_can_create_comments(self):
        self.client.login(username='nick', password='12345')

        # формируем запрос к странице поста
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))

        # проверяем, что на странице доступна кнопка для отправки комментариев
        self.assertContains(resp, 'Отправить')

        # создаем два новых комментария
        post = Post.objects.get(id=1)
        for i in range(2):
            self.client.post(reverse('add_comment', kwargs={'username': self.user.username, 'post_id': 1}),
                             {'author': self.user.username, 'post': post, 'text': f'Комментарий {i}'})

        # проверяем, что комментарии были добавлены
        resp = self.client.get(reverse('post', kwargs={'username': self.user.username, 'post_id': 1}))
        for i in range(2):
            self.assertContains(resp, f'Комментарий {i}')

    def test_get_error_404(self):

        # формируем запрос к несуществующей странице
        resp = self.client.get(reverse('post', kwargs={'username': 'fake_username', 'post_id': 2}))

        # проверяем, что сервер возвращает код 404
        self.assertEqual(resp.status_code, 404)

    def test_cache(self):
        key = make_template_fragment_key('index_page', [1])
        self.assertFalse(cache.get(key))
        self.client.get('')
        self.assertTrue(cache.get(key))

    def test_logged_can_follow(self):
        # авторизуемся
        self.client.login(username='nick', password='12345')

        # создаем нового пользователя и создаем из под него новый пост
        user2 = User.objects.create_user(username='user2', password='12345')
        text_post2 = 'Тестовый пост2'
        Post.objects.create(author=user2, text=text_post2)

        # проверяем что новый пост недоступен на странице '/follow' для пользователя nick
        cache.clear()
        resp = self.client.get(reverse('follow_index'))
        self.assertNotContains(resp, text_post2)

        # подписываемся nick на user2 и проверяем доступность поста text_post2
        cache.clear()
        self.client.get(reverse('profile_follow', kwargs={'username': user2.username}))
        resp = self.client.get(reverse('follow_index'))
        self.assertContains(resp, text_post2)

        # отписываемся от user2 и проверяем, что пост больше недоступен
        cache.clear()
        self.client.get(reverse('profile_unfollow', kwargs={'username': user2.username}))
        resp = self.client.get(reverse('follow_index'))
        self.assertNotContains(resp, text_post2)
