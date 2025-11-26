from fastapi import FastAPI

from .database import Base, engine
from .routers import (
    activities,
    auth_routes,
    cities,
    expenses,
    itineraries,
    places,
    reviews,
    users,
    weather,
)

app = FastAPI(title="Travel Planner API")

# IMPORTANT: Create all tables in Neon
Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(users.router)
app.include_router(itineraries.router)
app.include_router(cities.router)
app.include_router(places.router)
app.include_router(activities.router)
app.include_router(reviews.router)
app.include_router(expenses.router)
app.include_router(weather.router)
