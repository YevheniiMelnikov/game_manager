import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory

register(UserFactory)


@pytest.fixture
def user_data() -> dict:
    return {
        "username": "new_user",
        "password": "strongpass123",
        "role": "Participant",
    }


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture(autouse=True, scope="session")
def django_db_setup():  # to enable DB access in session-scoped fixtures like init_groups
    pass


@pytest.fixture(autouse=True)
@pytest.mark.django_db(transaction=True)
def init_groups():
    call_command("migrate", "--noinput")
    if not Group.objects.filter(name="Participant").exists():
        call_command("init_roles")
