from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.db.models.signals import pre_save, pre_delete, post_save

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]
STATUS_CHOICES = [
    ("todo", "To Do"),
    ("in_progress", "In Progress"),
    ("done", "Done"),
]


TASK_HISTORY_TRACK_FIELDS = ["title", "description", "priority", "status", "due_date", "completed_at"]


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
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
    ]

    user = models.ForeignKey("taskapp.User", on_delete=models.CASCADE, related_name="task_histories")
    task = models.ForeignKey("taskapp.Task", on_delete=models.CASCADE, related_name="histories")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"History({self.action}) for Task {self.task_id} by {self.user}"


def _subset_task_dict(task: "Task") -> dict:
    
    data = model_to_dict(task, fields=TASK_HISTORY_TRACK_FIELDS)
    for k, v in data.items():
        if hasattr(v, "isoformat"):
            data[k] = v.isoformat()
    return data


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance: "Task", **kwargs):
    
    if instance.pk:
        try:
            prev = Task.objects.get(pk=instance.pk)
            instance._previous_state = _subset_task_dict(prev)
        except Task.DoesNotExist:
            instance._previous_state = None
    else:
        instance._previous_state = None

    
    if instance.status == "done" and instance.completed_at is None:
        instance.completed_at = timezone.now()


@receiver(post_save, sender=Task)
def task_post_save_history_and_notifications(sender, instance: "Task", created: bool, **kwargs):

    user = instance.user
    new_state = _subset_task_dict(instance)
    old_state = getattr(instance, "_previous_state", None)
    changes = {}

    if created:
        
        TaskHistory.objects.create(user=user, task=instance, action="created", changes=new_state)
        
        Notification.objects.create(
            user=user,
            task=instance,
            message=f"Task '{instance.title}' was created."
        )
        if instance.due_date and instance.due_date <= timezone.now() + timedelta(hours=24):
            Notification.objects.create(
                user=user,
                task=instance,
                message=f"Task '{instance.title}' is due soon ({instance.due_date:%Y-%m-%d %H:%M})."
            )
        return

    
    if old_state is not None:
        for f in TASK_HISTORY_TRACK_FIELDS:
            if old_state.get(f) != new_state.get(f):
                changes[f] = [old_state.get(f), new_state.get(f)]

    if changes:
        TaskHistory.objects.create(user=user, task=instance, action="updated", changes=changes)

        if "status" in changes:
            old_status, new_status = changes["status"]
            Notification.objects.create(
                user=user,
                task=instance,
                message=f"Task '{instance.title}' status changed: {old_status} ➜ {new_status}."
            )

        if "due_date" in changes and instance.due_date:
            Notification.objects.create(
                user=user,
                task=instance,
                message=f"Task '{instance.title}' due date updated to {instance.due_date:%Y-%m-%d %H:%M}."
            )

        if "completed_at" in changes and instance.status == "done":
            Notification.objects.create(
                user=user,
                task=instance,
                message=f"Task '{instance.title}' marked completed."
            )


@receiver(pre_delete, sender=Task)
def task_pre_delete_history(sender, instance: "Task", **kwargs):
    TaskHistory.objects.create(
        user=instance.user,
        task=instance,
        action="deleted",
        changes=_subset_task_dict(instance),
    )
    Notification.objects.create(
        user=instance.user,
        task=instance,
        message=f"Task '{instance.title}' was deleted."
    )
