from rest_framework import serializers
from .models import Company, Participant, Game, GameSession, GameResults


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # отображает имя пользователя
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Participant
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class GameSessionSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True)

    class Meta:
        model = GameSession
        fields = "__all__"


class GameResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameResults
        fields = "__all__"
