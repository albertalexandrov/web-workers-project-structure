from typing import Any

from web.exceptions import NotFoundError


class GetOr404Mixin:
    def get_or_404(self, instance: Any, error: str = "Объект не найден") -> Any:
        if not instance:
            raise NotFoundError(error=error)
        return instance
