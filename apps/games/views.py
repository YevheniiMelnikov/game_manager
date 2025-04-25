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
USER_TABLE = User._meta.db_table
GROUP_TABLE = Group._meta.db_table
LINK_TABLE = f"{USER_TABLE}_groups"
LINK_USER_COL = f"{User._meta.model_name}_id"


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
                    f"INSERT INTO {LINK_TABLE} ({LINK_USER_COL}, group_id) "
                    "SELECT %s, id FROM {group_table} WHERE name=%s".format(group_table=GROUP_TABLE),
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
        return render(request, "games/register.html", {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
            return render(request, "games/register.html", {"form": form})

        data = form.cleaned_data

        with transaction.atomic():
            company = None
            if data.get("company_id"):
                company, _ = Company.objects.get_or_create(
                    id=data["company_id"], defaults={"name": f"Company {data['company_id']}"}
                )
            else:
                company, _ = Company.objects.get_or_create(name="Default Company")

            user = User.objects.create_user(
                username=data["username"],
                password=data["password"],
                role=data["role"],
                company=company,
                is_active=True,
            )

            group, _ = Group.objects.get_or_create(name=data["role"])

            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO {LINK_TABLE} ({LINK_USER_COL}, group_id) VALUES (%s, %s)",
                    [user.id, group.id],
                )

        login(request, user)
        messages.success(request, "Registration successful")
        return redirect("register_success")


class RegistrationSuccessView(View):
    def get(self, request):
        return render(request, "games/register_success.html")
