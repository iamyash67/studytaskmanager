from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Per-user categories for organising tasks by subject."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Task(models.Model):
    """Active tasks owned by a user."""
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    title = models.CharField(max_length=255)
    deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    estimated_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Estimated hours to complete the task',
    )
    in_progress = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['deadline', 'created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.deadline:
            return self.deadline < timezone.now().date()
        return False


class CompletedTask(models.Model):
    """Archive of tasks that have been marked as completed."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_tasks')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.title} (completed)"
