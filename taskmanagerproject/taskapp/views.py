from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Task, Notification, TaskHistory
from .permissions import IsOwner
from .serializers import (
    TaskSerializer,
    NotificationSerializer,
    RegisterSerializer,
    TaskHistorySerializer,
)
from .filters import TaskFilter, NotificationFilter, TaskHistoryFilter
from .forms import LoginForm, SignupForm, TaskForm


class RegisterView(CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = RegisterSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "completed_at", "priority", "status"]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "done"
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at"])
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NotificationFilter
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        updated = qs.update(is_read=True)
        return Response({"updated": updated}, status=status.HTTP_200_OK)


class TaskHistoryViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = TaskHistorySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TaskHistoryFilter
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return TaskHistory.objects.filter(user=self.request.user).select_related("task")


class HomeView(TemplateView):
    template_name = "landing.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "login_form": LoginForm(),
            "signup_form": SignupForm(),
        })


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.cleaned_data["user"])
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect("dashboard")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard.html"

    def get(self, request):
        tasks = Task.objects.filter(user=request.user).order_by("-created_at")
        notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:20]
        form = TaskForm()
        return render(request, self.template_name, {
            "tasks": tasks,
            "notifications": notifications,
            "form": form,
        })


@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.success(request, "Task created.")
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(request, "task_form.html", {"form": form, "title": "Create Task"})


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            return redirect("dashboard")
    else:
        form = TaskForm(instance=task)
    return render(request, "task_form.html", {"form": form, "title": "Edit Task"})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("dashboard")
    return render(request, "confirm_delete.html", {"object": task})


@login_required
def toggle_done(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.status = "done" if task.status != "done" else "todo"
        task.save(update_fields=["status"])
        messages.info(request, f"Task marked {'done' if task.status == 'done' else 'to do'}.")
    return redirect("dashboard")
