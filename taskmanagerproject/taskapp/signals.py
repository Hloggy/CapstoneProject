from datetime import timedelta
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils import timezone
from .models import Task, Notification, TaskHistory

TASK_HISTORY_TRACK_FIELDS = ["title", "description", "priority", "status", "due_date", "completed_at"]

def _subset_task_dict(task: "Task"):
    data = model_to_dict(task, fields=TASK_HISTORY_TRACK_FIELDS)
    for k, v in data.items():
        if hasattr(v, "isoformat"):
            data[k] = v.isoformat()
    return data

@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance: Task, **kwargs):
    if instance.pk:
        try:
            prev = Task.objects.get(pk=instance.pk)
            instance._previous_state = _subset_task_dict(prev)
        except Task.DoesNotExist:
            instance._previous_state = None
    else:
        instance._previous_state = None

@receiver(post_save, sender=Task)
def task_post_save_history_and_notifications(sender, instance: Task, created, **kwargs):
    user = instance.user
    new_state = _subset_task_dict(instance)
    old_state = getattr(instance, "_previous_state", None)
    changes = {}

    if created:
        TaskHistory.objects.create(user=user, task=instance, action="created", changes=new_state)
        Notification.objects.create(user=user, task=instance, message=f"Task '{instance.title}' was created.")
        if instance.due_date and instance.due_date <= timezone.now() + timedelta(hours=24):
            Notification.objects.create(
                user=user, task=instance,
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
                user=user, task=instance,
                message=f"Task '{instance.title}' status changed: {old_status} ➜ {new_status}."
            )
        if "due_date" in changes and instance.due_date:
            Notification.objects.create(
                user=user, task=instance,
                message=f"Task '{instance.title}' due date updated to {instance.due_date:%Y-%m-%d %H:%M}."
            )

    if instance.status == "done" and instance.completed_at is None:
    
        Task.objects.filter(pk=instance.pk, completed_at__isnull=True).update(completed_at=timezone.now())
        Notification.objects.create(user=user, task=instance, message=f"Task '{instance.title}' marked completed.")

@receiver(pre_delete, sender=Task)
def task_pre_delete_history(sender, instance: Task, **kwargs):
    TaskHistory.objects.create(user=instance.user, task=instance, action="deleted", changes=_subset_task_dict(instance))
    Notification.objects.create(user=instance.user, task=instance, message=f"Task '{instance.title}' was deleted.")

