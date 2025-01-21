class BaseAppException(Exception):
    """Base exception class for application"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(BaseAppException):
    """Database related errors"""
    pass

class QueryGenerationError(BaseAppException):
    """LLM query generation errors"""
    pass

class ValidationError(BaseAppException):
    """Input validation errors"""
    def __init__(self, message):
        super().__init__(message, status_code=400)