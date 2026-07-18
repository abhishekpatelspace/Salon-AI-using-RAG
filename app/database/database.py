import os
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salon_ai.db")
if DATABASE_URL.startswith("mysql://"):
	DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine_kwargs: dict[str, Any] = {
	"pool_pre_ping": True,
}

if IS_SQLITE:
	engine_kwargs["connect_args"] = {"check_same_thread": False}
elif DATABASE_URL.startswith("mysql"):
	engine_kwargs["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "3600"))
	engine_kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
	engine_kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = scoped_session(
	sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
