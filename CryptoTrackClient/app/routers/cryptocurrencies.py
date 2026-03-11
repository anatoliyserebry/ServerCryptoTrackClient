from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, crud
from ..database import get_db
from ..services.price_fetcher import fetch_all_prices
from ..services.fiat_service import get_fiat_rate

router = APIRouter(prefix="/crypto", tags=["cryptocurrencies"])

@router.get("/", response_model=List[schemas.Crypto])
async def get_cryptocurrencies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    vs_currency: str = Query("USD", description="Фиатная валюта для отображения цен")
):
    cryptos = crud.get_cryptocurrencies(db, skip=skip, limit=limit)
    if vs_currency.upper() == "USD":
        return cryptos

    rate = await get_fiat_rate(vs_currency.upper(), base="USD", db=db)
    if rate is None:
        raise HTTPException(status_code=400, detail=f"Unsupported fiat currency: {vs_currency}")

    for crypto in cryptos:
        if crypto.current_price:
            crypto.current_price = crypto.current_price * rate
        if crypto.market_cap:
            crypto.market_cap = crypto.market_cap * rate
        if crypto.volume_24h:
            crypto.volume_24h = crypto.volume_24h * rate
    return cryptos

@router.get("/{crypto_id}", response_model=schemas.Crypto)
async def get_crypto(
    crypto_id: int,
    db: Session = Depends(get_db),
    vs_currency: str = Query("USD", description="Фиатная валюта для отображения цены")
):
    crypto = crud.get_crypto(db, crypto_id)
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")

    if vs_currency.upper() != "USD":
        rate = await get_fiat_rate(vs_currency.upper(), base="USD", db=db)
        if rate is None:
            raise HTTPException(status_code=400, detail=f"Unsupported fiat currency: {vs_currency}")
        if crypto.current_price:
            crypto.current_price = crypto.current_price * rate
        if crypto.market_cap:
            crypto.market_cap = crypto.market_cap * rate
        if crypto.volume_24h:
            crypto.volume_24h = crypto.volume_24h * rate
    return crypto

@router.get("/{crypto_id}/history", response_model=List[schemas.PriceHistory])
def get_price_history(
    crypto_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_price_history(db, crypto_id, limit)

@router.post("/convert", response_model=schemas.ConversionResponse)
async def convert_currency(
    req: schemas.ConversionRequest,
    db: Session = Depends(get_db)
):
    from_cur = req.from_currency.upper()
    to_cur = req.to_currency.upper()
    amount = req.amount

    crypto_from = crud.get_crypto_by_symbol(db, from_cur)
    crypto_to = crud.get_crypto_by_symbol(db, to_cur)

    if crypto_from and crypto_to:
        if crypto_from.current_price is None or crypto_to.current_price is None:
            raise HTTPException(status_code=400, detail="Price data not available")
        rate = crypto_to.current_price / crypto_from.current_price
        converted = amount * rate
    elif crypto_from and not crypto_to:
        fiat_rate = await get_fiat_rate(to_cur, base="USD", db=db)
        if fiat_rate is None:
            raise HTTPException(status_code=400, detail=f"Unsupported fiat currency: {to_cur}")
        if crypto_from.current_price is None:
            raise HTTPException(status_code=400, detail="Price data not available")
        converted = amount * crypto_from.current_price * fiat_rate
        rate = crypto_from.current_price * fiat_rate
    elif not crypto_from and crypto_to:
        fiat_rate = await get_fiat_rate(from_cur, base="USD", db=db)
        if fiat_rate is None:
            raise HTTPException(status_code=400, detail=f"Unsupported fiat currency: {from_cur}")
        if crypto_to.current_price is None:
            raise HTTPException(status_code=400, detail="Price data not available")
        usd_amount = amount / fiat_rate
        converted = usd_amount / crypto_to.current_price
        rate = 1 / (crypto_to.current_price * fiat_rate)
    else:
        if from_cur == to_cur:
            converted = amount
            rate = 1.0
        else:
            rate = await get_fiat_rate(to_cur, base=from_cur, db=db)
            if rate is None:
                rate_from_usd = await get_fiat_rate(from_cur, base="USD", db=db)
                rate_to_usd = await get_fiat_rate(to_cur, base="USD", db=db)
                if rate_from_usd is None or rate_to_usd is None:
                    raise HTTPException(status_code=400, detail="Fiat conversion not available")
                rate = rate_to_usd / rate_from_usd
            converted = amount * rate

    return schemas.ConversionResponse(
        from_currency=from_cur,
        to_currency=to_cur,
        amount=amount,
        converted_amount=converted,
        rate=rate
    )

@router.post("/update-prices", response_model=dict)
async def update_prices(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(fetch_all_prices, db)
    return {"message": "Price update started"}