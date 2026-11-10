from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.Serializer):
    phone = serializers.RegexField(r"^\+251[79]\d{8}$")
    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Could not register with these details.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, data):
        # role/standing are never taken from input (mass-assignment guard, T2)
        return User.objects.create_user(
            phone=data["phone"], password=data["password"],
            full_name=data["full_name"], email=data.get("email"))
