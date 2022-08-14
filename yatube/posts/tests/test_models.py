import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый текст',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст вавдыалбмзав'
        )

    def test_post_have_correct_names(self):
        post = PostModelTest.post
        input_text = str(post)
        expected_text = post.text[:15]
        self.assertEqual(input_text, expected_text)

    def test_group_have_correct_names(self):
        group = PostModelTest.group
        input_text = str(group)
        expected_text = group.title
        self.assertEqual(input_text, expected_text)


if __name__ == '__main__':
    unittest.main()
