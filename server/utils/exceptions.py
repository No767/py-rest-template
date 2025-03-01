from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self):
        self.status_code = 404
        self.detail = "Resource not found"


class ConflictException(HTTPException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Conflict"


class UnauthorizedException(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = "Unauthorized"
