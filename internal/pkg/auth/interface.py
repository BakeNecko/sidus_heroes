import abc
from typing import Protocol


class Auth(Protocol):
    @abc.abstractmethod
    def encode_token(self, user_id: int | str):
        ...

    @abc.abstractmethod
    def decode_token(self, token: str) -> str:
        ...

    @staticmethod
    @abc.abstractmethod
    def verify_password(plain_password: str, hashed_password: bytes) -> bool:
        ...

    @staticmethod
    @abc.abstractmethod
    def encode_password(password: str) -> bytes:
        ...
