from sqlalchemy import Column, Integer, String, create_engine, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=True)
    hlogin = Column(String(255), nullable=True)
    hpassword = Column(String(255), nullable=True)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    sex = Column(String(50), nullable=True)
    photo_avatar = Column(String(255), nullable=True)
    photo_banner = Column(String(255), nullable=True)
    subscriptions = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    is_group = Column(String(255), nullable=True)
    about_us = Column(String(255), nullable=True)
    date_create = Column(Date, nullable=True)
    photo_avatar = Column(String(255), nullable=True)
    photo_banner = Column(String(255), nullable=True)

    users = Column(String(255), nullable=True)
    messages = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Message(Base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    to_name = Column(String(255), nullable=True)
    date_create = Column(Date, nullable=True)
    message = Column(String(255), nullable=True)
    type_mess = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    author = Column(String(255), nullable=True)
    date_create = Column(DateTime, nullable=True)
    file = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    content = Column(String(255), nullable=True)
    likes = Column(String(255), nullable=True)
    comments = Column(String(255), nullable=True)
    views = Column(String(255), nullable=True)


    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=True)
    author = Column(String(255), nullable=True)
    date_create = Column(DateTime, nullable=True)
    message = Column(String(255), nullable=True)


    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)