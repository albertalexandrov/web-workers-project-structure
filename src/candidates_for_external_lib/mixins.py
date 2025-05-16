from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class ReprMixin:
    __repr_attrs__ = None

    def __repr__(self):
        if not self.__repr_attrs__:
            return super().__repr__()
        class_name, params = self.__class__.__name__, []
        for field in self.__repr_attrs__:
            value = getattr(self, field, "Атрибут не найден")
            params.append("{}={}".format(field, value))
        params = ", ".join(params)  # type: ignore[assignment]
        return f"{class_name}({params})"
