"""
Custom exceptions for the application.

Provides domain-specific exceptions with HTTP status codes.
"""

from typing import Any, Optional


class AppException(Exception):
    """
    Base exception for application errors.

    Attributes:
        message: Error message
        status_code: HTTP status code
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize application exception."""
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        result = {"error": self.message, "status_code": self.status_code}
        if self.details:
            result["details"] = self.details
        return result


class NotFoundException(AppException):
    """
    Exception raised when resource is not found.

    Attributes:
        message: Error message
        resource_type: Type of resource that was not found
        resource_id: ID of the resource
    """

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
    ) -> None:
        """Initialize not found exception."""
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id is not None:
            details["resource_id"] = str(resource_id)

        super().__init__(message=message, status_code=404, details=details)


class ValidationException(AppException):
    """
    Exception raised when input validation fails.

    Attributes:
        message: Error message
        field: Field that failed validation
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
    ) -> None:
        """Initialize validation exception."""
        details = {}
        if field:
            details["field"] = field

        super().__init__(message=message, status_code=422, details=details)


class BusinessRuleException(AppException):
    """
    Exception raised when business rule is violated.

    Raised when an operation is not allowed according to business logic.

    Attributes:
        message: Error message
        rule: Business rule that was violated
    """

    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
    ) -> None:
        """Initialize business rule exception."""
        details = {}
        if rule:
            details["violated_rule"] = rule

        super().__init__(message=message, status_code=400, details=details)


class ConflictException(AppException):
    """
    Exception raised when there's a conflict with existing data.

    Attributes:
        message: Error message
        conflict_type: Type of conflict
    """

    def __init__(
        self,
        message: str,
        conflict_type: Optional[str] = None,
    ) -> None:
        """Initialize conflict exception."""
        details = {}
        if conflict_type:
            details["conflict_type"] = conflict_type

        super().__init__(message=message, status_code=409, details=details)
