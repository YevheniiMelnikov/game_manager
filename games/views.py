from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from .models import Company, Participant, Game, GameSession, GameResults
from .serializers import (
    CompanySerializer,
    ParticipantSerializer,
    GameSerializer,
    GameSessionSerializer,
    GameResultsSerializer,
    RegisterSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")  # TODO: REMOVE IN PROD
class CompanyListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # TODO: CHANGE TO HAS-API-KEY
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


@method_decorator(csrf_exempt, name="dispatch")
class ParticipantListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


@method_decorator(csrf_exempt, name="dispatch")
class GameListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Game.objects.all()
    serializer_class = GameSerializer


@method_decorator(csrf_exempt, name="dispatch")
class GameSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer


@method_decorator(csrf_exempt, name="dispatch")
class GameResultsListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = GameResults.objects.all()
    serializer_class = GameResultsSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({"message": "User registered and logged in"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
