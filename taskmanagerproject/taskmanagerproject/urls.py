"""
URL configuration for taskmanagerproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taskapp.views import (
    TaskViewSet,
    NotificationViewSet,
    TaskHistoryViewSet,
    RegisterView,
    HomeView,
    DashboardView,
    login_view,
    logout_view,
    signup_view,
    create_task, 
    edit_task, 
    delete_task, 
    toggle_done,
)
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taskapp.views import (
    TaskViewSet, NotificationViewSet, TaskHistoryViewSet,
    RegisterView, HomeView, DashboardView,
    login_view, logout_view, signup_view,
    create_task, edit_task, delete_task, toggle_done,  # ← add
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"task-history", TaskHistoryViewSet, basename="taskhistory")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("register/", RegisterView.as_view(), name="register"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]


try:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

    urlpatterns += [
        path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    ]
except Exception:
    
    pass



router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"task-history", TaskHistoryViewSet, basename="taskhistory")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("register/", RegisterView.as_view(), name="register"),

    # HTML
    path("tasks/create/", create_task, name="task_create"),
    path("tasks/<int:pk>/edit/", edit_task, name="task_edit"),
    path("tasks/<int:pk>/delete/", delete_task, name="task_delete"),
    path("tasks/<int:pk>/toggle-done/", toggle_done, name="task_toggle_done"),

    # API
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
