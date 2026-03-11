from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..services.fiat_service import get_all_fiat_rates, get_fiat_rate

router = APIRouter(prefix="/fiat", tags=["fiat"])

@router.get("/rates", response_model=Dict[str, float])
async def get_rates(base: str = "USD", db: Session = Depends(get_db)):
    rates = await get_all_fiat_rates(base, db)
    if not rates:
        raise HTTPException(status_code=503, detail="Unable to fetch fiat rates")
    return rates

@router.get("/rate/{target}")
async def get_rate(target: str, base: str = "USD", db: Session = Depends(get_db)):
    rate = await get_fiat_rate(target.upper(), base.upper(), db)
    if rate is None:
        raise HTTPException(status_code=404, detail=f"Rate for {target} not found")
    return {"base": base.upper(), "target": target.upper(), "rate": rate}