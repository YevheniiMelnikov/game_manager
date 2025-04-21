from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction, connection
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import Group

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Company, Game, GameSession, GameResults
from .serializers import (
    CompanySerializer,
    GameSerializer,
    GameSessionSerializer,
    GameResultsSerializer,
    UserSerializer,
    RegisterSerializer,
)
from .forms import RegistrationForm

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer


class GameResultsViewSet(viewsets.ModelViewSet):
    queryset = GameResults.objects.all()
    serializer_class = GameResultsSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO auth_user_groups (user_id, group_id) SELECT %s, id FROM auth_group WHERE name=%s",
                    [user.id, user.role],
                )
        login(request, user)
        return Response({"message": "User registered and logged in"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


class UserRegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "games/register.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
            return render(request, "games/register.html", {"form": form})
        data = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                password=data["password"],
                role=data["role"],
                company_id=data.get("company_id"),
                is_active=True,
            )
            group, _ = Group.objects.get_or_create(name=data["role"])
            user.groups.add(group)
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO auth_user (username, password, is_active, date_joined) VALUES (%s, %s, %s, NOW())",
                    [data["username"], user.password, True],
                )
                cursor.execute(
                    "SELECT id FROM auth_user WHERE username=%s ORDER BY date_joined DESC LIMIT 1",
                    [data["username"]],
                )
                raw_user_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO auth_group (name) SELECT %s WHERE NOT EXISTS (SELECT 1 FROM auth_group WHERE name=%s)",
                    [data["role"], data["role"]],
                )
                cursor.execute("SELECT id FROM auth_group WHERE name=%s", [data["role"]])
                raw_group_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, %s)",
                    [raw_user_id, raw_group_id],
                )
        login(request, user)
        messages.success(request, "Registration successful")
        return redirect("register_success")


class RegistrationSuccessView(View):
    def get(self, request):
        return render(request, "games/register_success.html")
