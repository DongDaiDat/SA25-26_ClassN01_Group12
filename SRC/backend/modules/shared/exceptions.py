from rest_framework.exceptions import APIException

class BusinessRuleViolation(APIException):
    status_code = 422
    default_code = "BUSINESS_RULE_VIOLATION"
    default_detail = "Business rule violated"

    def __init__(self, code: str, message: str, details=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.code = code
        self.detail = message
        self.details = details or {}
        super().__init__(detail=message)

class ConflictError(BusinessRuleViolation):
    def __init__(self, code: str, message: str, details=None):
        super().__init__(code=code, message=message, details=details, status_code=409)
