from django.forms import ModelForm

from .models import Post, Comment

from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': _('Текст'), 'group': _('Группа'),
                  'image': _('Рисунок')}
        help_texts = {
            'text': _('Текст поста'),
            'group': _('Группа, в которой состоит пост'),
            'image': _('Рисунок к посту'),
        }


class CommentForm(ModelForm):
    class Meta():
        model = Comment
        fields = (
            # 'post',
            # 'author',
            'text',
            # 'created'
        )
        labels = {
            # 'post': _('Пост'),
            # 'author': _('Автор'),
            'text': _('Текст'),
            # 'created': _('Дата публикации')
        }
        help_texts = {
            # 'post': _('К какому посту'),
            # 'author': _('Автор комментария'),
            'text': _('Текст комментария'),
            # 'created': _('Дата публикации комментария'),
        }
