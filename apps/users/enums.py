from enum import Enum


class DjangoChoicesEnum(Enum):
    @classmethod
    def choices(cls):
        return [(tag.value, tag.name) for tag in cls]


class UserRole(str, DjangoChoicesEnum):
    SUPERADMIN = "SuperAdmin"
    COMPANYADMIN = "CompanyAdmin"
    PARTICIPANT = "Participant"
