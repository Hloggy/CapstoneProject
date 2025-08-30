import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    priority = django_filters.CharFilter(field_name="priority", lookup_expr="iexact")

    created_between = django_filters.DateFromToRangeFilter(field_name="created_at")
    due_between = django_filters.DateFromToRangeFilter(field_name="due_date")
    completed_between = django_filters.DateFromToRangeFilter(field_name="completed_at")

    is_completed = django_filters.BooleanFilter(method="filter_is_completed")

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
        ]

    def filter_is_completed(self, queryset, name, value):
        if value:
            return queryset.exclude(completed_at__isnull=True)
        return queryset.filter(completed_at__isnull=True)

