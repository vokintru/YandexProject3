import datetime

import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class Post(SqlAlchemyBase, UserMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    tegs = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    liked = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

    def __repr__(self):
        return f'<Post> {self.id} {self.author} {self.text} {self.file} {self.time}'
