from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from internal.app.api.common import USER_CACHE_KEY
from internal.app.api.dependencies import get_current_user
from internal.app.container import Container
from internal.db.repositories.user import UserRepository
from internal.models.schemas import OutUserSchema, UserSchema, UserSchemaUpdate

router = APIRouter(tags=['users'])


@router.get('/me', status_code=status.HTTP_200_OK, response_model=OutUserSchema, name='user:me')
@inject
async def me(user: UserSchema = Depends(get_current_user)):
    return user


@router.get(
    '/get/{_id}',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    response_model=OutUserSchema,
    name="user:get"
)
@inject
async def get_user(
        _id: int,
        cache=Depends(Provide[Container.cache]),
        repository: UserRepository = Depends(Provide[Container.user_repository]),
):
    cache_key = USER_CACHE_KEY.format(id=_id)
    if cache_user := await cache.get(cache_key):
        return cache_user

    user = await repository.get_by_id(_id)

    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'User doesn`t exists')

    res = OutUserSchema(**user.dict())
    await cache.set(cache_key, res.dict(), 3600)

    return res


@router.patch('/me', status_code=status.HTTP_200_OK, response_model=OutUserSchema, name='user:update')
@inject
async def update_user(
        user_update: UserSchemaUpdate,
        user: UserSchema = Depends(get_current_user),
        cache=Depends(Provide[Container.cache]),
        repository: UserRepository = Depends(Provide[Container.user_repository])
):
    if res := await repository.update_by_id(_id=user.id, **user_update.dict(exclude_unset=True)):
        cache_key = USER_CACHE_KEY.format(id=user.id)
        await cache.remove_key(cache_key)
        return res
    raise HTTPException(status.HTTP_400_BAD_REQUEST, 'User doesn`t exists')


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT, response_class=Response, name='user:delete')
@inject
async def delete_user(
        user: UserSchema = Depends(get_current_user),
        repository: UserRepository = Depends(Provide[Container.user_repository])
):
    if not await repository.delete_by_id(user.id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content='User not found')
