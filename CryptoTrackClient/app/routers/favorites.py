from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, crud
from ..database import get_db
from ..auth import get_current_active_user

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.get("/", response_model=List[schemas.Favorite])
def get_favorites(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    return crud.get_user_favorites(db, current_user.id)

@router.post("/", response_model=schemas.Favorite)
def add_favorite(fav: schemas.FavoriteBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    crypto = crud.get_crypto(db, fav.crypto_id)
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")
    existing = db.query(models.Favorite).filter_by(user_id=current_user.id, crypto_id=fav.crypto_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")
    favorite = models.Favorite(user_id=current_user.id, crypto_id=fav.crypto_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite

@router.delete("/{crypto_id}", status_code=204)
def remove_favorite(crypto_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    favorite = db.query(models.Favorite).filter_by(user_id=current_user.id, crypto_id=crypto_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return