from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_admin, get_db

router = APIRouter(prefix="/places", tags=["places"])


@router.post("/", response_model=schemas.PlaceRead, status_code=status.HTTP_201_CREATED)
def create_place(
    payload: schemas.PlaceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    city = db.query(models.City).get(payload.city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    place = models.Place(**payload.dict())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.get("/", response_model=List[schemas.PlaceRead])
def list_places(db: Session = Depends(get_db)):
    return db.query(models.Place).order_by(models.Place.place_name).all()


@router.get("/{place_id}", response_model=schemas.PlaceRead)
def get_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(models.Place).get(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.put("/{place_id}", response_model=schemas.PlaceRead)
def update_place(
    place_id: int,
    payload: schemas.PlaceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    place = db.query(models.Place).get(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    data = payload.dict(exclude_unset=True)
    if "city_id" in data:
        city = db.query(models.City).get(data["city_id"])
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
    for key, value in data.items():
        setattr(place, key, value)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    place = db.query(models.Place).get(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    db.delete(place)
    db.commit()

