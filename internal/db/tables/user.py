from sqlalchemy import Column, Integer, LargeBinary, String, TypeDecorator

from internal.db.tables.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True)
    password = Column(String)
    username = Column(String(55), unique=True)
    email = Column(String(200), unique=True)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"username={self.username})>"
