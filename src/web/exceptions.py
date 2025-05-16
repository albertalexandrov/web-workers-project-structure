class RequestBodyValidationError(Exception):
    def __init__(self, validation_errors: dict) -> None:
        self.validation_errors = validation_errors
