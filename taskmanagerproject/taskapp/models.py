from django.db import models
from django.contrib.auth.models import AbstractUser

PRIORITY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]
STATUS_CHOICES = [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    def __str__(self): 
        return self.username


class Task(models.Model):
    user = models.ForeignKey("taskapp.User", on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["completed_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user})"

class Notification(models.Model):
    user = models.ForeignKey("taskapp.User", on_delete=models.CASCADE, related_name="notifications")
    task = models.ForeignKey("taskapp.Task", on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notif to {self.user}: {self.message[:30]}"

class TaskHistory(models.Model):
    ACTION_CHOICES = [("created", "Created"), ("updated", "Updated"), ("deleted", "Deleted")]
    user = models.ForeignKey("taskapp.User", on_delete=models.CASCADE, related_name="task_histories")
    task = models.ForeignKey("taskapp.Task", on_delete=models.CASCADE, related_name="histories")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"History({self.action}) for Task {self.task_id} by {self.user}"

