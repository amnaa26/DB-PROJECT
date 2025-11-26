from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin, get_db

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post("/", response_model=schemas.CityRead, status_code=status.HTTP_201_CREATED)
def create_city(
    payload: schemas.CityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    city = models.City(**payload.dict())
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


@router.get("/", response_model=List[schemas.CityRead])
def list_cities(db: Session = Depends(get_db)):
    return db.query(models.City).order_by(models.City.name).all()


@router.get("/{city_id}", response_model=schemas.CityRead)
def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(models.City).get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.put("/{city_id}", response_model=schemas.CityRead)
def update_city(
    city_id: int,
    payload: schemas.CityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    city = db.query(models.City).get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(city, key, value)
    db.commit()
    db.refresh(city)
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    city = db.query(models.City).get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    db.delete(city)
    db.commit()

