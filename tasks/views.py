import calendar
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Count

from .models import Task, CompletedTask, Category
from .forms import RegisterForm, LoginForm, TaskForm, CategoryForm
from .services import complete_task_and_archive

PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}


# ─── Authentication ───────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'tasks/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    category_filter = request.GET.get('category', '')
    tasks = Task.objects.filter(user=request.user).select_related('category')

    if category_filter:
        tasks = tasks.filter(category__id=category_filter)

    today = now().date()
    soon = today + timedelta(days=3)
    pending_tasks = list(tasks.filter(in_progress=True))
    pending_tasks.sort(key=lambda t: (
        PRIORITY_ORDER.get(t.priority, 1),
        t.deadline is None,
        t.deadline or t.created_at.date(),
    ))
    completed_tasks = CompletedTask.objects.filter(user=request.user).order_by('-completed_at')
    categories = Category.objects.filter(user=request.user)
    pending_count = len(pending_tasks)
    completed_count = completed_tasks.count()
    total = pending_count + completed_count
    progress = int((completed_count / total) * 100) if total > 0 else 0

    dates = list(
        CompletedTask.objects.filter(user=request.user)
        .values_list('completed_at__date', flat=True)
        .distinct()
        .order_by('-completed_at__date')[:60]
    )
    dates_set = set(dates)
    streak = 0
    day = today
    while day in dates_set:
        streak += 1
        day -= timedelta(days=1)

    start_week = today - timedelta(days=today.weekday())
    weekly_hours = (
        Task.objects.filter(user=request.user, in_progress=True, deadline__gte=start_week)
        .exclude(estimated_hours__isnull=True)
    )
    total_weekly_hours = sum(t.estimated_hours for t in weekly_hours if t.estimated_hours)

    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'categories': categories,
        'selected_category': category_filter,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'progress': progress,
        'today': today,
        'soon': soon,
        'streak': streak,
        'total_weekly_hours': total_weekly_hours,
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def weekly_stats_json(request):
    """
    Returns completed tasks per day for last 7 days for Chart.js
    """
    today = now().date()
    start = today - timedelta(days=6)

    qs = (
        CompletedTask.objects
        .filter(user=request.user, completed_at__date__gte=start, completed_at__date__lte=today)
        .annotate(day=TruncDate('completed_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    counts_by_day = {row['day']: row['count'] for row in qs}

    labels = []
    values = []
    for i in range(7):
        day = start + timedelta(days=i)
        labels.append(day.strftime('%a'))
        values.append(counts_by_day.get(day, 0))

    return JsonResponse({'labels': labels, 'values': values})


@login_required
def calendar_view(request):
    today = now().date()
    year = int(request.GET.get('y', today.year))
    month = int(request.GET.get('m', today.month))
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    month_tasks = Task.objects.filter(
        user=request.user,
        in_progress=True,
        deadline__year=year,
        deadline__month=month,
    ).select_related('category')

    tasks_by_day = {}
    for task in month_tasks:
        tasks_by_day.setdefault(task.deadline.day, []).append(task)

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)
    prev_year, prev_month = year, month - 1
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    next_year, next_month = year, month + 1
    if next_month > 12:
        next_month = 1
        next_year += 1

    return render(request, 'tasks/calendar.html', {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'weeks': weeks,
        'tasks_by_day': tasks_by_day,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    })


# ─── Tasks ────────────────────────────────────────────────────────────────────

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.user, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm(request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.user, request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully.')
            return redirect('dashboard')
    else:
        form = TaskForm(request.user, instance=task)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('dashboard')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        completed = complete_task_and_archive(task=task)
        messages.success(request, f'"{completed.title}" marked as completed! Well done 🎉')
        return redirect('dashboard')

    return render(request, 'tasks/task_complete_confirm.html', {'task': task})


@require_POST
@login_required
def task_complete_ajax(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    completed = complete_task_and_archive(task=task)

    pending_count = Task.objects.filter(user=request.user, in_progress=True).count()
    completed_count = CompletedTask.objects.filter(user=request.user).count()

    return JsonResponse({
        "ok": True,
        "message": f'"{completed.title}" marked as completed!',
        "completed_task": {
            "title": completed.title,
            "category": completed.category,
            "completed_at": completed.completed_at.strftime("%d %b %Y"),
        },
        "counts": {
            "pending": pending_count,
            "completed": completed_count,
        },
    })


# ─── Categories ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            try:
                category.save()
                messages.success(request, f'Category "{category.name}" added.')
                return redirect('category_list')
            except Exception:
                form.add_error('name', 'You already have a category with this name.')

    return render(request, 'tasks/category_list.html', {
        'categories': categories,
        'form': form,
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('category_list')

    return render(request, 'tasks/category_confirm_delete.html', {'category': category})


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    task_count = Task.objects.filter(user=request.user).count()
    completed_count = CompletedTask.objects.filter(user=request.user).count()
    category_count = Category.objects.filter(user=request.user).count()

    return render(request, 'tasks/profile.html', {
        'task_count': task_count,
        'completed_count': completed_count,
        'category_count': category_count,
    })
