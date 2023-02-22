from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from storage_app.db_config import Base
from storage_app.articles.models.db_article_models import Article


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(EmailType, unique=True, nullable=False, index=True)
    password = Column(String(50), nullable=False)

    articles = relationship('Article', back_populates="creator", passive_deletes=True)
