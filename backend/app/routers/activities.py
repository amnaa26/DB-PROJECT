from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/activities", tags=["activities"])


def _get_activity_or_404(activity_id: int, db: Session) -> models.Activity:
    activity = db.query(models.Activity).get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


def _ensure_itinerary_access(
    itinerary_id: int, db: Session, current_user: models.User
) -> models.Itinerary:
    itinerary = db.query(models.Itinerary).get(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    if itinerary.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")
    return itinerary


@router.post("/", response_model=schemas.ActivityRead, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ensure_itinerary_access(payload.itinerary_id, db, current_user)
    if payload.place_id:
        place = db.query(models.Place).get(payload.place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
    activity = models.Activity(**payload.dict())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.get("/", response_model=List[schemas.ActivityRead])
def list_activities(
    itinerary_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Activity)
    if itinerary_id:
        itinerary = _ensure_itinerary_access(itinerary_id, db, current_user)
        query = query.filter(models.Activity.itinerary_id == itinerary.itinerary_id)
    elif current_user.user_type != "admin":
        query = query.join(models.Itinerary).filter(
            models.Itinerary.user_id == current_user.user_id
        )
    return query.order_by(models.Activity.day_no).all()


@router.put("/{activity_id}", response_model=schemas.ActivityRead)
def update_activity(
    activity_id: int,
    payload: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity = _get_activity_or_404(activity_id, db)
    _ensure_itinerary_access(activity.itinerary_id, db, current_user)
    data = payload.dict(exclude_unset=True)
    if "place_id" in data and data["place_id"] is not None:
        place = db.query(models.Place).get(data["place_id"])
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")
    for key, value in data.items():
        setattr(activity, key, value)
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity = _get_activity_or_404(activity_id, db)
    _ensure_itinerary_access(activity.itinerary_id, db, current_user)
    db.delete(activity)
    db.commit()

