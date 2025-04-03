from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Company, Participant, Game, GameSession, GameResults


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Participant
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


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Participant.ROLES)
    company_id = serializers.IntegerField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate(self, data):
        if data.get("role") == "CompanyAdmin":
            if not data.get("company_id"):
                raise serializers.ValidationError({"company_id": "This field is required for CompanyAdmin role."})
            if not Company.objects.filter(id=data["company_id"]).exists():
                raise serializers.ValidationError({"company_id": "Company with given id does not exist."})
        return data

    def create(self, validated_data):
        company = None
        if validated_data.get("company_id"):
            company = Company.objects.get(id=validated_data["company_id"])
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        Participant.objects.create(user=user, role=validated_data["role"], company=company)
        group, _ = Group.objects.get_or_create(name=validated_data["role"])
        user.groups.add(group)
        return user
