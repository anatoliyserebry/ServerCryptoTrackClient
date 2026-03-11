from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    fcm_token: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    fcm_token: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class CryptoBase(BaseModel):
    symbol: str
    name: str

class CryptoCreate(CryptoBase):
    pass

class Crypto(CryptoBase):
    id: int
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    last_updated: datetime
    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    crypto_id: int

class Favorite(FavoriteBase):
    id: int
    user_id: int
    added_at: datetime
    cryptocurrency: Crypto
    class Config:
        from_attributes = True

class PriceHistoryBase(BaseModel):
    crypto_id: int
    price: float
    timestamp: datetime

class PriceHistory(PriceHistoryBase):
    id: int
    class Config:
        from_attributes = True

class NotificationSettings(BaseModel):
    threshold_percent: float

class FiatRateSchema(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    last_updated: datetime
    class Config:
        from_attributes = True

class ConversionRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class ConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    converted_amount: float
    rate: float