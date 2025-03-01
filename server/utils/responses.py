from pydantic import BaseModel


class NotFoundMessage(BaseModel, frozen=True):
    message: str = "Resource not found"


class ConflictMessage(BaseModel, frozen=True):
    message: str = "Conflict"


class UnauthorizedMessage(BaseModel, frozen=True):
    message: str = "Unauthorized"
