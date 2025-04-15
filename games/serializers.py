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


ROLE_CHOICES = [("SuperAdmin", "SuperAdmin"), ("CompanyAdmin", "CompanyAdmin"), ("Participant", "Participant")]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    company_id = serializers.IntegerField(required=False)

    @staticmethod
    def validate_username(value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, data):
        if data.get("role") == "CompanyAdmin" and not data.get("company_id"):
            raise serializers.ValidationError({"company_id": "This field is required for CompanyAdmin role."})
        return data

    def create(self, validated_data):
        company = None
        if validated_data.get("company_id"):
            from .models import Company

            company = Company.objects.get(id=validated_data["company_id"])
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            company=company,
            role=validated_data["role"],
        )
        group, _ = Group.objects.get_or_create(name=validated_data["role"])
        user.groups.add(group)
        return user
