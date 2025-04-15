from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, get_user_model
from .models import Company, Game, GameSession, GameResults
from .serializers import (
    CompanySerializer,
    GameSerializer,
    GameSessionSerializer,
    GameResultsSerializer,
    RegisterSerializer,
    UserSerializer,
)
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction, connection
from django.conf import settings

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


class UserRegistrationView(View):
    def get(self, request):
        return render(request, "games/register.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")
        company_id = request.POST.get("company_id")

        errors = {}
        if not username:
            errors["username"] = "Username is required."
        if not password:
            errors["password"] = "Password is required."
        if role not in ["SuperAdmin", "CompanyAdmin", "Participant"]:
            errors["role"] = "Invalid role selected."
        if role == "CompanyAdmin" and not company_id:
            errors["company_id"] = "Company ID is required for CompanyAdmin role."

        if errors:
            return render(request, "games/register.html", {"errors": errors})

        from django.contrib.auth.hashers import make_password

        hashed_password = make_password(password)
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO games_customuser (username, password, role, company_id, is_active, date_joined)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                        [username, hashed_password, role, company_id if company_id else None, True],
                    )
                    if settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
                        cursor.execute("SELECT last_insert_rowid()")
                    else:
                        cursor.execute("SELECT currval(pg_get_serial_sequence('games_customuser','id'))")
                    user_id = cursor.fetchone()[0]
                    cursor.execute("SELECT id FROM auth_group WHERE name = %s", [role])
                    group = cursor.fetchone()
                    if not group:
                        cursor.execute("INSERT INTO auth_group (name) VALUES (%s)", [role])
                        if settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
                            cursor.execute("SELECT last_insert_rowid()")
                        else:
                            cursor.execute("SELECT currval(pg_get_serial_sequence('auth_group','id'))")
                        group_id = cursor.fetchone()[0]
                    else:
                        group_id = group[0]
                    cursor.execute(
                        "INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, %s)", [user_id, group_id]
                    )
            from django.contrib.auth import authenticate, login

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            return redirect("register_success")
        except Exception as e:
            errors["non_field"] = str(e)
            return render(request, "games/register.html", {"errors": errors})


class RegistrationSuccessView(View):
    def get(self, request):
        return render(request, "games/register_success.html")
