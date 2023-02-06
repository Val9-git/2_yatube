from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = get_page_obj(posts, request)
    context = {'page_obj': page_obj}
    return render(request,
                  'posts/index.html',
                  context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_obj(posts, request)
    return render(request,
                  'posts/group_list.html',
                  {**{'group': group, 'page_obj': page_obj}})


def profile(request, username):
    author = User.objects.get(username=username)
    posts = author.posts.all()
    page_obj = get_page_obj(posts, request)
    following = False
    if Follow.objects.filter(user=request.user.id, author=author):
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request,
                  'posts/profile.html',
                  context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post_list = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post_list)
    context = {
        'post': post_list,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template_name = 'posts/post_create.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', new_post.author.username)
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request, 'posts:post_detail', context)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(post_list, request)
    context = {'page_obj': page_obj}
    return render(request,
                  'posts/follow.html',
                  context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
