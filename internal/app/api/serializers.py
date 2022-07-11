import pydantic


class SingInSerializer(pydantic.BaseModel):
    password: str
    username: str


class TokenSerializer(pydantic.BaseModel):
    token: str
