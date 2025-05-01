import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_view_success(client, user_data):
    url = reverse("api_register")
    response = client.post(url, user_data)

    assert response.status_code == 201
    assert "id" in response.data
    assert response.data["username"] == user_data["username"]
    assert response.data["role"] == user_data["role"]

    user = User.objects.get(username=user_data["username"])
    assert user.role == "Participant"


@pytest.mark.django_db
def test_login_view_success(client, user_factory):
    user = user_factory(username="test_login_user")
    user.set_password("strongpass123")
    user.save()

    url = reverse("api_login")
    response = client.post(url, {"username": user.username, "password": "strongpass123"})

    assert response.status_code == 200
    assert response.data.get("message") == "Login successful"
