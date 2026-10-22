class ExternalServiceError(Exception):
    """Base error for an unavailable or malformed external service."""


class ServiceUnavailableError(ExternalServiceError):
    """Raised after retrying a temporary external-service failure."""


class ExternalResponseError(ExternalServiceError):
    """Raised when an external service returns an invalid response."""


class CityNotFoundError(ExternalServiceError):
    """Raised when a requested city cannot be found."""


class CurrencyNotFoundError(ExternalServiceError):
    """Raised when a requested currency code cannot be found."""
