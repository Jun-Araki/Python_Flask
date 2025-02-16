import logging

import pandas as pd
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from surprise import SVD, Dataset, NormalPredictor, Reader
from surprise.model_selection import cross_validate

import settings
from app.models.db import BaseDatabase, database
from app.models.restaurant import Restaurant
from app.models.user import User

logger = logging.getLogger(__name__)
TOP_RECOMMEND_RESTAURANT_NUM = 10


class Rate(BaseDatabase):
    __tablename__ = "rate"
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"))
    restaurant_id = Column(ForeignKey("restaurant.id", ondelete="CASCADE"))
    value = Column(Integer)
    UniqueConstraint(user_id, restaurant_id)

    @staticmethod
    def update_or_create(user: User, restaurant: Restaurant, value: int) -> None:
        session = database.connnect_db()
        rate = (
            session.query(Rate)
            .filter(Rate.user_id == user.id, Rate.restaurant_id == restaurant.id)
            .first()
        )
        if rate:
            rate.value = value
            session.add(rate)
            session.commit()
            session.close()
            return rate
        rate = Rate(user_id=user.id, restaurant_id=restaurant.id, value=value)
        session.add(rate)
        session.commit()
        session.close()

    def recommend_restaurant(user: User) -> list:
        """Use machine learning to measure recommended restaurants and return the name of the recommended restaurant

        Args:
            user: User object you want to recommend
        Returns: A list of recommended restaurant names
        """
        if not settings.RECOMMEND_ENGIN_ENABLE:
            session = database.connnect_db()
            recommend = [
                r.name
                for r in session.query(Restaurant).all()[:TOP_RECOMMEND_RESTAURANT_NUM]
            ]
            session.close()
            return recommend

        session = database.connnect_db()
        df = pd.read_sql("SELECT user_id, restaurant_id, value from rate", session.bind)
        session.close()

        dataset_columns = ["user_id", "restaurant_id", "value"]
        reader = Reader()
        data = Dataset.load_from_df(df[dataset_columns], reader)
        try:
            cross_validate(NormalPredictor(), data, cv=2)
        except ValueError as ex:
            logger.error({"action": "recommended_restaurant", "error": ex})
            return None

        svd = SVD()

        trainset = data.build_full_trainset()
        svd.fit(trainset)

        predict_df = df.copy()
        item_id = "restaurant_id"
        predict_df["Predicted_Score"] = predict_df[item_id].apply(
            lambda x: svd.predict(user.id, x).est
        )
        predict_df = predict_df.sort_values(by=["Predicted_Score"], ascending=False)
        predict_df = predict_df.drop_duplicates(subset=item_id)

        if predict_df is None:
            logger.error(
                {"action": "recommended_restaurant", "status": "no predict data"}
            )
            return []

        recommended_restaurants = []
        for index, row in predict_df.iterrows():
            restaurant_id = int(row["restaurant_id"])
            restaurant = Restaurant.get(restaurant_id)
            recommended_restaurants.append(restaurant.name)

        return recommended_restaurants[:TOP_RECOMMEND_RESTAURANT_NUM]
