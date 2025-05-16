from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from db import session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = session_factory()
    try:
        yield session  # NOSONAR
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()