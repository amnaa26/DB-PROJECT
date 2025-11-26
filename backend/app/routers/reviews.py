from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _get_review_or_404(review_id: int, db: Session) -> models.Review:
    review = db.query(models.Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


def _ensure_review_owner(review: models.Review, current_user: models.User) -> None:
    if review.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")


@router.post("/", response_model=schemas.ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Cannot create for other users")
    place = db.query(models.Place).get(payload.place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    review = models.Review(**payload.dict())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/", response_model=List[schemas.ReviewRead])
def list_reviews(
    place_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Review)
    if place_id:
        query = query.filter(models.Review.place_id == place_id)
    elif current_user.user_type != "admin":
        query = query.filter(models.Review.user_id == current_user.user_id)
    return query.order_by(models.Review.review_date.desc()).all()


@router.put("/{review_id}", response_model=schemas.ReviewRead)
def update_review(
    review_id: int,
    payload: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    review = _get_review_or_404(review_id, db)
    _ensure_review_owner(review, current_user)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(review, key, value)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    review = _get_review_or_404(review_id, db)
    _ensure_review_owner(review, current_user)
    db.delete(review)
    db.commit()

