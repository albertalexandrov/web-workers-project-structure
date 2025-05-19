from typing import Any

# todo: тоже в принципе можно вынести в библиотеку вместе с их обработчиками


class RequestBodyValidationError(Exception):
    def __init__(self, validation_errors: dict) -> None:
        self.validation_errors = validation_errors


class NotFoundError(Exception):
    def __init__(self, error: str = "Не найдено") -> None:
        self.error = error


class BadRequestError(Exception):
    def __init__(self, error: Any) -> None:
        self.error = error


class AnyBodyBadRequestError(Exception):
    def __init__(self, body: Any):
        self.body = body
