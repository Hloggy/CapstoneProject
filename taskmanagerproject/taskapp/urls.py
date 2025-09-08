from django.urls import path, include
from .views import (
    HomeView,
    DashboardView,
    login_view,
    logout_view,
    signup_view,
    create_task,
    edit_task,
    delete_task,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),

    path("tasks/new/", create_task, name="task_create"),
    path("tasks/<int:pk>/edit/", edit_task, name="task_edit"),
    path("tasks/<int:pk>/delete/", delete_task, name="task_delete"),

    path("", include("taskapp.urls")),  
]
