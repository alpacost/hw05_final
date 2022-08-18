from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import pagination


def index(request):
    post_list = Post.objects.all()
    page_obj = pagination(request, post_list)
    context = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def follow_identify(request, username):
    follow = get_object_or_404(User, username=username)
    return Follow.objects.filter(user=request.user, author=follow).exists()


def profile(request, username):
    name = get_object_or_404(User, username=username)
    full_name = name.get_full_name()
    posts = Post.objects.filter(author=name)
    posts_number = posts.count()
    page_obj = pagination(request, posts)
    author = name
    following = follow_identify(request, username)
    context = {
        'full_name': full_name,
        'page_obj': page_obj,
        'posts_number': posts_number,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    author = post.author
    posts_number = (Post.objects.filter(author=author)).count()
    title = post.text[:30]
    context = {
        'post': post,
        'author': author,
        'title': title,
        'posts_number': posts_number,
        'form': comment_form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if request.method == 'POST':
        if form.is_valid():
            author = request.user
            result = form.save(commit=False)
            result.author = author
            result.save()
            return redirect('posts:profile', username=request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        is_edit = True
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return (
                redirect('posts:post_detail', post_id))
        return render(request,
                      'posts/create_post.html',
                      {'form': form,
                       'is_edit': is_edit,
                       'post_id': post_id})
    return redirect('posts:post_detail', post_id=post_id)


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


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follow = get_object_or_404(User, username=username)
    if request.user.id != follow.id:
        Follow.objects.get_or_create(user=request.user, author=follow)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = get_object_or_404(User, username=username)
    if request.user.id != follow.id:
        get_object_or_404(Follow, user=request.user, author=follow).delete()
    return redirect('posts:profile', username=username)
