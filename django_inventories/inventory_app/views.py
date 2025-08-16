from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import InventoryItem, User, InventoryChangeLog, Category
from .serializers import (
    InventoryItemSerializer, 
    UserSerializer, 
    InventoryChangeLogSerializer,
    CategorySerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsOwnerOrAdmin
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import render

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'quantity']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        queryset = InventoryItem.objects.filter(created_by=user)
        
        # Filter for low stock items
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock is not None:
            try:
                threshold = int(low_stock)
                queryset = queryset.filter(quantity__lt=threshold)
            except ValueError:
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        change = request.data.get('change', 0)
        notes = request.data.get('notes', '')
        
        try:
            change = int(change)
        except ValueError:
            return Response(
                {'error': 'Change must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        previous_quantity = item.quantity
        new_quantity = previous_quantity + change
        
        if new_quantity < 0:
            return Response(
                {'error': 'Resulting quantity cannot be negative'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item.quantity = new_quantity
        item.save()
        
        # Log the change
        action_type = 'STOCK_IN' if change > 0 else 'STOCK_OUT'
        InventoryChangeLog.objects.create(
            item=item,
            user=request.user,
            action=action_type,
            quantity_change=change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            notes=notes
        )
        
        return Response(
            InventoryItemSerializer(item).data,
            status=status.HTTP_200_OK
        )

class InventoryChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryChangeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'item']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        user = self.request.user
        return InventoryChangeLog.objects.filter(user=user)

def index(request):
    return render(request, 'inventory_app/index.html')

