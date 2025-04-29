import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db(transaction=True)
def test_register_view_success(user_data) -> None:
    client = APIClient()
    url = reverse("api_register")
    response = client.post(url, user_data)

    assert response.status_code == 201
    assert "message" in response.data
    assert response.data["message"] == "User registered"


@pytest.mark.django_db(transaction=True)
def test_login_view_success(user_factory) -> None:
    user = user_factory(username="test_login_user")
    user.set_password("strongpass123")
    user.save()

    client = APIClient()
    url = reverse("api_login")
    response = client.post(url, {"username": user.username, "password": "strongpass123"})

    assert response.status_code == 200
    assert "message" in response.data
    assert response.data["message"] == "Login successful"
