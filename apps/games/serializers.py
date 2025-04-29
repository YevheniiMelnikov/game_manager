from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Game, GameSession, GameResults, Company

User = get_user_model()


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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
