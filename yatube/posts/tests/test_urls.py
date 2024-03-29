import unittest

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='test text',
            author=cls.author
        )
        cls.group = Group.objects.create(
            title='test group',
            slug='test',
            description='test desc'
        )

    def setUp(self):
        self.user = User.objects.create_user(username='HasName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(StaticUrlTests.author)

    def test_everyone_pages(self):
        """ Тестирование страниц с общим доступом """

        templates = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.author.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/'
        }
        for template, address in templates.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit(self):
        """ Тестирование редактирования поста """

        responses = {
            self.authorized_author_client: 200,
            self.authorized_client: 302,
            self.client: 302,
        }
        for username, status in responses.items():
            with self.subTest(username=username):
                response = username.get(f'/posts/{self.post.pk}/edit/')
                self.assertEqual(response.status_code, status)

    def test_post_create(self):
        """ Тестирование сощдания поста """

        responses = {
            self.authorized_client: 200,
            self.client: 302,
        }
        for username, status in responses.items():
            with self.subTest(username=username):
                response = username.get('/create/')
                self.assertEqual(response.status_code, status)

    def test_404_page(self):
        """ Тестирвание перехода на несуществующую страницу """

        template = 'core/404.html'
        response = self.client.get('/unexciting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, template)


if __name__ == '__main__':
    unittest.main()
