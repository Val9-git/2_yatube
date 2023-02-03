# posts/tests/test_forms.py
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
# , CommentForm
from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            # comment_author=cls.user
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # small_gif = (
        #     b'\x47\x49\x46\x38\x39\x61\x02\x00'
        #     b'\x01\x00\x80\x00\x00\x00\x00\x00'
        #     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        #     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        #     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        #     b'\x0A\x00\x3B'
        # )
        # uploaded = SimpleUploadedFile(
        #     name='small.gif',
        #     content=small_gif,
        #     content_type='image/gif'
        # )
        # form_data = {
        #     'text': 'Тест с картинкой',
        #     'group': self.group.id,
        #     'image': uploaded,
        # }

    def test_post_form_creation(self):
        """Валидная форма создает запись."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тест с картинкой',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.context['post'], self.post)

    def test_post_form_edition(self):
        """Валидная форма создает отредактированную запись."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data_edit = {
            'text': 'Редактированный тест с картинкой',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.pk}/')
        # self.assertRedirects(response, reverse('posts: post_detail',
        #                      kwargs={'post_id': self.post.pk}))

        self.assertTrue(
            Post.objects.filter(
                text='Редактированный тест с картинкой',
                group=self.group.id,
                image=Post.objects.last().image
                # 'posts/small.gif'
            ).exists()
        )

    def test_create_comment_authorized_only(self):
        """Комментирует только авторизованный пользователь"""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Комментарий'}
        response = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post_id, self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.id}))
