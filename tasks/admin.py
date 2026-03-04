from django.contrib import admin
from .models import Task, CompletedTask, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'deadline', 'in_progress', 'created_at')
    list_filter = ('user', 'in_progress', 'category')

@admin.register(CompletedTask)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'completed_at')
    list_filter = ('user',)
