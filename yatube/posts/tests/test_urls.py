# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='just_user')
        cls.author_user = User.objects.create_user(username='author_user')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_user,
            text='Тестовый пост',
        )

        cls.urls_for_guest = {
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user}/',
            f'/posts/{cls.post.pk}/',
        }
        cls.url_names_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author_user}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_authorized_client = Client()
        self.author_authorized_client.force_login(self.author_user)

    def test_page_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        for address in self.urls_for_guest:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author_only(self):
        """Страница /edit/ доступна автору поста только."""
        response = self.author_authorized_client.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_redirect(self):
        """Страница создания поста перенаправляет
        неавторизованнного пользователя на страницу авторизации."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_page_url_exists_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        for address, template in self.url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
        self.assertTemplateUsed(response, template)

    def test_not_found(self):
        """Несуществующая страница возвращает 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
