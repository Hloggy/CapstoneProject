from rest_framework import serializers
from .models import InventoryItem, User, InventoryChangeLog, Category
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class InventoryItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True,
        required=False,
        allow_null=True
    )
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'quantity', 'price', 
            'category', 'category_id', 'created_by', 
            'date_added', 'last_updated'
        ]
        read_only_fields = ['created_by', 'date_added', 'last_updated']
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

class InventoryChangeLogSerializer(serializers.ModelSerializer):
    item = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    
    class Meta:
        model = InventoryChangeLog
        fields = [
            'id', 'item', 'user', 'action', 'quantity_change',
            'previous_quantity', 'new_quantity', 'timestamp', 'notes'
        ]
        read_only_fields = fields

