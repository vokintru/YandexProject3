import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class SortUrl(SqlAlchemyBase, UserMixin):
    __tablename__ = 'shorturls'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    textid = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<SortUrl> {self.id} {self.textid} {self.url}'
