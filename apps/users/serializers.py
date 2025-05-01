from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.services import UserService

User = get_user_model()

if TYPE_CHECKING:
    from apps.users.models import User as UserType


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "company", "role")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False)

    def validate_company_id(self, value: int) -> int:
        if self.initial_data.get("role") == "CompanyAdmin" and not value:
            raise serializers.ValidationError("Field 'company_id' is required for CompanyAdmin role")
        return value

    def create(self, validated_data: dict) -> "UserType":
        company_id = validated_data.pop("company_id", None)
        password = validated_data.pop("password")
        return UserService.create_user(
            username=validated_data["username"],
            password=password,
            role=validated_data["role"],
            company_id=company_id,
        )

    class Meta:
        model = User
        fields = ("username", "password", "role", "company_id")
