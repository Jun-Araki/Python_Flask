from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm.session import Session

from app.models.db import BaseDatabase, database


class User(BaseDatabase):
    __tablename__ = "user"
    name = Column(String)
    UniqueConstraint(name)

    @staticmethod
    def get_or_create(name) -> Session:
        session = database.connnect_db()
        row = session.query(User).filter(User.name == name).first()
        if row:
            session.close()
            return row
        user = User(name=name)
        session.add(user)
        session.commit()

        row = session.query(User).filter(User.name == name).first()
        session.close()
        return row
