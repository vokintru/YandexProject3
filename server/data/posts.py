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
    file_path = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    tegs = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    liked = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    orig_post = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    count_reposts = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    count_comments = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'<Post> id: {self.id} author: {self.author} text: {self.text} file_path: {self.file_path} ' \
               f'time: {self.time} liked: {self.liked} orig_post: {self.orig_post} count_reposts: {self.count_reposts} '
