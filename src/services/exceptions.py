class AppError(Exception):
    """Základní chyba aplikace."""

class ConfigError(AppError):
    pass

class ValidationError(AppError):
    pass

class DatabaseError(AppError):
    pass

class TransactionError(AppError):
    pass
