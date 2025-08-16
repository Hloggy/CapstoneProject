from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryItemViewSet,
    UserViewSet,
    InventoryChangeLogViewSet,
    CategoryViewSet,
    CustomTokenObtainPairView,
    index
)

router = DefaultRouter()
router.register(r'items', InventoryItemViewSet, basename='item')
router.register(r'users', UserViewSet, basename='user')
router.register(r'history', InventoryChangeLogViewSet, basename='history')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', index, name='index'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/', include(router.urls)),
]

