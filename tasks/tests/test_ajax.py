from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tasks.models import Category, CompletedTask, Task


class AjaxTaskCompletionTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")
        self.cat = Category.objects.create(user=self.u1, name="AI")

    def test_ajax_complete_moves_task(self):
        task = Task.objects.create(user=self.u1, title="Complete me", category=self.cat)
        self.client.login(username="u1", password="pass12345")

        url = reverse("task_complete_ajax", args=[task.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        self.assertTrue(CompletedTask.objects.filter(user=self.u1, title="Complete me").exists())

    def test_ajax_complete_denies_other_user_task(self):
        task = Task.objects.create(user=self.u2, title="Not yours")
        self.client.login(username="u1", password="pass12345")

        url = reverse("task_complete_ajax", args=[task.pk])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        self.assertEqual(response.status_code, 404)
