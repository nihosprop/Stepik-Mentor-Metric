from enum import Enum


class Role(Enum):
    """Bot user roles."""

    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    VISITOR = 'visitor'
