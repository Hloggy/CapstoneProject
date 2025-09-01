from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, NotificationViewSet

# DRF Router automatically generates /tasks/ and /notifications/ endpoints
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),  # this will expose /api/tasks/ and /api/notifications/
]
