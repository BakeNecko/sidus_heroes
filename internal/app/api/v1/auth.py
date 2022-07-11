import copy

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette import status

from internal.app.api.serializers import SingInSerializer, TokenSerializer
from internal.app.container import Container
from internal.db.repositories.user import UserRepository
from internal.models.schemas import InUserSchema, OutUserSchema
from internal.pkg.auth import AuthJWT

router = APIRouter()


@router.post(
    '/sign-up',
    status_code=status.HTTP_201_CREATED,
    response_model=OutUserSchema,
    name="auth:register",
)
@inject
async def sign_up(
        body: InUserSchema,
        auth: AuthJWT = Depends(Provide[Container.auth]),
        repository: UserRepository = Depends(Provide[Container.user_repository]),
):
    data = copy.copy(body)
    data.password = str(auth.encode_password(data.password))
    user = await repository.create(data)
    if user:
        return OutUserSchema(**user.dict())
    raise HTTPException(status.HTTP_400_BAD_REQUEST, 'User with current email or username already exists.')


@router.post(
    '/sign-in',
    status_code=status.HTTP_200_OK,
    response_model=TokenSerializer,
    name="auth:login",
)
@inject
async def sign_in(
        form_data: SingInSerializer = Body(),
        auth: AuthJWT = Depends(Provide[Container.auth]),
        repository: UserRepository = Depends(Provide[Container.user_repository]),
):
    """Я не стал париться над реализацией refresh токенов,
    и хранения их refreshSessions(id,user_id,refresh_token,fingerprint,ip, etc) в Redis.
    Т.к это рутина. info: https://gist.github.com/zmts/802dc9c3510d79fd40f9dc38a12bccfc
    """
    user = await repository.get(username=form_data.username)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'User with current username doesn`t exists.')
    if auth.verify_password(form_data.password, user.password):
        return TokenSerializer(token=auth.encode_token(user.id))
    raise HTTPException(status.HTTP_400_BAD_REQUEST, 'The passwords didn`t match')
