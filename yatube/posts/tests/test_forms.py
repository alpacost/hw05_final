import unittest

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class TestPostForms(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='test post',
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_new_posts(self):
        """ Тестирование создания нового поста """

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
        count_posts = Post.objects.count()
        new_post = {
            'text': 'test pos',
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=new_post,
            follow=True
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)

    def test_posts_edit(self):
        """ Тестирование редактирования поста """

        count_posts = Post.objects.count()
        new_post = {
            'text': 'test pos'
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=new_post,
            follow=True
        )
        self.assertEqual(Post.objects.count(), count_posts)
        self.assertEqual(Post.objects.get(pk=1).text, new_post['text'])


if __name__ == '__main__':
    unittest.main()
