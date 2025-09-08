import django_filters
from django.utils import timezone
from datetime import timedelta
from django.db.models import Exists, OuterRef
from .models import Task, Notification, TaskHistory


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="iexact")

    created_between = django_filters.DateTimeFromToRangeFilter(field_name="created_at")
    due_between = django_filters.DateTimeFromToRangeFilter(field_name="due_date")
    completed_between = django_filters.DateTimeFromToRangeFilter(field_name="completed_at")

    is_completed = django_filters.BooleanFilter(method="filter_is_completed")

    
    overdue = django_filters.BooleanFilter(method="filter_overdue", help_text="True = due_date < now and not completed")
    due_within_hours = django_filters.NumberFilter(method="filter_due_within_hours", help_text="Return tasks due within N hours")
    has_notifications = django_filters.BooleanFilter(method="filter_has_notifications")

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "created_between",
            "due_between",
            "completed_between",
            "is_completed",
            "overdue",
            "due_within_hours",
            "has_notifications",
        ]

    def filter_is_completed(self, queryset, name, value):
        if value:
            return queryset.exclude(completed_at__isnull=True)
        return queryset.filter(completed_at__isnull=True)

    def filter_overdue(self, queryset, name, value):
        now = timezone.now()
        if value is True:
            return queryset.filter(due_date__lt=now, completed_at__isnull=True)
        if value is False:
            return queryset.exclude(due_date__lt=now, completed_at__isnull=True)
        return queryset

    def filter_due_within_hours(self, queryset, name, value):
        
        try:
            hours = int(value)
        except (TypeError, ValueError):
            return queryset
        now = timezone.now()
        window = now + timedelta(hours=hours)
        return queryset.filter(due_date__gte=now, due_date__lte=window, completed_at__isnull=True)

    def filter_has_notifications(self, queryset, name, value):
        notif_qs = Notification.objects.filter(task=OuterRef("pk"))
        qs = queryset.annotate(_has_notifs=Exists(notif_qs))
        if value is True:
            return qs.filter(_has_notifs=True)
        if value is False:
            return qs.filter(_has_notifs=False)
        return queryset


class NotificationFilter(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter(field_name="is_read")
    created_between = django_filters.DateTimeFromToRangeFilter(field_name="created_at")
    task = django_filters.NumberFilter(field_name="task__id")

    class Meta:
        model = Notification
        fields = ["is_read", "task", "created_between"]


class TaskHistoryFilter(django_filters.FilterSet):
    action = django_filters.CharFilter(field_name="action", lookup_expr="iexact")  
    task = django_filters.NumberFilter(field_name="task__id")
    created_between = django_filters.DateTimeFromToRangeFilter(field_name="created_at")

    class Meta:
        model = TaskHistory
        fields = ["action", "task", "created_between"]

