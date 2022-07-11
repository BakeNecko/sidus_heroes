from typing import TYPE_CHECKING, Callable

from dependency_injector import containers, providers

from internal.app.settings import GlobalSettings
from internal.db.database import PostgresDatabase
from internal.db.repositories.user import UserRepository
from internal.pkg.auth import AuthJWT
from internal.pkg.cache import RedisCache

if TYPE_CHECKING:
    from internal.pkg.auth import Auth
    from internal.pkg.cache import Cache


class Container(containers.DeclarativeContainer):
    # Need for @inject
    wiring_config = containers.WiringConfiguration(modules=[
        ".api.v1.users",
        ".api.v1.auth",
        ".api.dependencies",
    ])
    settings: Callable[..., GlobalSettings] = providers.ThreadLocalSingleton(
        GlobalSettings,
    )
    s = settings()

    cache: Callable[..., 'Cache'] = providers.ThreadLocalSingleton(
        RedisCache,
        host=s.REDIS_HOST,
        port=s.REDIS_PORT,
    )

    db: Callable[..., 'PostgresDatabase'] = providers.ThreadLocalSingleton(
        PostgresDatabase,
        db_url=s.ASYNC_DB_URL
    )

    auth: Callable[..., 'Auth'] = providers.Factory(
        AuthJWT,
        secret_key=s.SECRET_KEY,
    )

    user_repository: Callable[..., 'UserRepository'] = providers.Factory(
        UserRepository,
        context_async_session=db.provided.async_session,
    )
