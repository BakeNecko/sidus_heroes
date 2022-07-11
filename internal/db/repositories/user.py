from typing import Type

from internal.db.repositories.base import BaseRepository
from internal.db.tables.user import User
from internal.models.schemas import InUserSchema, UserSchema


class UserRepository(BaseRepository[InUserSchema, UserSchema, User]):
    @property
    def _in_schema(self) -> Type[InUserSchema]:
        return InUserSchema

    @property
    def _schema(self) -> Type[UserSchema]:
        return UserSchema

    @property
    def _table(self) -> Type[User]:
        return User
