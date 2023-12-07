import datetime
from sqlalchemy import Table, Column, String, Boolean, Integer, DateTime, ForeignKey

from .base import metadata


chats = Table(
    'chats',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('tg_chat_id', String),
    Column('name', String),
)

lesson = Table(
    'lesson',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('name', String),
    Column('description', String),
    Column('photo_id', String),
    Column('audio_id', String),
    Column('created_at', DateTime, default=datetime.datetime.utcnow()),
    Column('is_activ', Boolean),
)

lesson_info = Table(
    'lesson_info',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('lesson_id', Integer, ForeignKey('lesson.id', ondelete="CASCADE"), nullable=False),
    Column('name', String),
    Column('description', String),
    Column('photo_id', String),
    Column('audio_id', String),
    Column('created_at', DateTime, default=datetime.datetime.utcnow()),
    Column('is_activ', Boolean),
)