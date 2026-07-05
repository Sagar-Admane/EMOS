class RouterError(Exception):
    """Base exception for ai router errors."""


class UnsupportedIntentError(RouterError):
    """Raised when the router cannot resolve a supported intent."""


class MissingConfigurationError(RouterError):
    """Raised when a required routing configuration is missing."""
