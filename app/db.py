from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Table,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import datetime

engine = create_engine("sqlite:///weather.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# users table
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String)


# favorites table
class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"))
    city = Column(String)


# weather caching table
class WeatherCache(Base):
    __tablename__ = "weather_cache"
    city = Column(String, primary_key=True)
    temperature = Column(Integer)
    condition = Column(String)
    fetched_at = Column(DateTime)


Base.metadata.create_all(bind=engine)

# ===== HELPER FUNTIONS =====


def reset_all_tables():
    with SessionLocal() as session:
        session.query(Favorite).delete()
        session.query(WeatherCache).delete()
        session.query(User).delete()
        session.commit()


# ~~~~ FAVORITES ~~~~


def normalize_city(city):
    return city.strip().lower()


def get_user_favorites(username):
    with SessionLocal() as db:
        results = db.query(Favorite).filter(Favorite.username == username).all()
        return [fav.city for fav in results]


def add_favorites(username, cities):
    with SessionLocal() as db:
        existing = set([normalize_city(c) for c in get_user_favorites(username)])
        for city in cities:
            norm_city = normalize_city(city)
            if norm_city not in existing:
                db.add(Favorite(username=username, city=norm_city))
        db.commit()


def remove_favorite(username, city):
    norm_city = normalize_city(city)
    with SessionLocal() as db:
        db.query(Favorite).filter(
            Favorite.username == username, Favorite.city == norm_city
        ).delete()
        db.commit()
