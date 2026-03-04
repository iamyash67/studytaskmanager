from .models import CompletedTask


def complete_task_and_archive(*, task):
    """Move a pending task into the completed archive."""
    user = task.user

    completed = CompletedTask.objects.create(
        user=user,
        title=task.title,
        category=task.category.name if task.category else '',
        created_at=task.created_at,
        deadline=task.deadline,
    )
    task.delete()
    return completed
