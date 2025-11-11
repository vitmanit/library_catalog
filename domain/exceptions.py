class BookCatalogException(Exception):
    """Base exception for book catalog"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class BookNotFoundException(BookCatalogException):
    """Book not found exception"""
    pass


class BookAlreadyExistsException(BookCatalogException):
    """Book already exists exception"""
    pass


class ExternalServiceException(BookCatalogException):
    """External service error"""
    pass


class ValidationException(BookCatalogException):
    """Validation error"""
    pass