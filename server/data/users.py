import datetime

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

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bio = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    followers = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    follow = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    badges = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

    def __repr__(self):
        return f'<Account> {self.id} {self.name} {self.bio} {self.avatar} {self.followers} {self.follow} {self.badges}'

