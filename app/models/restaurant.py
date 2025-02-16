from typing import Union

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm.session import Session

from app.models.db import BaseDatabase, database


class Restaurant(BaseDatabase):
    __tablename__ = "restaurant"
    name = Column(String)
    UniqueConstraint(name)

    @staticmethod
    def get(restaurant_id: int) -> Union[Session, None]:
        session = database.connnect_db()
        row = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if row:
            session.close()
            return row
        return None

    @staticmethod
    def get_or_create(name: str) -> Session:
        session = database.connnect_db()
        row = session.query(Restaurant).filter(Restaurant.name == name).first()
        if row:
            session.close()
            return row
        restaurant = Restaurant(name=name)
        session.add(restaurant)
        session.commit()

        row = session.query(Restaurant).filter(Restaurant.name == name).first()
        session.close()
        return row
