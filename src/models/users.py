from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from models.base import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
