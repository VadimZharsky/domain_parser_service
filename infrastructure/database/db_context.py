
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DbContext:
    def __init__(self, url: str) -> None:
        self._engine = create_async_engine(url=f"sqlite+aiosqlite:///{url}", echo=False)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def session(self) -> AsyncSession:
        return self._session_factory()
