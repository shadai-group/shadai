class IngestionError(Exception):
    """Raised when there's an error during the file ingestion process."""

    pass


class IntelligenceAPIError(Exception):
    """Raised when an Intelligence API request fails."""

    pass


class ConfigurationError(Exception):
    """Raised when there's an error in the configuration."""

    pass
