class AuthException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code
