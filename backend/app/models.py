from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, Table, Time, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# MANY-TO-MANY: itineraries <-> cities
itinerary_cities = Table(
    "itinerary_cities",
    Base.metadata,
    Column("itinerary_id", Integer, ForeignKey("itineraries.itinerary_id", ondelete="CASCADE"), primary_key=True),
    Column("city_id", Integer, ForeignKey("cities.city_id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    email = Column(String(256), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    contact_info = Column(Text)
    user_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    itineraries = relationship("Itinerary", back_populates="owner", cascade="all, delete")
    reviews = relationship("Review", back_populates="author")

class Itinerary(Base):
    __tablename__ = "itineraries"
    itinerary_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    title = Column(String(255))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_budget = Column(Numeric(12,2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="itineraries")
    cities = relationship("City", secondary=itinerary_cities, back_populates="itineraries")
    activities = relationship("Activity", back_populates="itinerary")
    expenses = relationship("Expense", back_populates="itinerary")

class City(Base):
    __tablename__ = "cities"
    city_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    province = Column(String(255))

    places = relationship("Place", back_populates="city")
    weather = relationship("Weather", back_populates="city")
    itineraries = relationship("Itinerary", secondary=itinerary_cities, back_populates="cities")

class Place(Base):
    __tablename__ = "places"
    place_id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.city_id", ondelete="SET NULL"))
    place_name = Column(String(255))
    description = Column(Text)
    category = Column(String(100))
    location = Column(JSON)

    city = relationship("City", back_populates="places")
    activities = relationship("Activity", back_populates="place")
    reviews = relationship("Review", back_populates="place")

class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.itinerary_id", ondelete="CASCADE"))
    place_id = Column(Integer, ForeignKey("places.place_id", ondelete="SET NULL"))
    day_no = Column(Integer)
    start_time = Column(Time)
    notes = Column(Text)

    itinerary = relationship("Itinerary", back_populates="activities")
    place = relationship("Place", back_populates="activities")

class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    place_id = Column(Integer, ForeignKey("places.place_id", ondelete="CASCADE"))
    rating = Column(Integer)
    rating_comment = Column(Text)
    review_date = Column(Date)

    author = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")

class Weather(Base):
    __tablename__ = "weather"
    weather_id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.city_id", ondelete="CASCADE"))
    date = Column(Date)
    temperature = Column(JSON)
    conditions = Column(String(255))

    city = relationship("City", back_populates="weather")

class Expense(Base):
    __tablename__ = "expenses"
    expense_id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.itinerary_id", ondelete="CASCADE"))
    description = Column(Text)
    amount = Column(Numeric(12,2))
    category = Column(String(100))

    itinerary = relationship("Itinerary", back_populates="expenses")
