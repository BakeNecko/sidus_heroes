from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException
from jose import jwt

from internal.pkg.auth.interface import Auth


class AuthJWT(Auth):
    def __init__(self, secret_key: str, algo: str = 'HS256') -> None:
        self.secret_key = secret_key
        self.algo = algo

    def encode_token(self, user_id: int | str):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=30),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algo,
        )

    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algo])
            if payload.get('scope') == 'access_token':
                return payload['sub']
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail='Invalid token')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: bytes) -> bool:
        # SQLAlchemy ужасно работает с LargeBytes, по этому пароль хранится, как str(bytes(...))
        hashed_password = hashed_password.decode('utf-8')[2:-1]
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def encode_password(password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
