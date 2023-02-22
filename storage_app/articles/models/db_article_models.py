from datetime import datetime
import enum

from sqlalchemy import Column, Text, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from storage_app.db_config import Base


class Language(enum.IntEnum):
    """Languages options"""
    ENGLISH = 1
    RUSSIAN = 2


class Category(enum.IntEnum):
    """Categories options"""
    DEVOPS = 1
    PYTHON = 2
    TESTING = 3
    JAVASCRIPT = 4
    OTHER = 5


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    brief_description = Column(Text, nullable=True)
    category = Column(Enum(Category))
    language = Column(Enum(Language), nullable=False)
    url = Column(URLType, nullable=True)
    file = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)

    creator = relationship("User", back_populates="articles")
