from .base import metadata, engine, DATABASE_URL

from .data_base import chats




metadata.create_all(bind=engine)