from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

engine = create_async_engine(settings.db.dsn, **settings.db.options)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
