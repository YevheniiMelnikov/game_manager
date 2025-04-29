from typing import Optional, TYPE_CHECKING

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpRequest

from apps.users.models import Company

if TYPE_CHECKING:
    from apps.users.models import User
else:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class UserService:
    @staticmethod
    def _get_or_create_company(company_id: Optional[int]) -> Company:
        if company_id:
            company, _ = Company.objects.get_or_create(id=company_id, defaults={"name": f"Company {company_id}"})
        else:
            company, _ = Company.objects.get_or_create(name="Default Company")
        return company

    @staticmethod
    def _attach_group(user: "User", role: str) -> None:
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

    @classmethod
    @transaction.atomic
    def create_user(
        cls,
        *,
        username: str,
        password: str,
        role: str,
        company_id: Optional[int] = None,
    ) -> "User":
        company = cls._get_or_create_company(company_id)
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            company=company,
            is_active=True,
        )
        cls._attach_group(user, role)
        return user

    @classmethod
    def register_and_login(
        cls,
        request: HttpRequest,
        *,
        username: str,
        password: str,
        role: str,
        company_id: Optional[int] = None,
    ) -> "User":
        user = cls.create_user(
            username=username,
            password=password,
            role=role,
            company_id=company_id,
        )
        login(request, user)
        return user

    @staticmethod
    def authenticate_and_login(request: HttpRequest, *, username: str, password: str) -> Optional["User"]:
        if not username or not password:
            return None
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
        return user
