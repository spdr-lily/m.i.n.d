from enum import Enum
from typing import List


class Role(str, Enum):
    ADMIN = "admin"
    PSYCHOLOGIST = "psychologist"
    PSYCHIATRIST = "psychiatrist"
    RESEARCHER = "researcher"
    CLINICAL_SUPERVISOR = "clinical_supervisor"


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
    MANAGE_CONSENT = "manage:consent"
    READ_INFERENCE = "read:inference"
    RUN_INFERENCE = "run:inference"
    MANAGE_SYSTEM = "manage:system"


ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: [
        Permission.READ_PATIENT, Permission.WRITE_PATIENT, Permission.DELETE_PATIENT,
        Permission.READ_CONSULTATION, Permission.WRITE_CONSULTATION, Permission.DELETE_CONSULTATION,
        Permission.READ_DIAGNOSIS, Permission.WRITE_DIAGNOSIS,
        Permission.READ_REFERENCE, Permission.WRITE_REFERENCE,
        Permission.MANAGE_USERS, Permission.READ_AUDIT,
        Permission.MANAGE_CONSENT, Permission.READ_INFERENCE, Permission.RUN_INFERENCE,
        Permission.MANAGE_SYSTEM,
    ],
    Role.PSYCHIATRIST: [
        Permission.READ_PATIENT, Permission.WRITE_PATIENT,
        Permission.READ_CONSULTATION, Permission.WRITE_CONSULTATION,
        Permission.READ_DIAGNOSIS, Permission.WRITE_DIAGNOSIS,
        Permission.READ_REFERENCE, Permission.WRITE_REFERENCE,
        Permission.READ_AUDIT,
        Permission.READ_INFERENCE, Permission.RUN_INFERENCE,
    ],
    Role.PSYCHOLOGIST: [
        Permission.READ_PATIENT, Permission.WRITE_PATIENT,
        Permission.READ_CONSULTATION, Permission.WRITE_CONSULTATION,
        Permission.READ_DIAGNOSIS,
        Permission.READ_REFERENCE,
        Permission.READ_INFERENCE, Permission.RUN_INFERENCE,
    ],
    Role.CLINICAL_SUPERVISOR: [
        Permission.READ_PATIENT,
        Permission.READ_CONSULTATION,
        Permission.READ_DIAGNOSIS,
        Permission.READ_REFERENCE,
        Permission.READ_AUDIT,
        Permission.READ_INFERENCE,
        Permission.MANAGE_CONSENT,
    ],
    Role.RESEARCHER: [
        Permission.READ_PATIENT,
        Permission.READ_CONSULTATION,
        Permission.READ_DIAGNOSIS,
        Permission.READ_REFERENCE,
        Permission.READ_INFERENCE,
    ],
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
