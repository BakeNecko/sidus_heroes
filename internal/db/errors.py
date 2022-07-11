from enum import Enum


class DBException(Exception):
    pass


class UserAlreadyExists(DBException):
    pass
