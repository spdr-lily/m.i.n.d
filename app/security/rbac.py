from enum import Enum
from typing import List, Optional
from uuid import UUID


class Role(str, Enum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    VIEWER = "viewer"


class Permission(str, Enum):
    READ_PATIENT = "read:patient"
    WRITE_PATIENT = "write:patient"
    DELETE_PATIENT = "delete:patient"
    READ_CONSULTATION = "read:consultation"
    WRITE_CONSULTATION = "write:consultation"
    DELETE_CONSULTATION = "delete:consultation"
    READ_DIAGNOSIS = "read:diagnosis"
    WRITE_DIAGNOSIS = "write:diagnosis"
    READ_REFERENCE = "read:reference"
    WRITE_REFERENCE = "write:reference"
    MANAGE_USERS = "manage:users"
    READ_AUDIT = "read:audit"


ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: [
        Permission.READ_PATIENT, Permission.WRITE_PATIENT, Permission.DELETE_PATIENT,
        Permission.READ_CONSULTATION, Permission.WRITE_CONSULTATION, Permission.DELETE_CONSULTATION,
        Permission.READ_DIAGNOSIS, Permission.WRITE_DIAGNOSIS,
        Permission.READ_REFERENCE, Permission.WRITE_REFERENCE,
        Permission.MANAGE_USERS, Permission.READ_AUDIT,
    ],
    Role.CLINICIAN: [
        Permission.READ_PATIENT, Permission.WRITE_PATIENT,
        Permission.READ_CONSULTATION, Permission.WRITE_CONSULTATION,
        Permission.READ_DIAGNOSIS, Permission.WRITE_DIAGNOSIS,
        Permission.READ_REFERENCE,
    ],
    Role.VIEWER: [
        Permission.READ_PATIENT,
        Permission.READ_CONSULTATION,
        Permission.READ_DIAGNOSIS,
        Permission.READ_REFERENCE,
    ],
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
