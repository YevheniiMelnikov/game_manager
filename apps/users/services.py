from typing import Optional, TYPE_CHECKING

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import HttpRequest
from loguru import logger

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
            company, created = Company.objects.get_or_create(id=company_id, defaults={"name": f"Company {company_id}"})
        else:
            company, created = Company.objects.get_or_create(name="Default Company")
        if created:
            logger.info(f"Created new company: {company}")
        return company

    @staticmethod
    def _attach_group(user: "User", role: str) -> None:
        try:
            group = Group.objects.get(name=role)
        except Group.DoesNotExist:
            logger.error(f"Tried to assign non-existent group: '{role}'")
            raise ValueError(f"Group '{role}' is not defined.")
        user.groups.add(group)
        logger.debug(f"Attached user '{user.username}' to group '{role}'")

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
        logger.info(f"Creating user '{username}' with role '{role}' and company_id={company_id}")
        company = cls._get_or_create_company(company_id)
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            company=company,
            is_active=True,
        )
        cls._attach_group(user, role)
        logger.success(f"User created: {user.username} (ID: {user.id})")
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
        logger.info(f"User '{user.username}' logged in after registration")
        return user

    @staticmethod
    def authenticate_and_login(request: HttpRequest, *, username: str, password: str) -> Optional["User"]:
        if not username or not password:
            logger.warning("Attempted login with missing credentials")
            return None
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            logger.info(f"User '{user.username}' logged in successfully")
        else:
            logger.warning(f"Login failed for username: {username}")
        return user
