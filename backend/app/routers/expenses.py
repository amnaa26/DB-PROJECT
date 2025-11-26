from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _get_expense_or_404(expense_id: int, db: Session) -> models.Expense:
    expense = db.query(models.Expense).get(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


def _ensure_itinerary_access(
    itinerary_id: int, db: Session, current_user: models.User
) -> None:
    itinerary = db.query(models.Itinerary).get(itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    if itinerary.user_id != current_user.user_id and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Not permitted")


@router.post("/", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ensure_itinerary_access(payload.itinerary_id, db, current_user)
    expense = models.Expense(**payload.dict())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=List[schemas.ExpenseRead])
def list_expenses(
    itinerary_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Expense)
    if itinerary_id:
        _ensure_itinerary_access(itinerary_id, db, current_user)
        query = query.filter(models.Expense.itinerary_id == itinerary_id)
    elif current_user.user_type != "admin":
        query = query.join(models.Itinerary).filter(
            models.Itinerary.user_id == current_user.user_id
        )
    return query.order_by(models.Expense.expense_id.desc()).all()


@router.put("/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(
    expense_id: int,
    payload: schemas.ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = _get_expense_or_404(expense_id, db)
    _ensure_itinerary_access(expense.itinerary_id, db, current_user)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = _get_expense_or_404(expense_id, db)
    _ensure_itinerary_access(expense.itinerary_id, db, current_user)
    db.delete(expense)
    db.commit()

