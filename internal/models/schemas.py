from typing import Optional

from pydantic import BaseModel, constr


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


class UserSchemaBase(BaseSchema):
    username: str
    email: str


class UserSchemaUpdate(BaseSchema):
    username: Optional[str]
    email: Optional[str]


class InUserSchema(UserSchemaBase):
    password: constr(min_length=6, max_length=12)


class UserSchema(UserSchemaBase):
    id: int
    password: bytes


class OutUserSchema(UserSchemaBase):
    id: int
