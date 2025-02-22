class ContactMergeConflict(Exception):
    def __init__(self, message="Contact merge conflict detected"):
        self.message = message
        super().__init__(self.message)

class RateLimitExceeded(Exception):
    """Custom rate limit exception"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass