import enum


class UserRole(str, enum.Enum):
    guest = "guest"
    user = "user"
    editor = "editor"
    moderator = "moderator"
    admin = "admin"
    owner = "owner"
    banned = "banned"