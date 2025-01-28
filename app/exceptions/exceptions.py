from typing import Optional

class BaseAppException(Exception):
    """Base exception class for application"""
    def __init__(self, message: str, status_code: int = 500, original_error: Optional[Exception] = None):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)

class DatabaseError(BaseAppException):
    """Database related errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Database error: {message}",
            status_code=500,
            original_error=original_error
        )

class QueryGenerationError(BaseAppException):
    """LLM query generation errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Query generation failed: {message}",
            status_code=500,
            original_error=original_error
        )

class SchemaError(BaseAppException):
    """Schema related errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"Schema error: {message}",
            status_code=500,
            original_error=original_error
        )

class ValidationError(BaseAppException):
    """Input validation errors"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Validation error: {message}",
            status_code=400
        )

class LLMServiceError(BaseAppException):
    """OpenAI API related errors"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"LLM service error: {message}",
            status_code=503,
            original_error=original_error
        )