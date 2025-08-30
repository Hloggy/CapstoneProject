from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "first_name", "last_name"]
        read_only_fields = ["id", "date_joined"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class TaskSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "user_id",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["id", "user_id", "created_at", "completed_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "task", "message", "is_read", "created_at"]
        read_only_fields = ["id", "message", "created_at", "task"]

