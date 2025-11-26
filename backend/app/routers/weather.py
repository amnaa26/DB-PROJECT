from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin, get_db

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("/", response_model=schemas.WeatherRead, status_code=status.HTTP_201_CREATED)
def create_weather_entry(
    payload: schemas.WeatherCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    weather = models.Weather(**payload.dict())
    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather


@router.get("/", response_model=List[schemas.WeatherRead])
def list_weather(db: Session = Depends(get_db)):
    return db.query(models.Weather).order_by(models.Weather.date.desc()).all()


@router.get("/{weather_id}", response_model=schemas.WeatherRead)
def get_weather(weather_id: int, db: Session = Depends(get_db)):
    weather = db.query(models.Weather).get(weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return weather


@router.put("/{weather_id}", response_model=schemas.WeatherRead)
def update_weather(
    weather_id: int,
    payload: schemas.WeatherUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    weather = db.query(models.Weather).get(weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather record not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(weather, key, value)
    db.commit()
    db.refresh(weather)
    return weather


@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(
    weather_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    weather = db.query(models.Weather).get(weather_id)
    if not weather:
        raise HTTPException(status_code=404, detail="Weather record not found")
    db.delete(weather)
    db.commit()

