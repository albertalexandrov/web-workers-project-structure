from typing import Callable

from fastapi.requests import Request
from fastapi.responses import Response


async def example_middleware(request: Request, call_next: Callable) -> Response:
    # пример миддлвари
    print(f"Поступил запрос на {request.url}")
    return await call_next(request)