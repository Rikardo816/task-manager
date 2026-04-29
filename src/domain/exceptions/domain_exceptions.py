class DomainException(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainException):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
        )


class AlreadyExistsError(DomainException):
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
            code="ALREADY_EXISTS",
        )


class UnauthorizedError(DomainException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, code="UNAUTHORIZED")


class ForbiddenError(DomainException):
    def __init__(
        self,
        message: str = "You don't have permission to perform this action",
    ) -> None:
        super().__init__(message=message, code="FORBIDDEN")


class BusinessRuleViolationError(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")
