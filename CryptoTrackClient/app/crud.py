from sqlalchemy.orm import Session
from . import models

def get_cryptocurrencies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Cryptocurrency).offset(skip).limit(limit).all()

def get_crypto(db: Session, crypto_id: int):
    return db.query(models.Cryptocurrency).filter(models.Cryptocurrency.id == crypto_id).first()

def get_crypto_by_symbol(db: Session, symbol: str):
    return db.query(models.Cryptocurrency).filter(models.Cryptocurrency.symbol == symbol).first()

def get_user_favorites(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()

def get_price_history(db: Session, crypto_id: int, limit: int = 100):
    return db.query(models.PriceHistory).filter(
        models.PriceHistory.crypto_id == crypto_id
    ).order_by(models.PriceHistory.timestamp.desc()).limit(limit).all()