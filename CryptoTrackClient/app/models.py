from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    fcm_token = Column(String, nullable=True)

    favorites = relationship("Favorite", back_populates="user")

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    favorites = relationship("Favorite", back_populates="cryptocurrency")
    price_history = relationship("PriceHistory", back_populates="cryptocurrency")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    cryptocurrency = relationship("Cryptocurrency", back_populates="favorites")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    crypto_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    cryptocurrency = relationship("Cryptocurrency", back_populates="price_history")

class FiatRate(Base):
    __tablename__ = "fiat_rates"
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String, nullable=False)
    target_currency = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint('base_currency', 'target_currency', name='_base_target_uc'),)