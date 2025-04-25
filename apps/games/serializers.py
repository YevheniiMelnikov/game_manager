from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Company, Game, GameSession, GameResults

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class GameSessionSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = GameSession
        fields = "__all__"


class GameResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameResults
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "company", "role")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    company_id = serializers.IntegerField(write_only=True, required=False)

    def validate_company_id(self, value):
        if self.initial_data.get("role") == "CompanyAdmin" and not value:
            raise serializers.ValidationError("This field is required for CompanyAdmin role.")
        return value

    def create(self, validated_data):
        company_id = validated_data.pop("company_id", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        if company_id:
            user.company_id = company_id
        user.save()
        group, _ = Group.objects.get_or_create(name=user.role)
        user.groups.add(group)
        return user

    class Meta:
        model = User
        fields = ("username", "password", "role", "company_id")
