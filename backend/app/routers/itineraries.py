from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


def _get_itinerary_or_404(itinerary_id: int, db: Session) -> models.Itinerary:
    itinerary = db.query(models.Itinerary).get(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


def _enforce_owner_or_admin(
    itinerary: models.Itinerary, current_user: models.User
) -> None:
    if itinerary.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Not permitted for this itinerary")


@router.post("/", response_model=schemas.ItineraryRead, status_code=201)
def create_itinerary(
    payload: schemas.ItineraryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Cannot create for other users")
    itinerary = models.Itinerary(**payload.dict())
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return itinerary


@router.get("/", response_model=List[schemas.ItineraryRead])
def list_itineraries(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Itinerary)
    if current_user.user_type != "admin":
        query = query.filter(models.Itinerary.user_id == current_user.user_id)
    return query.order_by(models.Itinerary.start_date).all()


@router.get("/{itinerary_id}", response_model=schemas.ItineraryRead)
def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    itinerary = _get_itinerary_or_404(itinerary_id, db)
    _enforce_owner_or_admin(itinerary, current_user)
    return itinerary


@router.put("/{itinerary_id}", response_model=schemas.ItineraryRead)
def update_itinerary(
    itinerary_id: int,
    payload: schemas.ItineraryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    itinerary = _get_itinerary_or_404(itinerary_id, db)
    _enforce_owner_or_admin(itinerary, current_user)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(itinerary, key, value)
    db.commit()
    db.refresh(itinerary)
    return itinerary


@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    itinerary = _get_itinerary_or_404(itinerary_id, db)
    _enforce_owner_or_admin(itinerary, current_user)
    db.delete(itinerary)
    db.commit()


@router.post("/{itinerary_id}/cities/{city_id}", status_code=201)
def add_city_to_itinerary(
    itinerary_id: int,
    city_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    itinerary = _get_itinerary_or_404(itinerary_id, db)
    _enforce_owner_or_admin(itinerary, current_user)
    city = db.query(models.City).get(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    if city in itinerary.cities:
        raise HTTPException(status_code=400, detail="City already in itinerary")
    itinerary.cities.append(city)
    db.commit()
    return {"detail": "City added"}


@router.delete("/{itinerary_id}/cities/{city_id}", status_code=204)
def remove_city_from_itinerary(
    itinerary_id: int,
    city_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    itinerary = _get_itinerary_or_404(itinerary_id, db)
    _enforce_owner_or_admin(itinerary, current_user)
    city = db.query(models.City).get(city_id)
    if not city or city not in itinerary.cities:
        raise HTTPException(status_code=404, detail="City not linked to itinerary")
    itinerary.cities.remove(city)
    db.commit()

from ..services.csp_scheduler import generate_schedule


@router.post("/plan", tags=["itineraries"])
def plan_itinerary(
    payload: schemas.ItineraryPlanRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    schedule = generate_schedule(
        activities=[act.dict() for act in payload.activities],
        start_date=payload.start_date,
        end_date=payload.end_date,
        constraints=payload.constraints
    )

    return schedule
