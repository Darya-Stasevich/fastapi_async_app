import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, validator


class Language(int, Enum):
    ENGLISH = 1
    RUSSIAN = 2


class Category(int, Enum):
    DEVOPS = 1
    PYTHON = 2
    TESTING = 3
    JAVASCRIPT = 4
    OTHER = 5


class ArticleCreate(BaseModel):
    title: str
    brief_description: Optional[str] = None
    category: Category
    language: Language
    url: Optional[HttpUrl] = None
    file: Optional[str] = None

    @validator('title')
    def validate_title(cls, value):
        if value.replace(' ', '') == '' or len(value) > 100:
            raise ValueError("Title can't be empty or longer than 100 symbols")
        return value

    @validator('brief_description')
    def validate_brief_description(cls, value):
        if value:
            if len(value) > 250:
                raise ValueError("Comment can't be longer than 250 symbols")
        return value

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        use_enum_values = True


class ArticleOut(ArticleCreate):
    id: int
    user_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ArticlePatch(BaseModel):
    title: str = None
    brief_description: Optional[str] = None
    category: Category = None
    language: Language = None
    url: Optional[HttpUrl] = None
    file: Optional[str] = None
