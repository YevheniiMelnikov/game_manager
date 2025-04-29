import pytest
from pytest_factoryboy import register

from apps.users.tests.factories import UserFactory

register(UserFactory)


@pytest.fixture
def user_data() -> dict:
    return {
        "username": "new_user",
        "password": "strongpass123",
        "role": "Participant",
    }
