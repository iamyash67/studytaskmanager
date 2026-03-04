from django.contrib.auth.models import User
from django.test import TestCase

from tasks.models import Category, Task


class TaskModelTests(TestCase):
    def test_task_create_model(self):
        user = User.objects.create_user(username="u1", password="pass12345")
        category = Category.objects.create(user=user, name="AI")

        task = Task.objects.create(user=user, title="Test", category=category)

        self.assertEqual(task.title, "Test")
        self.assertEqual(task.user.username, "u1")
