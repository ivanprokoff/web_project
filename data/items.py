from data.db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Items(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'items'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    thing = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    multiplier = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=1)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    description = sqlalchemy.Column(sqlalchemy.String)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    creator = orm.relation('User')
    list_name = sqlalchemy.Column(sqlalchemy.String)
