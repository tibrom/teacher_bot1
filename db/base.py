from databases import Database
from sqlalchemy import create_engine, MetaData
import os




DATABASE_URL = "postgresql://root:root@teacher_db:5432/teacher_db" #os.getenv('DATABASE_URL')

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(
    DATABASE_URL,
)