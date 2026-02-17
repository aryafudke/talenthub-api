from typing import Any, Optional, Dict


class TalentHubException(Exception):
    """Base exception for all TalentHub errors"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# ==================== NOT FOUND EXCEPTIONS ====================

class NotFoundException(TalentHubException):
    """Resource not found"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code=f"{resource.upper()}_NOT_FOUND",
            status_code=404
        )


class EmployeeNotFoundException(NotFoundException):
    def __init__(self, employee_id: Any):
        super().__init__("Employee", employee_id)


class DepartmentNotFoundException(NotFoundException):
    def __init__(self, department_id: Any):
        super().__init__("Department", department_id)


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: Any):
        super().__init__("User", user_id)


# ==================== DUPLICATE EXCEPTIONS ====================

class DuplicateException(TalentHubException):
    """Resource already exists"""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            code=f"DUPLICATE_{resource.upper()}_{field.upper()}",
            status_code=400
        )


class DuplicateEmailException(DuplicateException):
    def __init__(self, email: str):
        super().__init__("Employee", "email", email)


class DuplicateEmployeeIdException(DuplicateException):
    def __init__(self, employee_id: str):
        super().__init__("Employee", "employee_id", employee_id)


class DuplicateDepartmentNameException(DuplicateException):
    def __init__(self, name: str):
        super().__init__("Department", "name", name)


# ==================== AUTH EXCEPTIONS ====================

class AuthenticationException(TalentHubException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401
        )


class InvalidCredentialsException(AuthenticationException):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenException(AuthenticationException):
    def __init__(self):
        super().__init__("Invalid or expired token")


# ==================== AUTHORIZATION EXCEPTIONS ====================

class AuthorizationException(TalentHubException):
    """Not authorized to perform action"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            code="ACCESS_DENIED",
            status_code=403
        )


class InsufficientPermissionsException(AuthorizationException):
    def __init__(self, required_roles: list):
        roles_str = ", ".join(required_roles)
        super().__init__(f"Access denied. Required roles: {roles_str}")


# ==================== VALIDATION EXCEPTIONS ====================

class ValidationException(TalentHubException):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


# ==================== AI/LLM EXCEPTIONS ====================

class SmartSearchException(TalentHubException):
    """Smart search failed"""
    
    def __init__(self, message: str = "Failed to process search query"):
        super().__init__(
            message=message,
            code="SMART_SEARCH_ERROR",
            status_code=500
        )