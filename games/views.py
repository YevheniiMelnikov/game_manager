from rest_framework import generics
from .models import Company, Participant, Game, GameSession, GameResults
from .serializers import (
    CompanySerializer,
    ParticipantSerializer,
    GameSerializer,
    GameSessionSerializer,
    GameResultsSerializer,
)


class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ParticipantListCreateView(generics.ListCreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameSessionListCreateView(generics.ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer


class GameResultsListCreateView(generics.ListCreateAPIView):
    queryset = GameResults.objects.all()
    serializer_class = GameResultsSerializer
