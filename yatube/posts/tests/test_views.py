# posts/tests/test_views.py
from django.conf import settings as s
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, Follow
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache


from ..forms import PostForm

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author_user')

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )

        cls.pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug':
                    cls.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':
                    cls.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    cls.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    cls.post.pk}): 'posts/post_create.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_page_cache(self):
        new_post = Post.objects.create(author=self.user, text='Тест кеш')
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, new_post.text)
        new_post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response, new_post.text)
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotContains(response, new_post.text)

    def test_view_uses_correct_template(self):
        """View функции использует соответствующий шаблон."""
        for reverse_name, template in self.pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post(self, context):
        self.assertEqual(context.text, self.post.text)
        self.assertEqual(context.author, self.post.author)
        self.assertEqual(context.group, self.post.group)
        self.assertEqual(context.id, self.post.id)
        self.assertEqual(context.pub_date, self.post.pub_date)
        self.assertEqual(context.image, self.post.image)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post(response.context['page_obj'][0])

    def test_group_posts_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug})))
        self.check_post(response.context['page_obj'][0])

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:profile',
                    kwargs={'username': self.user})))
        self.check_post(response.context['page_obj'][0])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})))
        self.check_post(response.context['post'])

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIn('form', response.context)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_created_on_right_pages(self):
        """Проверка появления нового поста на правильных страницах"""
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        }
        for page in page_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                context_post = response.context['page_obj'][0]
                self.assertEqual(context_post, self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый пост')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page_contains_ten_records(self):
        """Проверка разделитиля страниц на количество записей"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), s.POSTS_Q)

    def test_paginator_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create(username='test_author')
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)
        cls.user_fol = User.objects.create(username='test_user_fol')
        cls.authorized_user_fol_client = Client()
        cls.authorized_user_fol_client.force_login(cls.user_fol)
        cls.user_unfol = User.objects.create(username='test_user_unfol')
        cls.authorized_user_unfol_client = Client()
        cls.authorized_user_unfol_client.force_login(cls.user_unfol)

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )

    def test_follow(self):
        """Тест работы подписки на автора."""
        client = FollowViewsTest.authorized_user_unfol_client
        user = FollowViewsTest.user_unfol
        author = FollowViewsTest.author
        client.get(reverse('posts:profile_follow', args=[author.username]))
        follower = Follow.objects.filter(user=user, author=author).exists()
        self.assertTrue(follower, 'Подписка не работает')

    def test_unfollow(self):
        """Тест работы отписки от автора."""
        client = FollowViewsTest.authorized_user_unfol_client
        user = FollowViewsTest.user_unfol
        author = FollowViewsTest.author
        client.get(reverse('posts:profile_unfollow', args=[author.username]),)
        follower = Follow.objects.filter(user=user, author=author).exists()
        self.assertFalse(follower, 'Отписка не работает')

    def test_new_author_post_for_follower(self):
        client = FollowViewsTest.authorized_user_fol_client
        author = FollowViewsTest.author
        group = FollowViewsTest.group
        client.get(reverse('posts:profile_follow', args=[author.username]))
        new_post = Post.objects.create(
            text='test_new_post', group=group, author=author)
        cache.clear()
        response_new = client.get(reverse('posts:follow_index'))
        new_posts = response_new.context['page_obj']
        self.assertEqual(len(response_new.context['page_obj']), 2)
        self.assertIn(new_post, new_posts)

    def test_new_author_post_for_unfollower(self):
        client = FollowViewsTest.authorized_user_unfol_client
        author = FollowViewsTest.author
        group = FollowViewsTest.group

        new_post = Post.objects.create(
            text='test_new_post',
            group=group,
            author=author
        )
        cache.clear()
        response_new = client.get(reverse('posts:follow_index'))
        new_posts = response_new.context['page_obj']
        self.assertEqual(len(response_new.context['page_obj']), 0)
        self.assertNotIn(new_post, new_posts)
