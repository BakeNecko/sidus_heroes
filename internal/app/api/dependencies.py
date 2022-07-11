from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette import status

from internal.app.container import Container
from internal.db.repositories.user import UserRepository
from internal.pkg.auth import AuthJWT

if TYPE_CHECKING:
    from internal.models.schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@inject
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        repository: UserRepository = Depends(Provide[Container.user_repository]),
        auth: AuthJWT = Depends(Provide[Container.auth]),
) -> 'UserSchema':
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = auth.decode_token(token)
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await repository.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    return user
