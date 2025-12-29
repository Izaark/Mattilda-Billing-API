from fastapi import status
from .base import AppException


class EntityNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    
    def __init__(self, entity_name: str, entity_id: int):
        detail = f"{entity_name} with id {entity_id} not found"
        super().__init__(detail)


class EntityAlreadyExists(AppException):
    status_code = status.HTTP_409_CONFLICT
    
    def __init__(self, entity_name: str, field: str, value: str):
        detail = f"{entity_name} with {field}={value} already exists"
        super().__init__(detail)


class InvalidOperation(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message: str):
        super().__init__(message)


class ValidationError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message: str):
        super().__init__(message)


class DatabaseError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(self, operation: str):
        detail = f"Failed to {operation}"
        super().__init__(detail)

