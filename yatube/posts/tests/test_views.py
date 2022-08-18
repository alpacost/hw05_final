import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post, User

User = get_user_model()


class TestPostsViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VasyaPupkin')
        cls.group = Group.objects.create(
            title='test group',
            slug='test',
            description='test desc'
        )
        for i in range(0, 13):
            Post.objects.create(
                text='test text' + str(i),
                author=cls.user,
                group=cls.group
            )
        cls.post = Post.objects.get(pk=1)
        cls.test_post = Post.objects.get(pk=13)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.tess = User.objects.create_user(username='Vasya')
        self.tester_client = Client()
        self.tester_client.force_login(self.tess)
        self.newbie = User.objects.create_user(username='test')

    def test_namespase(self):
        """ Тестирвание namespace"""

        templates = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }

        for namespace, template in templates.items():
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                self.assertTemplateUsed(response, template)

    def test_context_paginator(self):
        """ Тестирвание контекста в паджинаторм """

        templates = {
            'posts/index.html':
                reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug':
                                                    self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username':
                                                 self.user.username}),
        }
        expected_context = {
            'posts/index.html': Post,
            'posts/group_list.html':
                type(Post.objects.filter(group=self.group)[0]),
            'posts/profile.html':
                type(Post.objects.filter(author=self.user)[0]),
        }
        for template, namespace in templates.items():
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                form_field = response.context.get('page_obj')
                self.assertIsInstance(form_field.object_list[0],
                                      expected_context[template])
                self.assertEqual(len(form_field.object_list),
                                 settings.POSTS_AMOUNT)

    def test_context_post_detail(self):
        """ Тестирвание post_detail """

        templates = {
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        }
        expected_context = {
            'posts/post_detail.html': self.post,
        }
        for template, namespace in templates.items():
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                form_field = response.context.get('post')
                self.assertEqual(form_field, expected_context[template])

    def test_context_form(self):
        """ Тестирвание страниц с формами поста """

        templates = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }
        expected_context = {
            'posts/create_post.html': PostForm,
        }
        for namespace, template in templates.items():
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                form_field = response.context.get('form')
                self.assertEqual(type(form_field), expected_context[template])

    def test_post_group_exist(self):
        """ Тестирвание поста с группой """

        templates = {
            'posts/index.html':
                reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
        }
        posts = Post.objects.create(
            text='tasty',
            author=self.user,
            group=self.group
        )
        for template, namespace in templates.items():
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                form_field = response.context.get('page_obj').object_list[0]
                self.assertEqual(form_field, posts)

    def test_image_in_context(self):
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
        post = Post.objects.create(
            text='яблоко',
            group=self.group,
            image=uploaded,
            author=self.user
        )
        templates = (reverse('posts:index'),
                     reverse('posts:profile',
                             kwargs={'username': self.user.username}),
                     reverse('posts:group_list',
                             kwargs={'slug': self.group.slug}),
                     )
        for namespace in templates:
            with self.subTest(value=namespace):
                response = self.authorized_client.get(namespace)
                form_field = response.context.get('page_obj').object_list[0]
                self.assertTrue(form_field.image)
        namespace = (reverse('posts:post_detail', kwargs={'post_id': post.pk}))
        response = self.authorized_client.get(namespace)
        form_field = response.context.get('post')
        self.assertTrue(form_field.image)

    def test_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        form_field = response.context.get('page_obj').object_list
        Post.objects.filter(pk=self.test_post.pk).delete()
        self.assertIn(self.test_post, form_field)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        form_field = response.context.get('page_obj').object_list
        self.assertNotIn(self.test_post, form_field)

    def test_follow(self):
        self.tester_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        follow = Follow.objects.filter(user=self.tess, author=self.user)
        self.assertTrue(follow.exists())
        self.tester_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username})
        )
        self.assertFalse(follow.exists())

    def test_unfollow(self):
        self.tester_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username}))
        follow = Follow.objects.filter(user=self.tess, author=self.user)
        self.tester_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user.username})
        )
        self.assertFalse(follow.exists())

    def test_follow_index(self):
        template = reverse('posts:follow_index')
        expected_values = {
            self.authorized_client: 0,
            self.tester_client: 1
        }
        self.tester_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.newbie.username}))
        for client, value in expected_values.items():
            with self.subTest(value=template):
                Post.objects.create(
                    text='яблоко',
                    author=self.newbie
                )
                response = client.get(template)
                filed = response.context.get('page_obj').object_list
                self.assertEqual(len(filed), value)
                Post.objects.all().delete()


if __name__ == '__main__':
    unittest.main()
