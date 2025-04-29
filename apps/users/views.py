from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.forms import RegistrationForm
from apps.users.serializers import RegisterSerializer, UserSerializer
from apps.users.services import UserService

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.register_and_login(
            request,
            **serializer.validated_data,
        )
        return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = UserService.authenticate_and_login(
            request,
            username=username,
            password=password,
        )
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


class UserRegistrationView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, self.template_name, {"form": form})

        UserService.register_and_login(request, **form.cleaned_data)
        messages.success(request, "Registration successful")
        return redirect("register_success")


class RegistrationSuccessView(View):
    template_name = "users/register_success.html"

    def get(self, request):
        return render(request, self.template_name)
