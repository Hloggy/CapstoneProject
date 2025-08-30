from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Task, Notification

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "email", "date_joined", "is_staff")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "priority", "status", "due_date", "created_at", "completed_at")
    list_filter = ("priority", "status")
    search_fields = ("title", "description")
    ordering = ("-created_at",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "message", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("message",)
    ordering = ("-created_at",)

