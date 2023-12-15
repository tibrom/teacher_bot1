from .base import metadata, engine, DATABASE_URL

from .data_base import chats, lesson, lesson_info, message_index




metadata.create_all(bind=engine)