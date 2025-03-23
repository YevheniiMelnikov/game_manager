from rest_framework import serializers
from .models import Game, GameSession, GameResults


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = "__all__"


class GameResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameResults
        fields = "__all__"
