from candidates_for_external_lib.repositories.base import BaseRepository
from models.users import User


class UsersRepository(BaseRepository):
    model = User