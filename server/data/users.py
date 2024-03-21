import datetime
import random

import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    def __repr__(self):
        return f'<User> {self.id} {self.username} {self.modified_date}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Account(SqlAlchemyBase, UserMixin):
    __tablename__ = 'accounts'

    default_avatars = [
        "static/img/default_avatars/avatar0.png",
        "static/img/default_avatars/avatar1.png",
        "static/img/default_avatars/avatar2.png",
        "static/img/default_avatars/avatar3.png",
        "static/img/default_avatars/avatar4.png",
        "static/img/default_avatars/avatar5.png",
        "static/img/default_avatars/avatar6.png",
        "static/img/default_avatars/avatar7.png",
        "static/img/default_avatars/avatar8.png",
        "static/img/default_avatars/avatar9.png",
    ]

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bio = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=False, default=random.choice(default_avatars))
    followers = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default=[])
    follow = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default=[])

    def __repr__(self):
        return f'<User> {self.id} {self.username} {self.name} {self.avatar} {self.followers} {self.follow}'

